try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"


from ._sample_data import make_sample_data_coins  # noqa: F401
from ._widget import SplineitQWidget  # noqa: F401
from ._reader import get_reader  # noqa: F401
