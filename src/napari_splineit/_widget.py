"""
This module is an example of a barebones QWidget plugin for napari

It implements the Widget specification.
see: https://napari.org/plugins/stable/npe2_manifest_specification.html

Replace code below according to your needs.
"""
from qtpy.QtWidgets import QFormLayout, QLineEdit, QPushButton, QWidget
import numpy as np
from .widgets import SpinSlider
from .layer.layer_factory import layer_factory
from .interpolation import CubicInterpolator, SplineInterpolator
from .interpolation.splinegenerator import SplineCurve, B3


class SplineitQWidget(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        # add the widgets
        self._setup_ui()

        # connect the widgets events / signals
        self._connect_ui()

    def _setup_ui(self):
        self._layer_name_edit = QLineEdit("Splines")
        self._add_layer_btn = QPushButton("Add empty layer")

        self.n_ctrl_points_widget = SpinSlider(minmax=[4, 200], value=20)

        self._add_from_selected_mask = QPushButton("Add layer from mask")
        self.setLayout(QFormLayout())
        self.layout().addRow("name", self._layer_name_edit)
        self.layout().addRow(self._add_layer_btn)
        self.layout().addRow("#ctrl-points", self.n_ctrl_points_widget)
        self.layout().addRow(self._add_from_selected_mask)

    def _connect_ui(self):
        self._add_layer_btn.clicked.connect(self._on_add_layers)
        self._add_from_selected_mask.clicked.connect(
            self._on_add_layers_from_mask
        )

    # todo check for name clashes
    def _get_layer_base_name(self):
        base_name = self._layer_name_edit.text()
        return base_name

    def _on_add_layers_from_mask(self):
        selected = list(self.viewer.layers.selection)
        if len(selected) != 1:
            raise RuntimeError("exactly one layer must be selected")
        selected_layer = selected[0]
        mask = selected_layer.data_raw
        mask = np.squeeze(mask)
        if mask.ndim != 2:
            raise RuntimeError("mask must be a 2D image")

        M = self.n_ctrl_points_widget.value()
        splineCurve = SplineCurve(M, B3(), True, 0)
        cp = splineCurve.getCoefsFromBinaryMask(mask)

        interpolator = UhlmannSplines()
        base_name = self._get_layer_base_name()
        layer_factory(
            self.viewer,
            interpolator=interpolator,
            data=cp,
            ctrl_layer_name=f"{base_name}-CTRL",
            interpolated_layer_name=f"{base_name}-Interpolated",
        )

    def _on_add_layers(self):
        interpolator = SplineInterpolator(k=3)
        base_name = self._get_layer_base_name()
        layer_factory(
            self.viewer,
            interpolator=interpolator,
            ctrl_layer_name=f"{base_name}-CTRL",
            interpolated_layer_name=f"{base_name}-Interpolated",
        )
