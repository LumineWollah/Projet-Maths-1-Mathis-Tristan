# projection 3D -> 2D, calculée à la main (pas de lib 3D)
from __future__ import annotations

import math
from typing import List, Optional, Tuple

from algo.trimestre_3.vecteurs import Point3, Vecteur3, cross, dot, length, normalize, sub

Point2 = Tuple[float, float]
Mat4 = List[List[float]]  # matrice 4x4 en listes Python


def matrice_identite() -> Mat4:
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def matrice_translation(tx: float, ty: float, tz: float) -> Mat4:
    return [
        [1.0, 0.0, 0.0, tx],
        [0.0, 1.0, 0.0, ty],
        [0.0, 0.0, 1.0, tz],
        [0.0, 0.0, 0.0, 1.0],
    ]


def matrice_rotation_x(angle: float) -> Mat4:
    c = math.cos(angle)
    s = math.sin(angle)
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, c, -s, 0.0],
        [0.0, s, c, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def matrice_rotation_y(angle: float) -> Mat4:
    c = math.cos(angle)
    s = math.sin(angle)
    return [
        [c, 0.0, s, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [-s, 0.0, c, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def matrice_rotation_z(angle: float) -> Mat4:
    c = math.cos(angle)
    s = math.sin(angle)
    return [
        [c, -s, 0.0, 0.0],
        [s, c, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def multiplier_matrices(a: Mat4, b: Mat4) -> Mat4:
    # produit matriciel 4x4 fait à la main
    res = [[0.0] * 4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            s = 0.0
            for k in range(4):
                s += a[i][k] * b[k][j]
            res[i][j] = s
    return res


def appliquer_matrice(m: Mat4, point: Point3) -> Point3:
    # on traite le point en coordonnées homogènes
    x, y, z = point
    xh = m[0][0] * x + m[0][1] * y + m[0][2] * z + m[0][3]
    yh = m[1][0] * x + m[1][1] * y + m[1][2] * z + m[1][3]
    zh = m[2][0] * x + m[2][1] * y + m[2][2] * z + m[2][3]
    wh = m[3][0] * x + m[3][1] * y + m[3][2] * z + m[3][3]
    if wh != 0.0:
        return (xh / wh, yh / wh, zh / wh)
    return (xh, yh, zh)


def matrice_vue(oeil: Point3, cible: Point3, haut: Vecteur3 = (0.0, 1.0, 0.0)) -> Mat4:
    # matrice look-at calculée à la main
    avant = normalize(sub(cible, oeil))
    droite = normalize(cross(avant, haut))
    vrai_haut = cross(droite, avant)

    return [
        [droite[0], droite[1], droite[2], -dot(droite, oeil)],
        [vrai_haut[0], vrai_haut[1], vrai_haut[2], -dot(vrai_haut, oeil)],
        [-avant[0], -avant[1], -avant[2], dot(avant, oeil)],
        [0.0, 0.0, 0.0, 1.0],
    ]


def matrice_projection_perspective(fov_y: float, ratio: float, proche: float, loin: float) -> Mat4:
    # fov_y en radians
    f = 1.0 / math.tan(fov_y / 2.0)
    return [
        [f / ratio, 0.0, 0.0, 0.0],
        [0.0, f, 0.0, 0.0],
        [0.0, 0.0, (loin + proche) / (proche - loin), (2.0 * loin * proche) / (proche - loin)],
        [0.0, 0.0, -1.0, 0.0],
    ]


def matrice_projection_orthographique(
    gauche: float,
    droite: float,
    bas: float,
    haut: float,
    proche: float,
    loin: float,
) -> Mat4:
    return [
        [2.0 / (droite - gauche), 0.0, 0.0, -(droite + gauche) / (droite - gauche)],
        [0.0, 2.0 / (haut - bas), 0.0, -(haut + bas) / (haut - bas)],
        [0.0, 0.0, -2.0 / (loin - proche), -(loin + proche) / (loin - proche)],
        [0.0, 0.0, 0.0, 1.0],
    ]


def projet_orthographique(point: Point3, echelle: float = 1.0) -> Point2:
    # vue de dessus simplifiée, utile pour debug
    return (point[0] * echelle, point[1] * echelle)


def projet_perspective_simple(point: Point3, distance_camera: float = 5.0, focale: float = 400.0) -> Optional[Point2]:
    # perspective basique: on divise par la profondeur
    z = point[2] + distance_camera
    if z <= 0.01:
        return None
    sx = focale * point[0] / z
    sy = focale * point[1] / z
    return (sx, sy)


def projet_vue_perspective(
    point_vue: Point3,
    focale: float,
    largeur_ecran: int,
    hauteur_ecran: int,
    echelle: float = 1.0,
) -> Optional[Tuple[Point2, float]]:
    # projection après matrice vue, la caméra regarde vers -Z
    profondeur = -point_vue[2]
    if profondeur <= 0.01:
        return None
    sx = focale * point_vue[0] / profondeur
    sy = focale * point_vue[1] / profondeur
    ecran = convertir_vers_ecran((sx, sy), largeur_ecran, hauteur_ecran, echelle)
    return (ecran, profondeur)


def convertir_vers_ecran(
    point_proj: Point2,
    largeur_ecran: int,
    hauteur_ecran: int,
    echelle: float = 1.0,
) -> Point2:
    # ramène le point projeté au centre du canvas
    cx = largeur_ecran / 2.0
    cy = hauteur_ecran / 2.0
    return (cx + point_proj[0] * echelle, cy - point_proj[1] * echelle)


def transformer_point(
    point: Point3,
    matrice_vue: Mat4,
    matrice_proj: Mat4,
) -> Tuple[Point3, float]:
    # enchaîne vue + projection, renvoie aussi la profondeur pour le z-buffer plus tard
    p_vue = appliquer_matrice(matrice_vue, point)
    p_clip = appliquer_matrice(matrice_proj, p_vue)
    profondeur = p_clip[2]
    return p_clip, profondeur


def normaliser_device_vers_ecran(
    point_clip: Point3,
    largeur_ecran: int,
    hauteur_ecran: int,
) -> Optional[Point2]:
    # passage des coords normalisées [-1,1] vers pixels écran
    x, y, z = point_clip
    if z <= 0.0:
        return None
    sx = (x + 1.0) * 0.5 * largeur_ecran
    sy = (1.0 - y) * 0.5 * hauteur_ecran
    return (sx, sy)


def camera_orbite(cible: Point3, distance: float, angle_x: float, angle_y: float) -> Point3:
    # position de l'oeil autour de la cible, angle_x = vertical, angle_y = horizontal
    cx, cy, cz = cible
    ox = cx + distance * math.cos(angle_x) * math.sin(angle_y)
    oy = cy + distance * math.sin(angle_x)
    oz = cz + distance * math.cos(angle_x) * math.cos(angle_y)
    return (ox, oy, oz)
