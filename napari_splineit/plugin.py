from napari_plugin_engine import napari_hook_implementation
from .napari_splineit import napari_splineit


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    return napari_splineit
