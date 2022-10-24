from napari.layers.shapes import Shapes as ShapesLayer
from napari.layers.shapes.shapes import Mode

from napari._qt.layer_controls.qt_shapes_controls import QtShapesControls
from napari._qt.layer_controls.qt_layer_controls_container import (
    layer_to_controls,
)

import numpy as np


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

    def to_labels(self, labels_shape=None):
        """Return an integer labels image.

        Parameters
        ----------
        labels_shape : np.ndarray | tuple | None
            Tuple defining shape of labels image to be generated. If non
            specified, takes the max of all the vertiecs

        Returns
        -------
        labels : np.ndarray
            Integer array where each value is either 0 for background or an
            integer up to N for points inside the shape at the index value - 1.
            For overlapping shapes z-ordering will be respected.
        """
        if labels_shape is None:
            # See https://github.com/napari/napari/issues/2778
            # Point coordinates land on pixel centers. We want to find the
            # smallest shape that will hold the largest point in the data,
            # using rounding.
            labels_shape = np.round(self._extent_data[1]) + 1

        labels_shape = np.ceil(labels_shape).astype("int")
        labels = self.to_labels_impl(labels_shape=labels_shape)

        return labels

    def to_labels_impl(self, labels_shape=None, zoom_factor=1, offset=[0, 0]):
        """Returns a integer labels image, where each shape is embedded in an
        array of shape labels_shape with the value of the index + 1
        corresponding to it, and 0 for background. For overlapping shapes
        z-ordering will be respected.

        Parameters
        ----------
        labels_shape : np.ndarray | tuple | None
            2-tuple defining shape of labels image to be generated. If non
            specified, takes the max of all the vertices
        zoom_factor : float
            Premultiplier applied to coordinates before generating mask. Used
            for generating as downsampled mask.
        offset : 2-tuple
            Offset subtracted from coordinates before multiplying by the
            zoom_factor. Used for putting negative coordinates into the mask.

        Returns
        -------
        labels : np.ndarray
            MxP integer array where each value is either 0 for background or an
            integer up to N for points inside the corresponding shape.
        """
        if labels_shape is None:
            labels_shape = self._data_view.displayed_vertices.max(
                axis=0
            ).astype(np.int)

        labels = np.zeros(labels_shape, dtype=int)

        for ind in self._data_view._z_order[::1]:
            mask = self._data_view.shapes[ind].to_mask(
                labels_shape, zoom_factor=zoom_factor, offset=offset
            )
            labels[mask] = ind + 1

        return labels


layer_to_controls[InterpolatedLayer] = InterpolatedLayerControls
