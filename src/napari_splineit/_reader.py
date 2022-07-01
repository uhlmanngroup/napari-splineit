import json

import numpy
from napari.components.viewer_model import ViewerModel

from .interpolation import interpolator_factory
from .layer.layer_factory import layer_factory


def get_reader(path):
    # If we recognize the format, we return the actual reader function
    if isinstance(path, str) and path.endswith(".splineit"):
        return splineit_file_reader
    # otherwise we return None.
    return None


def splineit_file_reader(path):

    with open(path) as f:
        raw_data = json.load(f)

    # the data
    list_of_polygons = raw_data["data"]
    list_of_polygons = [numpy.array(p) for p in list_of_polygons]

    # the interpolator arguments
    name = raw_data["method"]["name"]
    kwargs = raw_data["method"]["args"]
    interpolator = interpolator_factory(name=name, **kwargs)

    # additional optional arguments
    layer_attributes = {"interpolator": interpolator}

    if "opacity" in raw_data:
        layer_attributes["opacity"] = float(raw_data["opacity"])

    if "z_index" in raw_data:
        # ! important ! napari only accepts a list of ints as z_index
        # but not a numpy array
        layer_attributes["z_index"] = raw_data["z_index"]

    if "edge_width" in raw_data:
        layer_attributes["edge_width"] = raw_data["edge_width"]

    if "edge_color" in raw_data:
        layer_attributes["edge_color"] = numpy.array(
            raw_data["edge_color"], dtype="float32"
        )

    if "face_color" in raw_data:
        layer_attributes["face_color"] = numpy.array(
            raw_data["face_color"], dtype="float32"
        )

    print("layer_attributes", layer_attributes)

    return [(list_of_polygons, layer_attributes, "splineit_ctrl")]


# Supporting Napari readers with a custom layer  is a bit hacky:
#  - Napari assumes that the layer is in the namespace of `napari.layers`.
#    (this "monkeypatching" is done in `_ctrl_layer.py`)
#  - The small-cased name of the layer is in `napari.layers.NAMES`.
#  - There is a method add_<layer-name> (ie add_splineit_ctrl)
#    in the viewer class. (this "monkeypatching" is done in `_ctrl_layer.py`)
#  - We use the name `Splineit_Ctrl` instead of just `CtrlPtrLayer`
#    to avoid any name clashes.
def _add_methods():
    def add_splineit_ctrl(
        self,
        data,
        name,
        interpolator,
        edge_color=None,
        face_color=None,
        edge_width=None,
        z_index=None,
        opacity=None,
    ):
        interpolated_layer, ctrl_layer = layer_factory(
            viewer=self,
            data=data,
            interpolator=interpolator,
            ctrl_layer_name=f"{name}",
            interpolated_layer_name=f"{name}-IP",
            edge_color=edge_color,
            face_color=face_color,
            edge_width=edge_width,
            z_index=z_index,
            opacity=opacity,
        )
        return interpolated_layer, ctrl_layer

    ViewerModel.add_splineit_ctrl = add_splineit_ctrl


# do the monkey patching and delte method after that
_add_methods()
del _add_methods
