import types
import unittest

import numpy as np

from core.config import config
from core.landmarks import (
    extract_holistic_landmarks,
    normalize_landmarks,
    validate_landmarks,
)


def _landmark(x, y, z):
    return types.SimpleNamespace(x=x, y=y, z=z)


def _landmark_list(count, offset=0.0):
    return types.SimpleNamespace(
        landmark=[
            _landmark(offset + i / 100.0, offset + i / 200.0, offset + i / 300.0)
            for i in range(count)
        ]
    )


class LandmarksTestCase(unittest.TestCase):
    def test_extract_returns_fixed_length_vector_when_every_region_exists(self):
        results = types.SimpleNamespace(
            left_hand_landmarks=_landmark_list(21, 0.1),
            right_hand_landmarks=_landmark_list(21, 0.2),
            pose_landmarks=_landmark_list(33, 0.3),
            face_landmarks=_landmark_list(300, 0.4),
        )

        vector = extract_holistic_landmarks(results)

        self.assertEqual(vector.shape, (config.FEATURES,))
        self.assertTrue(validate_landmarks(vector))

    def test_extract_fills_missing_regions_with_zeros(self):
        results = types.SimpleNamespace(
            left_hand_landmarks=None,
            right_hand_landmarks=None,
            pose_landmarks=None,
            face_landmarks=None,
        )

        vector = extract_holistic_landmarks(results)

        self.assertEqual(vector.shape, (config.FEATURES,))
        self.assertTrue(np.allclose(vector, 0))
        self.assertFalse(validate_landmarks(vector))

    def test_normalize_preserves_shape_and_rejects_bad_inputs(self):
        landmarks = np.arange(config.FEATURES, dtype=np.float64)

        normalized = normalize_landmarks(landmarks)

        self.assertEqual(normalized.shape, (config.FEATURES,))
        self.assertFalse(np.any(np.isnan(normalized)))
        self.assertIsNone(normalize_landmarks(None))
        self.assertEqual(len(normalize_landmarks(np.zeros(3))), 3)

    def test_validate_rejects_nan_inf_and_wrong_length(self):
        valid = np.ones(config.FEATURES, dtype=np.float64)
        with_nan = valid.copy()
        with_nan[0] = np.nan
        with_inf = valid.copy()
        with_inf[0] = np.inf

        self.assertTrue(validate_landmarks(valid))
        self.assertFalse(validate_landmarks(with_nan))
        self.assertFalse(validate_landmarks(with_inf))
        self.assertFalse(validate_landmarks(np.ones(config.FEATURES - 1)))


if __name__ == "__main__":
    unittest.main()
