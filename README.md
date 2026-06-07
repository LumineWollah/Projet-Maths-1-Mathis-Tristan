# Projet Maths – Géométrie graphique

Application Python/Tkinter regroupant quatre modules de géométrie graphique : découpage de polygones, remplissage, courbes de Bézier et B-Splines/NURBS.

## Lancement

```bash
python main.py
```

**Prérequis :** Python 3.10+ (stdlib uniquement : `tkinter`, `math`).

## Structure du projet

```
Projet-Maths-1-Mathis-Tristan/
├── main.py                  # Point d'entrée
├── README.md
│
├── algo/                    # Algorithmes (logique pure, sans UI)
│   ├── __init__.py
│   ├── sutherland_hodgman.py  # Découpage Sutherland-Hodgman + triangulation
│   ├── lca.py                 # Remplissage par scanline (LCA, winding)
│   ├── bezier.py              # Courbes de Bézier (Casteljau, Bernstein)
│   └── bspline_nurbs.py       # B-Splines et NURBS (Cox-de-Boor)
│
└── UI/                      # Interfaces graphiques Tkinter
    ├── __init__.py
    ├── main_menu.py           # Menu principal
    ├── decoupage_window.py    # Module découpage
    ├── remplissage_window.py  # Module remplissage
    ├── bezier_window.py       # Module Bézier
    └── bspline_window.py      # Module B-Splines / NURBS
```

## Où trouver quoi ?

| Fonctionnalité | Algorithme (`algo/`) | Interface (`UI/`) |
|---|---|---|
| Découpage de polygones | `sutherland_hodgman.py` | `decoupage_window.py` |
| Remplissage de polygones | `lca.py` | `remplissage_window.py` |
| Courbes de Bézier | `bezier.py` | `bezier_window.py` |
| B-Splines / NURBS | `bspline_nurbs.py` | `bspline_window.py` |

## Modules

### Découpage (`algo/sutherland_hodgman.py`)
- `sutherland_hodgman()` : découpage classique (fenêtre convexe)
- `clip_subject_with_window_triangulation()` : bonus pour fenêtre concave (ear clipping)

### Remplissage (`algo/lca.py`)
- `lca_fill(polygon, rule)` : remplissage par scanline
  - `"evenodd"` : règle pair/impair (LCA)
  - `"winding"` : enroulement non nul

### Bézier (`algo/bezier.py`)
- `bezier_point()` : évaluation via De Casteljau
- `bernstein_point()` : évaluation via polynômes de Bernstein
- `bezier_polyline()` : échantillonnage en polyligne

### B-Splines / NURBS (`algo/bspline_nurbs.py`)
- `bspline_point()` : courbe B-Spline
- `nurbs_point()` : courbe NURBS pondérée
- `open_uniform_knots()` / `parse_knots()` : gestion du vecteur nodal
