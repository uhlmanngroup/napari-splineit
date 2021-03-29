import sys
import napari
from .napari_splineit import start_napari_splineit


def main():
    fns = sys.argv[1:]
    viewer = napari.Viewer()
    if len(fns) > 0:
        viewer.open(fns, stack=False)
    viewer.window.add_dock_widget(napari_splineit(), area='right')
    napari.run()


if __name__ == '__main__':
    main()
