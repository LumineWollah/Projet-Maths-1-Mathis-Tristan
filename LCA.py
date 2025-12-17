import math

def lca_fill(polygon, rule="evenodd"):
    """
    Remplissage scanline.
    rule:
      - "evenodd"  : nombre d'intersections (pair/impair)  -> ton LCA actuel
      - "winding"  : nombre d'enroulement non nul (non-zero winding)
    Retour : liste de segments (y, x1, x2)
    """
    if len(polygon) < 3:
        return []

    rule = (rule or "evenodd").lower().strip()
    if rule in ("evenodd", "even-odd", "parity"):
        return _fill_evenodd_lca(polygon)
    elif rule in ("winding", "nonzero", "non-zero"):
        return _fill_winding_scanline(polygon)
    else:
        raise ValueError(f"Unknown fill rule: {rule}")


# ============================================================
# 1) EVEN-ODD : ton algo LCA (quasi inchangé)
# ============================================================
def _fill_evenodd_lca(polygon):
    if len(polygon) < 3:
        return []

    leb = []
    n = len(polygon)

    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]

        if y1 == y2:
            continue

        if y1 < y2:
            ymin, ymax = y1, y2
            x_at_ymin = x1
            dy = (y2 - y1)
            dx = (x2 - x1) / dy
        else:
            ymin, ymax = y2, y1
            x_at_ymin = x2
            dy = (y1 - y2)
            dx = (x1 - x2) / dy

        leb.append({"ymin": ymin, "ymax": ymax, "x": x_at_ymin, "dx": dx})

    if not leb:
        return []

    leb.sort(key=lambda e: (e["ymin"], e["x"], e["dx"]))

    y_start = int(math.ceil(min(e["ymin"] for e in leb)))
    y_end   = int(math.floor(max(e["ymax"] for e in leb)))

    lca = []
    segs = []

    leb_i = 0
    leb_len = len(leb)

    for y in range(y_start, y_end + 1):
        while leb_i < leb_len and leb[leb_i]["ymin"] <= y:
            e = leb[leb_i]
            leb_i += 1

            if y < e["ymax"]:
                e = dict(e)
                e["x"] = e["x"] + (y - e["ymin"]) * e["dx"]
                lca.append(e)

        lca = [e for e in lca if y < e["ymax"]]

        if len(lca) >= 2:
            lca.sort(key=lambda e: e["x"])
            for i in range(0, len(lca) - 1, 2):
                x1 = lca[i]["x"]
                x2 = lca[i + 1]["x"]
                if x2 > x1:
                    segs.append((y, x1, x2))

        for e in lca:
            e["x"] += e["dx"]

    return segs


# ============================================================
# 2) WINDING (non-zero) : gestion polygones croisés
# ============================================================
def _fill_winding_scanline(polygon):
    """
    Non-zero winding rule.
    On parcourt chaque scanline, on calcule toutes les intersections (x, delta_wind),
    on trie par x, puis on remplit les intervalles où winding != 0.
    """
    n = len(polygon)
    if n < 3:
        return []

    # Plage Y
    ys = [p[1] for p in polygon]
    y_start = int(math.floor(min(ys)))
    y_end   = int(math.ceil(max(ys)))

    segs = []

    # On utilise y + 0.5 pour éviter les ambiguïtés exactes sur les sommets
    for y in range(y_start, y_end + 1):
        y_scan = y + 0.5

        inter = []  # [(x, deltaWind), ...]

        for i in range(n):
            x1, y1 = polygon[i]
            x2, y2 = polygon[(i + 1) % n]

            if y1 == y2:
                continue  # horizontale ignorée

            ymin = min(y1, y2)
            ymax = max(y1, y2)

            # convention demi-ouverte [ymin, ymax[
            if not (ymin <= y_scan < ymax):
                continue

            # intersection X
            t = (y_scan - y1) / (y2 - y1)
            x = x1 + t * (x2 - x1)

            # delta winding : +1 si l'arête monte, -1 si elle descend
            delta = 1 if y2 > y1 else -1
            inter.append((x, delta))

        if len(inter) < 2:
            continue

        inter.sort(key=lambda it: it[0])

        winding = 0
        for i in range(len(inter) - 1):
            x_i, d_i = inter[i]
            winding += d_i

            x_next = inter[i + 1][0]
            if winding != 0 and x_next > x_i:
                segs.append((y, x_i, x_next))

    return segs
