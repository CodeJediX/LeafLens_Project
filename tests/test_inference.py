import json
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from scripts.inference import analyse, display_label, normalise_scores, prepare_image
from scripts.knowledge_base import GUIDANCE


class FakeModel:
    def __init__(self, scores):
        self.scores = np.asarray([scores], dtype=np.float32)

    def predict(self, image_batch, verbose=0):
        self.batch_shape = image_batch.shape
        return self.scores


class InferenceTests(unittest.TestCase):
    def test_existing_probabilities_are_not_softmaxed_twice(self):
        scores = np.array([0.82, 0.12, 0.06])
        np.testing.assert_allclose(normalise_scores(scores), scores, atol=1e-8)

    def test_logits_receive_stable_softmax(self):
        probabilities = normalise_scores(np.array([1001.0, 1000.0]))
        np.testing.assert_allclose(probabilities.sum(), 1.0)
        self.assertGreater(probabilities[0], probabilities[1])

    def test_grayscale_images_become_rgb_batches(self):
        batch = prepare_image(Image.new("L", (80, 50), color=120))
        self.assertEqual(batch.shape, (1, 224, 224, 3))
        self.assertEqual(batch.dtype, np.float32)

    def test_close_predictions_are_flagged_for_confirmation(self):
        model = FakeModel([0.48, 0.43, 0.09])
        result = analyse(model, ["blast", "brown_spot", "normal"], Image.new("RGB", (20, 20)))
        self.assertEqual(result.primary.label, "blast")
        self.assertTrue(result.is_uncertain)
        self.assertEqual(model.batch_shape, (1, 224, 224, 3))

    def test_clear_prediction_keeps_true_confidence(self):
        result = analyse(
            FakeModel([0.81, 0.11, 0.08]),
            ["healthy", "white_spot", "anthracnose"],
            Image.new("RGB", (20, 20)),
        )
        self.assertAlmostEqual(result.primary.confidence, 0.81, places=6)
        self.assertFalse(result.is_uncertain)

    def test_display_label(self):
        self.assertEqual(display_label("bacterial_leaf_blight"), "Bacterial Leaf Blight")

    def test_every_model_class_has_field_guidance(self):
        root = Path(__file__).resolve().parents[1]
        for crop, metrics_path in {
            "paddy": root / "model" / "paddy_model" / "metrics.json",
            "tea": root / "model" / "tea_model" / "metrics.json",
        }.items():
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            self.assertEqual(set(metrics["class_names"]), set(GUIDANCE[crop]))


if __name__ == "__main__":
    unittest.main()
