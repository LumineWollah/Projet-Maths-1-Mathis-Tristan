# échantillonne une courbe 2D pour le profil d'extrusion (appels S1)
from __future__ import annotations

from typing import List, Literal, Optional, Sequence, Tuple

from algo.bezier import bezier_point
from algo.bspline_nurbs import bspline_point, nurbs_point, open_uniform_knots

Point2 = Tuple[float, float]
TypeCourbe = Literal["bezier", "bspline", "nurbs"]


def evaluer_profil_2d(
    points_controle: Sequence[Point2],
    t: float,
    type_courbe: TypeCourbe = "bezier",
    degre: int = 3,
    knots: Optional[Sequence[float]] = None,
    weights: Optional[Sequence[float]] = None,
) -> Optional[Point2]:
    if not points_controle:
        return None

    if type_courbe == "bezier":
        # appel de la fonction qu'on a fait au premier projet
        return bezier_point(list(points_controle), t)

    nb = len(points_controle)
    p = degre
    U = list(knots) if knots is not None else open_uniform_knots(nb, p)

    if type_courbe == "bspline":
        # appel de la fonction qu'on a fait au premier projet
        return bspline_point(list(points_controle), p, t, U)

    if type_courbe == "nurbs":
        w = list(weights) if weights is not None else [1.0] * nb
        # appel de la fonction qu'on a fait au premier projet
        pt = nurbs_point(list(points_controle), w, p, t, U)
        return pt

    raise ValueError(f"type de courbe inconnu: {type_courbe}")


def echantillonner_profil_2d(
    points_controle: Sequence[Point2],
    nb_points: int = 32,
    type_courbe: TypeCourbe = "bezier",
    degre: int = 3,
) -> List[Point2]:
    if len(points_controle) < 2 or nb_points < 2:
        return []

    profil: List[Point2] = []
    for i in range(nb_points):
        t = i / (nb_points - 1)
        pt = evaluer_profil_2d(points_controle, t, type_courbe, degre)
        if pt is not None:
            profil.append(pt)
    return profil
