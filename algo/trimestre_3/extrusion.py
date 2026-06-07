# extrusion d'un profil 2D le long d'une trajectoire 3D
from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

from algo.trimestre_3.courbes_3d import TypeCourbe, evaluer_trajectoire
from algo.trimestre_3.vecteurs import Point3, Vecteur3, add, cross, dot, normalize, scale, sub

Point2 = Tuple[float, float]
Grille3D = List[List[Point3]]


def _tangente_trajectoire(
    points_traj: Sequence[Point3],
    t: float,
    type_courbe: TypeCourbe,
    degre: int,
) -> Vecteur3:
    eps = 0.001
    t0 = max(0.0, t - eps)
    t1 = min(1.0, t + eps)
    p0 = evaluer_trajectoire(points_traj, t0, type_courbe, degre)
    p1 = evaluer_trajectoire(points_traj, t1, type_courbe, degre)
    if p0 is None or p1 is None:
        return (0.0, 0.0, 1.0)
    return normalize(sub(p1, p0))


def _repere_local(tangente: Vecteur3) -> Tuple[Vecteur3, Vecteur3]:
    # construit les axes du plan du profil perpendiculaire à la trajectoire
    ref = (0.0, 1.0, 0.0)
    if abs(dot(tangente, ref)) > 0.95:
        ref = (0.0, 0.0, 1.0)
    droite = normalize(cross(ref, tangente))
    if droite == (0.0, 0.0, 0.0):
        droite = (1.0, 0.0, 0.0)
    haut = normalize(cross(tangente, droite))
    return droite, haut


def _echelle_sur_t(t: float, echelle_debut: float, echelle_fin: float) -> float:
    return echelle_debut + (echelle_fin - echelle_debut) * t


def _point_profil_3d(
    centre: Point3,
    droite: Vecteur3,
    haut: Vecteur3,
    profil_uv: Point2,
    hauteur: float,
    echelle: float,
) -> Point3:
    u, v = profil_uv
    offset = add(scale(droite, u * echelle), scale(haut, v * hauteur))
    return add(centre, offset)


def extruder(
    profil_2d: Sequence[Point2],
    points_traj: Sequence[Point3],
    nb_traj: int = 30,
    type_courbe: TypeCourbe = "bezier",
    degre: int = 3,
    hauteur: float = 1.0,
    echelle_debut: float = 1.0,
    echelle_fin: float = 1.0,
) -> Grille3D:
    # grille[i][j] = point 3D, i le long de la trajectoire, j le long du profil
    if len(profil_2d) < 2 or len(points_traj) < 2 or nb_traj < 2:
        return []

    grille: Grille3D = []
    for i in range(nb_traj):
        t = i / (nb_traj - 1)
        centre = evaluer_trajectoire(points_traj, t, type_courbe, degre)
        if centre is None:
            continue
        tangente = _tangente_trajectoire(points_traj, t, type_courbe, degre)
        droite, haut_local = _repere_local(tangente)
        echelle = _echelle_sur_t(t, echelle_debut, echelle_fin)

        ligne: List[Point3] = []
        for profil_uv in profil_2d:
            ligne.append(
                _point_profil_3d(centre, droite, haut_local, profil_uv, hauteur, echelle)
            )
        grille.append(ligne)

    return grille
