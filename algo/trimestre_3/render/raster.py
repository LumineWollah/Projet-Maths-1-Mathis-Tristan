# rasterizer maison + z-buffer fait à la main
from __future__ import annotations

import math
from typing import List, Optional, Tuple

Couleur = Tuple[int, int, int]
PointEcran = Tuple[float, float, float]


class ZBuffer:
    def __init__(self, largeur: int, hauteur: int):
        self.largeur = largeur
        self.hauteur = hauteur
        self.reset()

    def reset(self):
        # infini = aucun pixel dessiné pour l'instant
        self.depth = [[math.inf for _ in range(self.largeur)] for _ in range(self.hauteur)]

    def test_profondeur(self, x: int, y: int, z: float) -> bool:
        if x < 0 or y < 0 or x >= self.largeur or y >= self.hauteur:
            return False
        if z < self.depth[y][x]:
            self.depth[y][x] = z
            return True
        return False


class Rasterizer:
    def __init__(self, largeur: int, hauteur: int):
        self.largeur = largeur
        self.hauteur = hauteur
        self.zbuffer = ZBuffer(largeur, hauteur)
        self.zbuffer_actif = True
        self._reset_couleurs()

    def _reset_couleurs(self):
        # fond blanc
        self.pixels = [[(255, 255, 255) for _ in range(self.largeur)] for _ in range(self.hauteur)]

    def clear(self, utiliser_zbuffer: bool = True):
        self.zbuffer_actif = utiliser_zbuffer
        self.zbuffer.reset()
        self._reset_couleurs()

    def redimensionner(self, largeur: int, hauteur: int):
        self.largeur = largeur
        self.hauteur = hauteur
        self.zbuffer = ZBuffer(largeur, hauteur)
        self._reset_couleurs()

    def _plot(self, x: int, y: int, z: float, couleur: Couleur):
        if x < 0 or y < 0 or x >= self.largeur or y >= self.hauteur:
            return
        if self.zbuffer_actif:
            if self.zbuffer.test_profondeur(x, y, z):
                self.pixels[y][x] = couleur
        else:
            self.pixels[y][x] = couleur

    def tracer_ligne_rapide(
        self,
        x0: float, y0: float,
        x1: float, y1: float,
        couleur: Couleur,
    ):
        # ligne sans z-buffer, moins de calculs
        dx = x1 - x0
        dy = y1 - y0
        steps = int(max(abs(dx), abs(dy), 1))
        for i in range(steps + 1):
            t = i / steps
            x = int(round(x0 + dx * t))
            y = int(round(y0 + dy * t))
            if 0 <= x < self.largeur and 0 <= y < self.hauteur:
                self.pixels[y][x] = couleur

    def tracer_point(self, x: float, y: float, z: float, couleur: Couleur, rayon: int = 2):
        cx = int(round(x))
        cy = int(round(y))
        for dy in range(-rayon, rayon + 1):
            for dx in range(-rayon, rayon + 1):
                if dx * dx + dy * dy <= rayon * rayon:
                    self._plot(cx + dx, cy + dy, z, couleur)

    def tracer_ligne(
        self,
        x0: float, y0: float, z0: float,
        x1: float, y1: float, z1: float,
        couleur: Couleur,
    ):
        # on découppe la ligne en petits pas pour interpoler z
        dx = x1 - x0
        dy = y1 - y0
        steps = int(max(abs(dx), abs(dy), 1))
        for i in range(steps + 1):
            t = i / steps
            x = x0 + dx * t
            y = y0 + dy * t
            z = z0 + (z1 - z0) * t
            self._plot(int(round(x)), int(round(y)), z, couleur)

    def tracer_polyligne(self, points: List[PointEcran], couleur: Couleur):
        if len(points) < 2:
            return
        for i in range(len(points) - 1):
            a = points[i]
            b = points[i + 1]
            self.tracer_ligne(a[0], a[1], a[2], b[0], b[1], b[2], couleur)

    def tracer_triangle(
        self,
        p0: PointEcran,
        p1: PointEcran,
        p2: PointEcran,
        couleur: Couleur,
    ):
        # remplissage scanline basique avec z interpolé
        pts = sorted([p0, p1, p2], key=lambda p: p[1])
        y_min = int(math.floor(min(p[1] for p in pts)))
        y_max = int(math.ceil(max(p[1] for p in pts)))

        for y in range(y_min, y_max + 1):
            intersections = []
            for a, b in ((p0, p1), (p1, p2), (p2, p0)):
                y1, y2 = a[1], b[1]
                if y1 == y2:
                    continue
                if (y < min(y1, y2)) or (y >= max(y1, y2)):
                    continue
                t = (y - a[1]) / (b[1] - a[1])
                x = a[0] + (b[0] - a[0]) * t
                z = a[2] + (b[2] - a[2]) * t
                intersections.append((x, z))

            if len(intersections) < 2:
                continue

            intersections.sort(key=lambda it: it[0])
            x_debut = int(math.ceil(intersections[0][0]))
            x_fin = int(math.floor(intersections[-1][0]))
            z_debut = intersections[0][1]
            z_fin = intersections[-1][1]

            if x_fin < x_debut:
                continue

            for x in range(x_debut, x_fin + 1):
                if x_fin == x_debut:
                    z = z_debut
                else:
                    alpha = (x - x_debut) / (x_fin - x_debut)
                    z = z_debut + (z_fin - z_debut) * alpha
                self._plot(x, y, z, couleur)

    def _aire_signee(self, a: PointEcran, b: PointEcran, c: PointEcran) -> float:
        return (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])

    def tracer_triangle_gouraud(
        self,
        p0: PointEcran,
        p1: PointEcran,
        p2: PointEcran,
        c0: Couleur,
        c1: Couleur,
        c2: Couleur,
    ):
        # barycentrique correct pour interpoler couleur et profondeur
        area = self._aire_signee(p0, p1, p2)
        if abs(area) < 1e-8:
            return

        y_min = max(0, int(math.floor(min(p0[1], p1[1], p2[1]))))
        y_max = min(self.hauteur - 1, int(math.ceil(max(p0[1], p1[1], p2[1]))))
        x_min = max(0, int(math.floor(min(p0[0], p1[0], p2[0]))))
        x_max = min(self.largeur - 1, int(math.ceil(max(p0[0], p1[0], p2[0]))))

        for y in range(y_min, y_max + 1):
            py = y + 0.5
            for x in range(x_min, x_max + 1):
                px = x + 0.5
                w0 = self._aire_signee((px, py, 0), p1, p2) / area
                w1 = self._aire_signee(p0, (px, py, 0), p2) / area
                w2 = self._aire_signee(p0, p1, (px, py, 0)) / area
                if w0 < 0 or w1 < 0 or w2 < 0:
                    continue
                z = w0 * p0[2] + w1 * p1[2] + w2 * p2[2]
                col = (
                    int(w0 * c0[0] + w1 * c1[0] + w2 * c2[0]),
                    int(w0 * c0[1] + w1 * c1[1] + w2 * c2[1]),
                    int(w0 * c0[2] + w1 * c1[2] + w2 * c2[2]),
                )
                self._plot(x, y, z, col)

    def vers_chaine_photo(self) -> str:
        # format attendu par tk.PhotoImage
        lignes = []
        for y in range(self.hauteur):
            morceaux = []
            for x in range(self.largeur):
                r, g, b = self.pixels[y][x]
                morceaux.append(f"#{r:02x}{g:02x}{b:02x}")
            lignes.append("{" + " ".join(morceaux) + "}")
        return " ".join(lignes)
