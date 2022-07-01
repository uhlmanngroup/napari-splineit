from napari_splineit import make_sample_data_coins


def test_sample_data_coins():
    data = make_sample_data_coins()
    assert len(data) == 2
