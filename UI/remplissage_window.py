import tkinter as tk
from tkinter import ttk

from algo.lca import lca_fill


class RemplissageWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Remplissage – LCA / Scanline (multi-polygones)")
        self.geometry("1000x700")

        self.polygons = []
        self.current_drawing = []
        self.fill_segments = []

        self.fill_rule = tk.StringVar(value="evenodd")

        self.dragging_point = None
        self.dragging_offset = (0, 0)

        self.create_widgets()
        self.bind_events()

    def create_widgets(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(side="top", fill="x", pady=8)

        ttk.Label(
            top_frame,
            text="Remplissage (clic gauche = points/drag, clic droit = fermer un polygone)",
        ).pack(side="left", padx=8)

        ttk.Button(top_frame, text="Effacer tout", command=self.clear_all) \
            .pack(side="left", padx=20)

        self.canvas = tk.Canvas(self, width=900, height=600, bg="white")
        self.canvas.pack(pady=10)

        ttk.Label(top_frame, text="Règle :").pack(side="left", padx=(20, 4))
        ttk.Radiobutton(
            top_frame, text="Pair/impair",
            variable=self.fill_rule, value="evenodd",
            command=self.remplir,
        ).pack(side="left")
        ttk.Radiobutton(
            top_frame, text="Enroulement non nul",
            variable=self.fill_rule, value="winding",
            command=self.remplir,
        ).pack(side="left", padx=(8, 0))

    def bind_events(self):
        self.canvas.bind("<ButtonPress-1>", self.start_drag_or_add_point)
        self.canvas.bind("<B1-Motion>", self.drag_point)
        self.canvas.bind("<ButtonRelease-1>", self.release_drag)
        self.canvas.bind("<Button-3>", self.right_click)

    def start_drag_or_add_point(self, event):
        x, y = event.x, event.y

        hit = self.find_nearest_vertex(x, y)
        if hit is not None:
            self.dragging_point = hit
            kind = hit[0]

            if kind == "poly":
                poly_idx, idx = hit[1], hit[2]
                px, py = self.polygons[poly_idx][idx]
            else:
                idx = hit[1]
                px, py = self.current_drawing[idx]

            self.dragging_offset = (px - x, py - y)
            return

        self.current_drawing.append((x, y))
        self.redraw()

    def right_click(self, event):
        if len(self.current_drawing) < 3:
            return

        self.polygons.append(self.current_drawing[:])
        self.current_drawing = []
        self.remplir()

    def drag_point(self, event):
        if not self.dragging_point:
            return

        kind = self.dragging_point[0]
        x = event.x + self.dragging_offset[0]
        y = event.y + self.dragging_offset[1]

        if kind == "poly":
            poly_idx, idx = self.dragging_point[1], self.dragging_point[2]
            self.polygons[poly_idx][idx] = (x, y)
            self.remplir()
        else:
            idx = self.dragging_point[1]
            self.current_drawing[idx] = (x, y)
            self.redraw()

    def release_drag(self, event):
        self.dragging_point = None

    def find_nearest_vertex(self, x, y):
        radius = 8

        for pi, poly in enumerate(self.polygons):
            for vi, (px, py) in enumerate(poly):
                if (px - x) ** 2 + (py - y) ** 2 <= radius ** 2:
                    return ("poly", pi, vi)

        for i, (px, py) in enumerate(self.current_drawing):
            if (px - x) ** 2 + (py - y) ** 2 <= radius ** 2:
                return ("current", i)

        return None

    def draw_polygon(self, points, color, dash=None):
        if len(points) >= 2:
            for i in range(len(points) - 1):
                self.canvas.create_line(*points[i], *points[i + 1],
                                        fill=color, width=2, dash=dash)

        if len(points) >= 3:
            self.canvas.create_line(*points[-1], *points[0],
                                    fill=color, width=2, dash=dash)

        for x, y in points:
            r = 4
            self.canvas.create_oval(x - r, y - r, x + r, y + r,
                                    fill=color, outline=color)

    def redraw(self):
        self.canvas.delete("all")

        for y, x1, x2 in self.fill_segments:
            self.canvas.create_line(x1, y, x2, y, fill="orange")

        for poly in self.polygons:
            self.draw_polygon(poly, color="blue")

        if self.current_drawing:
            self.draw_polygon(self.current_drawing, color="gray", dash=(4, 2))

    def remplir(self):
        self.fill_segments = []

        for poly in self.polygons:
            if len(poly) >= 3:
                self.fill_segments.extend(lca_fill(poly, rule=self.fill_rule.get()))

        self.redraw()

    def clear_all(self):
        self.polygons = []
        self.current_drawing = []
        self.fill_segments = []
        self.redraw()
