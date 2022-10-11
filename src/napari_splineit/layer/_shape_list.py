import napari
import numpy as np
import types

from napari.layers.shapes import Shapes as ShapesLayer
from napari.layers.shapes.shapes import ShapeList as ShapeList
from napari.layers.shapes.shapes import Mode

import contextlib
import time


class CtrlLayerShapeList(ShapeList):
    def __init__(self, *args, ctrl_layer, interpolated_layer, **kwargs):
        self.ctrl_layer = ctrl_layer
        self.interpolated_layer = interpolated_layer
        self.propagate = True
        super(CtrlLayerShapeList, self).__init__(*args, **kwargs)
        self.mode = "DIRECT"

    def edit(
        self, index, data, face_color=None, edge_color=None, new_type=None
    ):

        super(CtrlLayerShapeList, self).edit(
            index=index,
            data=data,
            face_color=face_color,
            edge_color=edge_color,
            new_type=new_type,
        )

        if self.propagate:
            new_data = self.ctrl_layer.interpolate(data)
            self.update_interpolated(
                index=index, data=new_data, new_type=new_type
            )

    def run_interpolation(self):

        interpolated_polygons = [
            self.ctrl_layer.interpolate(s.data)
            for index, s in enumerate(self.shapes)
        ]

        with self.interpolated_layer.events.set_data.blocker():

            with timeit("save colors"):
                edge_color = self.interpolated_layer.edge_color
                face_color = self.interpolated_layer.face_color
            # self.interpolated_layer._data_view.remove_all()
            print(f"{len(face_color) = }  {len(interpolated_polygons) = }")

            with timeit("remove all"):
                self.interpolated_layer.selected_data = set(
                    range(self.interpolated_layer.nshapes)
                )
                self.interpolated_layer.remove_selected()

            print(f"{len(self.interpolated_layer.face_color) = }")

            with timeit("add polygons to interpolated_layer"):
                self.interpolated_layer.add_polygons(interpolated_polygons)

            with timeit("restore colors"):
                self.interpolated_layer.edge_color = edge_color
                self.interpolated_layer.face_color = face_color

        self.interpolated_layer.refresh()

        # for index,s in enumerate(self.shapes):
        #     new_data = self.ctrl_layer.interpolate(s.data)
        #     self.update_interpolated(index=index, data=new_data, new_type=None)
        # self.interpolated_layer.refresh()

    def update_interpolated(self, data, index, new_type=None):
        with self.interpolated_layer.events.set_data.blocker():
            self.interpolated_layer._data_view.edit(
                index=index, data=data, new_type=new_type
            )
            self.interpolated_layer._data_view._update_displayed()
        self.interpolated_layer.refresh()

    def shift(self, index, shift):
        if self.propagate:
            self.interpolated_layer._data_view.shift(index, shift.copy())
        super(CtrlLayerShapeList, self).shift(index, shift.copy())
        if self.propagate:
            self.interpolated_layer.refresh()

    def scale(self, index, scale, center=None):
        if self.propagate:
            self.interpolated_layer._data_view.scale(index, scale, center)
        super(CtrlLayerShapeList, self).scale(index, scale, center)
        if self.propagate:
            self.interpolated_layer.refresh()

    def rotate(self, index, angle, center=None):
        if self.propagate:
            self.interpolated_layer._data_view.rotate(index, angle, center)
        super(CtrlLayerShapeList, self).rotate(index, angle, center)
        if self.propagate:
            self.interpolated_layer.refresh()

    def flip(self, index, axis, center=None):
        if self.propagate:
            self.interpolated_layer._data_view.flip(index, axis, center)
        super(CtrlLayerShapeList, self).flip(index, axis, center)
        if self.propagate:
            self.interpolated_layer.refresh()

    def transform(self, index, transform):
        if self.propagate:
            self.interpolated_layer._data_view.transform(
                index, transform.copy()
            )
        super(CtrlLayerShapeList, self).transform(index, transform.copy())
        if self.propagate:
            self.interpolated_layer.refresh()

    def update_z_index(self, index, z_index):
        if self.propagate:
            self.interpolated_layer._data_view.update_z_index(index, z_index)
        super(CtrlLayerShapeList, self).update_z_index(index, z_index)
        if self.propagate:
            self.interpolated_layer.refresh()

    # def remove(self, index, renumber=True):
    #     print("remove ", index, renumber)
    #     if renumber:

    #         self.interpolated_layer._data_view.remove(index, renumber)
    #     super(CtrlLayerShapeList, self).remove(index, renumber)
    #     if renumber:
    #         self.interpolated_layer.refresh()
