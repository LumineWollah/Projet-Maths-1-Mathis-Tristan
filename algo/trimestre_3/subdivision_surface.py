# subdivision d un reseau de controle de surface de bezier
from __future__ import annotations

from typing import List, Sequence, Tuple

from algo.trimestre_3.vecteurs import Point3, lerp3d

Reseau3D = List[List[Point3]]


def subdiviser_courbe_bezier_3d(
    points: Sequence[Point3], t: float = 0.5
) -> Tuple[List[Point3], List[Point3]]:
    # subdivision de casteljau d une courbe 3D en deux morceaux
    n = len(points)
    if n < 2:
        return list(points), list(points)

    if t < 0.0:
        t = 0.0
    elif t > 1.0:
        t = 1.0

    niveaux: List[List[Point3]] = [list(points)]
    courant = list(points)
    while len(courant) > 1:
        courant = [lerp3d(courant[i], courant[i + 1], t) for i in range(len(courant) - 1)]
        niveaux.append(courant[:])

    gauche = [niveaux[k][0] for k in range(n)]
    droite = [niveaux[n - 1 - k][k] for k in range(n)]
    return gauche, droite


def _fusionner_subdivision(gauche: Sequence[Point3], droite: Sequence[Point3]) -> List[Point3]:
    return list(gauche) + list(droite[1:])


def subdiviser_reseau_lignes(reseau: Sequence[Sequence[Point3]], t: float = 0.5) -> Reseau3D:
    # subdivise chaque ligne du reseau suivant v a t
    resultat: Reseau3D = []
    for ligne in reseau:
        g, d = subdiviser_courbe_bezier_3d(ligne, t)
        resultat.append(_fusionner_subdivision(g, d))
    return resultat


def subdiviser_reseau_colonnes(reseau: Sequence[Sequence[Point3]], t: float = 0.5) -> Reseau3D:
    # subdivise chaque colonne du reseau suivant u a t
    if not reseau:
        return []
    nu = len(reseau)
    nv = len(reseau[0])
    colonnes_sub: List[List[Point3]] = []
    for j in range(nv):
        colonne = [reseau[i][j] for i in range(nu)]
        g, d = subdiviser_courbe_bezier_3d(colonne, t)
        colonnes_sub.append(_fusionner_subdivision(g, d))

    nv2 = len(colonnes_sub[0])
    nu2 = len(colonnes_sub)
    resultat: Reseau3D = [[(0.0, 0.0, 0.0) for _ in range(nu2)] for _ in range(nv2)]
    for j in range(nu2):
        for i in range(nv2):
            resultat[i][j] = colonnes_sub[j][i]
    return resultat


def subdiviser_reseau(reseau: Sequence[Sequence[Point3]], t: float = 0.5) -> Reseau3D:
    # lignes puis colonnes avec de casteljau a t
    apres_lignes = subdiviser_reseau_lignes(reseau, t)
    return subdiviser_reseau_colonnes(apres_lignes, t)


def extraire_quatre_sous_reseaux(reseau: Sequence[Sequence[Point3]]) -> Tuple[Reseau3D, Reseau3D, Reseau3D, Reseau3D]:
    # extrait les 4 sous reseaux 4x4 apres une subdivision complete
    nu = len(reseau)
    nv = len(reseau[0]) if nu > 0 else 0
    demi_u = (nu - 1) // 2
    demi_v = (nv - 1) // 2

    def extraire(i0: int, j0: int) -> Reseau3D:
        patch: Reseau3D = []
        for i in range(i0, i0 + demi_u + 1):
            ligne = [reseau[i][j] for j in range(j0, j0 + demi_v + 1)]
            patch.append(ligne)
        return patch

    sw = extraire(0, 0)
    se = extraire(0, demi_v)
    nw = extraire(demi_u, 0)
    ne = extraire(demi_u, demi_v)
    return sw, se, nw, ne


def subdiviser_reseau_en_4(reseau: Sequence[Sequence[Point3]], t: float = 0.5) -> Reseau3D:
    # subdivise le reseau en 4 sous patches et renvoie le reseau raffine complet
    return subdiviser_reseau(reseau, t)
