from .cubic import CubicInterpolator
from .spline import SplineInterpolator
from .uhlmann import UhlmannSplines


registered_interplators = {
    CubicInterpolator.name: CubicInterpolator,
    SplineInterpolator.name: SplineInterpolator,
    UhlmannSplines.name: UhlmannSplines,
}


def interpolator_factory(name, **kwargs):
    return registered_interplators[name](**kwargs)
