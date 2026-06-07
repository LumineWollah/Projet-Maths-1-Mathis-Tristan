# Cox–de–Boor (B-Spline) + NURBS
# Convention:
# - nb_ctrl = len(points)
# - p = degré
# - knot vector length = nb_ctrl + p + 1


def parse_knots(text: str):
    """Parse "0,0,0,0, 0.5, 1,1,1,1" -> [float, ...]"""
    parts = [s.strip() for s in text.replace(";", ",").split(",")]
    vals = []
    for s in parts:
        if not s:
            continue
        vals.append(float(s))
    return vals


def open_uniform_knots(nb_ctrl: int, p: int):
    """
    Vecteur nodal ouvert uniforme (clamped).
    U = [0..0, u1, u2, ..., 1..1] avec (p+1) zéros et (p+1) uns.
    """
    m = nb_ctrl + p + 1
    if m <= 0:
        return []

    if nb_ctrl <= p:
        return [0.0] * (m - 1) + [1.0]

    U = [0.0] * (p + 1)
    interior_count = m - 2 * (p + 1)
    if interior_count > 0:
        for k in range(1, interior_count + 1):
            U.append(k / (interior_count + 1))
    U += [1.0] * (p + 1)
    return U


def N_ip(i: int, p: int, t: float, U):
    """Récurrence Cox-de-Boor. Division par 0 -> contribution 0."""
    if p == 0:
        if (U[i] <= t < U[i + 1]) or (t == U[-1] and U[i] <= t <= U[i + 1]):
            return 1.0
        return 0.0

    left = 0.0
    right = 0.0

    denom1 = U[i + p] - U[i]
    if denom1 != 0:
        left = (t - U[i]) / denom1 * N_ip(i, p - 1, t, U)

    denom2 = U[i + p + 1] - U[i + 1]
    if denom2 != 0:
        right = (U[i + p + 1] - t) / denom2 * N_ip(i + 1, p - 1, t, U)

    return left + right


def bspline_point(points, p: int, t: float, U):
    x = 0.0
    y = 0.0
    nb = len(points)
    for i in range(nb):
        b = N_ip(i, p, t, U)
        x += points[i][0] * b
        y += points[i][1] * b
    return (x, y)


def nurbs_point(points, weights, p: int, t: float, U):
    numx = 0.0
    numy = 0.0
    denom = 0.0
    nb = len(points)
    for i in range(nb):
        b = N_ip(i, p, t, U)
        w = weights[i]
        numx += points[i][0] * b * w
        numy += points[i][1] * b * w
        denom += b * w
    if denom == 0:
        return None
    return (numx / denom, numy / denom)
