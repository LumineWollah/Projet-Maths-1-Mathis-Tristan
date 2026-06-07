# modèle de Phong simplifié, lumière fixe dans la scène
from __future__ import annotations

from typing import Tuple

from algo.trimestre_3.vecteurs import Point3, Vecteur3, dot, normalize, scale, sub

Couleur = Tuple[int, int, int]
CouleurF = Tuple[float, float, float]

# lumière au dessus à droite, assez proche pour voir les ombres
LUMIERE_POSITION: Point3 = (4.0, 9.0, 5.0)

COULEUR_BASE_EXTRUSION: CouleurF = (0.55, 0.82, 0.95)


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _clamp255(v: float) -> int:
    return max(0, min(255, int(round(v))))


def couleur_vers_hex(couleur: Couleur) -> str:
    # format #RRGGBB pour tkinter
    r, g, b = couleur
    return f"#{_clamp255(r):02x}{_clamp255(g):02x}{_clamp255(b):02x}"


def eclairage_phong(
    point: Point3,
    normale: Vecteur3,
    oeil: Point3,
    couleur_base: CouleurF = COULEUR_BASE_EXTRUSION,
    lumiere: Point3 = LUMIERE_POSITION,
    ka: float = 0.12,
    kd: float = 0.9,
    ks: float = 0.45,
    shininess: float = 20.0,
) -> Couleur:
    n = normalize(normale)
    if n == (0.0, 0.0, 0.0):
        return (
            _clamp255(couleur_base[0] * ka * 255),
            _clamp255(couleur_base[1] * ka * 255),
            _clamp255(couleur_base[2] * ka * 255),
        )

    l_dir = normalize(sub(lumiere, point))
    v_dir = normalize(sub(oeil, point))

    # double face pour ne pas tout éteindre
    ndotl = dot(n, l_dir)
    diff = _clamp01(abs(ndotl))

    ref = sub(scale(n, 2.0 * ndotl), l_dir)
    spec = _clamp01(abs(dot(ref, v_dir))) ** shininess

    # on calcule chaque canal RGB séparément puis on clamp en int
    r = couleur_base[0] * (ka + kd * diff) * 255.0 + ks * spec * 255.0
    g = couleur_base[1] * (ka + kd * diff) * 255.0 + ks * spec * 255.0
    b = couleur_base[2] * (ka + kd * diff) * 255.0 + ks * spec * 255.0

    return (_clamp255(r), _clamp255(g), _clamp255(b))


def eclairage_phong_texture(
    point: Point3,
    normale: Vecteur3,
    oeil: Point3,
    u: float,
    v: float,
    utiliser_texture: bool = False,
    lumiere: Point3 = LUMIERE_POSITION,
) -> Couleur:
    # couleur de base = damier ou couleur unie, puis Phong par dessus
    from algo.trimestre_3.texture import couleur_base_texture

    base = couleur_base_texture(u, v, utiliser_texture)
    return eclairage_phong(point, normale, oeil, couleur_base=base, lumiere=lumiere)
