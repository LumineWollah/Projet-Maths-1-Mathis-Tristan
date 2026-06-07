import tkinter as tk
from tkinter import ttk

from algo.bspline_nurbs import (
    bspline_point,
    nurbs_point,
    open_uniform_knots,
    parse_knots,
)


class BSplineNURBSWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("BSplines / NURBS")
        self.geometry("1200x800")

        self.all_curves = []
        self.all_weights = []
        self.all_custom_knots = []
        self.current_curve_idx = -1
        self.dragging_point = None
        self.dragging_offset = (0, 0)

        self.step = tk.DoubleVar(value=0.01)
        self.degree = tk.IntVar(value=3)
        self.use_nurbs = tk.BooleanVar(value=False)
        self.use_custom_knots = tk.BooleanVar(value=False)
        self.knots_text = tk.StringVar(value="")

        self.create_widgets()
        self.bind_events()
        self.redraw()

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
            command=lambda _: self.redraw(),
        )
        self.slider.pack(side="left", padx=5)

        knotbar = ttk.Frame(self)
        knotbar.pack(side="top", fill="x", pady=(0, 5))

        ttk.Checkbutton(
            knotbar, text="Noeuds custom (courbe courante)",
            variable=self.use_custom_knots,
            command=self.redraw,
        ).pack(side="left", padx=5)

        ttk.Label(knotbar, text="U =").pack(side="left")
        ttk.Entry(knotbar, textvariable=self.knots_text, width=80).pack(side="left", padx=5)
        ttk.Button(knotbar, text="Appliquer", command=self.apply_custom_knots).pack(side="left", padx=5)

        self.canvas = tk.Canvas(self, width=1100, height=700, bg="white")
        self.canvas.pack(pady=5)

    def bind_events(self):
        self.canvas.bind("<ButtonPress-1>", self.on_click_left)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.start_new_curve)
        self.canvas.bind("<KeyPress>", self.on_key_press)
        self.bind("<Delete>", lambda e: self.delete_selected_point())
        self.bind("<Return>", lambda e: self.apply_custom_knots())

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

    def find_nearest(self, x, y):
        best = None
        min_d = 100
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
            self.all_weights[self.current_curve_idx].append(1.0)
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
                    self.all_curves.pop(c)
                    self.all_weights.pop(c)
                    self.all_custom_knots.pop(c)
                    self.current_curve_idx = len(self.all_curves) - 1

                self.dragging_point = None
                self.redraw()

    def apply_custom_knots(self):
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
            U = parse_knots(self.knots_text.get())
        except Exception:
            return

        nb = len(pts)
        needed = nb + p + 1
        if nb < 2 or p < 1:
            return
        if len(U) != needed:
            return
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
        return open_uniform_knots(nb_ctrl, p)

    def on_key_press(self, event):
        k = event.keysym.lower()

        if k in ("plus", "kp_add", "equal"):
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
        w = max(0.1, min(50, w))
        self.all_weights[c][p] = w
        self.redraw()

    def redraw(self):
        self.canvas.delete("all")

        try:
            step_val = self.step.get()
            if step_val <= 0.001:
                step_val = 0.01
        except Exception:
            step_val = 0.01

        for c_idx, curve in enumerate(self.all_curves):
            is_sel = (c_idx == self.current_curve_idx)
            col = "purple" if is_sel else "gray"

            if len(curve) < 2:
                for p_idx, pt in enumerate(curve):
                    r = 6 if self.dragging_point == (c_idx, p_idx) else 4
                    outline = "red" if self.dragging_point == (c_idx, p_idx) else "black"
                    self.canvas.create_oval(pt[0] - r, pt[1] - r, pt[0] + r, pt[1] + r,
                                            fill=col, outline=outline)
                continue

            for i in range(len(curve) - 1):
                p1, p2 = curve[i], curve[i + 1]
                self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill="lightgray", dash=(2, 2))

            p = int(self.degree.get())
            nb_ctrl = len(curve)
            if p < 1:
                p = 1
            if nb_ctrl > p:
                U = self._get_knots_for_curve(c_idx, nb_ctrl, p)
                t0 = U[p]
                t1 = U[nb_ctrl]

                nb_seg = max(10, int(1.0 / step_val))
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

            for p_idx, pt in enumerate(curve):
                is_pt_sel = (self.dragging_point == (c_idx, p_idx))
                r = 6 if is_pt_sel else 4
                outline = "red" if is_pt_sel else "black"
                self.canvas.create_oval(pt[0] - r, pt[1] - r, pt[0] + r, pt[1] + r,
                                        fill=col, outline=outline)

                if self.use_nurbs.get() and is_sel:
                    w = self.all_weights[c_idx][p_idx] if p_idx < len(self.all_weights[c_idx]) else 1.0
                    self.canvas.create_text(pt[0] + 12, pt[1] - 10, text=f"w={w:.1f}", fill="black")
