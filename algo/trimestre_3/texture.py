# coordonnées UV et texture procédurale pour l'extrusion
from __future__ import annotations

from typing import List, Sequence, Tuple

from algo.trimestre_3.vecteurs import Point3

UV = Tuple[float, float]
GrilleUV = List[List[UV]]
CouleurF = Tuple[float, float, float]


def grille_uv_extrusion(nb_traj: int, nb_profil: int) -> GrilleUV:
    # u le long du profil (j), v le long de la trajectoire (i)
    if nb_traj < 1 or nb_profil < 1:
        return []

    grille: GrilleUV = []
    for i in range(nb_traj):
        v = i / (nb_traj - 1) if nb_traj > 1 else 0.0
        ligne: List[UV] = []
        for j in range(nb_profil):
            u = j / (nb_profil - 1) if nb_profil > 1 else 0.0
            ligne.append((u, v))
        grille.append(ligne)
    return grille


def grille_uv_depuis_grille(grille: Sequence[Sequence[Point3]]) -> GrilleUV:
    if not grille or not grille[0]:
        return []
    return grille_uv_extrusion(len(grille), len(grille[0]))


def couleur_texture_damier(u: float, v: float, nb_cases: int = 10) -> CouleurF:
    # damier noir et blanc basé sur les UV
    u = max(0.0, min(1.0, u))
    v = max(0.0, min(1.0, v))
    case_u = int(u * nb_cases)
    case_v = int(v * nb_cases)
    if (case_u + case_v) % 2 == 0:
        return (0.92, 0.92, 0.92)
    return (0.18, 0.22, 0.28)


def couleur_base_texture(u: float, v: float, actif: bool) -> CouleurF:
    if not actif:
        from algo.trimestre_3.eclairage import COULEUR_BASE_EXTRUSION
        return COULEUR_BASE_EXTRUSION
    return couleur_texture_damier(u, v)
