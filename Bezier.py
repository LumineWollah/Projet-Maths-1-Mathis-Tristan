from __future__ import annotations
from typing import List, Tuple, Optional

Point = Tuple[float, float]


def lerp(a: Point, b: Point, t: float) -> Point:
    """Linear interpolation between points a and b."""
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def bezier_point(points: List[Point], t: float) -> Point:
    """
    Compute a point on the Bézier curve defined by `points` at ratio t in [0, 1],
    using De Casteljau algorithm.
    All weights are equal -> standard Bézier curve.
    """
    if not points:
        raise ValueError("bezier_point: points must not be empty")
    if len(points) == 1:
        return points[0]

    # Clamp t safely (keeps drawing robust)
    if t < 0.0:
        t = 0.0
    elif t > 1.0:
        t = 1.0

    work = points[:]
    # Repeatedly interpolate until one point remains
    while len(work) > 1:
        work = [lerp(work[i], work[i + 1], t) for i in range(len(work) - 1)]
    return work[0]


def bezier_polyline(points: List[Point], step: float = 0.01) -> List[Point]:
    """
    Sample the Bézier curve into a polyline.
    step: ratio increment (e.g., 0.01 -> ~101 points).
    """
    if step <= 0:
        raise ValueError("bezier_polyline: step must be > 0")
    if len(points) < 2:
        return points[:]

    # Ensure we include t=1.0
    n = int(round(1.0 / step))
    if n < 1:
        n = 1

    sampled: List[Point] = []
    for i in range(n + 1):
        t = i / n
        sampled.append(bezier_point(points, t))
    return sampled


def draw_bezier_on_canvas(
    canvas,
    control_points: List[Point],
    step: float = 0.01,
    color: str = "black",
    width: int = 2,
    dash: Optional[Tuple[int, int]] = None,
    tags: str = "bezier",
) -> List[Point]:
    """
    Draw a Bézier curve on a Tkinter Canvas.
    Returns the sampled polyline points (world/screen coords = whatever you pass in).

    You can pass points in your "world" coords IF you transform them before calling
    (e.g., using your world_to_screen).
    """
    if len(control_points) < 2:
        return control_points[:]

    curve = bezier_polyline(control_points, step=step)

    # Draw as connected line segments
    for i in range(len(curve) - 1):
        x1, y1 = curve[i]
        x2, y2 = curve[i + 1]
        canvas.create_line(x1, y1, x2, y2, fill=color, width=width, dash=dash, tags=tags)

    return curve
