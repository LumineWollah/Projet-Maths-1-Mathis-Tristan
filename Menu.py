import tkinter as tk
from tkinter import ttk

import Sutherland_Hodgman as SH


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
    # Pan handlers (NEW)
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

    def open_decoupage(self):
        DecoupageWindow(self)

    def open_remplissage(self):
        tk.Toplevel(self).title("Remplissage")


if __name__ == "__main__":
    app = MainMenu()
    app.mainloop()
