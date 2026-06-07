# fenêtre extrusion : construction courbe 2D à gauche, surface 3D à droite
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Tuple, Union

from algo.trimestre_3.courbes_3d import TypeCourbe
from algo.trimestre_3.extrusion import (
    extruder,
    extruder_revolution_z,
    extruder_simple,
)
from algo.trimestre_3.maillage import maillage_depuis_grille
from algo.trimestre_3.profil_courbe import echantillonner_profil_2d
from algo.trimestre_3.texture import grille_uv_depuis_grille
from algo.trimestre_3.vecteurs import Point3
from UI.trimestre_3.widgets.canvas_3d import Canvas3D

Point2 = Tuple[float, float]


class ExtrusionWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Extrusion")
        self.geometry("1200x750")

        # points de contrôle 2D du profil
        self.points_controle_2d: List[Point2] = [
            (0.25, -0.45),
            (0.60, -0.15),
            (0.42, 0.25),
            (0.70, 0.55),
        ]
        self.drag_ctrl: Optional[Union[int, str]] = None
        self.drag_offset = (0.0, 0.0)

        # Extrusion généralisée demandée par le sujet : trajectoire dans le plan z = 0
        self.trajectoire_plane_z0: List[Point3] = [
            (-3.0, -0.6, 0.0),
            (-1.0, 1.2, 0.0),
            (1.0, -1.2, 0.0),
            (3.0, 0.6, 0.0),
        ]

        # Bonus : trajectoire 3D quelconque
        self.trajectoire_3d_bonus: List[Point3] = [
            (-3.0, 0.0, 0.0),
            (-1.0, 1.0, 1.0),
            (1.0, 1.0, -1.0),
            (3.0, 0.0, 0.0),
        ]

        self.var_primitive = tk.StringVar(value="simple")
        self.var_type_profil = tk.StringVar(value="bezier")
        self.var_type_traj = tk.StringVar(value="bezier")
        self.var_hauteur = tk.DoubleVar(value=2.0)
        self.var_echelle_debut = tk.DoubleVar(value=1.0)
        self.var_echelle_fin = tk.DoubleVar(value=0.6)
        self.var_nb_traj = tk.IntVar(value=32)
        self.var_nb_profil = tk.IntVar(value=32)
        self.var_texture = tk.BooleanVar(value=False)

        self._build_ui()
        self._bind_canvas_2d()
        self._dessiner_canvas_2d()
        self._recalculer_extrusion()

    def _build_ui(self):
        panneau = ttk.Panedwindow(self, orient="horizontal")
        panneau.pack(fill="both", expand=True, padx=8, pady=8)

        gauche = ttk.Frame(panneau, width=390)
        droite = ttk.Frame(panneau)
        panneau.add(gauche, weight=1)
        panneau.add(droite, weight=3)

        ttk.Label(
            gauche,
            text="Construction 2D : clic = point de contrôle, drag = déplacer",
        ).pack(anchor="w", padx=4, pady=4)

        self.canvas_2d = tk.Canvas(gauche, width=340, height=340, bg="white")
        self.canvas_2d.pack(padx=4, pady=4)

        ctrl = ttk.Frame(gauche)
        ctrl.pack(fill="x", padx=4, pady=6)

        ttk.Label(ctrl, text="Primitive").grid(row=0, column=0, sticky="w")
        prim_btns = ttk.Frame(ctrl)
        prim_btns.grid(row=0, column=1, sticky="w")
        for txt, val in [
            ("Extrusion simple", "simple"),
            ("Révolution autour de z", "revolution"),
            ("Extrusion généralisée z=0", "generalisee"),
            ("Bonus - courbe 3D quelconque", "bonus_3d"),
        ]:
            ttk.Radiobutton(
                prim_btns,
                text=txt,
                value=val,
                variable=self.var_primitive,
                command=self._recalculer_extrusion,
            ).pack(anchor="w")

        ttk.Label(ctrl, text="Courbe profil").grid(row=1, column=0, sticky="w", pady=(8, 0))
        profil_btns = ttk.Frame(ctrl)
        profil_btns.grid(row=1, column=1, sticky="w", pady=(8, 0))
        for txt, val in [("Bézier", "bezier"), ("B-Spline", "bspline"), ("NURBS", "nurbs")]:
            ttk.Radiobutton(
                profil_btns,
                text=txt,
                value=val,
                variable=self.var_type_profil,
                command=self._profil_change,
            ).pack(side="left")

        ttk.Label(ctrl, text="Courbe trajectoire").grid(row=2, column=0, sticky="w", pady=2)
        traj_btns = ttk.Frame(ctrl)
        traj_btns.grid(row=2, column=1, sticky="w")
        for txt, val in [("Bézier", "bezier"), ("B-Spline", "bspline"), ("NURBS", "nurbs")]:
            ttk.Radiobutton(
                traj_btns,
                text=txt,
                value=val,
                variable=self.var_type_traj,
                command=self._recalculer_extrusion,
            ).pack(side="left")

        ttk.Label(ctrl, text="Hauteur").grid(row=3, column=0, sticky="w", pady=4)
        ttk.Scale(
            ctrl,
            from_=0.2,
            to=4.0,
            variable=self.var_hauteur,
        ).grid(row=3, column=1, sticky="ew")

        ttk.Label(ctrl, text="Échelle début / rayon").grid(row=4, column=0, sticky="w")
        ttk.Scale(
            ctrl,
            from_=0.2,
            to=2.0,
            variable=self.var_echelle_debut,
        ).grid(row=4, column=1, sticky="ew")

        ttk.Label(ctrl, text="Échelle fin").grid(row=5, column=0, sticky="w")
        ttk.Scale(
            ctrl,
            from_=0.1,
            to=2.0,
            variable=self.var_echelle_fin,
        ).grid(row=5, column=1, sticky="ew")

        ttk.Label(ctrl, text="Pas trajectoire").grid(row=6, column=0, sticky="w")
        ttk.Spinbox(
            ctrl,
            from_=8,
            to=80,
            width=5,
            textvariable=self.var_nb_traj,
        ).grid(row=6, column=1, sticky="w")

        ttk.Label(ctrl, text="Pas profil").grid(row=7, column=0, sticky="w")
        ttk.Spinbox(
            ctrl,
            from_=8,
            to=80,
            width=5,
            textvariable=self.var_nb_profil,
        ).grid(row=7, column=1, sticky="w")

        ttk.Checkbutton(
            ctrl,
            text="Texture (Damier)",
            variable=self.var_texture,
            command=self._toggle_texture,
        ).grid(row=8, column=0, columnspan=2, sticky="w", pady=4)

        btns = ttk.Frame(ctrl)
        btns.grid(row=9, column=0, columnspan=2, pady=10)
        ttk.Button(btns, text="Générer", command=self._recalculer_extrusion).pack(side="left", padx=4)
        ttk.Button(btns, text="Effacer points", command=self._effacer_points).pack(side="left", padx=4)
        ttk.Button(btns, text="Profil demo", command=self._profil_demo).pack(side="left", padx=4)

        ctrl.columnconfigure(1, weight=1)

        ttk.Label(
            droite,
            text="Vue 3D : glisser = Wireframe, relâcher = rendu ombré",
        ).pack(anchor="w", padx=4)

        self.canvas3d = Canvas3D(droite, largeur=760, hauteur=660)
        self.canvas3d.pack(fill="both", expand=True, padx=4, pady=4)

    def _bind_canvas_2d(self):
        self.canvas_2d.bind("<ButtonPress-1>", self._clic_2d)
        self.canvas_2d.bind("<B1-Motion>", self._drag_2d)
        self.canvas_2d.bind("<ButtonRelease-1>", lambda e: setattr(self, "drag_ctrl", None))
        self.canvas_2d.bind("<Button-3>", self._suppr_point_2d)

    def _vers_canvas(self, uv: Point2) -> Tuple[float, float]:
        cx, cy = 170.0, 170.0
        echelle = 120.0
        return (cx + uv[0] * echelle, cy - uv[1] * echelle)

    def _vers_uv(self, x: float, y: float) -> Point2:
        cx, cy = 170.0, 170.0
        echelle = 120.0
        return ((x - cx) / echelle, (cy - y) / echelle)

    def _hit_controle(self, x, y) -> Optional[int]:
        for i, uv in enumerate(self.points_controle_2d):
            px, py = self._vers_canvas(uv)
            if (px - x) ** 2 + (py - y) ** 2 <= 64:
                return i
        return None

    def _clic_2d(self, event):
        hit = self._hit_controle(event.x, event.y)
        if hit is not None:
            uv = self.points_controle_2d[hit]
            px, py = self._vers_canvas(uv)
            self.drag_ctrl = hit
            self.drag_offset = (px - event.x, py - event.y)
            return

        self.points_controle_2d.append(self._vers_uv(event.x, event.y))
        self._dessiner_canvas_2d()
        self._recalculer_extrusion()

    def _drag_2d(self, event):
        if self.drag_ctrl is None:
            return

        uv = self._vers_uv(event.x + self.drag_offset[0], event.y + self.drag_offset[1])
        self.points_controle_2d[self.drag_ctrl] = uv
        self._dessiner_canvas_2d()
        self._recalculer_extrusion()

    def _suppr_point_2d(self, event):
        hit = self._hit_controle(event.x, event.y)
        if hit is not None and len(self.points_controle_2d) > 2:
            self.points_controle_2d.pop(hit)
            self.drag_ctrl = None
            self._dessiner_canvas_2d()
            self._recalculer_extrusion()

    def _effacer_points(self):
        self.points_controle_2d = []
        self._dessiner_canvas_2d()

    def _profil_demo(self):
        self.points_controle_2d = [
            (0.25, -0.45),
            (0.60, -0.15),
            (0.42, 0.25),
            (0.70, 0.55),
        ]
        self._dessiner_canvas_2d()
        self._recalculer_extrusion()

    def _profil_change(self):
        self._dessiner_canvas_2d()
        self._recalculer_extrusion()

    def _dessiner_canvas_2d(self):
        self.canvas_2d.delete("all")
        self.canvas_2d.create_rectangle(20, 20, 320, 320, outline="#dddddd")
        self.canvas_2d.create_line(20, 170, 320, 170, fill="#eeeeee")
        self.canvas_2d.create_line(170, 20, 170, 320, fill="#eeeeee")

        pts = self.points_controle_2d
        if len(pts) >= 2:
            for i in range(len(pts) - 1):
                a = self._vers_canvas(pts[i])
                b = self._vers_canvas(pts[i + 1])
                self.canvas_2d.create_line(*a, *b, fill="#bbbbbb", dash=(4, 3))

        if len(pts) >= 2:
            courbe = echantillonner_profil_2d(
                pts,
                nb_points=int(self.var_nb_profil.get()),
                type_courbe=self.var_type_profil.get(),
            )
            for i in range(len(courbe) - 1):
                a = self._vers_canvas(courbe[i])
                b = self._vers_canvas(courbe[i + 1])
                self.canvas_2d.create_line(*a, *b, fill="#1a5fcc", width=2)

        if self.var_primitive.get() == "revolution":
            self.canvas_2d.create_line(170, 20, 170, 320, fill="#ff9999", width=2)
            self.canvas_2d.create_text(
                178,
                30,
                text="axe z",
                fill="#cc5555",
                anchor="w",
                font=("Arial", 8),
            )

        for i, uv in enumerate(pts):
            x, y = self._vers_canvas(uv)
            self.canvas_2d.create_oval(x - 5, y - 5, x + 5, y + 5, fill="#cc3333", outline="#881111")
            self.canvas_2d.create_text(x + 10, y - 10, text=str(i), fill="#555555", font=("Arial", 8))

    def _centre_grille(self, grille: List[List[Point3]]) -> Point3:
        sx = sy = sz = 0.0
        n = 0
        for ligne in grille:
            for p in ligne:
                sx += p[0]
                sy += p[1]
                sz += p[2]
                n += 1

        if n == 0:
            return (0.0, 0.0, 0.0)
        return (sx / n, sy / n, sz / n)

    def _recalculer_extrusion(self):
        self._dessiner_canvas_2d()

        if len(self.points_controle_2d) < 2:
            return

        profil_2d = echantillonner_profil_2d(
            self.points_controle_2d,
            nb_points=int(self.var_nb_profil.get()),
            type_courbe=self.var_type_profil.get(),
        )
        if len(profil_2d) < 2:
            return

        primitive = self.var_primitive.get()

        if primitive == "simple":
            grille = extruder_simple(
                profil_2d=profil_2d,
                hauteur=float(self.var_hauteur.get()),
                echelle_debut=float(self.var_echelle_debut.get()),
                echelle_fin=float(self.var_echelle_fin.get()),
            )
        elif primitive == "revolution":
            grille = extruder_revolution_z(
                profil_2d=profil_2d,
                nb_angles=int(self.var_nb_traj.get()),
                hauteur=float(self.var_hauteur.get()),
                echelle_rayon=float(self.var_echelle_debut.get()),
            )
        elif primitive == "generalisee":
            grille = extruder(
                profil_2d=profil_2d,
                points_traj=self.trajectoire_plane_z0,
                nb_traj=int(self.var_nb_traj.get()),
                type_courbe=self.var_type_traj.get(),
                hauteur=float(self.var_hauteur.get()),
                echelle_debut=float(self.var_echelle_debut.get()),
                echelle_fin=float(self.var_echelle_fin.get()),
            )
        else:
            grille = extruder(
                profil_2d=profil_2d,
                points_traj=self.trajectoire_3d_bonus,
                nb_traj=int(self.var_nb_traj.get()),
                type_courbe=self.var_type_traj.get(),
                hauteur=float(self.var_hauteur.get()),
                echelle_debut=float(self.var_echelle_debut.get()),
                echelle_fin=float(self.var_echelle_fin.get()),
            )

        if not grille:
            return

        _, triangles = maillage_depuis_grille(grille)
        centre = self._centre_grille(grille)
        self.canvas3d.projecteur.definir_cible(centre)

        grille_uv = grille_uv_depuis_grille(grille)
        self.canvas3d.set_surface(grille, triangles, grille_uv)
        self.canvas3d.set_texture_actif(self.var_texture.get())

    def _toggle_texture(self):
        self.canvas3d.set_texture_actif(self.var_texture.get())