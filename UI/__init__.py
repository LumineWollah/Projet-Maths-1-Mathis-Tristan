"""Interfaces graphiques Tkinter du projet."""

from UI.main_menu import MainMenu
from UI.decoupage_window import DecoupageWindow
from UI.remplissage_window import RemplissageWindow
from UI.bezier_window import BezierWindow
from UI.bspline_window import BSplineNURBSWindow

__all__ = [
    "MainMenu",
    "DecoupageWindow",
    "RemplissageWindow",
    "BezierWindow",
    "BSplineNURBSWindow",
]
