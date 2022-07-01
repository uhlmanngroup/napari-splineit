from .utils import phi_generator_impl, getCoefsFromKnots
from .splinegenerator import B3, SplineCurveSample

from .interpolator_base import InterpolatorBase

from qtpy.QtWidgets import QWidget


def curve_from_cp(cp):

    if cp.shape[0] > 3:
        cp = getCoefsFromKnots(cp, "cubic")
        phi = phi_generator_impl(cp.shape[0], 20 * cp.shape[0], "cubic")
        SplineContour = SplineCurveSample(cp.shape[0], B3(), True, cp)
        curve = SplineContour.sample(phi)
        return curve
    return cp.copy()


class UhlmannSplinesUI(QWidget):
    def __init__(self, layer):
        super().__init__()
        self.layer = layer


class UhlmannSplines(InterpolatorBase):

    UI = UhlmannSplinesUI
    name = "UhlmannSplines"

    def __call__(self, ctrl_points):
        return curve_from_cp(ctrl_points)
