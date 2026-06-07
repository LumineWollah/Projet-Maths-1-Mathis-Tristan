"""Couche render : projection et raster (appelle algo/trimestre_3, pas de formules ici)."""

from algo.trimestre_3.render.projection import Projecteur
from algo.trimestre_3.render.raster import Rasterizer, ZBuffer

__all__ = ["Projecteur", "Rasterizer", "ZBuffer"]
