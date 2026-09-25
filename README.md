# LeafLens

LeafLens is a field-friendly AI screening app for visible paddy and tea leaf conditions. Upload a clear photograph, select the crop, and receive the model's top match, its real confidence score, alternative matches, and practical next checks.

**Live app:** [codejedix.github.io/LeafLens_Project](https://codejedix.github.io/LeafLens_Project/)

The hosted edition uses LiteRT to run the selected model inside the visitor's browser. Leaf photos stay on the device and no application server is required.

> LeafLens is a screening aid—not a laboratory diagnosis or a substitute for an agronomist. Confirm uncertain or high-impact results before treatment.

## What changed in v2

- Rebuilt the interface as a responsive, accessible field workflow.
- Fixed a double-softmax bug that compressed prediction scores.
- Removed the artificial `+70%` confidence inflation.
- Added uncertainty detection based on both confidence and top-two margin.
- Correctly handles EXIF rotation, grayscale images, and RGB conversion.
- Added top-three model matches and downloadable field reports.
- Rewrote recommendations to avoid presenting chemical treatment as certain.
- Delayed TensorFlow loading until analysis, improving first render time.
- Reduced production dependencies from a full notebook environment to four direct packages.
- Added unit tests, CI, a non-root Docker image, health checks, and Streamlit configuration.
- Added a browser-native GitHub Pages edition with quantized on-device models.

## Supported classes

| Crop | Classes | Reported validation accuracy |
| --- | ---: | ---: |
| Paddy rice | 10 | 81.98% |
| Tea | 8 | 81.92% |

Accuracy is taken from the saved training metadata. It does not guarantee performance on every phone, region, cultivar, growth stage, or lighting condition.

## Run locally

Python 3.11 is recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

The application expects these tracked model files:

```text
model/paddy_model/paddy_model.h5
model/tea_model/tea_model.h5
```

## Run with Docker

```bash
docker build -t leaflens .
docker run --rm -p 8501:8501 leaflens
```

Open `http://localhost:8501`.

## Deploy on Streamlit Community Cloud

1. Push the repository to GitHub.
2. Open [share.streamlit.io](https://share.streamlit.io/).
3. Choose this repository and branch.
4. Set the entry point to `streamlit_app.py`.
5. Deploy.

No secrets are required. The first prediction can be slower while TensorFlow and the selected model initialise.

## GitHub Pages deployment

The `docs/` directory contains the static hosted edition. Its two `.tflite` models are generated from the tracked Keras files with:

```bash
python scripts/export_tflite.py
```

GitHub Pages is configured to publish `docs/` from `main`. The first scan downloads only the selected crop model; later scans in the same visit reuse it.

## Test

The lightweight test suite does not load TensorFlow or the model weights:

```bash
python -m unittest discover -s tests -v
python -m compileall -q scripts streamlit_app.py
```

## Repository hygiene

The original repository committed the full training datasets, making clones unnecessarily large. New datasets are ignored by `.gitignore`; keep training data in object storage or a versioned dataset service and keep only source code, metrics, and deployable model artifacts in the product repository. Removing already-tracked datasets from Git history should be handled as a separate, coordinated migration because it rewrites repository history.

## Responsible use

- Use one sharp, well-lit leaf image with the symptom visible.
- Retake the image when confidence is low or top classes are close.
- Inspect several plants; one image does not represent an entire field.
- Confirm diagnoses before applying pesticides.
- Follow local regulations, product labels, and agricultural extension advice.
