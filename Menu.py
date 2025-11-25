import tkinter as tk
from tkinter import ttk
import Sutherland_Hodgman as SH
import LCA
# ==================================================================
#             FENÊTRAGE – Sutherland-Hodgman
# ==================================================================
class DecoupageWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Découpage – Sutherland-Hodgman")
        self.geometry("1000x700")

        # Drawing options
        self.current_mode = "subject"   # or "clip"
        self.subject_polygon = []
        self.clip_polygon = []
        self.result_polygon = []

        self.current_drawing = []  # list of points being drawn

        # UI + events
        self.create_widgets()
        self.bind_events()

        # Dragging
        self.dragging_point = None      # (poly_type, index)
        self.dragging_offset = (0, 0)   # offset between click and vertex

    # ------------------------------------------------------------
    # UI creation
    # ------------------------------------------------------------
    def create_widgets(self):
        # Top bar with mode buttons
        top_frame = ttk.Frame(self)
        top_frame.pack(side="top", fill="x", pady=8)

        ttk.Label(top_frame, text="Mode de dessin :").pack(side="left", padx=8)

        self.btn_mode_subject = ttk.Button(
            top_frame, text="Polygone à découper", command=self.set_mode_subject
        )
        self.btn_mode_subject.pack(side="left", padx=5)

        self.btn_mode_clip = ttk.Button(
            top_frame, text="Fenêtre de découpe", command=self.set_mode_clip
        )
        self.btn_mode_clip.pack(side="left", padx=5)

        ttk.Button(top_frame, text="Clipping !", command=self.perform_clipping) \
            .pack(side="left", padx=20)

        ttk.Button(top_frame, text="Effacer tout", command=self.clear_all) \
            .pack(side="left", padx=20)

        # Drawing canvas
        self.canvas = tk.Canvas(self, width=900, height=600, bg="white")
        self.canvas.pack(pady=10)

    # ------------------------------------------------------------
    # Event binding
    # ------------------------------------------------------------
    def bind_events(self):
        self.canvas.bind("<ButtonPress-1>", self.start_drag_or_add_point)
        self.canvas.bind("<B1-Motion>", self.drag_point)
        self.canvas.bind("<ButtonRelease-1>", self.release_drag)

        self.canvas.bind("<Button-3>", self.right_click)    # close polygon

    # ------------------------------------------------------------
    # Mode switch
    # ------------------------------------------------------------
    def set_mode_subject(self):
        self.current_mode = "subject"

    def set_mode_clip(self):
        self.current_mode = "clip"

    # ------------------------------------------------------------
    # Click handlers
    # ------------------------------------------------------------
    def start_drag_or_add_point(self, event):
        x, y = event.x, event.y

        # Try to find a vertex within 8px radius
        hit = self.find_nearest_vertex(x, y)
        if hit is not None:
            poly_type, idx = hit
            self.dragging_point = hit

            # Compute drag offset for smooth dragging
            if poly_type == "subject":
                px, py = self.subject_polygon[idx]
            elif poly_type == "clip":
                px, py = self.clip_polygon[idx]
            else:
                px, py = self.current_drawing[idx]

            self.dragging_offset = (px - x, py - y)
            return

        # No vertex selected → add new vertex (normal drawing)
        self.current_drawing.append((x, y))
        self.redraw()

    def right_click(self, event):
        """Finish the polygon."""
        if len(self.current_drawing) < 3:
            return

        if self.current_mode == "subject":
            self.subject_polygon = self.current_drawing[:]
        else:
            self.clip_polygon = self.current_drawing[:]

        self.current_drawing = []
        self.redraw()

    # ------------------------------------------------------------
    # Drawing routine
    # ------------------------------------------------------------
    def draw_polygon(self, points, color, tags="poly", dash=None, width=2, fill=""):
        """Draws a polygon on the canvas."""
        if len(points) >= 2:
            for i in range(len(points) - 1):
                self.canvas.create_line(*points[i], *points[i+1],
                                        fill=color, width=width, dash=dash, tags=tags)

        if len(points) >= 3:
            # close polygon
            self.canvas.create_line(*points[-1], *points[0],
                                    fill=color, width=width, dash=dash, tags=tags)

        # draw vertices
        for x, y in points:
            r = 4
            self.canvas.create_oval(x-r, y-r, x+r, y+r,
                                    fill=color, outline=color, tags=tags)

    def drag_point(self, event):
        if not self.dragging_point:
            return

        poly_type, idx = self.dragging_point
        x = event.x + self.dragging_offset[0]
        y = event.y + self.dragging_offset[1]

        if poly_type == "subject":
            self.subject_polygon[idx] = (x, y)
        elif poly_type == "clip":
            self.clip_polygon[idx] = (x, y)
        else:
            self.current_drawing[idx] = (x, y)

        self.redraw()

    def release_drag(self, event):
        self.dragging_point = None

    def find_nearest_vertex(self, x, y):
        """Return (poly_type, index) if near a vertex, else None."""
        radius = 8  # selection tolerance

        # Check subject polygon
        for i, (px, py) in enumerate(self.subject_polygon):
            if (px - x)**2 + (py - y)**2 <= radius**2:
                return ("subject", i)

        # Check clipping polygon
        for i, (px, py) in enumerate(self.clip_polygon):
            if (px - x)**2 + (py - y)**2 <= radius**2:
                return ("clip", i)

        # Check currently drawn polygon
        for i, (px, py) in enumerate(self.current_drawing):
            if (px - x)**2 + (py - y)**2 <= radius**2:
                return ("current", i)

        return None

    def redraw(self):
        """Clear canvas and redraw everything."""
        self.canvas.delete("all")

        # Subject polygon = blue
        if self.subject_polygon:
            self.draw_polygon(self.subject_polygon, color="blue")

        # Clip window = red
        if self.clip_polygon:
            self.draw_polygon(self.clip_polygon, color="red")

        # Polygon currently being drawn = dashed gray
        if self.current_drawing:
            self.draw_polygon(self.current_drawing, color="gray", dash=(4, 2))

        # Result polygon = green
        if self.result_polygon:
            self.draw_polygon(self.result_polygon, color="green", width=3)

    # ------------------------------------------------------------
    # Clipping
    # ------------------------------------------------------------
    def perform_clipping(self):
        if len(self.subject_polygon) < 3 or len(self.clip_polygon) < 3:
            return

        try:
            self.result_polygon = SH.sutherland_hodgman(
                self.subject_polygon,
                self.clip_polygon
            )
        except Exception as e:
            print("Error during clipping:", e)

        self.redraw()

    # ------------------------------------------------------------
    # Clear
    # ------------------------------------------------------------
    def clear_all(self):
        self.subject_polygon = []
        self.clip_polygon = []
        self.result_polygon = []
        self.current_drawing = []
        self.redraw()


