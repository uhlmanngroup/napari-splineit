from napari.layers.shapes import Shapes as ShapesLayer
from napari.layers.shapes.shapes import Mode

from napari._qt.layer_controls.qt_shapes_controls import QtShapesControls
from napari._qt.layer_controls.qt_layer_controls_container import (
    layer_to_controls,
)


class InterpolatedLayerControls(QtShapesControls):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # disable interactions which are prohibited
        # since we do them on the ctrl layer and
        # the respective interaction is automatically
        # propagated to the interpolated layer
        self.rectangle_button.setEnabled(False)
        self.ellipse_button.setEnabled(False)
        self.line_button.setEnabled(False)
        self.path_button.setEnabled(False)
        self.polygon_button.setEnabled(False)
        self.vertex_insert_button.setEnabled(False)
        self.vertex_remove_button.setEnabled(False)
        self.move_front_button.setEnabled(False)
        self.move_back_button.setEnabled(False)
        self.delete_button.setEnabled(False)


class InterpolatedLayer(ShapesLayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = Mode.PAN_ZOOM

        # this is set in the constructor of CtrlPtrLayer
        self.ctrl_layer = None


layer_to_controls[InterpolatedLayer] = InterpolatedLayerControls
