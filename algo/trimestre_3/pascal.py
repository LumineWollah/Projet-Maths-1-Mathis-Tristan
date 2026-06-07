# triangle de Pascal pour les coefficients binomiaux (surfaces de Bézier)
from __future__ import annotations

from typing import List


def triangle_pascal(n: int) -> List[List[int]]:
    # renvoie les lignes 0..n du triangle de Pascal
    if n < 0:
        return []
    lignes: List[List[int]] = []
    for i in range(n + 1):
        ligne = [1]
        if i > 0:
            prev = lignes[i - 1]
            for j in range(1, i):
                ligne.append(prev[j - 1] + prev[j])
            ligne.append(1)
        lignes.append(ligne)
    return lignes


def binom(n: int, k: int) -> int:
    # coefficient binomial C(n,k) via le triangle de Pascal
    if k < 0 or k > n:
        return 0
    tri = triangle_pascal(n)
    return tri[n][k]
