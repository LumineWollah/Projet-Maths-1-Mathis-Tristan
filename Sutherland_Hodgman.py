# ----------------------------------------------------
# Basic vector helper
# ----------------------------------------------------
def sub(a, b): return (a[0] - b[0], a[1] - b[1])


# ----------------------------------------------------
# 1. coupe(S, P, Fi, Fi1)
# ----------------------------------------------------
def coupe(S, P, Fi, Fi1):
    edge = sub(Fi1, Fi)
    toS = sub(S, Fi)
    toP = sub(P, Fi)

    crossS = edge[0] * toS[1] - edge[1] * toS[0]
    crossP = edge[0] * toP[1] - edge[1] * toP[0]

    # Reject parallel or colinear case
    if crossS == 0 and crossP == 0:
        return False

    # Real crossing only if opposite signs
    return (crossS < 0 and crossP > 0) or (crossS > 0 and crossP < 0)



# ----------------------------------------------------
# 2. intersection(S, P, Fi, Fi1)
# ----------------------------------------------------
def intersection(S, P, Fi, Fi1):
    x1, y1 = S
    x2, y2 = P
    x3, y3 = Fi
    x4, y4 = Fi1

    denom = (x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4)
    if denom == 0:
        return S 

    t = ((x1 - x3)*(y3 - y4) - (y1 - y3)*(x3 - x4)) / denom
    return (x1 + t*(x2 - x1), y1 + t*(y2 - y1))


# ----------------------------------------------------
# 3. visible(S, Fi, Fi1)
# ----------------------------------------------------
def visible(S, Fi, Fi1):
    edge = sub(Fi1, Fi)
    toS = sub(S, Fi)
    cross = edge[0] * toS[1] - edge[1] * toS[0]
    return cross > 0


# ----------------------------------------------------
# Orientation helper
# ----------------------------------------------------
def polygon_area(poly):
    area = 0
    for i in range(len(poly) - 1):
        x1, y1 = poly[i]
        x2, y2 = poly[i+1]
        area += x1*y2 - x2*y1
    return area / 2


# ----------------------------------------------------
# Sutherland–Hodgman 
# ----------------------------------------------------
def sutherland_hodgman(PL, PW):
    # Ensure window closed
    if PW[0] != PW[-1]:
        PW = PW + [PW[0]]

    if polygon_area(PW) < 0:
        PW = PW[::-1]  # reverse to CCW

    N1 = len(PL)

    for i in range(len(PW) - 1):
        Fi = PW[i]
        Fi1 = PW[i + 1]

        PS = []
        N2 = 0

        S = PL[-1]
        F = PL[0]

        # Process all edges SP
        for Pj in PL:
            if coupe(S, Pj, Fi, Fi1):
                I = intersection(S, Pj, Fi, Fi1)
                PS.append(I)
                N2 += 1

            S = Pj

            if visible(S, Fi, Fi1):
                PS.append(S)
                N2 += 1

        # Process last edge (S = last point, F = first)
        if N2 > 0:
            if coupe(S, F, Fi, Fi1):
                I = intersection(S, F, Fi, Fi1)
                PS.append(I)
                N2 += 1

            PL = PS
            N1 = N2

    return PL