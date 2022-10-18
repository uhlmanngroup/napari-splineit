from napari.utils.events import Event

from ._interpolated_layer import InterpolatedLayer
from ._ctrl_layer import CtrlLayer

import numpy as np


def layer_factory(
    viewer,
    interpolator,
    data=None,
    ctrl_layer_name="CtrLayer",
    interpolated_layer_name="Interpolated",
    edge_color=None,
    face_color=None,
    current_edge_color=None,
    current_face_color=None,
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

    ctrl_layer = CtrlLayer(
        name=ctrl_layer_name,
        metadata={
            "interpolator": interpolator,
            "interpolated_layer": interpolated_layer,
        },
        interpolator=interpolator,
        interpolated_layer=interpolated_layer,
    )

    print("add layer")
    viewer.add_layer(ctrl_layer)
    print("DONE")

    if data is not None:

        print("SUB")
        ctrl_layer.add(
            data=data,
            interpolated_layer_kwargs=dict(
                edge_color=edge_color,
                face_color=face_color,
                edge_width=edge_width,
            ),
        )
        if current_edge_color is not None:
            interpolated_layer.current_edge_color = current_edge_color
        if current_face_color is not None:
            interpolated_layer.current_face_color = current_face_color

        if z_index is not None:
            ctrl_layer.z_index = z_index

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
