# fmt: on
import napari
import napari.layers
import numpy as np

from napari._qt.layer_controls.qt_layer_controls_container import \
    layer_to_controls  # fmt: skip
from napari._qt.layer_controls.qt_shapes_controls import QtShapesControls
from napari.layers.shapes import Shapes as ShapesLayer
from qtpy.QtWidgets import QComboBox

from ..interpolation import interpolator_factory, registered_interplators
from ._shape_list import CtrlLayerShapeList

# fmt: off

from napari.layers.shapes._shapes_utils import extract_shape_type,number_of_shapes,get_default_shape_type


class CtrlLayerControls(QtShapesControls):
    def __init__(self, layer):
        super().__init__(layer)

        # we only allow for polygon shapes and disable all other shapes
        self.rectangle_button.setEnabled(False)
        self.ellipse_button.setEnabled(False)
        self.line_button.setEnabled(False)
        self.path_button.setEnabled(False)

        # the current interpolator
        ip_type = type(layer.interpolator)

        # # dropdown list with all interpolator types
        self.method_selector = QComboBox()
        self.method_selector.addItems(registered_interplators.keys())
        self.method_selector.setCurrentText(ip_type.name)
        self.method_selector.currentIndexChanged.connect(self.on_method_change)

        # the ui of the interpolator itself
        self.layer_ui = ip_type.UI(layer=layer)

        self.layout().addRow("method", self.method_selector)
        self.layout().addRow(self.layer_ui)

        # keep track of the parameters of the individual method
        # st. we can restore the last used parameter when
        # an already used method is selected from the combo box
        self.method_kwargs = {ip_type.name: layer.interpolator.marshal()}

    def on_method_change(self):

        # store the parameters of the last method
        last_method = self.layer.interpolator
        self.method_kwargs[type(last_method).name] = last_method.marshal()

        # the new method
        new_method_name = self.method_selector.currentText()

        # restore parameters
        kwargs = self.method_kwargs.get(new_method_name, {})
        interpolator = interpolator_factory(name=new_method_name, **kwargs)
        self.layer.interpolator = interpolator

        # remove old control ui and add new ui
        interpolator_ui_cls = type(interpolator).UI
        self.layout().removeRow(self.layer_ui)
        self.layer_ui = interpolator_ui_cls(layer=self.layer)
        self.layout().addRow(self.layer_ui)

        # run interpolation
        self.layer.run_interpolation()


