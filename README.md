# Projet Maths — Informatique Graphique (S1 + Trimestre 3)

Application Python/Tkinter : géométrie graphique 2D (Semestre 1) et modélisation 3D par extrusion et surfaces de Bézier (Trimestre 3).

**Lancement :** `python main.py`  
**Prérequis :** Python 3.10+ (stdlib uniquement : `tkinter`, `math`).

---

## Structure du projet

```
Projet-Maths-1-Mathis-Tristan/
├── main.py
├── README.md
│
├── algo/                              # Semestre 1 — maths 2D
│   ├── bezier.py
│   ├── bspline_nurbs.py
│   ├── sutherland_hodgman.py
│   ├── lca.py
│   └── trimestre_3/                   # Trimestre 3 — maths 3D
│       ├── vecteurs.py
│       ├── courbes_3d.py
│       ├── projection.py
│       ├── extrusion.py
│       ├── maillage.py
│       ├── normales.py
│       ├── eclairage.py
│       ├── texture.py
│       ├── profil_courbe.py
│       ├── pascal.py
│       ├── surfaces_bezier.py
│       ├── subdivision_surface.py
│       └── render/
│           ├── projection.py          # Projecteur (orchestration)
│           └── raster.py              # Z-buffer manuel
│
└── UI/
    ├── main_menu.py
    ├── decoupage_window.py            # S1
    ├── remplissage_window.py          # S1
    ├── bezier_window.py               # S1
    ├── bspline_window.py              # S1
    └── trimestre_3/
        ├── extrusion_window.py
        ├── surfaces_window.py
        ├── test_3d_window.py
        └── widgets/
            └── canvas_3d.py
```

**Principe d'architecture :** toutes les formules sont dans `algo/`. L'UI ne fait qu'appeler les fonctions et afficher le résultat. Le dossier `render/` ne contient aucune formule, seulement la projection orchestrée et le z-buffer.

---

## Section 1 — Checklist du sujet

### Partie A — Extrusion graphique

- [x] **A.1** Courbes 3D : Bézier (De Casteljau), B-Splines (Cox-de Boor), NURBS — reprise du S1 avec sélection utilisateur
- [x] **A.2** Primitives d'extrusion interactives : profil 2D + trajectoire 3D
- [x] **A.3** Maillage triangulaire / rectangulaire des surfaces d'extrusion
- [x] **A.4** Tableau des normales en chaque sommet de la grille
- [x] **A.5** Coloriage et modèle d'éclairage (Phong : ambiant + diffuse + spéculaire)
- [x] **A.6** Texturage procédural : coordonnées UV + motif damier
- [x] **A.7** Visualisation 3D interactive : projection perspective, caméra orbite, z-buffer, rotation souris, zoom molette, rendu adaptatif

**Bonus Partie A (non traités, choix de stabilité pour la soutenance) :**

- [ ] Réfraction / transparence
- [ ] Extrusion généralisée (âme 3D hors plan z = 0)

### Partie B — Surfaces de Bézier

- [x] **B.1** Réseau de points de contrôle 3D (lignes et colonnes), exemple bi-cubique 4×4
- [x] **B.2** Produit tensoriel direct avec polynômes de Bernstein via le triangle de Pascal (`binom`)
- [x] **B.3** Produit tensoriel par double De Casteljau (réutilisation du S1 via `courbes_3d.py`)
- [x] **B.4** Subdivision du réseau en 4 : lignes puis colonnes à t = 0,5
- [x] **B.5** Maillage des surfaces générées
- [x] **B.6** Tableau des normales (flat shading par triangle)
- [x] **B.7** Coloriage, texturage et lumière Phong sur la surface

**Bonus Partie B (non traités, choix de stabilité pour la soutenance) :**

- [ ] Caméra libre avancée
- [ ] Raccordement de surfaces (continuité C¹ entre patches)

---

## Section 2 — Cartographie du code

