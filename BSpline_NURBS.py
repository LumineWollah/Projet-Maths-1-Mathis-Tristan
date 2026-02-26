import tkinter as tk
from tkinter import ttk
import math

# ============================================================
# Cox–de–Boor (Bases B-Spline) + NURBS
# Convention:
# - nb_ctrl = len(points)
# - p = degré
# - knot vector length = nb_ctrl + p + 1
# - i in [0 .. nb_ctrl-1]
# - param t in [U[p] .. U[nb_ctrl]]
# ============================================================

def _parse_knots(text: str):
    """
    Parse "0,0,0,0, 0.5, 1,1,1,1" -> [float,...]
    Accepts spaces.
    """
    parts = [s.strip() for s in text.replace(";", ",").split(",")]
    vals = []
    for s in parts:
        if not s:
            continue
        vals.append(float(s))
    return vals

def _open_uniform_knots(nb_ctrl: int, p: int):
    """
    Open uniform (clamped) knots so endpoints are interpolated:
    U = [0..0, u1, u2, ..., 1..1] with (p+1) zeros and (p+1) ones
    Total length = nb_ctrl + p + 1
    """
    m = nb_ctrl + p + 1
    if m <= 0:
        return []

    if nb_ctrl <= p:
        # deg too high -> still return something safe
        return [0.0] * (m - 1) + [1.0]

    # first and last clamped
    U = [0.0] * (p + 1)
    interior_count = m - 2 * (p + 1)
    if interior_count > 0:
        for k in range(1, interior_count + 1):
            U.append(k / (interior_count + 1))
    U += [1.0] * (p + 1)
    return U

def N_ip(i: int, p: int, t: float, U):
    """
    Cox-de-Boor recursion.
    IMPORTANT consigne: if division by 0 -> contribute 0.
    """
    # base
    if p == 0:
        # include last knot special case
        if (U[i] <= t < U[i + 1]) or (t == U[-1] and U[i] <= t <= U[i + 1]):
            return 1.0
        return 0.0

    left = 0.0
    right = 0.0

    denom1 = U[i + p] - U[i]
    if denom1 != 0:
        left = (t - U[i]) / denom1 * N_ip(i, p - 1, t, U)
    else:
        left = 0.0  # consigne

    denom2 = U[i + p + 1] - U[i + 1]
    if denom2 != 0:
        right = (U[i + p + 1] - t) / denom2 * N_ip(i + 1, p - 1, t, U)
    else:
        right = 0.0  # consigne

    return left + right

def bspline_point(points, p: int, t: float, U):
    x = 0.0
    y = 0.0
    nb = len(points)
    for i in range(nb):
        b = N_ip(i, p, t, U)
        x += points[i][0] * b
        y += points[i][1] * b
    return (x, y)

def nurbs_point(points, weights, p: int, t: float, U):
    numx = 0.0
    numy = 0.0
    denom = 0.0
    nb = len(points)
    for i in range(nb):
        b = N_ip(i, p, t, U)
        w = weights[i]
        numx += points[i][0] * b * w
        numy += points[i][1] * b * w
        denom += b * w
    if denom == 0:
        return None
    return (numx / denom, numy / denom)

# ============================================================
# Fenêtre (même squelette que BezierWindow)
# ============================================================

class BSplineNURBSWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("BSplines / NURBS")
        self.geometry("1200x800")

        # Données - même style que Bézier
        self.all_curves = []          # list[list[(x,y)]]
        self.all_weights = []         # list[list[float]] alignée sur all_curves
        self.all_custom_knots = []    # list[None or list[float]] (un vecteur par courbe)
        self.current_curve_idx = -1
        self.dragging_point = None    # (curve_idx, point_idx)
        self.dragging_offset = (0, 0)

        # Paramètres UI
        self.step = tk.DoubleVar(value=0.01)         # précision (comme Bézier)
        self.degree = tk.IntVar(value=3)             # p
        self.use_nurbs = tk.BooleanVar(value=False)  # toggle NURBS
        self.use_custom_knots = tk.BooleanVar(value=False)
        self.knots_text = tk.StringVar(value="")     # input custom knots

        self.create_widgets()
        self.bind_events()
        self.redraw()

    # ---------------- UI ----------------

    def create_widgets(self):
        top = ttk.Frame(self)
        top.pack(side="top", fill="x", pady=5)

        txt = (
            "Souris : Clic Gauche (Point/Drag) | Clic Droit (Nouv. Courbe)  ||  "
            "Delete (Suppr Point) | +/- (Poids NURBS) | Entrée (Appliquer noeuds)"
        )
        ttk.Label(top, text=txt).pack(side="left", padx=5)

        ttk.Button(top, text="Suppr Courbe", command=self.delete_current_curve).pack(side="left", padx=5)
        ttk.Button(top, text="Effacer Tout", command=self.clear_all).pack(side="left", padx=5)
        ttk.Button(top, text="Doubler Point", command=self.duplicate_point).pack(side="left", padx=5)

        ttk.Checkbutton(top, text="Mode NURBS (poids)", variable=self.use_nurbs, command=self.redraw).pack(side="left", padx=10)

        ttk.Label(top, text="Degré p :").pack(side="left", padx=(10, 2))
        ttk.Spinbox(top, from_=1, to=10, width=3, textvariable=self.degree, command=self.redraw).pack(side="left", padx=5)

        ttk.Label(top, text="Précision :").pack(side="left", padx=(10, 2))
        self.slider = ttk.Scale(
            top, from_=0.005, to=0.2, orient="horizontal",
            variable=self.step,
            command=lambda _: self.redraw()
        )
        self.slider.pack(side="left", padx=5)

        # Ligne noeuds (simple, même vibe que le reste)
        knotbar = ttk.Frame(self)
        knotbar.pack(side="top", fill="x", pady=(0, 5))

        ttk.Checkbutton(
            knotbar, text="Noeuds custom (courbe courante)",
            variable=self.use_custom_knots,
            command=self.redraw
        ).pack(side="left", padx=5)

        ttk.Label(knotbar, text="U =").pack(side="left")
        ttk.Entry(knotbar, textvariable=self.knots_text, width=80).pack(side="left", padx=5)
        ttk.Button(knotbar, text="Appliquer", command=self.apply_custom_knots).pack(side="left", padx=5)

        self.canvas = tk.Canvas(self, width=1100, height=700, bg="white")
        self.canvas.pack(pady=5)

    def bind_events(self):
        # même pattern que Bézier
        self.canvas.bind("<ButtonPress-1>", self.on_click_left)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.start_new_curve)

        self.canvas.bind("<KeyPress>", self.on_key_press)
        self.bind("<Delete>", lambda e: self.delete_selected_point())
        self.bind("<Return>", lambda e: self.apply_custom_knots())

    # ---------------- Gestion courbes ----------------

    def start_new_curve(self, event=None):
        self.all_curves.append([])
        self.all_weights.append([])
        self.all_custom_knots.append(None)
        self.current_curve_idx = len(self.all_curves) - 1
        self.dragging_point = None
        self.redraw()

    def delete_current_curve(self):
        if 0 <= self.current_curve_idx < len(self.all_curves):
            self.all_curves.pop(self.current_curve_idx)
            self.all_weights.pop(self.current_curve_idx)
            self.all_custom_knots.pop(self.current_curve_idx)

            self.current_curve_idx = len(self.all_curves) - 1
            self.dragging_point = None
            self.redraw()

    def clear_all(self):
        self.all_curves = []
        self.all_weights = []
        self.all_custom_knots = []
        self.current_curve_idx = -1
        self.dragging_point = None
        self.redraw()

    def duplicate_point(self):
        if self.dragging_point:
            c, p = self.dragging_point
            if c < len(self.all_curves) and p < len(self.all_curves[c]):
                pt = self.all_curves[c][p]
                w = self.all_weights[c][p]
                self.all_curves[c].insert(p + 1, pt)
                self.all_weights[c].insert(p + 1, w)
                self.dragging_point = (c, p + 1)
                self.redraw()

    # ---------------- Souris ----------------

    def find_nearest(self, x, y):
        best = None
        min_d = 100  # même idée que Bézier
        for c_idx, curve in enumerate(self.all_curves):
            for p_idx, pt in enumerate(curve):
                d = (pt[0] - x) ** 2 + (pt[1] - y) ** 2
                if d < min_d:
                    min_d = d
                    best = (c_idx, p_idx)
        return best

    def on_click_left(self, event):
        self.canvas.focus_set()
        x, y = event.x, event.y
        hit = self.find_nearest(x, y)

        if hit:
            self.dragging_point = hit
            self.current_curve_idx = hit[0]
            cur_pt = self.all_curves[hit[0]][hit[1]]
            self.dragging_offset = (cur_pt[0] - x, cur_pt[1] - y)
        else:
            if not self.all_curves:
                self.start_new_curve()
            if self.current_curve_idx == -1:
                self.current_curve_idx = 0

            self.all_curves[self.current_curve_idx].append((x, y))
            self.all_weights[self.current_curve_idx].append(1.0)  # poids par défaut
            self.dragging_point = (self.current_curve_idx, len(self.all_curves[self.current_curve_idx]) - 1)

        self.redraw()

    def on_drag(self, event):
        if self.dragging_point:
            c, p = self.dragging_point
            if c < len(self.all_curves) and p < len(self.all_curves[c]):
                nx = event.x + self.dragging_offset[0]
                ny = event.y + self.dragging_offset[1]
                self.all_curves[c][p] = (nx, ny)
                self.redraw()

    def on_release(self, event):
        pass

    def delete_selected_point(self):
        if self.dragging_point:
            c, p = self.dragging_point
            if c < len(self.all_curves) and p < len(self.all_curves[c]):
                self.all_curves[c].pop(p)
                self.all_weights[c].pop(p)

                if not self.all_curves[c]:
                    # si courbe vide, on supprime (même logique que Bézier)
                    self.all_curves.pop(c)
                    self.all_weights.pop(c)
                    self.all_custom_knots.pop(c)
                    self.current_curve_idx = len(self.all_curves) - 1

                self.dragging_point = None
                self.redraw()

    # ---------------- Noeuds ----------------

    def apply_custom_knots(self):
        """
        Applique un vecteur nodal custom à la courbe courante (et seulement celle-là).
        Si invalide -> on ignore (et on reste en uniforme).
        """
        c = self.current_curve_idx
        if c == -1 or c >= len(self.all_curves):
            return
        pts = self.all_curves[c]
        p = int(self.degree.get())

        if not self.use_custom_knots.get():
            self.all_custom_knots[c] = None
            self.redraw()
            return

        try:
            U = _parse_knots(self.knots_text.get())
        except:
            return

        nb = len(pts)
        needed = nb + p + 1
        if nb < 2 or p < 1:
            return
        if len(U) != needed:
            # longueur pas bonne -> ignore
            return
        # non décroissant
        for i in range(len(U) - 1):
            if U[i] > U[i + 1]:
                return

        self.all_custom_knots[c] = U
        self.redraw()

    def _get_knots_for_curve(self, c_idx, nb_ctrl, p):
        if self.use_custom_knots.get():
            U = self.all_custom_knots[c_idx]
            if U is not None and len(U) == nb_ctrl + p + 1:
                return U
        return _open_uniform_knots(nb_ctrl, p)

    # ---------------- Clavier ----------------

    def on_key_press(self, event):
        # + / - : poids NURBS du point sélectionné
        k = event.keysym.lower()

        if k in ("plus", "kp_add", "equal"):  # = souvent sur clavier FR pour +
            self._change_selected_weight(+0.1)
        elif k in ("minus", "kp_subtract"):
            self._change_selected_weight(-0.1)

    def _change_selected_weight(self, delta):
        if not self.use_nurbs.get():
            return
        if not self.dragging_point:
            return
        c, p = self.dragging_point
        if c >= len(self.all_weights) or p >= len(self.all_weights[c]):
            return
        w = self.all_weights[c][p] + delta
        if w < 0.1:
            w = 0.1
        if w > 50:
            w = 50
        self.all_weights[c][p] = w
        self.redraw()

    # ---------------- Dessin ----------------

    def redraw(self):
        self.canvas.delete("all")

        # sécurité step
        try:
            step_val = self.step.get()
            if step_val <= 0.001:
                step_val = 0.01
        except:
            step_val = 0.01

        for c_idx, curve in enumerate(self.all_curves):
            is_sel = (c_idx == self.current_curve_idx)
            col = "purple" if is_sel else "gray"

            # points seuls
            if len(curve) < 2:
                for p_idx, pt in enumerate(curve):
                    r = 6 if self.dragging_point == (c_idx, p_idx) else 4
                    outline = "red" if self.dragging_point == (c_idx, p_idx) else "black"
                    self.canvas.create_oval(pt[0]-r, pt[1]-r, pt[0]+r, pt[1]+r, fill=col, outline=outline)
                continue

            # polygone de contrôle (même look que Bézier)
            for i in range(len(curve) - 1):
                p1, p2 = curve[i], curve[i + 1]
                self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill="lightgray", dash=(2, 2))

            # ---- calcul courbe B-Spline / NURBS ----
            p = int(self.degree.get())
            nb_ctrl = len(curve)
            if p < 1:
                p = 1
            if nb_ctrl <= p:
                # degré trop haut pour nb points -> on n’essaie pas
                pass
            else:
                U = self._get_knots_for_curve(c_idx, nb_ctrl, p)

                t0 = U[p]
                t1 = U[nb_ctrl]  # borne sup

                # nombre de segments similaire à Bézier
                nb_seg = int(1.0 / step_val)
                if nb_seg < 10:
                    nb_seg = 10

                prev = None
                for s in range(nb_seg + 1):
                    t = t0 + (t1 - t0) * (s / nb_seg)

                    if self.use_nurbs.get():
                        pt = nurbs_point(curve, self.all_weights[c_idx], p, t, U)
                        if pt is None:
                            continue
                    else:
                        pt = bspline_point(curve, p, t, U)

                    if prev is not None:
                        self.canvas.create_line(prev[0], prev[1], pt[0], pt[1], fill=col, width=2)
                    prev = pt

            # points de contrôle (même style que Bézier) + affichage poids si NURBS
            for p_idx, pt in enumerate(curve):
                is_pt_sel = (self.dragging_point == (c_idx, p_idx))
                r = 6 if is_pt_sel else 4
                outline = "red" if is_pt_sel else "black"
                self.canvas.create_oval(pt[0]-r, pt[1]-r, pt[0]+r, pt[1]+r, fill=col, outline=outline)

                if self.use_nurbs.get() and is_sel:
                    w = self.all_weights[c_idx][p_idx] if p_idx < len(self.all_weights[c_idx]) else 1.0
                    # petit label discret
                    self.canvas.create_text(pt[0] + 12, pt[1] - 10, text=f"w={w:.1f}", fill="black")