"""Image preparation and prediction utilities for LeafLens.

This module deliberately has no Streamlit or TensorFlow dependency. Keeping the
prediction math here makes it cheap to test and prevents presentation code from
silently changing model confidence values.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence

import numpy as np
from PIL import Image, ImageOps


class PredictiveModel(Protocol):
    def predict(self, image_batch: np.ndarray, verbose: int = 0) -> np.ndarray: ...


@dataclass(frozen=True)
class Prediction:
    label: str
    confidence: float


@dataclass(frozen=True)
class AnalysisResult:
    primary: Prediction
    alternatives: tuple[Prediction, ...]
    is_uncertain: bool


def prepare_image(image: Image.Image, size: tuple[int, int] = (224, 224)) -> np.ndarray:
    """Return an orientation-corrected RGB image batch for the trained models."""
    clean_image = ImageOps.exif_transpose(image).convert("RGB")
    resized = clean_image.resize(size, Image.Resampling.LANCZOS)
    return np.expand_dims(np.asarray(resized, dtype=np.float32), axis=0)


def _softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - np.max(values)
    exponentials = np.exp(shifted)
    return exponentials / exponentials.sum()


def normalise_scores(raw_scores: np.ndarray) -> np.ndarray:
    """Use model probabilities as-is, applying softmax only to genuine logits.

    Both shipped LeafLens models already end in a softmax layer. The original
    application applied softmax a second time, which compressed every confidence
    score. This guard supports both probability- and logit-producing models.
    """
    scores = np.asarray(raw_scores, dtype=np.float64).reshape(-1)
    if not np.all(np.isfinite(scores)):
        raise ValueError("The model returned a non-finite prediction.")

    looks_like_probability = (
        np.all(scores >= 0)
        and np.all(scores <= 1)
        and np.isclose(scores.sum(), 1.0, atol=1e-3)
    )
    return scores / scores.sum() if looks_like_probability else _softmax(scores)


def analyse(
    model: PredictiveModel,
    class_names: Sequence[str],
    image: Image.Image,
    *,
    confidence_threshold: float = 0.55,
    margin_threshold: float = 0.12,
) -> AnalysisResult:
    """Run inference and flag results that are too close to call."""
    raw_output = model.predict(prepare_image(image), verbose=0)[0]
    probabilities = normalise_scores(raw_output)

    if len(probabilities) != len(class_names):
        raise ValueError(
            f"Model returned {len(probabilities)} scores for {len(class_names)} classes."
        )

    top_indices = np.argsort(probabilities)[::-1][:3]
    predictions = tuple(
        Prediction(label=class_names[index], confidence=float(probabilities[index]))
        for index in top_indices
    )
    runner_up = predictions[1].confidence if len(predictions) > 1 else 0.0
    uncertain = (
        predictions[0].confidence < confidence_threshold
        or predictions[0].confidence - runner_up < margin_threshold
    )
    return AnalysisResult(
        primary=predictions[0], alternatives=predictions[1:], is_uncertain=uncertain
    )


def display_label(label: str) -> str:
    """Convert training labels to consistent, human-readable names."""
    return label.replace("_", " ").strip().title()