| Notion mathématique / algorithmique | Fichier & fonction |
|---|---|
| De Casteljau 2D (S1) | `algo/bezier.py` → `bezier_point()` |
| De Casteljau 3D (pont S1) | `algo/trimestre_3/courbes_3d.py` → `bezier_de_casteljau_3d()` |
| Courbes 3D (Bézier / B-Spline / NURBS) | `algo/trimestre_3/courbes_3d.py` → `evaluer_trajectoire()`, `echantillonner_trajectoire()` |
| Profil 2D pour extrusion | `algo/trimestre_3/profil_courbe.py` → `echantillonner_profil_2d()` |
| Extrusion (profil × trajectoire) | `algo/trimestre_3/extrusion.py` → `extruder()` |
| Maillage rectangulaire / triangulaire | `algo/trimestre_3/maillage.py` → `maillage_depuis_grille()`, `maillage_rectangulaire()` |
| Normale d'un triangle | `algo/trimestre_3/normales.py` → `normale_triangle()` |
| Normales aux sommets (lissage) | `algo/trimestre_3/normales.py` → `normales_sommets_grille()` |
| Éclairage Phong | `algo/trimestre_3/eclairage.py` → `eclairage_phong()`, `eclairage_phong_texture()` |
| Coordonnées UV + texture damier | `algo/trimestre_3/texture.py` → `grille_uv_extrusion()`, `couleur_texture_damier()` |
| Projection 3D → 2D (matrices MVP) | `algo/trimestre_3/projection.py` → `matrice_vue()`, `matrice_projection_perspective()`, `projet_vue_perspective()` |
| Caméra orbite | `algo/trimestre_3/projection.py` → `camera_orbite()` |
| Z-buffer et rasterisation | `algo/trimestre_3/render/raster.py` → `ZBuffer`, `Rasterizer.tracer_triangle()` |
| Projecteur (couche render) | `algo/trimestre_3/render/projection.py` → `Projecteur.projeter_point()` |
| Triangle de Pascal / coefficients binomiaux | `algo/trimestre_3/pascal.py` → `triangle_pascal()`, `binom()` |
| Polynômes de Bernstein | `algo/trimestre_3/surfaces_bezier.py` → `bernstein()` |
| Produit tensoriel direct | `algo/trimestre_3/surfaces_bezier.py` → `surface_bezier_tensoriel_direct()` |
| Double De Casteljau (surface) | `algo/trimestre_3/surfaces_bezier.py` → `surface_bezier_double_casteljau()` |
| Subdivision réseau en 4 | `algo/trimestre_3/subdivision_surface.py` → `subdiviser_reseau_en_4()` |
| Opérations vectorielles 3D | `algo/trimestre_3/vecteurs.py` → `cross()`, `dot()`, `normalize()`, `lerp3d()` |
| Widget 3D (affichage, souris) | `UI/trimestre_3/widgets/canvas_3d.py` → `Canvas3D` |
| Fenêtre extrusion | `UI/trimestre_3/extrusion_window.py` → `ExtrusionWindow` |
| Fenêtre surfaces Bézier | `UI/trimestre_3/surfaces_window.py` → `SurfacesBezierWindow` |

---

## Section 3 — Récapitulatif mathématique

### Courbes 3D et De Casteljau

Pour évaluer une courbe de Bézier 3D en un paramètre $t \in [0, 1]$, on n'a pas recodé De Casteljau : on réutilise la version 2D du S1 sur chaque coordonnée indépendamment.

$$P(t) = \bigl(x(t),\ y(t),\ z(t)\bigr)$$

$$x(t) = \text{bezier\_point}\bigl([(p_0.x, 0), \ldots, (p_n.x, 0)],\ t\bigr)$$

Même principe pour $y(t)$ et $z(t)$. Le fichier `courbes_3d.py` est le pont entre le S1 et la 3D.

### Produit tensoriel direct (surface de Bézier)

Soit un réseau de contrôle $P_{ij}$ avec $i = 0..n$ et $j = 0..m$. La surface est :

$$S(u, v) = \sum_{i=0}^{n} \sum_{j=0}^{m} B_i^{n}(u)\, B_j^{m}(v)\, P_{ij}$$

