from napari.utils.events import Event

from ._interpolated_layer import InterpolatedLayer
from ._ctrl_layer import CtrlPtrLayer


def layer_factory(
    viewer,
    interpolator,
    data=None,
    ctrl_layer_name="CtrLayer",
    interpolated_layer_name="Interpolated",
    edge_color=None,
    face_color=None,
    edge_width=None,
    z_index=None,
    opacity=None,
):

    if opacity is None:
        opacity = 0.7
    interpolated_layer = InterpolatedLayer(
        name=interpolated_layer_name, opacity=opacity
    )
    viewer.add_layer(interpolated_layer)

    ctrl_layer = CtrlPtrLayer(
        name=ctrl_layer_name,
        metadata={
            "interpolator": interpolator,
            "interpolated_layer": interpolated_layer,
        },
        interpolator=interpolator,
        interpolated_layer=interpolated_layer,
    )

    viewer.add_layer(ctrl_layer)

    if data is not None:
        ctrl_layer.add_polygons(data=data)

        if z_index is not None:
            # z-index changes are automatically
            # updated in the interpolated layer
            ctrl_layer.z_index = z_index

        if edge_color is not None:
            interpolated_layer.edge_color = edge_color

        if face_color is not None:
            interpolated_layer.face_color = face_color

        if edge_width is not None:
            interpolated_layer.edge_width = edge_width

    # if either of the layers is deleted
    # we also delete the other one
    def on_removed(event: Event):
        layer = event.value
        if layer == interpolated_layer:
            if ctrl_layer in viewer.layers:
                viewer.layers.remove(ctrl_layer)
        elif layer == ctrl_layer:
            if interpolated_layer in viewer.layers:
                viewer.layers.remove(interpolated_layer)

    viewer.layers.events.removed.connect(on_removed)

    return interpolated_layer, ctrl_layer
