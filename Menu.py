import tkinter as tk
from tkinter import ttk
import Sutherland_Hodgman as SH


# ------------------------------------------------------------
# Algorithme de remplissage (scanline / LCA)
# ------------------------------------------------------------
def scanline_fill(polygon):
    """
    Calcule des segments horizontaux de remplissage pour un polygone.
    Retourne une liste de tuples (y, x1, x2).
    """
    if len(polygon) < 3:
        return []

    # Construction des arêtes
    edges = []
    n = len(polygon)
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]

        # On ignore les segments horizontaux
        if y1 == y2:
            continue

        if y1 < y2:
            ymin, ymax = y1, y2
            x_at_ymin = x1
            dy = y2 - y1
            dx = (x2 - x1) / dy
        else:
            ymin, ymax = y2, y1
            x_at_ymin = x2
            dy = y1 - y2
            dx = (x1 - x2) / dy

        edges.append({
            "ymin": ymin,
            "ymax": ymax,
            "x": x_at_ymin,
            "dx": dx
        })

    if not edges:
        return []

    y_min = int(min(p[1] for p in polygon))
    y_max = int(max(p[1] for p in polygon))

    scanlines = []

    # Balayage ligne par ligne
    for y in range(y_min, y_max + 1):
        xs = []
        for e in edges:
            if e["ymin"] <= y < e["ymax"]:  # convention classique
                x = e["x"] + (y - e["ymin"]) * e["dx"]
                xs.append(x)

        if len(xs) < 2:
            continue

        xs.sort()
        # On remplit par paires
        for i in range(0, len(xs) - 1, 2):
            x1 = xs[i]
            x2 = xs[i + 1]
            scanlines.append((y, x1, x2))

    return scanlines


# ==================================================================
#             FENÊTRAGE (ton code existant)
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
        self.title("Remplissage – LCA / Scanline")
        self.geometry("1000x700")

        # Un seul polygone à remplir
        self.polygon = []          # polygone fermé
        self.current_drawing = []  # points en cours de tracé
        self.fill_segments = []    # liste de (y, x1, x2)

        # UI + events
        self.create_widgets()
        self.bind_events()

        # Drag
        self.dragging_point = None      # ("poly" / "current", index)
        self.dragging_offset = (0, 0)

    # ------------------------------------------------------------
    # UI
    # ------------------------------------------------------------
    def create_widgets(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(side="top", fill="x", pady=8)

        ttk.Label(top_frame, text="Remplissage d'un polygone (clic gauche = points, clic droit = fermer)") \
            .pack(side="left", padx=8)

        ttk.Button(top_frame, text="Remplir", command=self.remplir) \
            .pack(side="left", padx=20)

        ttk.Button(top_frame, text="Effacer tout", command=self.clear_all) \
            .pack(side="left", padx=20)

        self.canvas = tk.Canvas(self, width=900, height=600, bg="white")
        self.canvas.pack(pady=10)

    def bind_events(self):
        self.canvas.bind("<ButtonPress-1>", self.start_drag_or_add_point)
        self.canvas.bind("<B1-Motion>", self.drag_point)
        self.canvas.bind("<ButtonRelease-1>", self.release_drag)

        self.canvas.bind("<Button-3>", self.right_click)  # fermer le polygone

    # ------------------------------------------------------------
    # Tracé & drag (recyclage logique du Découpage)
    # ------------------------------------------------------------
    def start_drag_or_add_point(self, event):
        x, y = event.x, event.y

        hit = self.find_nearest_vertex(x, y)
        if hit is not None:
            poly_type, idx = hit
            self.dragging_point = hit

            if poly_type == "poly":
                px, py = self.polygon[idx]
            else:
                px, py = self.current_drawing[idx]

            self.dragging_offset = (px - x, py - y)
            return

        # Ajout d'un nouveau point
        self.current_drawing.append((x, y))
        self.redraw()

    def right_click(self, event):
        """Ferme le polygone."""
        if len(self.current_drawing) < 3:
            return

        self.polygon = self.current_drawing[:]
        self.current_drawing = []
        self.remplir()  # remplissage dès que le polygone est fermé

    def drag_point(self, event):
        if not self.dragging_point:
            return

        poly_type, idx = self.dragging_point
        x = event.x + self.dragging_offset[0]
        y = event.y + self.dragging_offset[1]

        if poly_type == "poly":
            self.polygon[idx] = (x, y)
        else:
            self.current_drawing[idx] = (x, y)

        # IMPORTANT : on recalcule le remplissage à chaque mouvement
        if self.polygon and poly_type == "poly":
            self.remplir(recompute_only=True)
        else:
            self.redraw()

    def release_drag(self, event):
        self.dragging_point = None

    def find_nearest_vertex(self, x, y):
        """Retourne (poly_type, index) ou None."""
        radius = 8

        for i, (px, py) in enumerate(self.polygon):
            if (px - x)**2 + (py - y)**2 <= radius**2:
                return ("poly", i)

        for i, (px, py) in enumerate(self.current_drawing):
            if (px - x)**2 + (py - y)**2 <= radius**2:
                return ("current", i)

        return None

    # ------------------------------------------------------------
    # Dessin (reprend le style de DecoupageWindow)
    # ------------------------------------------------------------
    def draw_polygon(self, points, color, tags="poly", dash=None, width=2):
        if len(points) >= 2:
            for i in range(len(points) - 1):
                self.canvas.create_line(*points[i], *points[i+1],
                                        fill=color, width=width, dash=dash, tags=tags)

        if len(points) >= 3:
            self.canvas.create_line(*points[-1], *points[0],
                                    fill=color, width=width, dash=dash, tags=tags)

        for x, y in points:
            r = 4
            self.canvas.create_oval(x-r, y-r, x+r, y+r,
                                    fill=color, outline=color, tags=tags)

    def redraw(self):
        self.canvas.delete("all")

        # 1) Remplissage (en dessous des contours)
        for y, x1, x2 in self.fill_segments:
            self.canvas.create_line(x1, y, x2, y, fill="orange", width=1)

        # 2) Polygone en cours
        if self.polygon:
            self.draw_polygon(self.polygon, color="blue")

        if self.current_drawing:
            self.draw_polygon(self.current_drawing, color="gray", dash=(4, 2))

    # ------------------------------------------------------------
    # Remplissage
    # ------------------------------------------------------------
    def remplir(self, recompute_only=False):
        """
        Calcule le remplissage du polygone via scanline_fill.
        - recompute_only=True : ne touche pas au polygone, juste recalcule
          (utilisé pendant le drag).
        """
        if len(self.polygon) < 3:
            self.fill_segments = []
            self.redraw()
            return

        # Calcul des segments de remplissage
        self.fill_segments = scanline_fill(self.polygon)
        self.redraw()

    # ------------------------------------------------------------
    # Clear
    # ------------------------------------------------------------
    def clear_all(self):
        self.polygon = []
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