Les polynômes de Bernstein sont :

$$B_i^{n}(t) = \binom{n}{i}\, t^i\, (1-t)^{n-i}$$

Le coefficient $\binom{n}{i}$ est calculé avec le triangle de Pascal dans `pascal.py` via `binom(n, i)`. C'est le lien explicite demandé par le sujet entre Pascal et les surfaces bi-cubiques.

### Double De Casteljau

Au lieu de la double somme, on applique De Casteljau deux fois :

1. Pour chaque colonne $j$, calculer $Q_j = \text{DeCasteljau}(P_{0j}, \ldots, P_{nj}, u)$
2. Puis $S(u,v) = \text{DeCasteljau}(Q_0, \ldots, Q_m, v)$

Les deux méthodes (Pascal et Casteljau) produisent la même surface ; seule la voie de calcul change.

### Subdivision du réseau en 4

À $t = 0{,}5$, on subdivise d'abord chaque **ligne** du réseau (direction $v$) par De Casteljau, puis chaque **colonne** du résultat (direction $u$). Un réseau 4×4 devient 7×7. On obtient 4 sous-patches bicubiques qui recouvrent la même surface.

### Calcul des normales

Pour un triangle de sommets $p_0$, $p_1$, $p_2$ :

$$\vec{u} = p_1 - p_0, \quad \vec{v} = p_2 - p_0$$

$$\vec{N} = \frac{\vec{u} \times \vec{v}}{\|\vec{u} \times \vec{v}\|}$$

On utilise le flat shading : une normale par face, ce qui fait ressortir les ombres sur les surfaces extrudées et les surfaces de Bézier.

### Éclairage de Phong (simplifié)

$$I = k_a + k_d \max(\vec{N} \cdot \vec{L}, 0) + k_s \max(\vec{R} \cdot \vec{V}, 0)^{\alpha}$$

Avec $\vec{L}$ direction vers la lumière, $\vec{V}$ direction vers l'œil, $\vec{R}$ le reflet spéculaire.

### Projection 3D → 2D

Pipeline : point monde → matrice vue → matrice projection perspective → normalisation NDC → conversion en pixels écran. La caméra orbite autour d'une cible avec deux angles (rotation souris) et une distance (zoom molette).

---

## Section 4 — 10 questions / réponses pour l'oral

### Q1. Pourquoi avoir séparé le code mathématique de l'interface ?

**R :** Pour la soutenance. Toutes les formules sont dans `algo/`, l'UI ne fait qu'appeler des fonctions. Au tableau, j'ouvre `algo/trimestre_3/surfaces_bezier.py` et j'explique les maths sans chercher dans les boutons Tkinter. C'est aussi plus simple à tester et à maintenir.

### Q2. Comment avez-vous réutilisé le code 2D du premier trimestre pour faire de la 3D ?

**R :** Via `courbes_3d.py` : chaque coordonnée 3D passe par la fonction 2D du S1 (`bezier_point`, `bspline_point`, `nurbs_point`) en trichant avec un faux point $(x, 0)$ ou $(0, y)$. On ne recode pas De Casteljau, on l'appelle trois fois. Le commentaire « appel de la fonction qu'on a fait au premier projet » marque ces ponts dans le code.

### Q3. Quelle est la différence algorithmique entre le produit tensoriel direct et le double De Casteljau ?

**R :** Le produit tensoriel direct calcule une double somme avec les $B_i^n(u)$ dont les coefficients viennent de Pascal. Le double De Casteljau fait deux passes d'interpolation linéaire en cascade : colonnes en $u$, puis la ligne obtenue en $v$. Même surface, deux chemins de calcul — l'un analytique (Bernstein), l'autre géométrique (Casteljau).

### Q4. Comment fonctionne la subdivision du réseau en 4 ?

