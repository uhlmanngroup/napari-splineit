from .utils import phi_generator_impl, getCoefsFromKnots
from .splinegenerator import B3, SplineCurveSample

from .interpolator_base import InterpolatorBase

from qtpy.QtWidgets import QWidget


def curve_from_knots(knots):

    if knots.shape[0] > 3:
        ctrl_points = getCoefsFromKnots(knots, "cubic")
        phi = phi_generator_impl(ctrl_points.shape[0], 20 * ctrl_points.shape[0], "cubic")
        SplineContour = SplineCurveSample(ctrl_points.shape[0], B3(), True, ctrl_points)
        curve = SplineContour.sample(phi)
        return curve
    return knots.copy()


class UhlmannSplinesUI(QWidget):
    def __init__(self, layer):
        super().__init__()
        self.layer = layer


class UhlmannSplines(InterpolatorBase):

    UI = UhlmannSplinesUI
    name = "UhlmannSplines"

    def __call__(self, knots):
        return curve_from_knots(knots)
