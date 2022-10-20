import json


def write_splineit_json(path, data, attributes):

    interpolated_layer = attributes["metadata"]["interpolated_layer"]

    interpolator = attributes["metadata"]["interpolator"]

    return write_splineit(
        path=path,
        data=data,
        interpolator=interpolator,
        z_index=attributes["z_index"],
        edge_color=interpolated_layer.edge_color,
        face_color=interpolated_layer.face_color,
        edge_width=interpolated_layer.edge_width,
        opacity=interpolated_layer.opacity,
    )


def write_splineit(
    path,
    data,
    interpolator,
    z_index=None,
    edge_color=None,
    face_color=None,
    edge_width=None,
    opacity=None,
):
    def array2list(coordinates):
        return [list(coord) for coord in coordinates]

    json_data = [array2list(polygons) for polygons in data]

    name = type(interpolator).name
    args = interpolator.marshal()

    json_dict = {
        "data": json_data,
        "method": {"name": name, "args": args},
    }

    if z_index is not None:
        json_dict["z_index"] = [int(z) for z in z_index]

    if edge_color is not None:
        json_dict["edge_color"] = [list(color) for color in edge_color]

    if face_color is not None:
        json_dict["face_color"] = [list(color) for color in face_color]

    if edge_width is not None:
        json_dict["edge_width"] = [float(w) for w in edge_width]

    if opacity is not None:
        json_dict["opacity"] = float(opacity)

    with open(path, "w") as f:
        json.dump(json_dict, f, indent=4)

    return path
