import tempfile
import types
import unittest
import contextlib
import io
from pathlib import Path

import numpy as np

from ml import data_io


class DataIOTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.sequences_dir = Path(self.tmp.name) / "secuencias"
        self.sequences_dir.mkdir()
        self.previous_config = data_io.config
        data_io.config = types.SimpleNamespace(
            SEQUENCES_DIR=str(self.sequences_dir),
            FRAMES_PER_SEQUENCE=10,
            FEATURES=147,
        )

    def tearDown(self):
        data_io.config = self.previous_config
        self.tmp.cleanup()

    def _write_sequence(self, clase, filename, shape):
        folder = self.sequences_dir / clase
        folder.mkdir(exist_ok=True)
        sequence = np.arange(np.prod(shape), dtype=np.float64).reshape(shape)
        np.save(folder / filename, sequence)
        return sequence

    def test_ajustar_frames_downsamples_old_30_frame_sequences(self):
        sequence = np.arange(30 * 147, dtype=np.float64).reshape(30, 147)

        adjusted = data_io.ajustar_frames(sequence)

        self.assertEqual(adjusted.shape, (10, 147))
        expected_indices = np.linspace(0, 29, 10).round().astype(int)
        np.testing.assert_array_equal(adjusted, sequence[expected_indices])

    def test_ajustar_frames_rejects_invalid_feature_count(self):
        invalid = np.zeros((10, 146), dtype=np.float64)

        with self.assertRaises(ValueError):
            data_io.ajustar_frames(invalid)

    def test_cargar_datos_returns_sorted_labels_and_resampled_sequences(self):
        self._write_sequence("b", "b_0.npy", (10, 147))
        self._write_sequence("a", "a_0.npy", (30, 147))
        self._write_sequence("a", "bad.npy", (10, 146))

        with contextlib.redirect_stdout(io.StringIO()):
            X, y, labels = data_io.cargar_datos()

        self.assertEqual(labels, ["a", "b"])
        self.assertEqual(X.shape, (2, 10, 147))
        np.testing.assert_array_equal(y, np.array([0, 1]))

    def test_cargar_datos_raises_when_directory_is_missing(self):
        data_io.config = types.SimpleNamespace(
            SEQUENCES_DIR=str(Path(self.tmp.name) / "missing"),
            FRAMES_PER_SEQUENCE=10,
            FEATURES=147,
        )

        with self.assertRaises(data_io.DatasetError):
            data_io.cargar_datos()


if __name__ == "__main__":
    unittest.main()
