"""@package senml
Top-level namespace for the senml module
"""

# pylint: disable=too-few-public-methods

from .senml import SenMLDocument, SenMLMeasurement

from pkg_resources import get_distribution

__version__ = get_distribution('senml').version

__all__ = [
    'SenMLDocument',
    'SenMLMeasurement',
]
