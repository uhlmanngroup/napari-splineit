from .utils import phi_generator_impl, getCoefsFromKnots
from .splinegenerator import B3, SplineCurveSample
from qtpy.QtWidgets import QWidget, QFormLayout
from ..widgets import SpinSlider
from .interpolator_base import InterpolatorBase


def curve_from_knots(knots, n):

    if knots.shape[0] > 3:

        coefs = getCoefsFromKnots(knots, "cubic")

        phi = phi_generator_impl(coefs.shape[0], n * coefs.shape[0], "cubic")
        SplineContour = SplineCurveSample(coefs.shape[0], B3(), True, coefs)
        curve = SplineContour.sample(phi)
        return curve
    return knots.copy()


def knots_from_coefs(x):
    coefs = x
    phi = phi_generator_impl(coefs.shape[0], coefs.shape[0], "cubic")
    SplineContour = SplineCurveSample(coefs.shape[0], B3(), True, coefs)
    knots = SplineContour.sample(phi)
    return knots


class UhlmannSplinesUI(QWidget):
    def __init__(self, layer):
        super().__init__()
        self.layer = layer
        self.interpolator = self.layer.interpolator
        layout = QFormLayout()
        self.setLayout(layout)

        self.n_widget = SpinSlider(
            minmax=[1, 100], value=int(self.interpolator.n)
        )
        self.n_widget.valueChanged.connect(self.on_n_changed)
        layout.addRow("n", self.n_widget)

    def on_n_changed(self):
        value = self.n_widget.value()
        self.interpolator.n = value
        self.layer.run_interpolation()


class UhlmannSplines(InterpolatorBase):

    UI = UhlmannSplinesUI
    name = "UhlmannSplines"

    def __init__(self, n=4):
        super().__init__()
        self.n = 4

    def __call__(self, knots):
        return curve_from_knots(knots, self.n)
