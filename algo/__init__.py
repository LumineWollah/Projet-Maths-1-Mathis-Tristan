"""Algorithmes de géométrie graphique — Semestre 1 (découpage, remplissage, courbes 2D)."""

from algo.sutherland_hodgman import (
    sutherland_hodgman,
    clip_subject_with_window_triangulation,
)
from algo.lca import lca_fill
from algo.bezier import bezier_point, bernstein_point, bezier_polyline
from algo.bspline_nurbs import (
    bspline_point,
    nurbs_point,
    open_uniform_knots,
    parse_knots,
)

__all__ = [
    "sutherland_hodgman",
    "clip_subject_with_window_triangulation",
    "lca_fill",
    "bezier_point",
    "bernstein_point",
    "bezier_polyline",
    "bspline_point",
    "nurbs_point",
    "open_uniform_knots",
    "parse_knots",
]
