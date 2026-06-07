# surface de Bézier par produit tensoriel direct
from __future__ import annotations

import math
from typing import List, Sequence

from algo.trimestre_3.pascal import binom
from algo.trimestre_3.courbes_3d import bezier_de_casteljau_3d
from algo.trimestre_3.vecteurs import Point3

Reseau3D = List[List[Point3]]
GrilleSurface = List[List[Point3]]


def bernstein(n: int, i: int, t: float) -> float:
    # calcul de bernstein avec pascal (binom pour le coefficient)
    if i < 0 or i > n:
        return 0.0
    if t < 0.0:
        t = 0.0
    elif t > 1.0:
        t = 1.0
    return binom(n, i) * (t ** i) * ((1.0 - t) ** (n - i))


def point_surface_tensoriel(reseau_pts: Sequence[Sequence[Point3]], u: float, v: float) -> Point3:
    # produit tensoriel S(u,v) = somme_i somme_j B_i(u) B_j(v) P_ij
    nu = len(reseau_pts)
    nv = len(reseau_pts[0]) if nu > 0 else 0
    if nu < 1 or nv < 1:
        return (0.0, 0.0, 0.0)

    n = nu - 1
    m = nv - 1
    x = y = z = 0.0

    for i in range(nu):
        bu = bernstein(n, i, u)
        for j in range(nv):
            bv = bernstein(m, j, v)
            w = bu * bv
            p = reseau_pts[i][j]
            x += w * p[0]
            y += w * p[1]
            z += w * p[2]

    return (x, y, z)


def surface_bezier_tensoriel_direct(
    reseau_pts: Sequence[Sequence[Point3]],
    pas_u: int = 20,
    pas_v: int = 20,
) -> GrilleSurface:
    # echantillonne la surface sur une grille (u,v)
    return _surface_bezier_echantillon(reseau_pts, pas_u, pas_v, point_surface_tensoriel)


def _extraire_patch(reseau: Sequence[Sequence[Point3]], i0: int, j0: int) -> Reseau3D:
    patch: Reseau3D = []
    for i in range(i0, i0 + 4):
        patch.append([reseau[i][j] for j in range(j0, j0 + 4)])
    return patch


def _surface_bezier_echantillon(
    reseau_pts: Sequence[Sequence[Point3]],
    pas_u: int,
    pas_v: int,
    point_fn,
) -> GrilleSurface:
    if pas_u < 2:
        pas_u = 2
    if pas_v < 2:
        pas_v = 2
    if len(reseau_pts) < 2 or len(reseau_pts[0]) < 2:
        return []

    nu = len(reseau_pts)
    nv = len(reseau_pts[0])
    npu = (nu - 1) // 3
    npv = (nv - 1) // 3
    multi_patch = npu >= 2 and npv >= 2 and (nu - 1) % 3 == 0 and (nv - 1) % 3 == 0

    grille: GrilleSurface = []
    for iu in range(pas_u):
        u = iu / (pas_u - 1)
        ligne: List[Point3] = []
        for iv in range(pas_v):
            v = iv / (pas_v - 1)
            if multi_patch:
                pu = min(u * npu, npu - 1e-9)
                pv = min(v * npv, npv - 1e-9)
                iu_p = int(pu)
                iv_p = int(pv)
                u_loc = pu - iu_p
                v_loc = pv - iv_p
                patch = _extraire_patch(reseau_pts, iu_p * 3, iv_p * 3)
                ligne.append(point_fn(patch, u_loc, v_loc))
            else:
                ligne.append(point_fn(reseau_pts, u, v))
        grille.append(ligne)
    return grille


def point_surface_double_casteljau(
    reseau_pts: Sequence[Sequence[Point3]], u: float, v: float
) -> Point3:
    # double de casteljau: casteljau en u sur chaque colonne puis en v sur la ligne obtenue
    nu = len(reseau_pts)
    nv = len(reseau_pts[0]) if nu > 0 else 0
    if nu < 1 or nv < 1:
        return (0.0, 0.0, 0.0)

    intermediaires: List[Point3] = []
    for j in range(nv):
        colonne = [reseau_pts[i][j] for i in range(nu)]
        # appel de la fonction de De Casteljau du premier projet
        intermediaires.append(bezier_de_casteljau_3d(colonne, u))

    # appel de la fonction de De Casteljau du premier projet
    return bezier_de_casteljau_3d(intermediaires, v)


def surface_bezier_double_casteljau(
    reseau_pts: Sequence[Sequence[Point3]],
    pas_u: int = 20,
    pas_v: int = 20,
) -> GrilleSurface:
    # echantillonne la surface avec le double de casteljau
    return _surface_bezier_echantillon(reseau_pts, pas_u, pas_v, point_surface_double_casteljau)


def reseau_bicubique_demo() -> Reseau3D:
    # réseau 4x4 par défaut pour l'exemple bi-cubique
    reseau: Reseau3D = []
    for i in range(4):
        u = i / 3.0
        ligne: List[Point3] = []
        for j in range(4):
            v = j / 3.0
            x = (u - 0.5) * 5.0
            z = (v - 0.5) * 5.0
            y = 1.2 * math.sin(u * math.pi) * math.cos(v * math.pi)
            ligne.append((x, y, z))
        reseau.append(ligne)
    return reseau
