from napari_splineit import SplineitQWidget


# this test just checks if the widget can be instantiated
def test_splinit_widget(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    widget = SplineitQWidget(viewer)
    assert isinstance(widget, SplineitQWidget)