class CtrlLayer(ShapesLayer):
    def __init__(self, *args, interpolator, interpolated_layer, **kwargs):
        self.interpolator = interpolator
        self.interpolated_layer = interpolated_layer
        self.interpolated_layer.ctrl_layer = self
        super().__init__(
            *args, edge_color="transparent", face_color="transparent", **kwargs
        )

        self._data_view = CtrlLayerShapeList(
            ndisplay=self._ndisplay,
            ctrl_layer=self,
            interpolated_layer=interpolated_layer,
        )
        self._data_view.slice_key = np.array(self._slice_indices)[
            list(self._dims_not_displayed)
        ]

    # needed to make writer possible
    @property
    def _type_string(self):
        return "shapes"

    def set_polygons(self, data, edge_color, face_color,current_edge_color=None, current_face_color=None):
        self._data_view.propagate = False
        self.data = [(d,'polygon') for d in data]
        interpolated = [(self.interpolate(data=poly),'polygon') for poly in data]
        self.interpolated_layer.data = interpolated
        self.interpolated_layer.edge_color = edge_color
        self.interpolated_layer.face_color = face_color
        self._data_view.propagate = True
        if current_edge_color is not None:
            self.interpolated_layer.current_edge_color = edge_color
        if current_face_color is not None:
            self.interpolated_layer.current_face_color = face_color 

    def add(self, data, *, shape_type="polygon", interpolated_layer_kwargs=None, **kwargs):
        # print("data",len(data),"shape_type",shape_type)
        if interpolated_layer_kwargs is None:
            interpolated_layer_kwargs = dict()

        if shape_type == "":
            shape_type = "polygon"
        if shape_type != "polygon" and shape_type != "path" and not isinstance(shape_type,list):
            raise RuntimeError(f"only polygon shape type is allowed: {shape_type=}")

        data_is_3d_array = False
        if isinstance(data, np.ndarray) and data.ndim ==3:
            data_is_3d_array = True

        if isinstance(data, list) or data_is_3d_array:
            super().add(data=data, shape_type=shape_type, **kwargs)

            if self._data_view.propagate:

                interpolated = [self.interpolate(data=poly) for poly in data]

                if data_is_3d_array:
                    interpolated = np.array(interpolated)


                self.interpolated_layer.add(
                    data=interpolated,
                    shape_type=shape_type,
                    **{**kwargs,**interpolated_layer_kwargs}
                )


        else:
            super().add(data=data, shape_type=shape_type, **kwargs)

            if self._data_view.propagate:

                interpolated = self.interpolate(data=data)

                self.interpolated_layer.add(
                    data=interpolated, shape_type=shape_type, **kwargs
                )

    def remove_all(self):
        self.selected_data = set(range(self.nshapes))
        self.remove_selected()

    def interpolate(self, data):
        return self.interpolator(data)

    def run_interpolation(self):
        self._data_view.run_interpolation()

    @property
    def shape_type(self):
        """list of str: name of shape type for each shape."""
        return self._data_view.shape_types

    @shape_type.setter
    def shape_type(self, shape_type):
        if shape_type != "polygon":
            raise RuntimeError("only polygon shape is allowed")


    def remove_selected(self):

        self.interpolated_layer.selected_data = set(self.selected_data)
        self.interpolated_layer.remove_selected()
        super().remove_selected()


    @property
    def data(self):
        """list: Each element is an (N, D) array of the vertices of a shape."""
        return self._data_view.data

    @data.setter
    def data(self, data):
        self._finish_drawing()

        data, shape_type = extract_shape_type(data)
        n_new_shapes = number_of_shapes(data)
        # not given a shape_type through data
        if shape_type is None:
            shape_type = self.shape_type

        edge_widths = self._data_view.edge_widths
        edge_color = self._data_view.edge_color
        face_color = self._data_view.face_color
        z_indices = self._data_view.z_indices

        # fewer shapes, trim attributes
        if self.nshapes > n_new_shapes:
            shape_type = shape_type[:n_new_shapes]
            edge_widths = edge_widths[:n_new_shapes]
            z_indices = z_indices[:n_new_shapes]
            edge_color = edge_color[:n_new_shapes]
            face_color = face_color[:n_new_shapes]
        # more shapes, add attributes
        elif self.nshapes < n_new_shapes:
            n_shapes_difference = n_new_shapes - self.nshapes
            shape_type = (
                shape_type
                + [get_default_shape_type(shape_type)] * n_shapes_difference
            )
            edge_widths = edge_widths + [1] * n_shapes_difference
            z_indices = z_indices + [0] * n_shapes_difference
            edge_color = np.concatenate(
                (
                    edge_color,
                    self._get_new_shape_color(n_shapes_difference, 'edge'),
                )
            )
            face_color = np.concatenate(
                (
                    face_color,
                    self._get_new_shape_color(n_shapes_difference, 'face'),
                )
            )


        self._data_view = CtrlLayerShapeList(
            ndisplay=self._ndisplay,
            ctrl_layer=self,
            interpolated_layer=self.interpolated_layer,
        )

        self.add(
            data,
            shape_type=shape_type,
            edge_width=edge_widths,
            edge_color=edge_color,
            face_color=face_color,
            z_index=z_indices,
        )

        self._update_dims()
        self.events.data(value=self.data)
        self._set_editable()



layer_to_controls[CtrlLayer] = CtrlLayerControls


# Supporting Napari readers with a custom layer  is a bit hacky:
#  - Napari assumes that the layer is in the namespace of `napari.layers`.
#  - The small-cased name of the layer is in `napari.layers.NAMES`.
#  - There is a method add_<layer-name> (ie add_splineit_ctrl)
#    in the viewer class (implemented in `_reader.py`)
#  - We use the name `Splineit_Ctrl` instead of just `CtrlLayer`
#    to avoid any name clashes.
napari.layers.Splineit_Ctrl = CtrlLayer
napari.layers.NAMES.add("splineit_ctrl")
