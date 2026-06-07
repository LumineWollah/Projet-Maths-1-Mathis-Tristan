# fenêtre surfaces de Bézier : réseau de contrôle + surface tensorielle
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from algo.trimestre_3.maillage import maillage_depuis_grille
from algo.trimestre_3.subdivision_surface import subdiviser_reseau_en_4
from algo.trimestre_3.surfaces_bezier import (
    reseau_bicubique_demo,
    surface_bezier_double_casteljau,
    surface_bezier_tensoriel_direct,
)
from algo.trimestre_3.texture import grille_uv_depuis_grille
from algo.trimestre_3.vecteurs import somme_points
from UI.trimestre_3.widgets.canvas_3d import Canvas3D


class SurfacesBezierWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Surfaces de Bézier - produit tensoriel")
        self.geometry("1200x750")

        self.reseau = reseau_bicubique_demo()
        self.var_pas_u = tk.IntVar(value=24)
        self.var_pas_v = tk.IntVar(value=24)
        self.var_methode = tk.StringVar(value="pascal")

        self._build_ui()
        self._afficher_reseau()

    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(side="top", fill="x", padx=8, pady=6)

        ttk.Label(
            top,
            text="Réseau bi-cubique | molette = zoom | clic+glisser = rotation",
        ).pack(side="left", padx=4)

        ttk.Label(top, text="Méthode").pack(side="left", padx=(12, 4))
        ttk.Radiobutton(
            top, text="Produit Tensoriel (Pascal)",
            variable=self.var_methode, value="pascal",
        ).pack(side="left")
        ttk.Radiobutton(
            top, text="Double De Casteljau",
            variable=self.var_methode, value="casteljau",
        ).pack(side="left", padx=(4, 0))

        ttk.Label(top, text="Pas u").pack(side="left", padx=(16, 2))
        ttk.Spinbox(top, from_=8, to=60, width=4, textvariable=self.var_pas_u).pack(side="left")
        ttk.Label(top, text="Pas v").pack(side="left", padx=(8, 2))
        ttk.Spinbox(top, from_=8, to=60, width=4, textvariable=self.var_pas_v).pack(side="left")

        ttk.Button(top, text="Générer", command=self._generer_surface).pack(side="left", padx=16)

        panneau = ttk.Panedwindow(self, orient="horizontal")
        panneau.pack(fill="both", expand=True, padx=8, pady=8)

        gauche = ttk.Frame(panneau)
        droite = ttk.Frame(panneau)
        panneau.add(gauche, weight=1)
        panneau.add(droite, weight=1)

        barre_gauche = ttk.Frame(gauche)
        barre_gauche.pack(fill="x", padx=4, pady=(4, 0))
        ttk.Label(barre_gauche, text="Réseau de contrôle 3D (filet)").pack(side="left")
        ttk.Button(
            barre_gauche, text="Subdiviser en 4",
            command=self._subdiviser_reseau,
        ).pack(side="right", padx=4)

        self.canvas_reseau = Canvas3D(gauche, largeur=560, height=620)
        self.canvas_reseau.pack(fill="both", expand=True, padx=4, pady=4)

        ttk.Label(droite, text="Surface générée (relâcher souris = ombres)").pack(anchor="w", padx=4)
        self.canvas_surface = Canvas3D(droite, largeur=560, height=620)
        self.canvas_surface.pack(fill="both", expand=True, padx=4, pady=4)

    def _centre_reseau(self):
        n = 0
        sx = sy = sz = 0.0
        for row in self.reseau:
            for p in row:
                sx += p[0]
                sy += p[1]
                sz += p[2]
                n += 1
        if n == 0:
            return (0.0, 0.0, 0.0)
        return (sx / n, sy / n, sz / n)

    def _afficher_reseau(self):
        centre = self._centre_reseau()
        self.canvas_reseau.projecteur.definir_cible(centre)
        self.canvas_reseau.set_reseau_controle(self.reseau)

    def _subdiviser_reseau(self):
        if len(self.reseau) < 2 or len(self.reseau[0]) < 2:
            return
        self.reseau = subdiviser_reseau_en_4(self.reseau)
        self._afficher_reseau()

    def _generer_surface(self):
        pas_u = int(self.var_pas_u.get())
        pas_v = int(self.var_pas_v.get())

        if self.var_methode.get() == "casteljau":
            grille = surface_bezier_double_casteljau(self.reseau, pas_u, pas_v)
        else:
            grille = surface_bezier_tensoriel_direct(self.reseau, pas_u, pas_v)

        if not grille:
            return

        _, triangles = maillage_depuis_grille(grille)
        grille_uv = grille_uv_depuis_grille(grille)

        centre = somme_points([p for row in grille for p in row])
        n = len(grille) * len(grille[0])
        self.canvas_surface.projecteur.definir_cible((centre[0] / n, centre[1] / n, centre[2] / n))
        self.canvas_surface.set_surface(grille, triangles, grille_uv)
        self.canvas_surface.redraw(rapide=False)
