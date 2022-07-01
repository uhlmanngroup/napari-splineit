from qtpy.QtWidgets import QWidget,QHBoxLayout,QSlider,QSpinBox
from qtpy.QtCore import Qt,QSignalBlocker,Signal


class SpinSlider(QWidget):

    valueChanged = Signal(int)

    def __init__(self, minmax, value):
        super(SpinSlider, self).__init__()




        layout = QHBoxLayout()
        self.setLayout(layout)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setTickInterval(1)
        self.slider.setMinimum(minmax[0])
        self.slider.setMaximum(minmax[1])
        self.slider.setValue(value)
        self.slider.setTracking(False)
        self.slider.valueChanged.connect(self._on_slider_changed)

        self.spinbox = QSpinBox()
        self.spinbox.setMinimum(minmax[0])
        self.spinbox.setMaximum(minmax[1])
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

