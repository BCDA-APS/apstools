import pytest

from ..image_analysis import analyze_1D
from ..image_analysis import analyze_2D


@pytest.mark.parametrize(
    "data, expected, ndigits",
    [
        [
            # fmt: off
            dict(
                x=[.1, .2, .3, .4, .5, .6, .7, .8, .9, 1.0, 1.1],
                y=[0, 1, 2, 3, 4, 5, 4, 3, 2, 1, 0]
            ),
            # fmt: on
            dict(
                n=11,
                centroid=0.6,
                sigma=0.2,
                max_y=5,
                min_y=0,
                min_x=0.1,
                max_x=1.1,
                x_at_max_y=0.6,
                mean_x=0.6,
                mean_y=2.2727,
                stddev_x=0.33166,
                stddev_y=1.6787,
                correlation=0,
                intercept=2.2727,
                slope=0,
            ),
            4,
        ],
        [
            # fmt: off
            dict(
                y=[0, 1, 2, 3, 4, 5, 4, 3, 2, 1, 0]
            ),
            # fmt: on
            dict(
                n=11,
                mean_x=5.0,
                mean_y=2.2727,
                stddev_x=3.3166,
                stddev_y=1.6787,
                slope=0.0,
                intercept=2.2727,
                correlation=0.0,
                centroid=5.0,
                sigma=2.0,
                min_x=1,
                max_x=10,
                min_y=0,
                max_y=5,
                x_at_max_y=5,
            ),
            4,
        ],
        [
            dict(y=[0, 1, 0]),
            dict(
                n=3,
                centroid=1,
                sigma=0,
                max_y=1,
                min_y=0,
                min_x=1,
                max_x=2,
                x_at_max_y=1,
                mean_x=1,
                mean_y=1 / 3,
                stddev_x=1,
                stddev_y=0.58,
                correlation=0,
                intercept=0.33,
                slope=0,
            ),
            2,
        ],
    ],
)
def test_analyze_1D(data, expected, ndigits):
    x_arr = data.get("x")
    y_arr = data.get("y")
    results = analyze_1D(y_arr, x_arr)
    assert isinstance(results, dict)

    for k in expected.keys():
        # fmt: off
        assert (
            round(results[k], ndigits) == round(expected[k], ndigits)
        ), f"{k=} {results=} {expected=}"
        # fmt: on


@pytest.mark.parametrize(
    "data, expected, ndigits",
    [
        [
            dict(
                y=[
                    [0, 1, 2, 1, 0],
                    [1, 2, 3, 2, 1],
                    [2, 3, 4, 10, 2],
                    [1, 2, 3, 2, 1],
                ]
            ),
            dict(
                n=(5, 4),
                centroid=(2.1628, 1.8140),
                sigma=(1.1192, 0.8695),
                peak_position=(3, 2),
                max_y=10,
            ),
            4,
        ],
        [
            dict(
                y=[
                    [0, 100, 0],
                    [0, 0, 0],
                ]
            ),
            dict(
                n=(3, 2),
                centroid=(1, 0),
                sigma=(0, 0),
                peak_position=(1, 0),
                max_y=100,
            ),
            1,
        ],
    ],
)
def test_analyze_2D(data, expected, ndigits):
    image = data.get("y")
    results = analyze_2D(image)
    assert isinstance(results, dict)

    def compare_tuples(a, b, label):
        assert len(a) == len(b), label
        for r, e in zip(a, b):
            assert round(r, ndigits) == round(e, ndigits), label

    for k in expected.keys():
        assert k in results, k
        if isinstance(results[k], tuple):
            compare_tuples(results[k], expected[k], f"{k=} {results=}")
        else:
            assert round(results[k], ndigits) == round(expected[k], ndigits), results
