import json


def write_splineit_json(path, data, attributes):
    def array2list(coordinates):
        return [list(coord) for coord in coordinates]

    # marshal the data
    json_data = [array2list(polygons) for polygons in data]

    # marshal the interpolator
    interpolator = attributes["metadata"]["interpolator"]
    name = type(interpolator).name
    args = interpolator.marshal()

    # additional properties which are optional when loading
    z_index = [int(z) for z in attributes["z_index"]]

    # properties we need to take from the interpolated layer
    interpolated_layer = attributes["metadata"]["interpolated_layer"]
    edge_color = [list(color) for color in interpolated_layer.edge_color]
    face_color = [list(color) for color in interpolated_layer.face_color]
    edge_width = [float(w) for w in interpolated_layer.edge_width]
    opacity = interpolated_layer.opacity

    json_dict = {
        "data": json_data,
        "method": {"name": name, "args": args},
        "z_index": z_index,
        "edge_color": edge_color,
        "face_color": face_color,
        "edge_width": edge_width,
        "opacity": opacity,
    }

    with open(path, "w") as f:
        json.dump(json_dict, f, indent=4)

    return path
