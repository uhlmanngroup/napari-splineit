from napari.layers.shapes.shapes import ShapeList as ShapeList


class CtrlLayerShapeList(ShapeList):
    def __init__(self, *args, ctrl_layer, interpolated_layer, **kwargs):
        self.ctrl_layer = ctrl_layer
        self.interpolated_layer = interpolated_layer
        self.propagate = True
        super().__init__(*args, **kwargs)
        self.mode = "DIRECT"

    def edit(
        self, index, data, face_color=None, edge_color=None, new_type=None
    ):

        super().edit(
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

            # edge_color = self.interpolated_layer.edge_color
            # face_color = self.interpolated_layer.face_color
            # current_edge_color = self.interpolated_layer.edge_color
            # current_face_color = self.interpolated_layer.face_color
            print("set")
            self.interpolated_layer.data = interpolated_polygons
            # self.interpolated_layer.selected_data = set(
            #     range(self.interpolated_layer.nshapes)
            # )
            # self.interpolated_layer.remove_selected()

            # self.interpolated_layer.add_polygons(interpolated_polygons)
            # self.interpolated_layer.edge_color = edge_color
            # self.interpolated_layer.face_color = face_color

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
        super().shift(index, shift.copy())
        if self.propagate:
            self.interpolated_layer.refresh()

    def scale(self, index, scale, center=None):
        if self.propagate:
            self.interpolated_layer._data_view.scale(index, scale, center)
        super().scale(index, scale, center)
        if self.propagate:
            self.interpolated_layer.refresh()

    def rotate(self, index, angle, center=None):
        if self.propagate:
            self.interpolated_layer._data_view.rotate(index, angle, center)
        super().rotate(index, angle, center)
        if self.propagate:
            self.interpolated_layer.refresh()

    def flip(self, index, axis, center=None):
        if self.propagate:
            self.interpolated_layer._data_view.flip(index, axis, center)
        super().flip(index, axis, center)
        if self.propagate:
            self.interpolated_layer.refresh()

    def transform(self, index, transform):
        if self.propagate:
            self.interpolated_layer._data_view.transform(
                index, transform.copy()
            )
        super().transform(index, transform.copy())
        if self.propagate:
            self.interpolated_layer.refresh()

    def update_z_index(self, index, z_index):
        if self.propagate:
            self.interpolated_layer._data_view.update_z_index(index, z_index)
        super().update_z_index(index, z_index)
        if self.propagate:
            self.interpolated_layer.refresh()
