from qtpy.QtWidgets import QWidget,QHBoxLayout,QSlider,QSpinBox,QDoubleSpinBox
from qtpy.QtCore import Qt,QSignalBlocker,Signal



class DoubleSlider(QSlider):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.decimals = 5
        self._max_int = 10 ** self.decimals

        super().setMinimum(0)
        super().setMaximum(self._max_int)

        self._min_value = 0.0
        self._max_value = 1.0

    @property
    def _value_range(self):
        return self._max_value - self._min_value

    def value(self):
        return float(super().value()) / self._max_int * self._value_range + self._min_value

    def setValue(self, value):
        super().setValue(int((value - self._min_value) / self._value_range * self._max_int))

    def setMinimum(self, value):
        if value > self._max_value:
            raise ValueError("Minimum limit cannot be higher than maximum")

        self._min_value = value
        self.setValue(self.value())

    def setMaximum(self, value):
        if value < self._min_value:
            raise ValueError("Minimum limit cannot be higher than maximum")

        self._max_value = value
        self.setValue(self.value())

    def minimum(self):
        return self._min_value

    def maximum(self):
        return self._max_value


class DoubleSpinSlider(QWidget):

    valueChanged = Signal(int)

    def __init__(self, minmax, value, single_step=None):
        super(DoubleSpinSlider, self).__init__()

        if single_step is None:
            single_step = (minmax[1] - minmax[0])/10.0


        layout = QHBoxLayout()
        self.setLayout(layout)

        self.slider = DoubleSlider(Qt.Horizontal)

        self.slider.setMinimum(minmax[0])
        self.slider.setMaximum(minmax[1])
        self.slider.setValue(value)
        self.slider.setTracking(True)
        self.slider.valueChanged.connect(self._on_slider_changed)

        self.spinbox = QDoubleSpinBox()
        self.spinbox.setMinimum(minmax[0])
        self.spinbox.setMaximum(minmax[1])
        self.spinbox.setSingleStep(single_step)
        self.spinbox.setValue(value)
        self.spinbox.valueChanged.connect(self._on_spin_box_canged)

        layout.addWidget(self.spinbox,1)
        layout.addWidget(self.slider,4)

    def value(self):
        return self.slider.value()

    def _on_slider_changed(self):

        with QSignalBlocker(self.spinbox) as blocker:
            self.spinbox.setValue(self.slider.value())

        self.valueChanged.emit(self.slider.value())

    def _on_spin_box_canged(self):
        with QSignalBlocker(self.slider) as blocker:
            self.slider.setValue(self.spinbox.value())
        self.valueChanged.emit(self.slider.value())

