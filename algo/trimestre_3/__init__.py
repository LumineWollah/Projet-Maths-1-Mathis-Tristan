"""Algorithmes 3D — extrusion, surfaces de Bézier, projection, éclairage."""

from algo.trimestre_3.vecteurs import add, sub, dot, cross, normalize, lerp3d
from algo.trimestre_3.courbes_3d import evaluer_trajectoire, echantillonner_trajectoire
from algo.trimestre_3.projection import (
    matrice_vue,
    matrice_projection_perspective,
    projet_perspective_simple,
    appliquer_matrice,
    camera_orbite,
)
from algo.trimestre_3.extrusion import extruder
from algo.trimestre_3.maillage import maillage_depuis_grille, maillage_rectangulaire
from algo.trimestre_3.normales import normale_triangle, normales_sommets_grille
from algo.trimestre_3.eclairage import (
    eclairage_phong,
    eclairage_phong_texture,
    LUMIERE_POSITION,
    COULEUR_BASE_EXTRUSION,
    couleur_vers_hex,
)
from algo.trimestre_3.profil_courbe import echantillonner_profil_2d, evaluer_profil_2d
from algo.trimestre_3.texture import grille_uv_extrusion, couleur_texture_damier
from algo.trimestre_3.pascal import triangle_pascal, binom
from algo.trimestre_3.surfaces_bezier import (
    bernstein,
    surface_bezier_tensoriel_direct,
    surface_bezier_double_casteljau,
    reseau_bicubique_demo,
)
from algo.trimestre_3.subdivision_surface import subdiviser_reseau_en_4

__all__ = [
    "add",
    "sub",
    "dot",
    "cross",
    "normalize",
    "lerp3d",
    "evaluer_trajectoire",
    "echantillonner_trajectoire",
    "matrice_vue",
    "matrice_projection_perspective",
    "projet_perspective_simple",
    "appliquer_matrice",
    "camera_orbite",
    "extruder",
    "maillage_depuis_grille",
    "maillage_rectangulaire",
    "normale_triangle",
    "normales_sommets_grille",
    "eclairage_phong",
    "eclairage_phong_texture",
    "LUMIERE_POSITION",
    "COULEUR_BASE_EXTRUSION",
    "couleur_vers_hex",
    "echantillonner_profil_2d",
    "evaluer_profil_2d",
    "grille_uv_extrusion",
    "couleur_texture_damier",
    "triangle_pascal",
    "binom",
    "bernstein",
    "surface_bezier_tensoriel_direct",
    "surface_bezier_double_casteljau",
    "reseau_bicubique_demo",
    "subdiviser_reseau_en_4",
]
