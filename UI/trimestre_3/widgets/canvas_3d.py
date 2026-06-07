# widget 3D tkinter, rendu adaptatif rapide pendant le drag souris
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Sequence, Tuple

from algo.trimestre_3.courbes_3d import TypeCourbe, echantillonner_trajectoire
from algo.trimestre_3.eclairage import eclairage_phong_texture
from algo.trimestre_3.texture import GrilleUV
from algo.trimestre_3.maillage import TriangleGrille, points_des_triangles
from algo.trimestre_3.normales import NormaleSommet, normale_triangle, normales_sommets_grille
from algo.trimestre_3.vecteurs import Point3
from algo.trimestre_3.render.projection import Projecteur
from algo.trimestre_3.render.raster import Rasterizer

Grille3D = List[List[Point3]]


class Canvas3D(tk.Frame):
    def __init__(
        self,
        master=None,
        largeur: int = 800,
        hauteur: int = 600,
        points_controle: Optional[List[Point3]] = None,
        type_courbe: TypeCourbe = "bezier",
        **kwargs,
    ):
        super().__init__(master, **kwargs)

        self.largeur = largeur
        self.hauteur = hauteur

        self.projecteur = Projecteur(largeur, hauteur)
        self.projecteur.set_mode("orbite")
        self.raster = Rasterizer(largeur, hauteur)

        self.points_controle = points_controle or [
            (-2.0, 0.0, 0.0),
            (-1.0, 2.0, 1.0),
            (1.0, 2.0, -1.0),
            (2.0, 0.0, 0.0),
            (1.0, -2.0, 1.0),
            (-1.0, -2.0, -1.0),
        ]
        self.type_courbe: TypeCourbe = type_courbe
        self.nb_echantillons = 80

        self.grille: Optional[Grille3D] = None
        self.grille_uv: Optional[GrilleUV] = None
        self.triangles_grille: List[TriangleGrille] = []
        self.normales_sommets: NormaleSommet = {}
        self.utiliser_texture = False
        self.mode = "trajectoire"
        self.reseau_controle: Optional[Grille3D] = None

        self.souris_drag = False
        self.zoom_rapide = False
        self.souris_x0 = 0
        self.souris_y0 = 0
        self.sensibilite_souris = 0.005
        self.seuil_throttle = 2

        self._photo = None
        self._photo_ref = None
        self._mode_tkinter_rapide = False
        self._zoom_after_id = None

        self.canvas = tk.Canvas(self, width=largeur, height=hauteur, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.focus_set()

        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<ButtonPress-1>", self._on_souris_press)
        self.canvas.bind("<B1-Motion>", self._on_souris_motion)
        self.canvas.bind("<ButtonRelease-1>", self._on_souris_release)
        self.canvas.bind("<MouseWheel>", self._on_molette)
        self.canvas.bind("<Button-4>", self._on_molette_linux_up)
        self.canvas.bind("<Button-5>", self._on_molette_linux_down)

    def set_reseau_controle(self, reseau: Grille3D):
        self.reseau_controle = reseau
        self.mode = "reseau"
        self.redraw()

    def set_points_controle(self, points: List[Point3]):
        self.points_controle = points
        self.mode = "trajectoire"
        self.redraw()

    def set_type_courbe(self, type_courbe: TypeCourbe):
        self.type_courbe = type_courbe
        self.redraw()

    def set_surface(
        self,
        grille: Grille3D,
        triangles: Sequence[TriangleGrille],
        grille_uv: Optional[GrilleUV] = None,
    ):
        self.grille = grille
        self.grille_uv = grille_uv
        self.triangles_grille = list(triangles)
        self.normales_sommets = normales_sommets_grille(grille, triangles)
        self.mode = "surface"
        self.redraw()

    def set_texture_actif(self, actif: bool):
        self.utiliser_texture = actif
        self.redraw()

    def _on_resize(self, event):
        if event.width < 50 or event.height < 50:
            return
        self.largeur = event.width
        self.hauteur = event.height
        self.projecteur.redimensionner(event.width, event.height)
        self.raster.redimensionner(event.width, event.height)
        self.redraw()

    def _on_souris_press(self, event):
        self.souris_drag = True
        self.souris_x0 = event.x
        self.souris_y0 = event.y
        self.canvas.focus_set()

    def _on_souris_motion(self, event):
        if not self.souris_drag:
            return
        dx = event.x - self.souris_x0
        dy = event.y - self.souris_y0
        if abs(dx) + abs(dy) < self.seuil_throttle:
            return
        self.souris_x0 = event.x
        self.souris_y0 = event.y

        ax = self.projecteur.angle_orbite_x - dy * self.sensibilite_souris
        ay = self.projecteur.angle_orbite_y - dx * self.sensibilite_souris
        ax = max(-1.4, min(1.4, ax))
        self.projecteur.definir_orbite(ax, ay)
        self.redraw(rapide=True)

    def _on_souris_release(self, event):
        self.souris_drag = False
        self.zoom_rapide = False
        self.redraw(rapide=False)

    def _on_molette(self, event):
        if event.delta > 0:
            self.projecteur.ajuster_zoom(1.12)
        elif event.delta < 0:
            self.projecteur.ajuster_zoom(1.0 / 1.12)
        self.zoom_rapide = True
        self.redraw(rapide=True)
        self._planifier_fin_zoom()

    def _on_molette_linux_up(self, event):
        self.projecteur.ajuster_zoom(1.12)
        self.zoom_rapide = True
        self.redraw(rapide=True)
        self._planifier_fin_zoom()

    def _on_molette_linux_down(self, event):
        self.projecteur.ajuster_zoom(1.0 / 1.12)
        self.zoom_rapide = True
        self.redraw(rapide=True)
        self._planifier_fin_zoom()

    def _planifier_fin_zoom(self):
        if self._zoom_after_id is not None:
            self.after_cancel(self._zoom_after_id)
        self._zoom_after_id = self.after(180, self._fin_zoom)

    def _fin_zoom(self):
        self._zoom_after_id = None
        self.zoom_rapide = False
        self.redraw(rapide=False)

    def redraw(self, rapide: Optional[bool] = None):
        if rapide is None:
            rapide = self.souris_drag or self.zoom_rapide
        if rapide:
            self._redraw_rapide()
        else:
            self._redraw_haute_qualite()

    def _redraw_rapide(self):
        # wireframe tkinter natif, pas de z-buffer ni PhotoImage
        self._mode_tkinter_rapide = True
        self.canvas.delete("all")
        self._axes_tkinter()

        if self.mode == "surface" and self.grille and self.triangles_grille:
            self._wireframe_tkinter()
        elif self.mode == "reseau" and self.reseau_controle:
            self._reseau_tkinter()
        else:
            self._trajectoire_tkinter()

    def _axes_tkinter(self):
        origine = self.projecteur.projeter_point((0.0, 0.0, 0.0))
        if not origine:
            return
        for fin, col in [
            ((2.0, 0.0, 0.0), "#dd3333"),
            ((0.0, 2.0, 0.0), "#33bb33"),
            ((0.0, 0.0, 2.0), "#3355dd"),
        ]:
            bout = self.projecteur.projeter_point(fin)
            if bout:
                self.canvas.create_line(
                    origine[0], origine[1], bout[0], bout[1], fill=col, width=2,
                )

    def _redraw_haute_qualite(self):
        self._mode_tkinter_rapide = False
        self.raster.clear(utiliser_zbuffer=True)
        self._dessiner_axes_raster()

        if self.mode == "surface" and self.grille and self.triangles_grille:
            self._dessiner_surface_eclairee()
        elif self.mode == "reseau" and self.reseau_controle:
            self._dessiner_reseau_raster()
        else:
            self._dessiner_trajectoire_raster()

        self._afficher_buffer()

    def _reseau_tkinter(self):
        if not self.reseau_controle:
            return
        nu = len(self.reseau_controle)
        nv = len(self.reseau_controle[0])
        for i in range(nu):
            self._polyligne_tk(self._projeter_liste(self.reseau_controle[i]), "#666666")
        for j in range(nv):
            col = [self.reseau_controle[i][j] for i in range(nu)]
            self._polyligne_tk(self._projeter_liste(col), "#666666")
        for row in self.reseau_controle:
            for p in row:
                pe = self.projecteur.projeter_point(p)
                if pe:
                    self.canvas.create_oval(
                        pe[0] - 5, pe[1] - 5, pe[0] + 5, pe[1] + 5,
                        fill="#cc3333", outline="#881111",
                    )

    def _dessiner_reseau_raster(self):
        if not self.reseau_controle:
            return
        nu = len(self.reseau_controle)
        nv = len(self.reseau_controle[0])
        col_ligne = (100, 100, 100)
        col_pt = (200, 50, 50)
        for i in range(nu):
            pts = self._projeter_liste(self.reseau_controle[i])
            self.raster.tracer_polyligne(pts, col_ligne)
        for j in range(nv):
            col = [self.reseau_controle[i][j] for i in range(nu)]
            pts = self._projeter_liste(col)
            self.raster.tracer_polyligne(pts, col_ligne)
        for row in self.reseau_controle:
            for p in row:
                pe = self.projecteur.projeter_point(p)
                if pe:
                    self.raster.tracer_point(pe[0], pe[1], pe[2], col_pt, rayon=4)

    def _wireframe_tkinter(self):
        if not self.grille or not self.triangles_grille:
            return
        pas = max(1, len(self.triangles_grille) // 35)
        col = "#4488cc"

        for idx in range(0, len(self.triangles_grille), pas):
            tri_idx = self.triangles_grille[idx]
            pts_3d = []
            for i, j in tri_idx:
                pts_3d.append(self.grille[i][j])
            ecran = self._projeter_liste(pts_3d)
            if len(ecran) != 3:
                continue
            for a, b in ((0, 1), (1, 2), (2, 0)):
                self.canvas.create_line(
                    ecran[a][0], ecran[a][1], ecran[b][0], ecran[b][1],
                    fill=col, width=1,
                )

        # quelques lignes de structure sur la grille
        nu = len(self.grille)
        nv = len(self.grille[0]) if self.grille else 0
        pas_i = max(1, nu // 12)
        pas_j = max(1, nv // 4)
        for i in range(0, nu, pas_i):
            pts = self._projeter_liste(self.grille[i])
            self._polyligne_tk(pts, "#aaaaaa")
        for j in range(0, nv, pas_j):
            col_pts = self._projeter_liste([self.grille[i][j] for i in range(nu)])
            self._polyligne_tk(col_pts, "#aaaaaa")

    def _polyligne_tk(self, pts, couleur):
        if len(pts) < 2:
            return
        for k in range(len(pts) - 1):
            self.canvas.create_line(
                pts[k][0], pts[k][1], pts[k + 1][0], pts[k + 1][1],
                fill=couleur, width=1,
            )

    def _trajectoire_tkinter(self):
        trajectoire = echantillonner_trajectoire(
            self.points_controle,
            nb_points=max(20, self.nb_echantillons // 3),
            type_courbe=self.type_courbe,
        )
        pts = self._projeter_liste(trajectoire)
        self._polyligne_tk(pts, "#1e50c8")

    def _dessiner_trajectoire_raster(self):
        trajectoire = echantillonner_trajectoire(
            self.points_controle,
            nb_points=self.nb_echantillons,
            type_courbe=self.type_courbe,
        )
        pts_ecran = self._projeter_liste(trajectoire)
        pts_ctrl_ecran = self._projeter_liste(self.points_controle)
        self.raster.tracer_polyligne(pts_ecran, (30, 80, 200))
        for p in pts_ctrl_ecran:
            self.raster.tracer_point(p[0], p[1], p[2], (200, 40, 40), rayon=3)

    def _dessiner_surface_eclairee(self):
        if not self.grille or not self.triangles_grille:
            return
        oeil = self.projecteur.oeil

        for tri_idx in self.triangles_grille:
            (i0, j0), (i1, j1), (i2, j2) = tri_idx
            p0 = self.grille[i0][j0]
            p1 = self.grille[i1][j1]
            p2 = self.grille[i2][j2]

            # flat shading: une normale par face, les ombres ressortent mieux
            n_face = normale_triangle(p0, p1, p2)
            centre = (
                (p0[0] + p1[0] + p2[0]) / 3.0,
                (p0[1] + p1[1] + p2[1]) / 3.0,
                (p0[2] + p1[2] + p2[2]) / 3.0,
            )
            u_centre = v_centre = 0.5
            if self.grille_uv:
                uv0 = self.grille_uv[i0][j0]
                uv1 = self.grille_uv[i1][j1]
                uv2 = self.grille_uv[i2][j2]
                u_centre = (uv0[0] + uv1[0] + uv2[0]) / 3.0
                v_centre = (uv0[1] + uv1[1] + uv2[1]) / 3.0

            couleur = eclairage_phong_texture(
                centre, n_face, oeil, u_centre, v_centre, self.utiliser_texture,
            )

            e0 = self.projecteur.projeter_point(p0)
            e1 = self.projecteur.projeter_point(p1)
            e2 = self.projecteur.projeter_point(p2)
            if e0 and e1 and e2:
                self.raster.tracer_triangle(e0, e1, e2, couleur)

    def _projeter_liste(self, points_3d: List[Point3]):
        res = []
        for p in points_3d:
            pe = self.projecteur.projeter_point(p)
            if pe is not None:
                res.append(pe)
        return res

    def _dessiner_axes_raster(self):
        origine = self.projecteur.projeter_point((0.0, 0.0, 0.0))
        if origine is None:
            return
        for fin, col in [
            ((2.0, 0.0, 0.0), (220, 50, 50)),
            ((0.0, 2.0, 0.0), (50, 180, 50)),
            ((0.0, 0.0, 2.0), (50, 80, 220)),
        ]:
            bout = self.projecteur.projeter_point(fin)
            if bout:
                self.raster.tracer_ligne(
                    origine[0], origine[1], origine[2],
                    bout[0], bout[1], bout[2], col,
                )

    def _afficher_buffer(self):
        self._photo = tk.PhotoImage(width=self.largeur, height=self.hauteur)
        self._photo.put(self.raster.vers_chaine_photo())
        self._photo_ref = self._photo
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self._photo_ref)


class TestTrajectoire3DWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Test 3D - trajectoire projetée")
        self.geometry("900x700")

        top = ttk.Frame(self)
        top.pack(side="top", fill="x", pady=6)

        ttk.Label(
            top,
            text="Clic gauche + glisser = rotation (rapide), relâcher = rendu complet",
        ).pack(side="left", padx=8)

        self.var_type = tk.StringVar(value="bezier")
        ttk.Label(top, text="Courbe :").pack(side="left", padx=(16, 4))
        for label, val in [("Bézier", "bezier"), ("B-Spline", "bspline"), ("NURBS", "nurbs")]:
            ttk.Radiobutton(
                top, text=label, value=val,
                variable=self.var_type,
                command=self._changer_type,
            ).pack(side="left")

        ttk.Button(top, text="Redessiner", command=self._redessiner).pack(side="left", padx=12)

        self.canvas3d = Canvas3D(self, largeur=860, hauteur=620)
        self.canvas3d.pack(fill="both", expand=True, padx=10, pady=8)

    def _changer_type(self):
        self.canvas3d.set_type_courbe(self.var_type.get())

    def _redessiner(self):
        self.canvas3d.redraw(rapide=False)