**R :** On coupe la surface au milieu ($t = 0{,}5$). D'abord on subdivise chaque ligne du réseau avec De Casteljau (direction $v$), ce qui double la résolution en colonnes. Ensuite on subdivise chaque colonne (direction $u$). Un réseau 4×4 passe à 7×7 et on obtient 4 sous-patches bicubiques identiques géométriquement au patch initial.

### Q5. Comment calculez-vous la normale en un point pour gérer la lumière ?

**R :** Pour chaque triangle du maillage, on calcule $\vec{N} = \text{normalize}(\vec{u} \times \vec{v})$ avec deux arêtes du triangle. On utilise le flat shading : une seule normale par face, passée à `eclairage_phong_texture()` avec la position du centre du triangle et la direction de l'œil.

### Q6. Pourquoi Tkinter est-il suffisant si l'on gère le Z-buffer à la main ?

**R :** Tkinter sert uniquement à créer la fenêtre, les boutons et afficher l'image finale via `PhotoImage`. Le z-buffer, le remplissage de triangles et l'éclairage sont codés à la main dans `render/raster.py` et `algo/trimestre_3/eclairage.py`. On respecte la consigne : la librairie ne fait pas le travail du sujet, elle affiche juste nos pixels calculés.

### Q7. Comment avez-vous géré les problèmes de performances lors de la rotation de la caméra ?

**R :** Rendu adaptatif dans `Canvas3D` : pendant le drag ou le zoom, wireframe Tkinter natif (rapide, pas de z-buffer). Au relâchement de la souris, rendu complet avec z-buffer + Phong. Ça évite de recalculer des milliers de pixels à chaque frame.

### Q8. À quoi sert le triangle de Pascal dans votre code ?

**R :** Il calcule les coefficients binomiaux $\binom{n}{i}$ pour les polynômes de Bernstein dans `bernstein(n, i, t)`. C'est le lien mathématique explicite du sujet entre Pascal et le produit tensoriel direct des surfaces de Bézier.

### Q9. Comment fonctionne l'algorithme de projection de la 3D vers l'écran 2D ?

