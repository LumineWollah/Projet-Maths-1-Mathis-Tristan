# ----------------------------------------------------
# Basic vector helper
# ----------------------------------------------------
def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


# ----------------------------------------------------
# 1. coupe(S, P, Fi, Fi1)
# ----------------------------------------------------
def coupe(S, P, Fi, Fi1):
    edge = sub(Fi1, Fi)
    toS = sub(S, Fi)
    toP = sub(P, Fi)

    crossS = edge[0] * toS[1] - edge[1] * toS[0]
    crossP = edge[0] * toP[1] - edge[1] * toP[0]

    return crossS * crossP < 0


# ----------------------------------------------------
# 2. intersection(S, P, Fi, Fi1)
# ----------------------------------------------------
def intersection(S, P, Fi, Fi1):
    x1, y1 = S
    x2, y2 = P
    x3, y3 = Fi
    x4, y4 = Fi1

    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0:
        # parallel (degenerate case) -> return S safely
        return S

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


# ----------------------------------------------------
# 3. visible(S, Fi, Fi1)
# ----------------------------------------------------
def visible(S, Fi, Fi1):
    # Point S is "inside" if it is on the left side of edge Fi->Fi1
    edge = sub(Fi1, Fi)
    toS = sub(S, Fi)
    cross = edge[0] * toS[1] - edge[1] * toS[0]
    return cross >= 0


# ----------------------------------------------------
# Orientation helper: signed area (not closed polygon)
# >0 CCW, <0 CW
# ----------------------------------------------------
def polygon_area(poly):
    if len(poly) < 3:
        return 0.0
    a = 0.0
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        a += x1 * y2 - x2 * y1
    return a / 2.0


# ----------------------------------------------------
# Sutherland–Hodgman (fenêtre convexe)
# Uses ONLY coupe / intersection / visible as required
# ----------------------------------------------------
def sutherland_hodgman(PL, PW):
    """
    PL : list of vertices [(x,y), ...] (subject polygon)
    PW : list of vertices [(x,y), ...] (clipping window polygon)
         (convex required)
    Returns: clipped polygon as list of vertices [(x,y), ...] or [].
    """

    if len(PL) < 3 or len(PW) < 3:
        return []

    # Ensure window is CCW (required by visible() definition)
    if polygon_area(PW) < 0:
        PW = list(reversed(PW))

    N1 = len(PL)

    # For each window edge Fi->Fi+1
    for i in range(len(PW)):
        Fi = PW[i]
        Fi1 = PW[(i + 1) % len(PW)]

        PS = []
        N2 = 0

        # Iterate over vertices, keeping track of previous vertex S
        F = PL[0]
        S = PL[-1]

        for Pj in PL:
            if coupe(S, Pj, Fi, Fi1):
                I = intersection(S, Pj, Fi, Fi1)
                PS.append(I)
                N2 += 1

            S = Pj

            if visible(S, Fi, Fi1):
                PS.append(S)
                N2 += 1

        # If nothing survived this clipping edge -> empty
        if N2 == 0:
            return []

        PL = PS
        N1 = N2

    return PL


# ============================================================
# BONUS : Fenêtre quelconque via triangulation (Ear Clipping)
# ============================================================

EPS = 1e-9


def _area2(poly):
    """Signed doubled area for a polygon (not closed)."""
    a = 0.0
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        a += x1 * y2 - x2 * y1
    return a


def _ensure_ccw(poly):
    """Return a CCW-oriented copy (expects poly not closed)."""
    if _area2(poly) < 0:
        return list(reversed(poly))
    return poly[:]


def _cross(a, b, c):
    """Cross product of AB x AC."""
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _point_in_triangle(p, a, b, c):
    """Inclusive test (with EPS) for point inside triangle abc (CCW)."""
    c1 = _cross(a, b, p)
    c2 = _cross(b, c, p)
    c3 = _cross(c, a, p)
    return (c1 >= -EPS) and (c2 >= -EPS) and (c3 >= -EPS)


def triangulate_ear_clipping(polygon):
    """
    Ear clipping triangulation.
    Input: polygon as list [(x,y), ...] (NOT closed), simple polygon expected.
    Output: list of triangles, each triangle is [(x,y),(x,y),(x,y)]
    """
    if len(polygon) < 3:
        return []
    if len(polygon) == 3:
        return [polygon[:]]

    poly = _ensure_ccw(polygon)
    V = list(range(len(poly)))
    triangles = []

    def is_convex(i_prev, i_curr, i_next):
        a = poly[i_prev]
        b = poly[i_curr]
        c = poly[i_next]
        return _cross(a, b, c) > EPS  # strict convex for CCW

    guard = 0
    max_guard = len(V) * len(V) + 10

    while len(V) > 3 and guard < max_guard:
        guard += 1
        ear_found = False

        for k in range(len(V)):
            i_prev = V[(k - 1) % len(V)]
            i_curr = V[k]
            i_next = V[(k + 1) % len(V)]

            if not is_convex(i_prev, i_curr, i_next):
                continue

            a, b, c = poly[i_prev], poly[i_curr], poly[i_next]

            # No other vertex inside the ear triangle
            any_inside = False
            for j in V:
                if j in (i_prev, i_curr, i_next):
                    continue
                if _point_in_triangle(poly[j], a, b, c):
                    any_inside = True
                    break
            if any_inside:
                continue

            # Ear found
            triangles.append([a, b, c])
            del V[k]
            ear_found = True
            break

        if not ear_found:
            # Probably self-intersecting or degenerate polygon
            break

    if len(V) == 3:
        triangles.append([poly[V[0]], poly[V[1]], poly[V[2]]])

    return triangles


def clip_subject_with_window_triangulation(subject_polygon, window_polygon):
    """
    Clip a subject polygon with a (possibly concave) window by:
    - triangulating the window (ear clipping)
    - clipping subject against each triangle using existing S-H
    Returns: list of clipped polygons (pieces)
    """
    if len(subject_polygon) < 3 or len(window_polygon) < 3:
        return []

    win = window_polygon[:]
    # If user provided a closed polygon, drop last duplicate
    if len(win) >= 2 and win[0] == win[-1]:
        win = win[:-1]

    tris = triangulate_ear_clipping(win)

    results = []
    for tri in tris:
        res = sutherland_hodgman(subject_polygon, tri)
        if res and len(res) >= 3:
            results.append(res)

    return results