# ==================================================================
#             REMPLISSAGE – réutilise le tracé existant
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

        # UI + events
        self.create_widgets()
        self.bind_events()

        # Drag
        # ("poly", poly_index, vertex_index) ou ("current", index)
        self.dragging_point = None
        self.dragging_offset = (0, 0)

    # ------------------------------------------------------------
    # UI
    # ------------------------------------------------------------
    def create_widgets(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(side="top", fill="x", pady=8)

        ttk.Label(
            top_frame,
            text="Remplissage (clic gauche = points/drag, clic droit = fermer un polygone)"
        ).pack(side="left", padx=8)

        ttk.Button(top_frame, text="Remplir tous", command=self.remplir) \
            .pack(side="left", padx=20)

        ttk.Button(top_frame, text="Effacer tout", command=self.clear_all) \
            .pack(side="left", padx=20)

        self.canvas = tk.Canvas(self, width=900, height=600, bg="white")
        self.canvas.pack(pady=10)

    def bind_events(self):
        self.canvas.bind("<ButtonPress-1>", self.start_drag_or_add_point)
        self.canvas.bind("<B1-Motion>", self.drag_point)
        self.canvas.bind("<ButtonRelease-1>", self.release_drag)
        self.canvas.bind("<Button-3>", self.right_click)

    # ------------------------------------------------------------
    # Sélection / ajout point
    # ------------------------------------------------------------
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

        # Ajout d'un nouveau point
        self.current_drawing.append((x, y))
        self.redraw()

    # ------------------------------------------------------------
    # Fermeture du polygone courant
    # ------------------------------------------------------------
    def right_click(self, event):
        if len(self.current_drawing) < 3:
            return

        self.polygons.append(self.current_drawing[:])
        self.current_drawing = []
        self.remplir()  # recalcul du remplissage global

    # ------------------------------------------------------------
    # Drag
    # ------------------------------------------------------------
    def drag_point(self, event):
        if not self.dragging_point:
            return

        kind = self.dragging_point[0]
        x = event.x + self.dragging_offset[0]
        y = event.y + self.dragging_offset[1]

        if kind == "poly":
            poly_idx, idx = self.dragging_point[1], self.dragging_point[2]
            self.polygons[poly_idx][idx] = (x, y)
            self.remplir()  # MAJ en temps réel
        else:
            idx = self.dragging_point[1]
            self.current_drawing[idx] = (x, y)
            self.redraw()

    def release_drag(self, event):
        self.dragging_point = None

    # ------------------------------------------------------------
    # Cherche le sommet le plus proche
    # ------------------------------------------------------------
    def find_nearest_vertex(self, x, y):
        radius = 8

        # Polygones déjà créés
        for pi, poly in enumerate(self.polygons):
            for vi, (px, py) in enumerate(poly):
                if (px - x)**2 + (py - y)**2 <= radius**2:
                    return ("poly", pi, vi)

        # Polygone en cours
        for i, (px, py) in enumerate(self.current_drawing):
            if (px - x)**2 + (py - y)**2 <= radius**2:
                return ("current", i)

        return None

    # ------------------------------------------------------------
    # Dessin
    # ------------------------------------------------------------
    def draw_polygon(self, points, color, dash=None):
        if len(points) >= 2:
            for i in range(len(points) - 1):
                self.canvas.create_line(*points[i], *points[i+1],
                                        fill=color, width=2, dash=dash)

        if len(points) >= 3:
            self.canvas.create_line(*points[-1], *points[0],
                                    fill=color, width=2, dash=dash)

        for x, y in points:
            r = 4
            self.canvas.create_oval(x-r, y-r, x+r, y+r,
                                    fill=color, outline=color)

    def redraw(self):
        self.canvas.delete("all")

        # 1) Remplissage
        for y, x1, x2 in self.fill_segments:
            self.canvas.create_line(x1, y, x2, y, fill="orange")

        # 2) Polygones fermés
        for poly in self.polygons:
            self.draw_polygon(poly, color="blue")

        # 3) Polygone en cours
        if self.current_drawing:
            self.draw_polygon(self.current_drawing, color="gray", dash=(4, 2))

    # ------------------------------------------------------------
    # Remplissage global (LCA)
    # ------------------------------------------------------------
    def remplir(self):
        self.fill_segments = []

        for poly in self.polygons:
            if len(poly) >= 3:
                self.fill_segments.extend(LCA.scanline_fill(poly))

        self.redraw()

    # ------------------------------------------------------------
    # Clear
    # ------------------------------------------------------------
    def clear_all(self):
        self.polygons = []
        self.current_drawing = []
        self.fill_segments = []
        self.redraw()


# ==================================================================
#                  MAIN MENU
# ==================================================================
class MainMenu(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Projet Infographie")
        self.geometry("500x300")

        title = ttk.Label(self, text="Mazette j'adore les maths", font=("Arial", 22))
        title.pack(pady=25)

        # ---------- Découpage ----------
        btn_decoupage = ttk.Button(
            self,
            text="Découpage",
            command=self.open_decoupage
        )
        btn_decoupage.pack(pady=10)

        # ---------- Remplissage ----------
        btn_remplissage = ttk.Button(
            self,
            text="Remplissage",
            command=self.open_remplissage
        )
        btn_remplissage.pack(pady=10)

    def open_decoupage(self):
        DecoupageWindow(self)

    def open_remplissage(self):
        RemplissageWindow(self)


if __name__ == "__main__":
    app = MainMenu()
    app.mainloop()