**R :** On construit une matrice vue (position de la caméra orbite autour d'une cible) et une matrice de projection perspective. Le point 3D est transformé en coordonnées normalisées, puis converti en pixels écran. Tout est dans `algo/trimestre_3/projection.py` ; `Projecteur` dans `render/projection.py` orchestre sans recalculer les formules.

### Q10. Comment est générée la texture procédurale en damier ?

**R :** Chaque sommet reçoit des coordonnées UV : $u$ le long du profil (0 à 1), $v$ le long de la trajectoire (0 à 1). La fonction `couleur_texture_damier(u, v)` découpe l'espace UV en cases et alterne deux couleurs selon la parité de `int(u × 10) + int(v × 10)`. Pas d'image externe, tout est procédural.

---

## Section 5 — Tutoriel de soutenance (guide des fonctionnalités)

Ce guide décrit **tout ce que tu peux montrer à l'oral**, bouton par bouton, en langage simple. Lance l'appli avec `python main.py`.

### Menu principal

| Bouton | Ce que ça ouvre | À dire à l'oral |
|---|---|---|
| **Découpage** | Module Sutherland-Hodgman (2D) | « On coupe un polygone avec une fenêtre de clipping. » |
| **Remplissage** | Module LCA / scanline (2D) | « On remplit des polygones avec deux règles classiques. » |
| **Courbe de bézier** | Courbes 2D De Casteljau / Bernstein | « C'est notre base du S1, réutilisée ensuite en 3D. » |
| **BSplines / NURBS** | Courbes 2D avec Cox-de Boor | « Même principe, mais avec des B-Splines et des poids NURBS. » |
| **Test 3D (trajectoire)** | Première vue 3D : une courbe dans l'espace | « Pont entre le S1 et la 3D : une trajectoire projetée à l'écran. » |
| **Extrusion** | Partie A du sujet T3 | « On extrude un profil 2D le long d'une trajectoire 3D. » |
| **Surfaces de Bézier** | Partie B du sujet T3 | « On génère une surface à partir d'un réseau de points 3D. » |

---

### Module Découpage (`UI/decoupage_window.py`)

**Objectif :** montrer qu'un polygone est rogné à l'intérieur (ou à l'extérieur) d'une zone de découpe.

| Bouton / option | Action vulgarisée |
|---|---|
| **Polygone à découper** | Passe en mode « forme à couper ». Les clics ajoutent les sommets du polygone rouge. |
| **Fenêtre de découpe** | Passe en mode « cadre de découpe ». Les clics dessinent la fenêtre (polygone bleu). |
| **Effacer tout** | Vide le canvas et remet le zoom à zéro. |
| **Bonus : fenêtre quelconque (triangulation)** | Case à cocher du S1. Si la fenêtre n'est pas convexe, on la découpe en triangles avant le clipping. |

**Souris et clavier :**

- **Clic gauche** sur le fond : ajoute un point au polygone en cours.
- **Clic gauche** sur un point existant + glisser : déplace ce sommet.
- **Clic droit** : ferme le polygone en cours (minimum 3 points) et lance le découpage automatiquement.
- **Molette** : zoom avant / arrière sur le dessin.
- **Clic molette + glisser** : déplace la vue (pan).
- **Échap** : annule le polygone en cours de tracé sans le fermer.

**Ce qu'il faut montrer :** dessiner un polygone grand, une fenêtre convexe, clic droit pour fermer → la partie visible reste affichée en vert.

---

### Module Remplissage (`UI/remplissage_window.py`)

**Objectif :** remplir l'intérieur de polygones avec l'algorithme LCA (scanline).

| Bouton / option | Action vulgarisée |
|---|---|
| **Effacer tout** | Supprime tous les polygones et le remplissage. |
| **Pair/impair** | Règle « even-odd » : un rayon qui traverse un nombre impair de bords → intérieur. |
| **Enroulement non nul** | Règle « winding » : compte le sens de rotation des bords autour du pixel. |

**Souris :**

- **Clic gauche** : ajoute un sommet (ou déplace un point si tu cliques dessus).
- **Clic droit** : ferme le polygone (3 points min.) et déclenche le remplissage.

**Ce qu'il faut montrer :** deux polygones qui se croisent, basculer entre pair/impair et enroulement → la zone remplie change.

---

### Module Courbe de Bézier 2D (`UI/bezier_window.py`)

**Objectif :** illustrer De Casteljau vs Bernstein sur des courbes 2D (base du S1).

| Bouton / option | Action vulgarisée |
|---|---|
| **Suppr Courbe** | Supprime la courbe actuellement sélectionnée. |
| **Effacer Tout** | Supprime toutes les courbes. |
| **Algo Casteljau** | Case cochée = calcul géométrique (De Casteljau). Décochée = calcul par polynômes de Bernstein. |
| **Doubler Point** | Duplique le point de contrôle que tu es en train de déplacer (utile pour créer des cassures). |
| **Précision (slider)** | Plus la valeur est petite, plus la courbe est lisse (plus de segments dessinés). |

**Souris :**

- **Clic gauche** : place un point de contrôle sur la courbe active.
- **Clic gauche + glisser** sur un point : le déplace.
- **Clic droit** : démarre une nouvelle courbe (nouvelle liste de points).

**Clavier :** flèches = déplacer la vue, A/E = rotation, S/D = zoom, Suppr = effacer le point sélectionné.

**Ce qu'il faut montrer :** 4 points, courbe bleue, cocher/décocher Casteljau → même résultat visuel, deux algos différents.

---

### Module B-Splines / NURBS (`UI/bspline_window.py`)

**Objectif :** courbes plus flexibles que Bézier, avec degré et poids réglables.

| Bouton / option | Action vulgarisée |
|---|---|
| **Suppr Courbe** | Supprime la courbe active. |
| **Effacer Tout** | Vide tout. |
| **Doubler Point** | Duplique le point sélectionné. |
| **Mode NURBS (poids)** | Active les poids : certains points « attirent » plus la courbe. |
| **Degré p** | Degré de la B-Spline (3 = cubique, classique). |
| **Précision (slider)** | Finesse de l'échantillonnage de la courbe. |
| **Noeuds custom** | Case pour utiliser un vecteur nodal personnalisé sur la courbe active. |
| **Champ U =** | Saisie manuelle des valeurs de nœuds (knots), séparées par des espaces. |
| **Appliquer** | Valide les nœuds custom et redessine. |

**Souris :** clic gauche = point / drag, clic droit = nouvelle courbe.

**Clavier :** Suppr = supprimer un point, +/- = modifier le poids NURBS du point sélectionné, Entrée = appliquer les nœuds.

**Ce qu'il faut montrer :** B-Spline cubique avec 5–6 points, puis activer NURBS et monter un poids avec `+`.

---

### Test 3D — trajectoire (`UI/trimestre_3/test_3d_window.py`)

**Objectif :** première démo 3D — une courbe dans l'espace, projetée à l'écran.

| Bouton / option | Action vulgarisée |
|---|---|
| **Bézier / B-Spline / NURBS** | Choix du type de courbe 3D (réutilise le S1 via `courbes_3d.py`). |
| **Redessiner** | Force le rendu complet (avec z-buffer si applicable). |

**Souris sur le canvas 3D :**

- **Clic gauche + glisser** : fait tourner la caméra autour de l'objet (wireframe rapide pendant le mouvement).
- **Relâcher** : affiche le rendu complet.
- **Molette** : zoom avant / arrière.

**Ce qu'il faut montrer :** changer Bézier → B-Spline → NURBS, tourner la scène, expliquer le pont S1 → 3D.

---

### Extrusion — Partie A (`UI/trimestre_3/extrusion_window.py`)

**Objectif :** faire « glisser » un profil 2D le long d'un chemin 3D pour obtenir un volume.

**Panneau gauche (canvas 2D) :**

- **Clic gauche** sur le fond : ajoute un point de contrôle du profil.
- **Clic gauche + glisser** sur un point rouge : déplace ce point de contrôle.
- **Clic droit** sur un point : supprime ce point (minimum 2 points conservés).

| Bouton / option | Action vulgarisée |
|---|---|
| **Courbe profil — Bézier / B-Spline / NURBS** | Type de courbe utilisée pour lisser le profil 2D (trait bleu). |
| **Courbe trajectoire — Bézier / B-Spline / NURBS** | Type de courbe du chemin 3D que suit l'extrusion. |
| **Hauteur profil** | Agrandit ou rétrécit le profil dans le plan vertical (axe Y). |
| **Échelle début** | Taille du profil au départ de la trajectoire. |
| **Échelle fin** | Taille du profil à la fin (effet « cône » si différent du début). |
| **Pas trajectoire** | Nombre de coupes le long du chemin (plus = surface plus lisse). |
| **Pas profil** | Nombre de points sur le profil 2D. |
| **Texture (Damier)** | Active ou désactive le motif damier sur la surface 3D. |
| **Extruder** | Lance le calcul : profil × trajectoire → grille 3D + maillage + affichage. |
| **Effacer points** | Vide tous les points de contrôle du profil 2D. |
| **Profil demo** | Recharge l'exemple par défaut (4 points en forme de goutte). |

**Panneau droit (canvas 3D) :** même contrôles que Test 3D (rotation, zoom, relâcher = ombres Phong).

**Ce qu'il faut montrer en démo :**

1. Montrer le profil 2D et les points de contrôle.
2. Cliquer **Extruder** → surface 3D ombrée.
3. Cocher **Texture (Damier)** → damier procédural.
4. Changer **Échelle fin** puis **Extruder** → le volume se rétrécit.
5. Tourner la vue pour montrer les ombres (flat shading + Phong).

---

### Surfaces de Bézier — Partie B (`UI/trimestre_3/surfaces_window.py`)

**Objectif :** créer une surface 3D à partir d'un filet de points de contrôle (produit tensoriel).

| Bouton / option | Action vulgarisée |
|---|---|
| **Produit Tensoriel (Pascal)** | Calcule la surface avec la double somme et les coefficients binomiaux (triangle de Pascal). |
| **Double De Casteljau** | Calcule la même surface mais par deux passes De Casteljau (comme en S1, en 3D). |
| **Pas u / Pas v** | Résolution de la surface : combien de points d'échantillonnage en u et en v (plus = plus lisse, plus lent). |
| **Générer** | Lance le calcul choisi et affiche la surface maillée à droite. |
| **Subdiviser en 4** | Coupe le réseau de contrôle en 4 morceaux (De Casteljau à t = 0,5) : le filet passe de 4×4 à 7×7 points. |

**Panneau gauche :** filet de contrôle 3D (points rouges + segments gris).

**Panneau droit :** surface générée avec éclairage (relâcher la souris après rotation).

**Souris (les deux panneaux) :** rotation = clic + glisser, zoom = molette, relâcher = rendu ombré complet.

**Ce qu'il faut montrer en démo :**

1. Au lancement : réseau 4×4 bi-cubique déjà visible à gauche.
2. **Générer** avec Pascal → surface lisse à droite.
3. Basculer sur **Double De Casteljau** + **Générer** → même forme, autre algorithme.
4. **Subdiviser en 4** → le filet devient plus dense (7×7).
5. **Générer** à nouveau → même surface globale, réseau plus fin.
6. Tourner pour montrer les ombres sur les faces triangulées.

---

### Contrôles 3D communs (tous les canvas `Canvas3D`)

| Action | Effet |
|---|---|
| **Clic gauche + glisser** | Tourne la caméra autour de l'objet. Horizontal = tourne autour de Y, vertical = autour de X. Affichage wireframe (rapide) pendant le mouvement. |
| **Relâcher le clic** | Recalcule le rendu complet : z-buffer + éclairage Phong (ombres visibles). |
| **Molette vers le haut** | Zoome (rapproche la caméra). |
| **Molette vers le bas** | Dézoome (éloigne la caméra). |
| **~180 ms après le zoom** | Rendu complet automatique une fois le défilement terminé. |

**Axes affichés :** rouge = X, vert = Y, bleu = Z (repère 3D pour situer l'objet).

---

### Scénario de démo recommandé pour l'oral (~10 min)

**Ordre suggéré pour enchaîner sans se perdre :**

1. **Menu → Courbe de bézier** : 30 s — « Voici notre De Casteljau du S1, réutilisé partout ensuite. »
2. **Menu → Test 3D** : 1 min — « Même algo, mais en 3D via `courbes_3d.py`. »
3. **Menu → Extrusion** : 3 min — profil 2D, **Extruder**, texture damier, rotation avec ombres. « Partie A : extrusion + maillage + normales + Phong + UV. »
4. **Menu → Surfaces de Bézier** : 3 min — réseau 4×4, **Générer** (Pascal puis Casteljau), **Subdiviser en 4**. « Partie B : produit tensoriel, Pascal, subdivision. »
5. **Questions du prof** : ouvrir `algo/trimestre_3/surfaces_bezier.py` ou `extrusion.py` et s'appuyer sur la Section 2 et Section 4 de ce README.

**Rappel bonus :** ne pas cliquer sur la case « fenêtre quelconque » du découpage en disant que c'est un bonus S1 non prioritaire pour le T3, sauf si le prof demande explicitement.

---

## Modules Semestre 1 (rappel)

| Fonctionnalité | Algorithme | Interface |
|---|---|---|
| Découpage de polygones | `algo/sutherland_hodgman.py` | `UI/decoupage_window.py` |
| Remplissage de polygones | `algo/lca.py` | `UI/remplissage_window.py` |
| Courbes de Bézier 2D | `algo/bezier.py` | `UI/bezier_window.py` |
| B-Splines / NURBS 2D | `algo/bspline_nurbs.py` | `UI/bspline_window.py` |

**Modules Trimestre 3 :** voir Section 5 pour le détail de chaque bouton et le scénario de démo oral.
