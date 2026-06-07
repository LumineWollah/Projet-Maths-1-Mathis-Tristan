# calcul des normales pour le maillage
from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

from algo.trimestre_3.maillage import TriangleGrille
from algo.trimestre_3.vecteurs import Point3, Vecteur3, add, cross, normalize, scale, sub

NormaleSommet = Dict[Tuple[int, int], Vecteur3]


def normale_triangle(p0: Point3, p1: Point3, p2: Point3) -> Vecteur3:
    # produit vectoriel de deux arêtes du triangle
    e1 = sub(p1, p0)
    e2 = sub(p2, p0)
    return normalize(cross(e1, e2))


def normales_sommets_grille(
    grille: Sequence[Sequence[Point3]],
    triangles: Sequence[TriangleGrille],
) -> NormaleSommet:
    # moyenne des normales des faces autour de chaque sommet
    accum: Dict[Tuple[int, int], Vecteur3] = {}
    compte: Dict[Tuple[int, int], int] = {}

    for (i0, j0), (i1, j1), (i2, j2) in triangles:
        p0 = grille[i0][j0]
        p1 = grille[i1][j1]
        p2 = grille[i2][j2]
        n = normale_triangle(p0, p1, p2)
        for idx in ((i0, j0), (i1, j1), (i2, j2)):
            if idx not in accum:
                accum[idx] = (0.0, 0.0, 0.0)
                compte[idx] = 0
            accum[idx] = add(accum[idx], n)
            compte[idx] += 1

    resultat: NormaleSommet = {}
    for idx, vec in accum.items():
        resultat[idx] = normalize(scale(vec, 1.0 / compte[idx]))
    return resultat
