import math
import tkinter as tk
from tkinter import ttk

from algo.bezier import bezier_point, bernstein_point


class BezierWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Bézier")
        self.geometry("1200x800")

        self.all_curves = []
        self.current_curve_idx = -1
        self.dragging_point = None
        self.dragging_offset = (0, 0)

        self.step = tk.DoubleVar(value=0.01)
        self.use_casteljau = tk.BooleanVar(value=True)

        self.create_widgets()
        self.bind_events()
        self.redraw()

    def create_widgets(self):
        top = ttk.Frame(self)
        top.pack(side="top", fill="x", pady=5)

        txt = (
            "Souris : Clic Gauche (Point) | Clic Droit (Nouv. Courbe)  ||  "
            "Clavier : Flèches (Bouger) | A/E (Rotation) | S/D (Zoom)"
        )
        ttk.Label(top, text=txt).pack(side="left", padx=5)

        ttk.Button(top, text="Suppr Courbe", command=self.delete_current_curve).pack(side="left", padx=5)
        ttk.Button(top, text="Effacer Tout", command=self.clear_all).pack(side="left", padx=5)
        ttk.Checkbutton(top, text="Algo Casteljau", variable=self.use_casteljau, command=self.redraw).pack(side="left", padx=10)
        ttk.Button(top, text="Doubler Point", command=self.duplicate_point).pack(side="left", padx=5)

        ttk.Label(top, text="Précision :").pack(side="left", padx=(10, 2))
        self.slider = ttk.Scale(
            top, from_=0.005, to=0.2, orient="horizontal",
            variable=self.step,
            command=lambda _: self.redraw(),
        )
        self.slider.pack(side="left", padx=5)

        self.canvas = tk.Canvas(self, width=1100, height=700, bg="white")
        self.canvas.pack(pady=5)

    def bind_events(self):
        self.canvas.bind("<ButtonPress-1>", self.on_click_left)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.start_new_curve)
        self.canvas.bind("<KeyPress>", self.on_key_press)
        self.bind("<Delete>", lambda e: self.delete_selected_point())

    def _eval_point(self, points, t):
        if self.use_casteljau.get():
            return bezier_point(points, t)
        return bernstein_point(points, t)

    def start_new_curve(self, event=None):
        self.all_curves.append([])
        self.current_curve_idx = len(self.all_curves) - 1
        self.redraw()

    def delete_current_curve(self):
        if 0 <= self.current_curve_idx < len(self.all_curves):
            self.all_curves.pop(self.current_curve_idx)
            self.current_curve_idx = len(self.all_curves) - 1
            self.dragging_point = None
            self.redraw()

    def duplicate_point(self):
        if self.dragging_point:
            c, p = self.dragging_point
            if c < len(self.all_curves):
                pt = self.all_curves[c][p]
                self.all_curves[c].insert(p + 1, pt)
                self.redraw()

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
            self.all_curves[self.current_curve_idx].append((x, y))
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

    def delete_selected_point(self):
        if self.dragging_point:
            c, p = self.dragging_point
            if c < len(self.all_curves) and p < len(self.all_curves[c]):
                self.all_curves[c].pop(p)
                if not self.all_curves[c]:
                    self.all_curves.pop(c)
                    self.current_curve_idx = len(self.all_curves) - 1
                self.dragging_point = None
                self.redraw()

    def on_release(self, event):
        pass

    def get_centroid(self, curve):
        if not curve:
            return (0, 0)
        sx = sum(p[0] for p in curve)
        sy = sum(p[1] for p in curve)
        n = len(curve)
        return (sx / n, sy / n)

    def apply_matrix(self, a, b, c, d, tx, ty):
        if self.current_curve_idx == -1:
            return
        curve = self.all_curves[self.current_curve_idx]
        if not curve:
            return

        cx, cy = self.get_centroid(curve)
        new_pts = []
        for x, y in curve:
            lx = x - cx
            ly = y - cy
            nx = a * lx + b * ly
            ny = c * lx + d * ly
            new_pts.append((nx + cx + tx, ny + cy + ty))

        self.all_curves[self.current_curve_idx] = new_pts
        self.redraw()

    def on_key_press(self, event):
        if self.current_curve_idx == -1:
            return
        k = event.keysym.lower()
        dist = 10

        if k == "left":
            self.apply_matrix(1, 0, 0, 1, -dist, 0)
        elif k == "right":
            self.apply_matrix(1, 0, 0, 1, dist, 0)
        elif k == "up":
            self.apply_matrix(1, 0, 0, 1, 0, -dist)
        elif k == "down":
            self.apply_matrix(1, 0, 0, 1, 0, dist)
        elif k == "e":
            th = 0.1
            co, si = math.cos(th), math.sin(th)
            self.apply_matrix(co, -si, si, co, 0, 0)
        elif k == "a":
            th = -0.1
            co, si = math.cos(th), math.sin(th)
            self.apply_matrix(co, -si, si, co, 0, 0)
        elif k == "s":
            self.apply_matrix(1.1, 0, 0, 1.1, 0, 0)
        elif k == "d":
            self.apply_matrix(0.9, 0, 0, 0.9, 0, 0)
        elif k == "c":
            self.apply_matrix(1, 0.2, 0, 1, 0, 0)

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

    def clear_all(self):
        self.all_curves = []
        self.current_curve_idx = -1
        self.dragging_point = None
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
                for pt in curve:
                    self.canvas.create_oval(pt[0] - 2, pt[1] - 2, pt[0] + 2, pt[1] + 2, fill=col)
                continue

            for i in range(len(curve) - 1):
                p1, p2 = curve[i], curve[i + 1]
                self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill="lightgray", dash=(2, 2))

            nb_seg = int(1.0 / step_val)
            prev = curve[0]

            for i in range(1, nb_seg + 1):
                t = min(i * step_val, 1.0)
                curr = self._eval_point(curve, t)
                self.canvas.create_line(prev[0], prev[1], curr[0], curr[1], fill=col, width=2)
                prev = curr

            for p_idx, pt in enumerate(curve):
                is_pt_sel = (self.dragging_point == (c_idx, p_idx))
                r = 6 if is_pt_sel else 4
                outline = "red" if is_pt_sel else "black"
                self.canvas.create_oval(pt[0] - r, pt[1] - r, pt[0] + r, pt[1] + r,
                                        fill=col, outline=outline)
