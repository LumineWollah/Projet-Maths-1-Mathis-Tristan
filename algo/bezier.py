from __future__ import annotations

import math
from typing import List, Optional, Tuple

Point = Tuple[float, float]


def lerp(a: Point, b: Point, t: float) -> Point:
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def bezier_point(points: List[Point], t: float) -> Point:
    """Point sur une courbe de Bézier via l'algorithme de De Casteljau."""
    if not points:
        raise ValueError("bezier_point: points must not be empty")
    if len(points) == 1:
        return points[0]

    if t < 0.0:
        t = 0.0
    elif t > 1.0:
        t = 1.0

    work = points[:]
    while len(work) > 1:
        work = [lerp(work[i], work[i + 1], t) for i in range(len(work) - 1)]
    return work[0]


def bernstein_point(points: List[Point], t: float) -> Point:
    """Point sur une courbe de Bézier via les polynômes de Bernstein."""
    if not points:
        raise ValueError("bernstein_point: points must not be empty")
    if len(points) == 1:
        return points[0]

    if t < 0.0:
        t = 0.0
    elif t > 1.0:
        t = 1.0

    n = len(points) - 1
    x, y = 0.0, 0.0
    for i, pos in enumerate(points):
        binom = math.comb(n, i)
        b = binom * (t ** i) * ((1 - t) ** (n - i))
        x += pos[0] * b
        y += pos[1] * b
    return (x, y)


def bezier_polyline(
    points: List[Point],
    step: float = 0.01,
    use_casteljau: bool = True,
) -> List[Point]:
    """Échantillonne une courbe de Bézier en polyligne."""
    if step <= 0:
        raise ValueError("bezier_polyline: step must be > 0")
    if len(points) < 2:
        return points[:]

    eval_fn = bezier_point if use_casteljau else bernstein_point

    n = int(round(1.0 / step))
    if n < 1:
        n = 1

    sampled: List[Point] = []
    for i in range(n + 1):
        t = i / n
        sampled.append(eval_fn(points, t))
    return sampled


def draw_bezier_on_canvas(
    canvas,
    control_points: List[Point],
    step: float = 0.01,
    color: str = "black",
    width: int = 2,
    dash: Optional[Tuple[int, int]] = None,
    tags: str = "bezier",
    use_casteljau: bool = True,
) -> List[Point]:
    """Dessine une courbe de Bézier sur un Canvas Tkinter."""
    if len(control_points) < 2:
        return control_points[:]

    curve = bezier_polyline(control_points, step=step, use_casteljau=use_casteljau)

    for i in range(len(curve) - 1):
        x1, y1 = curve[i]
        x2, y2 = curve[i + 1]
        canvas.create_line(x1, y1, x2, y2, fill=color, width=width, dash=dash, tags=tags)

    return curve
