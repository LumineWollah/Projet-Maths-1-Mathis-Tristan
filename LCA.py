import math

def lca_fill(polygon):
    """
    Remplissage par Liste des Côtés Actifs (LCA).
    Retourne une liste de segments (y, x1, x2).
    Convention classique :
      - ignore les arêtes horizontales
      - une arête est active pour y dans [ymin, ymax[
      - mise à jour incrémentale : x = x + dx à chaque scanline
    """
    if len(polygon) < 3:
        return []

    #Construire la LEB (Liste des Arêtes de Base)
    # Chaque arête stocke : ymin, ymax, x (à ymin), dx (delta x par +1 en y)
    leb = []
    n = len(polygon)

    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]

        # ignorer horizontales
        if y1 == y2:
            continue

        # orienter bas->haut
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

        leb.append({
            "ymin": ymin,
            "ymax": ymax,
            "x": x_at_ymin,
            "dx": dx
        })

    if not leb:
        return []

    # Trier LEB par ymin puis x puis dx (utile si plusieurs arêtes démarrent au même y)
    leb.sort(key=lambda e: (e["ymin"], e["x"], e["dx"]))

    # Plage de scan
    y_start = int(math.ceil(min(e["ymin"] for e in leb)))
    y_end   = int(math.floor(max(e["ymax"] for e in leb)))

    #Balayage avec LCA
    lca = []
    segs = []

    leb_i = 0
    leb_len = len(leb)

    for y in range(y_start, y_end + 1):
        #Ajouter dans la LCA les arêtes dont ymin <= y (et initialiser x au bon y)
        while leb_i < leb_len and leb[leb_i]["ymin"] <= y:
            e = leb[leb_i]
            leb_i += 1

            #Arête active seulement si y < ymax (convention [ymin, ymax[)
            if y < e["ymax"]:
                #recalage de x si ymin n'est pas entier
                #x(y) = x(ymin) + (y - ymin)*dx
                e = dict(e)  # copie
                e["x"] = e["x"] + (y - e["ymin"]) * e["dx"]
                lca.append(e)

        #Retirer celles qui ne sont plus actives (y >= ymax)
        lca = [e for e in lca if y < e["ymax"]]

        if len(lca) < 2:
            # mise à jour incrémentale quand même
            for e in lca:
                e["x"] += e["dx"]
            continue

        #Trier LCA par x courant
        lca.sort(key=lambda e: e["x"])

        #Remplir par paires
        #(si le polygone est simple, nombre d'intersections devrait être pair)
        for i in range(0, len(lca) - 1, 2):
            x1 = lca[i]["x"]
            x2 = lca[i + 1]["x"]
            if x2 > x1:
                segs.append((y, x1, x2))

        #Mise à jour incrémentale : x += dx
        for e in lca:
            e["x"] += e["dx"]

    return segs
