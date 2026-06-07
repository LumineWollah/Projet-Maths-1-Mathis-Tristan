# indices de maillage à partir d'une grille de points
from __future__ import annotations

from typing import List, Sequence, Tuple

from algo.trimestre_3.vecteurs import Point3

# un triangle sur la grille = 3 couples (i, j)
TriangleGrille = Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]
QuadGrille = Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int]]


def maillage_rectangulaire(nu: int, nv: int) -> Tuple[List[QuadGrille], List[TriangleGrille]]:
    # nu = nb points trajectoire, nv = nb points profil
    quads: List[QuadGrille] = []
    tris: List[TriangleGrille] = []

    for i in range(nu - 1):
        for j in range(nv - 1):
            a = (i, j)
            b = (i + 1, j)
            c = (i, j + 1)
            d = (i + 1, j + 1)
            quads.append((a, b, d, c))
            tris.append((a, b, c))
            tris.append((b, d, c))

    return quads, tris


def maillage_depuis_grille(grille: Sequence[Sequence[Point3]]) -> Tuple[List[QuadGrille], List[TriangleGrille]]:
    if not grille or not grille[0]:
        return [], []
    nu = len(grille)
    nv = len(grille[0])
    return maillage_rectangulaire(nu, nv)


def points_des_triangles(
    grille: Sequence[Sequence[Point3]],
    triangles: Sequence[TriangleGrille],
) -> List[Tuple[Point3, Point3, Point3]]:
    # convertit les indices grille en vrais points 3D
    resultat = []
    for (i0, j0), (i1, j1), (i2, j2) in triangles:
        p0 = grille[i0][j0]
        p1 = grille[i1][j1]
        p2 = grille[i2][j2]
        resultat.append((p0, p1, p2))
    return resultat
