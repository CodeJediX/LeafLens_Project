"""Export the two Keras classifiers as browser-friendly TFLite models."""

from pathlib import Path

import tensorflow as tf


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "models"


def export(source: Path, destination: Path) -> None:
    model = tf.keras.models.load_model(source, compile=False)

    fixed_input = tf.keras.Input(batch_shape=(1, 224, 224, 3), dtype=tf.float32)
    fixed_model = tf.keras.Model(fixed_input, model(fixed_input, training=False))
    converter = tf.lite.TFLiteConverter.from_keras_model(fixed_model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converted = converter.convert()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(converted)
    print(f"{destination.name}: {len(converted) / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    export(
        ROOT / "model" / "paddy_model" / "paddy_model.h5",
        OUTPUT / "paddy.tflite",
    )
    export(
        ROOT / "model" / "tea_model" / "tea_model.h5",
        OUTPUT / "tea.tflite",
    )
