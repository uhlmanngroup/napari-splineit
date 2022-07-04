import numpy as np
from scipy.interpolate import splrep, splev
from qtpy.QtWidgets import QWidget, QFormLayout
from ..widgets import SpinSlider
from .interpolator_base import InterpolatorBase


class SplineInterpolatorUI(QWidget):
    def __init__(self, layer):
        super().__init__()
        self.layer = layer
        self.interpolator = self.layer.interpolator
        layout = QFormLayout()
        self.setLayout(layout)

        self.order_widget = SpinSlider(
            minmax=[1, 3], value=self.interpolator.k
        )
        self.order_widget.valueChanged.connect(self.on_order_changed)

        self.s_widget = SpinSlider(
            minmax=[0, 50000], value=int(self.interpolator.s)
        )
        self.s_widget.valueChanged.connect(self.on_s_changed)

        self.n_widget = SpinSlider(
            minmax=[1, 100], value=int(self.interpolator.n)
        )
        self.n_widget.valueChanged.connect(self.on_n_changed)

        layout.addRow("k", self.order_widget)
        layout.addRow("s", self.s_widget)
        layout.addRow("n", self.n_widget)

    def on_n_changed(self):
        value = self.n_widget.value()
        self.interpolator.n = value
        self.layer.run_interpolation()

    def on_s_changed(self):
        value = self.s_widget.value()
        self.interpolator.s = value
        self.layer.run_interpolation()

    def on_order_changed(self):
        value = self.order_widget.value()
        self.interpolator.k = int(value)
        self.layer.run_interpolation()


class SplineInterpolator(InterpolatorBase):

    UI = SplineInterpolatorUI
    name = "SplineInterpolator"

    def __init__(self, k=3, s=0.0, n=10):
        super().__init__()
        self.k = k
        self.s = s
        self.n = n

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

            cs_x = splrep(t, knots[:, 0], per=True, k=self.k, s=self.s)
            cs_y = splrep(t, knots[:, 1], per=True, k=self.k, s=self.s)
            tfine = np.linspace(0, t[-1], self.n * knots.shape[0], endpoint=False)
            xx = splev(tfine, cs_x)[:, None]
            yy = splev(tfine, cs_y)[:, None]
            ret = np.concatenate([xx, yy], axis=1)
            return ret

    # return a dict which can be passed to constructor
    def marshal(self):
        return {"k": self.k, "s": self.s, "n": self.n}
