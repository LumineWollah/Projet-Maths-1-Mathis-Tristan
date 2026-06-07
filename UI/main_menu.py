import tkinter as tk
from tkinter import ttk

from UI.decoupage_window import DecoupageWindow
from UI.remplissage_window import RemplissageWindow
from UI.bezier_window import BezierWindow
from UI.bspline_window import BSplineNURBSWindow


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
        ttk.Button(self, text="BSplines / NURBS", command=self.open_bspline).pack()

    def open_decoupage(self):
        DecoupageWindow(self)

    def open_remplissage(self):
        RemplissageWindow(self)

    def open_bezier(self):
        BezierWindow(self)

    def open_bspline(self):
        BSplineNURBSWindow(self)
