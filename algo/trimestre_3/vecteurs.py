# opérations de base en 3D, tout le projet passe par ici
from __future__ import annotations

import math
from typing import Sequence, Tuple

Point3 = Tuple[float, float, float]
Vecteur3 = Tuple[float, float, float]


def add(a: Point3, b: Point3) -> Point3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def sub(a: Point3, b: Point3) -> Point3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def scale(v: Vecteur3, s: float) -> Vecteur3:
    return (v[0] * s, v[1] * s, v[2] * s)


def dot(a: Vecteur3, b: Vecteur3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a: Vecteur3, b: Vecteur3) -> Vecteur3:
    # produit vectoriel classique
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def length(v: Vecteur3) -> float:
    return math.sqrt(dot(v, v))


def normalize(v: Vecteur3) -> Vecteur3:
    ln = length(v)
    if ln == 0:
        return (0.0, 0.0, 0.0)
    return scale(v, 1.0 / ln)


def lerp3d(a: Point3, b: Point3, t: float) -> Point3:
    return (
        a[0] + (b[0] - a[0]) * t,
        a[1] + (b[1] - a[1]) * t,
        a[2] + (b[2] - a[2]) * t,
    )


def distance(a: Point3, b: Point3) -> float:
    return length(sub(a, b))


def milieu(a: Point3, b: Point3) -> Point3:
    return lerp3d(a, b, 0.5)


def somme_points(points: Sequence[Point3]) -> Point3:
    if not points:
        return (0.0, 0.0, 0.0)
    sx = sy = sz = 0.0
    for p in points:
        sx += p[0]
        sy += p[1]
        sz += p[2]
    return (sx, sy, sz)
