"""
Cognifi AI - Capture and Feature Extraction Module (Friend 1)
"""

from .adapter import TSharkCapture, normalize_packet
from .feature_window import FeatureExtractor, feature_dict_to_vector, FEATURE_NAMES

__all__ = [
    "TSharkCapture",
    "normalize_packet",
    "FeatureExtractor",
    "feature_dict_to_vector",
    "FEATURE_NAMES",
]