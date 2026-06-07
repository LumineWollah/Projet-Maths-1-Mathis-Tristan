# couche render : aucune formule ici, tout est dans algo/trimestre_3/projection.py
from __future__ import annotations

from typing import List, Optional, Tuple

from algo.trimestre_3.projection import (
    Mat4,
    Point2,
    appliquer_matrice,
    camera_orbite,
    convertir_vers_ecran,
    matrice_identite,
    matrice_projection_orthographique,
    matrice_projection_perspective,
    matrice_rotation_x,
    matrice_rotation_y,
    matrice_rotation_z,
    matrice_translation,
    matrice_vue,
    multiplier_matrices,
    normaliser_device_vers_ecran,
    projet_orthographique,
    projet_perspective_simple,
    projet_vue_perspective,
)
from algo.trimestre_3.vecteurs import Point3

PointEcran = Tuple[float, float, float]  # x, y, profondeur


class Projecteur:
    def __init__(self, largeur: int = 800, hauteur: int = 600):
        self.largeur = largeur
        self.hauteur = hauteur
        self.echelle = 80.0
        self.mode = "orbite"

        self.cible: Point3 = (0.0, 0.0, 0.0)
        self.distance_orbite = 10.0
        self.angle_orbite_x = 0.35
        self.angle_orbite_y = 0.8
        self.distance_camera = 5.0
        self.focale = 400.0

        self.matrice_modele: Mat4 = matrice_identite()
        self.oeil: Point3 = camera_orbite(
            self.cible, self.distance_orbite, self.angle_orbite_x, self.angle_orbite_y
        )
        self._maj_matrices_pipeline()

    def _maj_matrices_pipeline(self):
        ratio = self.largeur / max(self.hauteur, 1)
        self.matrice_vue = matrice_vue(self.oeil, self.cible)
        self.matrice_proj = matrice_projection_perspective(
            fov_y=0.9,
            ratio=ratio,
            proche=0.1,
            loin=100.0,
        )
        self.matrice_mvp = multiplier_matrices(
            self.matrice_proj,
            multiplier_matrices(self.matrice_vue, self.matrice_modele),
        )

    def redimensionner(self, largeur: int, hauteur: int):
        self.largeur = largeur
        self.hauteur = hauteur
        self._maj_matrices_pipeline()

    def set_mode(self, mode: str):
        # perspective_simple = rapide, pipeline = matrices complètes
        self.mode = mode

    def set_camera(self, oeil: Point3, cible: Point3):
        self.oeil = oeil
        self.cible = cible
        self._maj_matrices_pipeline()

    def definir_orbite(self, angle_x: float, angle_y: float, distance: Optional[float] = None):
        self.angle_orbite_x = angle_x
        self.angle_orbite_y = angle_y
        if distance is not None:
            self.distance_orbite = distance
        self.oeil = camera_orbite(
            self.cible, self.distance_orbite, self.angle_orbite_x, self.angle_orbite_y
        )
        self._maj_matrices_pipeline()

    def definir_cible(self, cible: Point3):
        self.cible = cible
        self.oeil = camera_orbite(
            self.cible, self.distance_orbite, self.angle_orbite_x, self.angle_orbite_y
        )
        self._maj_matrices_pipeline()

    def ajuster_zoom(self, facteur: float):
        # facteur > 1 = zoom avant, facteur < 1 = zoom arrière
        self.distance_orbite = max(2.0, min(40.0, self.distance_orbite / facteur))
        self.oeil = camera_orbite(
            self.cible, self.distance_orbite, self.angle_orbite_x, self.angle_orbite_y
        )
        self._maj_matrices_pipeline()

    def translater_modele(self, tx: float, ty: float, tz: float):
        self.matrice_modele = multiplier_matrices(
            matrice_translation(tx, ty, tz),
            self.matrice_modele,
        )
        self._maj_matrices_pipeline()

    def tourner_modele(self, ax: float, ay: float, az: float):
        rot = multiplier_matrices(
            matrice_rotation_z(az),
            multiplier_matrices(matrice_rotation_y(ay), matrice_rotation_x(ax)),
        )
        self.matrice_modele = multiplier_matrices(rot, self.matrice_modele)
        self._maj_matrices_pipeline()

    def reset_modele(self):
        self.matrice_modele = matrice_identite()
        self._maj_matrices_pipeline()

    def projeter_point(self, point: Point3) -> Optional[PointEcran]:
        # délègue tout le calcul à algo/
        p_modele = appliquer_matrice(self.matrice_modele, point)
        p_vue = appliquer_matrice(self.matrice_vue, p_modele)

        if self.mode == "orthographique":
            p2d = projet_orthographique(p_modele, self.echelle)
            ecran = convertir_vers_ecran(p2d, self.largeur, self.hauteur, 1.0)
            return (ecran[0], ecran[1], p_modele[2])

        if self.mode == "perspective_simple":
            p2d = projet_perspective_simple(p_modele, self.distance_camera, self.focale)
            if p2d is None:
                return None
            ecran = convertir_vers_ecran(p2d, self.largeur, self.hauteur, 1.0)
            return (ecran[0], ecran[1], p_modele[2])

        if self.mode == "orbite":
            res = projet_vue_perspective(p_vue, self.focale, self.largeur, self.hauteur, 1.0)
            if res is None:
                return None
            ecran, profondeur = res
            return (ecran[0], ecran[1], profondeur)

        # pipeline complet vue * projection (ancien mode)
        p_clip = appliquer_matrice(self.matrice_proj, p_vue)
        ecran = normaliser_device_vers_ecran(p_clip, self.largeur, self.hauteur)
        if ecran is None:
            return None
        return (ecran[0], ecran[1], -p_vue[2])

    def projeter_points(self, points: List[Point3]) -> List[PointEcran]:
        resultat = []
        for p in points:
            pe = self.projeter_point(p)
            if pe is not None:
                resultat.append(pe)
        return resultat
