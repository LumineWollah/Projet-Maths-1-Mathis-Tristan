# évaluation de trajectoires 3D en réutilisant le code du S1
from __future__ import annotations

from typing import List, Literal, Optional, Sequence

from algo.bezier import bezier_point
from algo.bspline_nurbs import bspline_point, nurbs_point, open_uniform_knots
from algo.trimestre_3.vecteurs import Point3

TypeCourbe = Literal["bezier", "bspline", "nurbs"]


def _bezier_3d(points_3d: Sequence[Point3], t: float) -> Point3:
    # en 3D chaque coordonnée suit la même courbe de Bézier
    # appel des fonctions qu'on a fait au premier projet
    x = bezier_point([(p[0], 0.0) for p in points_3d], t)[0]
    y = bezier_point([(0.0, p[1]) for p in points_3d], t)[1]
    z = bezier_point([(0.0, p[2]) for p in points_3d], t)[1]
    return (x, y, z)


def bezier_de_casteljau_3d(points_3d: Sequence[Point3], t: float) -> Point3:
    # appel de la fonction de De Casteljau du premier projet
    return _bezier_3d(points_3d, t)


def _bspline_3d(points_3d: Sequence[Point3], p: int, t: float, U: Sequence[float]) -> Point3:
    # appel des fonctions qu'on a fait au premier projet
    x = bspline_point([(pt[0], 0.0) for pt in points_3d], p, t, U)[0]
    y = bspline_point([(0.0, pt[1]) for pt in points_3d], p, t, U)[1]
    z = bspline_point([(0.0, pt[2]) for pt in points_3d], p, t, U)[1]
    return (x, y, z)


def _nurbs_3d(
    points_3d: Sequence[Point3],
    weights: Sequence[float],
    p: int,
    t: float,
    U: Sequence[float],
) -> Optional[Point3]:
    # appel des fonctions qu'on a fait au premier projet
    px = nurbs_point([(pt[0], 0.0) for pt in points_3d], weights, p, t, U)
    py = nurbs_point([(0.0, pt[1]) for pt in points_3d], weights, p, t, U)
    pz = nurbs_point([(0.0, pt[2]) for pt in points_3d], weights, p, t, U)
    if px is None or py is None or pz is None:
        return None
    return (px[0], py[1], pz[1])


def evaluer_trajectoire(
    points_3d: Sequence[Point3],
    t: float,
    type_courbe: TypeCourbe = "bezier",
    degre: int = 3,
    knots: Optional[Sequence[float]] = None,
    weights: Optional[Sequence[float]] = None,
) -> Optional[Point3]:
    # point sur la trajectoire 3D au paramètre t
    if not points_3d:
        return None

    if type_courbe == "bezier":
        return _bezier_3d(points_3d, t)

    nb = len(points_3d)
    p = degre
    U = list(knots) if knots is not None else open_uniform_knots(nb, p)

    if type_courbe == "bspline":
        return _bspline_3d(points_3d, p, t, U)

    if type_courbe == "nurbs":
        w = list(weights) if weights is not None else [1.0] * nb
        return _nurbs_3d(points_3d, w, p, t, U)

    raise ValueError(f"type de courbe inconnu: {type_courbe}")


def echantillonner_trajectoire(
    points_3d: Sequence[Point3],
    nb_points: int = 50,
    type_courbe: TypeCourbe = "bezier",
    degre: int = 3,
    knots: Optional[Sequence[float]] = None,
    weights: Optional[Sequence[float]] = None,
) -> List[Point3]:
    # renvoie une polyligne 3D pour dessiner la trajectoire
    if nb_points < 2:
        nb_points = 2
    if not points_3d:
        return []

    pts: List[Point3] = []
    for i in range(nb_points):
        t = i / (nb_points - 1)
        p = evaluer_trajectoire(
            points_3d, t, type_courbe, degre, knots, weights
        )
        if p is not None:
            pts.append(p)
    return pts
