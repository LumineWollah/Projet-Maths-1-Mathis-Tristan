import tkinter as tk
from tkinter import ttk

import Sutherland_Hodgman as SH
import LCA
import Bezier as BZ


# ==================================================================
#                 DÉCOUPAGE – Sutherland-Hodgman
# ==================================================================
class DecoupageWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Découpage – Sutherland-Hodgman")
        self.geometry("1000x700")

        # -----------------------------
        # State
        # -----------------------------
        self.current_mode = "subject"  # "subject" or "clip"

        self.subject_polygons = []
        self.clip_polygons = []
        self.result_polygons = []
        self.current_drawing = []

        # Dragging vertices
        self.dragging_point = None
        self.dragging_offset = (0, 0)

        # Bonus
        self.use_triangulation = tk.BooleanVar(value=False)

        # -----------------------------
        # View transform (zoom + pan)
        # -----------------------------
        self.zoom = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.min_zoom = 0.2
        self.max_zoom = 6.0

        # Pan with middle mouse
        self.panning = False
        self.pan_start = (0, 0)

        # -----------------------------
        # UI
        # -----------------------------
        self.create_widgets()
        self.bind_events()
        self.redraw()

    # ------------------------------------------------------------
    # UI creation
    # ------------------------------------------------------------
    def create_widgets(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(side="top", fill="x", pady=8)

        ttk.Label(top_frame, text="Mode de dessin :").pack(side="left", padx=8)

        ttk.Button(top_frame, text="Polygone à découper",
                   command=self.set_mode_subject).pack(side="left", padx=5)

        ttk.Button(top_frame, text="Fenêtre de découpe",
                   command=self.set_mode_clip).pack(side="left", padx=5)

        ttk.Button(top_frame, text="Effacer tout",
                   command=self.clear_all).pack(side="left", padx=10)

        ttk.Checkbutton(
            top_frame,
            text="Bonus : fenêtre quelconque (triangulation)",
            variable=self.use_triangulation,
            command=self.force_clipping
        ).pack(side="left", padx=10)

        self.canvas = tk.Canvas(self, width=900, height=600, bg="white")
        self.canvas.pack(pady=10)

    # ------------------------------------------------------------
    # Event binding
    # ------------------------------------------------------------
    def bind_events(self):
        self.canvas.bind("<ButtonPress-1>", self.start_drag_or_add_point)
        self.canvas.bind("<B1-Motion>", self.drag_point)
        self.canvas.bind("<ButtonRelease-1>", self.release_drag)

        self.canvas.bind("<Button-3>", self.right_click)

        # Zoom
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", self.on_wheel_up)
        self.canvas.bind("<Button-5>", self.on_wheel_down)

        # Pan (middle mouse button)
        self.canvas.bind("<ButtonPress-2>", self.start_pan)
        self.canvas.bind("<B2-Motion>", self.do_pan)
        self.canvas.bind("<ButtonRelease-2>", self.end_pan)

        self.bind("<Escape>", lambda e: self.cancel_current_drawing())

    # ------------------------------------------------------------
    # View helpers
    # ------------------------------------------------------------
    def world_to_screen(self, p):
        x, y = p
        return (x * self.zoom + self.pan_x, y * self.zoom + self.pan_y)

    def screen_to_world(self, x, y):
        return ((x - self.pan_x) / self.zoom, (y - self.pan_y) / self.zoom)

    def zoom_at(self, factor, cx, cy):
        wx, wy = self.screen_to_world(cx, cy)

        new_zoom = max(self.min_zoom, min(self.max_zoom, self.zoom * factor))
        factor = new_zoom / self.zoom
        self.zoom = new_zoom

        self.pan_x = cx - wx * self.zoom
        self.pan_y = cy - wy * self.zoom

        self.redraw()

    # ------------------------------------------------------------
    # Zoom handlers
    # ------------------------------------------------------------
    def on_mousewheel(self, event):
        if event.delta > 0:
            self.zoom_at(1.1, event.x, event.y)
        elif event.delta < 0:
            self.zoom_at(1 / 1.1, event.x, event.y)

    def on_wheel_up(self, event):
        self.zoom_at(1.1, event.x, event.y)

    def on_wheel_down(self, event):
        self.zoom_at(1 / 1.1, event.x, event.y)

    # ------------------------------------------------------------
    # Pan handlers
    # ------------------------------------------------------------
    def start_pan(self, event):
        self.panning = True
        self.pan_start = (event.x, event.y)

    def do_pan(self, event):
        if not self.panning:
            return

        dx = event.x - self.pan_start[0]
        dy = event.y - self.pan_start[1]

        self.pan_x += dx
        self.pan_y += dy

        self.pan_start = (event.x, event.y)
        self.redraw()

    def end_pan(self, event):
        self.panning = False

    # ------------------------------------------------------------
    # Mode switch
    # ------------------------------------------------------------
    def set_mode_subject(self):
        self.current_mode = "subject"

    def set_mode_clip(self):
        self.current_mode = "clip"

    # ------------------------------------------------------------
    # Editing helpers
    # ------------------------------------------------------------
    def cancel_current_drawing(self):
        self.current_drawing = []
        self.redraw()

    def clear_all(self):
        self.subject_polygons = []
        self.clip_polygons = []
        self.result_polygons = []
        self.current_drawing = []
        self.dragging_point = None

        self.zoom = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0

        self.redraw()

    # ------------------------------------------------------------
    # Hit test
    # ------------------------------------------------------------
    def find_nearest_vertex(self, sx, sy):
        r2 = 8 * 8

        for pi, poly in enumerate(self.subject_polygons):
            for vi, p in enumerate(poly):
                px, py = self.world_to_screen(p)
                if (px - sx) ** 2 + (py - sy) ** 2 <= r2:
                    return ("subject", pi, vi)

        for pi, poly in enumerate(self.clip_polygons):
            for vi, p in enumerate(poly):
                px, py = self.world_to_screen(p)
                if (px - sx) ** 2 + (py - sy) ** 2 <= r2:
                    return ("clip", pi, vi)

        for vi, p in enumerate(self.current_drawing):
            px, py = self.world_to_screen(p)
            if (px - sx) ** 2 + (py - sy) ** 2 <= r2:
                return ("current", None, vi)

        return None

    # ------------------------------------------------------------
    # Mouse logic
    # ------------------------------------------------------------
    def start_drag_or_add_point(self, event):
        hit = self.find_nearest_vertex(event.x, event.y)
        if hit:
            kind, pi, vi = hit
            self.dragging_point = hit

            wx, wy = self.screen_to_world(event.x, event.y)

            if kind == "subject":
                px, py = self.subject_polygons[pi][vi]
            elif kind == "clip":
                px, py = self.clip_polygons[pi][vi]
            else:
                px, py = self.current_drawing[vi]

            self.dragging_offset = (px - wx, py - wy)
            return

        wx, wy = self.screen_to_world(event.x, event.y)
        self.current_drawing.append((wx, wy))
        self.redraw()

    def drag_point(self, event):
        if not self.dragging_point:
            return

        kind, pi, vi = self.dragging_point
        wx, wy = self.screen_to_world(event.x, event.y)
        x = wx + self.dragging_offset[0]
        y = wy + self.dragging_offset[1]

        if kind == "subject":
            self.subject_polygons[pi][vi] = (x, y)
        elif kind == "clip":
            self.clip_polygons[pi][vi] = (x, y)
        else:
            self.current_drawing[vi] = (x, y)

        self.update_clipping()
        self.redraw()

    def release_drag(self, event):
        self.dragging_point = None

    def right_click(self, event):
        if len(self.current_drawing) < 3:
            return

        poly = self.current_drawing[:]
        if self.current_mode == "subject":
            self.subject_polygons.append(poly)
        else:
            self.clip_polygons.append(poly)

        self.current_drawing = []
        self.update_clipping()
        self.redraw()

    # ------------------------------------------------------------
    # Clipping
    # ------------------------------------------------------------
    def force_clipping(self):
        self.update_clipping()
        self.redraw()

    def update_clipping(self):
        self.result_polygons = []

        for subj in self.subject_polygons:
            for clip in self.clip_polygons:
                if self.use_triangulation.get():
                    pieces = SH.clip_subject_with_window_triangulation(subj, clip)
                    self.result_polygons.extend(pieces)
                else:
                    res = SH.sutherland_hodgman(subj, clip)
                    if res:
                        self.result_polygons.append(res)

    # ------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------
    def draw_grid(self, step=50):
        w = int(self.canvas.cget("width"))
        h = int(self.canvas.cget("height"))

        wx0, wy0 = self.screen_to_world(0, 0)
        wx1, wy1 = self.screen_to_world(w, h)

        import math
        x = math.floor(min(wx0, wx1) / step) * step
        while x <= max(wx0, wx1):
            sx0, sy0 = self.world_to_screen((x, wy0))
            sx1, sy1 = self.world_to_screen((x, wy1))
            self.canvas.create_line(sx0, sy0, sx1, sy1, fill="#e6e6e6")
            x += step

        y = math.floor(min(wy0, wy1) / step) * step
        while y <= max(wy0, wy1):
            sx0, sy0 = self.world_to_screen((wx0, y))
            sx1, sy1 = self.world_to_screen((wx1, y))
            self.canvas.create_line(sx0, sy0, sx1, sy1, fill="#e6e6e6")
            y += step

    def draw_polygon(self, points, outline, width=2, dash=None, fill=None, stipple=None):
        if len(points) < 2:
            return

        pts = [self.world_to_screen(p) for p in points]

        if fill and len(pts) >= 3:
            flat = [c for p in pts for c in p]
            self.canvas.create_polygon(
                *flat, outline=outline, fill=fill, width=width, stipple=stipple
            )

        for i in range(len(pts)):
            self.canvas.create_line(
                *pts[i], *pts[(i + 1) % len(pts)],
                fill=outline, width=width, dash=dash
            )

        for x, y in pts:
            r = 4
            self.canvas.create_oval(x - r, y - r, x + r, y + r,
                                    fill=outline, outline=outline)

    def redraw(self):
        self.canvas.delete("all")
        self.draw_grid()

        for poly in self.clip_polygons:
            self.draw_polygon(poly, outline="green")

        for poly in self.subject_polygons:
            self.draw_polygon(poly, outline="blue")

        if self.current_drawing:
            self.draw_polygon(self.current_drawing, outline="gray", dash=(4, 2))

        for poly in self.result_polygons:
            self.draw_polygon(poly, outline="red", width=3, fill="red", stipple="gray25")


# ==================================================================
#             REMPLISSAGE
# ==================================================================
class RemplissageWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Remplissage – LCA / Scanline (multi-polygones)")
        self.geometry("1000x700")

        # Plusieurs polygones
        self.polygons = []         # liste de polygones fermés : [[(x,y),...], ...]
        self.current_drawing = []  # points du polygone en cours
        self.fill_segments = []    # segments de remplissage global

        self.fill_rule = tk.StringVar(value="evenodd")

        # UI + events
        self.create_widgets()
        self.bind_events()

        # Drag
        self.dragging_point = None
        self.dragging_offset = (0, 0)

    def create_widgets(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(side="top", fill="x", pady=8)

        ttk.Label(
            top_frame,
            text="Remplissage (clic gauche = points/drag, clic droit = fermer un polygone)"
        ).pack(side="left", padx=8)

        ttk.Button(top_frame, text="Effacer tout", command=self.clear_all) \
            .pack(side="left", padx=20)

        self.canvas = tk.Canvas(self, width=900, height=600, bg="white")
        self.canvas.pack(pady=10)

        ttk.Label(top_frame, text="Règle :").pack(side="left", padx=(20, 4))

        ttk.Radiobutton(
            top_frame, text="Pair/impair",
            variable=self.fill_rule, value="evenodd",
            command=self.remplir
        ).pack(side="left")
        ttk.Radiobutton(
            top_frame, text="Enroulement non nul",
            variable=self.fill_rule, value="winding",
            command=self.remplir
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
                self.fill_segments.extend(LCA.lca_fill(poly, rule=self.fill_rule.get()))

        self.redraw()

    def clear_all(self):
        self.polygons = []
        self.current_drawing = []
        self.fill_segments = []
        self.redraw()

# ==================================================================
#                               BEZIER
# ==================================================================
class BezierWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Courbe de Bézier")
        self.geometry("1000x700")

        # Control polyline (points de contrôle)
        self.control_polyline = []   # [(x,y), ...]
        self.curve_points = []       # points échantillonnés de la courbe

        # Drag
        self.dragging_point = None   # index du point déplacé
        self.dragging_offset = (0, 0)

        # Slider = pas d'échantillonnage
        self.step = tk.DoubleVar(value=0.01)

        # Auto redraw
        self.auto_redraw = tk.BooleanVar(value=False)

        self.create_widgets()
        self.bind_events()
        self.redraw()

    # ------------------------------------------------------------
    # UI
    # ------------------------------------------------------------
    def create_widgets(self):
        top = ttk.Frame(self)
        top.pack(side="top", fill="x", pady=8)

        ttk.Label(
            top,
            text="Clic gauche = ajouter/déplacer • Clic droit = finir la polyline"
        ).pack(side="left", padx=8)

        ttk.Button(
            top, text="Tracer la courbe", command=self.compute_curve
        ).pack(side="left", padx=10)

        ttk.Button(
            top, text="Effacer tout", command=self.clear_all
        ).pack(side="left", padx=10)

        ttk.Label(top, text="Ratio (pas) :").pack(side="left", padx=(20, 5))

        self.slider = ttk.Scale(
            top,
            from_=0.01,
            to=0.5,
            orient="horizontal",
            variable=self.step,
            command=lambda _v: self.on_slider()
        )
        self.slider.pack(side="left", padx=5)

        self.step_label = ttk.Label(top, text=f"{self.step.get():.3f}")
        self.step_label.pack(side="left", padx=5)

        ttk.Checkbutton(
            top,
            text="Auto",
            variable=self.auto_redraw
        ).pack(side="left", padx=(10, 0))

        self.canvas = tk.Canvas(self, width=900, height=600, bg="white")
        self.canvas.pack(pady=10)

    # ------------------------------------------------------------
    # Events
    # ------------------------------------------------------------
    def bind_events(self):
        self.canvas.bind("<ButtonPress-1>", self.start_drag_or_add)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.release_drag)
        self.canvas.bind("<Button-3>", self.finish_polyline)

    # ------------------------------------------------------------
    # Slider
    # ------------------------------------------------------------
    def on_slider(self):
        self.step_label.config(text=f"{self.step.get():.3f}")

        if self.auto_redraw.get():
            self.compute_curve()

    # ------------------------------------------------------------
    # Clear
    # ------------------------------------------------------------
    def clear_all(self):
        self.control_polyline = []
        self.curve_points = []
        self.dragging_point = None
        self.redraw()

    # ------------------------------------------------------------
    # Utils
    # ------------------------------------------------------------
    def find_nearest(self, x, y):
        r2 = 8 * 8
        for i, (px, py) in enumerate(self.control_polyline):
            if (px - x) ** 2 + (py - y) ** 2 <= r2:
                return i
        return None

    # ------------------------------------------------------------
    # Mouse logic
    # ------------------------------------------------------------
    def start_drag_or_add(self, event):
        x, y = event.x, event.y
        hit = self.find_nearest(x, y)

        if hit is not None:
            self.dragging_point = hit
            px, py = self.control_polyline[hit]
            self.dragging_offset = (px - x, py - y)
            return

        self.control_polyline.append((x, y))

        if self.auto_redraw.get():
            self.compute_curve()
        else:
            self.curve_points = []
            self.redraw()

    def drag(self, event):
        if self.dragging_point is None:
            return

        i = self.dragging_point
        x = event.x + self.dragging_offset[0]
        y = event.y + self.dragging_offset[1]
        self.control_polyline[i] = (x, y)

        if self.auto_redraw.get():
            self.compute_curve()
        else:
            self.curve_points = []
            self.redraw()

    def release_drag(self, event):
        self.dragging_point = None

    def finish_polyline(self, event):
        # Pas de traitement spécial : la polyline reste telle quelle
        self.redraw()

    # ------------------------------------------------------------
    # Bézier
    # ------------------------------------------------------------
    def compute_curve(self):
        if len(self.control_polyline) < 2:
            self.curve_points = []
            self.redraw()
            return

        step = float(self.step.get())
        self.curve_points = BZ.bezier_polyline(self.control_polyline, step=step)
        self.redraw()

    # ------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------
    def draw_polyline(self, pts, color, dash=None, width=2):
        if len(pts) >= 2:
            for i in range(len(pts) - 1):
                self.canvas.create_line(
                    *pts[i], *pts[i + 1],
                    fill=color, width=width, dash=dash
                )

        for x, y in pts:
            r = 4
            self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill=color, outline=color
            )

    def redraw(self):
        self.canvas.delete("all")

        # Polyline de contrôle
        if self.control_polyline:
            self.draw_polyline(
                self.control_polyline,
                color="gray",
                dash=(4, 2),
                width=2
            )

        # Courbe de Bézier
        if self.curve_points and len(self.curve_points) >= 2:
            for i in range(len(self.curve_points) - 1):
                self.canvas.create_line(
                    *self.curve_points[i],
                    *self.curve_points[i + 1],
                    fill="purple",
                    width=3
                )


# ==================================================================
#                               MENU
# ==================================================================
class MainMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Menu Principal")
        self.geometry("500x300")

        ttk.Label(self, text="Mazette j'adore les maths",
                  font=("Arial", 22)).pack(pady=25)

        ttk.Button(self, text="Découpage", command=self.open_decoupage).pack(pady=10)
        ttk.Button(self, text="Remplissage", command=self.open_remplissage).pack(pady=10)
        ttk.Button(self, text="Courbe de bézier", command=self.open_bezier).pack(pady=10)

    def open_decoupage(self):
        DecoupageWindow(self)

    def open_remplissage(self):
        RemplissageWindow(self)

    def open_bezier(self):
        BezierWindow(self)


if __name__ == "__main__":
    app = MainMenu()
    app.mainloop()
