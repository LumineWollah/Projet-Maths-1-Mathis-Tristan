# ------------------------------------------------------------
# Algorithme de remplissage (scanline / LCA)
# ------------------------------------------------------------
def scanline_fill(polygon):
    """
    Calcule des segments horizontaux de remplissage pour un polygone.
    Retourne une liste de tuples (y, x1, x2).
    """
    if len(polygon) < 3:
        return []

    # Construction des arêtes
    edges = []
    n = len(polygon)
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]

        # On ignore les segments horizontaux
        if y1 == y2:
            continue

        if y1 < y2:
            ymin, ymax = y1, y2
            x_at_ymin = x1
            dy = y2 - y1
            dx = (x2 - x1) / dy
        else:
            ymin, ymax = y2, y1
            x_at_ymin = x2
            dy = y1 - y2
            dx = (x1 - x2) / dy

        edges.append({
            "ymin": ymin,
            "ymax": ymax,
            "x": x_at_ymin,
            "dx": dx
        })

    if not edges:
        return []

    y_min = int(min(p[1] for p in polygon))
    y_max = int(max(p[1] for p in polygon))

    scanlines = []

    # Balayage ligne par ligne
    for y in range(y_min, y_max + 1):
        xs = []
        for e in edges:
            if e["ymin"] <= y < e["ymax"]:  # convention classique
                x = e["x"] + (y - e["ymin"]) * e["dx"]
                xs.append(x)

        if len(xs) < 2:
            continue

        xs.sort()
        # On remplit par paires
        for i in range(0, len(xs) - 1, 2):
            x1 = xs[i]
            x2 = xs[i + 1]
            scanlines.append((y, x1, x2))

    return scanlines

