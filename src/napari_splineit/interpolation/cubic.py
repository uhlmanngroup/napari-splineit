import numpy as np
from scipy.interpolate import CubicSpline
from qtpy.QtWidgets import QWidget

from .interpolator_base import InterpolatorBase


class CubicInterpolatorUI(QWidget):
    def __init__(self, layer):
        super().__init__()
        self.layer = layer


class CubicInterpolator(InterpolatorBase):

    UI = CubicInterpolatorUI
    name = "CubicInterpolator"

    def __call__(self, knots):
        knots = np.require(knots)
        if knots.shape[0] < 3:
            first_point = knots[0, :]
            return np.concatenate([knots, first_point[None, :]], axis=0)

        else:

            first_point = knots[0, :]
            knots = np.concatenate(
                [knots, first_point[None, :]], axis=0
            )

            t = np.arange(knots.shape[0])
            cs_x = CubicSpline(t, knots[:, 0], bc_type="periodic")
            cs_y = CubicSpline(t, knots[:, 1], bc_type="periodic")
            tfine = np.linspace(0, t[-1], endpoint=False)
            xx = cs_x(tfine)[:, None]
            yy = cs_y(tfine)[:, None]

            ret = np.concatenate([xx, yy], axis=1)
            return ret
