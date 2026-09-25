"""LeafLens — field-ready crop health screening with Streamlit."""

from __future__ import annotations

import html
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
from PIL import Image, UnidentifiedImageError

from scripts.inference import AnalysisResult, analyse, display_label
from scripts.knowledge_base import GUIDANCE


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
MODEL_CONFIG = {
    "Paddy rice": {
        "key": "paddy",
        "eyebrow": "10 field conditions",
        "model": PROJECT_ROOT / "model" / "paddy_model" / "paddy_model.h5",
        "metrics": PROJECT_ROOT / "model" / "paddy_model" / "metrics.json",
    },
    "Tea": {
        "key": "tea",
        "eyebrow": "8 leaf conditions",
        "model": PROJECT_ROOT / "model" / "tea_model" / "tea_model.h5",
        "metrics": PROJECT_ROOT / "model" / "tea_model" / "metrics.json",
    },
}


st.set_page_config(
    page_title="LeafLens — Crop health, clearly seen",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ink: #183229;
            --muted: #5f6f68;
            --leaf: #1f6b49;
            --leaf-dark: #124431;
            --lime: #cfe66b;
            --paper: #f5f1e7;
            --cream: #fffdf7;
            --line: rgba(24, 50, 41, 0.16);
        }
        html { scroll-behavior: smooth; }
        [data-testid="stAppViewContainer"] {
            color: var(--ink);
            background:
                linear-gradient(rgba(31,107,73,.045) 1px, transparent 1px),
                linear-gradient(90deg, rgba(31,107,73,.045) 1px, transparent 1px),
                var(--paper);
            background-size: 32px 32px;
        }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stToolbar"] { right: 1rem; }
        .block-container { max-width: 1180px; padding-top: 1.1rem; padding-bottom: 5rem; }
        h1, h2, h3, .display-face { font-family: Georgia, 'Times New Roman', serif !important; color: var(--ink); }
        p, label, button, input, [data-testid="stMarkdownContainer"] { font-family: 'Trebuchet MS', 'Segoe UI', sans-serif; }

        .topbar { display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--line); padding:.55rem 0 1rem; }
        .brand { display:flex; align-items:center; gap:.7rem; font-weight:800; letter-spacing:-.02em; font-size:1.08rem; }
        .brand-mark { display:grid; place-items:center; width:34px; height:34px; border-radius:50% 8px 50% 8px; background:var(--leaf); color:white; transform:rotate(-8deg); }
        .status { display:flex; align-items:center; gap:.5rem; color:var(--muted); font-size:.82rem; }
        .status-dot { width:8px; height:8px; border-radius:50%; background:#5daa72; box-shadow:0 0 0 4px rgba(93,170,114,.15); }

        .hero { padding:4.6rem 0 2.3rem; max-width:940px; }
        .kicker { display:inline-flex; gap:.55rem; align-items:center; color:var(--leaf-dark); font-size:.75rem; font-weight:800; letter-spacing:.14em; text-transform:uppercase; }
        .kicker:before { content:''; width:30px; height:2px; background:var(--leaf); }
        .hero h1 { font-size:clamp(3.1rem, 8vw, 6.8rem); line-height:.88; letter-spacing:-.065em; margin:.8rem 0 1.2rem; max-width:900px; }
        .hero h1 em { color:var(--leaf); font-weight:400; }
        .hero-copy { max-width:650px; color:var(--muted); font-size:1.08rem; line-height:1.75; }
        .trust-row { display:flex; flex-wrap:wrap; gap:.7rem 1.4rem; margin-top:1.6rem; color:var(--ink); font-size:.82rem; font-weight:700; }
        .trust-row span:before { content:'✓'; color:var(--leaf); margin-right:.45rem; }

        .step-label { color:var(--leaf); text-transform:uppercase; letter-spacing:.14em; font-weight:800; font-size:.72rem; margin-bottom:.4rem; }
        .section-title { margin:.1rem 0 .35rem; font-size:2rem; letter-spacing:-.035em; }
        .section-copy { color:var(--muted); margin-bottom:1.2rem; }

        .st-key-diagnostic [data-testid="stVerticalBlockBorderWrapper"] { background:rgba(255,253,247,.94); border:1px solid var(--line); border-radius:24px; padding:1.25rem; box-shadow:0 24px 70px rgba(24,50,41,.09); }
        .scan-label { color:var(--muted); font-size:.66rem; letter-spacing:.16em; padding:.05rem 0 .35rem; }
        [data-baseweb="select"] > div, [data-testid="stFileUploaderDropzone"] { background:var(--cream) !important; border-color:var(--line) !important; }
        [data-testid="stFileUploaderDropzone"] { border:1.5px dashed rgba(31,107,73,.42) !important; border-radius:16px; padding:1.15rem; }
        [data-testid="stFileUploaderDropzone"] small { color:var(--muted); }
        [data-testid="stImage"] img { border-radius:16px; border:1px solid var(--line); }
        .stButton > button, .stDownloadButton > button {
            min-height:3rem; border-radius:999px; border:1px solid var(--leaf) !important;
            background:var(--leaf) !important; color:white !important; font-weight:800;
            transition:transform .18s ease, box-shadow .18s ease, background .18s ease;
        }
        .stButton > button:hover, .stDownloadButton > button:hover { transform:translateY(-2px); box-shadow:0 10px 24px rgba(31,107,73,.2); background:var(--leaf-dark) !important; }
        .stButton > button:focus-visible, .stDownloadButton > button:focus-visible { outline:3px solid var(--lime) !important; outline-offset:2px; }

        .tip-card { border-top:1px solid var(--line); padding-top:1rem; color:var(--muted); font-size:.82rem; line-height:1.6; }
        .tip-card strong { color:var(--ink); display:block; margin-bottom:.25rem; }

        .result-card { background:var(--ink); color:white; border-radius:20px; padding:1.5rem; position:relative; overflow:hidden; min-height:100%; }
        .result-card:after { content:'✦'; position:absolute; right:-.6rem; top:-2.7rem; font-size:9rem; color:rgba(207,230,107,.08); }
        .result-card .overline { color:var(--lime); font-size:.7rem; font-weight:800; letter-spacing:.15em; text-transform:uppercase; }
        .result-card h2 { color:white; font-size:clamp(2rem,4vw,3.5rem); line-height:1; margin:.55rem 0 .9rem; max-width:90%; }
        .confidence { display:flex; align-items:baseline; gap:.55rem; margin:.3rem 0 1rem; }
        .confidence strong { color:var(--lime); font-family:Georgia,serif; font-size:2rem; }
        .confidence span { color:rgba(255,255,255,.64); font-size:.78rem; }
        .summary { color:rgba(255,255,255,.76); line-height:1.65; font-size:.9rem; }
        .uncertain { background:#fff4dc; color:#6e431d; border:1px solid #ebcd96; border-radius:12px; padding:.85rem 1rem; margin:.8rem 0; font-size:.85rem; }

        .action-card { border:1px solid var(--line); background:var(--cream); border-radius:16px; padding:1rem 1.05rem; margin-bottom:.7rem; min-height:76px; }
        .action-num { color:var(--leaf); font-weight:900; margin-right:.55rem; }
        .rank-row { margin:.85rem 0; }
        .rank-meta { display:flex; justify-content:space-between; font-size:.78rem; margin-bottom:.3rem; color:var(--muted); }
        .rank-track { height:7px; border-radius:20px; background:#e4e4d9; overflow:hidden; }
        .rank-fill { height:100%; border-radius:20px; background:var(--leaf); }

        .model-note { display:grid; grid-template-columns:repeat(3,1fr); border-top:1px solid var(--line); border-bottom:1px solid var(--line); margin-top:4rem; }
        .model-note > div { padding:1.25rem; border-right:1px solid var(--line); }
        .model-note > div:last-child { border-right:0; }
        .model-note strong { display:block; font-family:Georgia,serif; font-size:1.5rem; margin-bottom:.2rem; }
        .model-note span { color:var(--muted); font-size:.76rem; }
        .disclaimer { color:var(--muted); font-size:.75rem; line-height:1.65; padding-top:1.1rem; }

        @media (max-width: 720px) {
            .block-container { padding: .7rem 1rem 3rem; }
            .hero { padding:3.2rem 0 1.7rem; }
            .hero h1 { font-size:3.45rem; }
            .st-key-diagnostic [data-testid="stVerticalBlockBorderWrapper"] { padding:.8rem; border-radius:18px; }
            .model-note { grid-template-columns:1fr; }
            .model-note > div { border-right:0; border-bottom:1px solid var(--line); }
            .model-note > div:last-child { border-bottom:0; }
            .status span:last-child { display:none; }
        }
        @media (prefers-reduced-motion: no-preference) {
            .hero > * { animation:rise .55s both; }
            .hero h1 { animation-delay:.08s; }
            .hero-copy { animation-delay:.15s; }
            .trust-row { animation-delay:.22s; }
            @keyframes rise { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:none; } }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource(show_spinner=False)
def load_model_and_metrics(model_key: str):
    config = next(item for item in MODEL_CONFIG.values() if item["key"] == model_key)
    if not config["model"].exists() or not config["metrics"].exists():
        raise FileNotFoundError(f"Missing model assets for {model_key}.")

    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
    import tensorflow as tf

    model = tf.keras.models.load_model(config["model"], compile=False)
    with config["metrics"].open(encoding="utf-8-sig") as metrics_file:
        metrics = json.load(metrics_file)
    return model, metrics


def safe_image(uploaded_file) -> Image.Image | None:
    if uploaded_file is None:
        return None
    try:
        image = Image.open(uploaded_file)
        image.verify()
        uploaded_file.seek(0)
        return Image.open(uploaded_file)
    except (UnidentifiedImageError, OSError, ValueError):
        st.error("That file does not appear to be a readable JPG or PNG image.")
        return None


def percentage(value: float) -> str:
    return f"{value * 100:.1f}%"


def render_rank(label: str, confidence: float) -> None:
    clean_label = html.escape(display_label(label))
    width = max(2, min(100, confidence * 100))
    st.markdown(
        f"""
        <div class="rank-row">
          <div class="rank-meta"><span>{clean_label}</span><strong>{percentage(confidence)}</strong></div>
          <div class="rank-track"><div class="rank-fill" style="width:{width:.1f}%"></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def report_text(crop: str, result: AnalysisResult, guidance: dict) -> str:
    lines = [
        "LEAFLENS FIELD SCREENING REPORT",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"Crop: {crop}",
        f"Screening result: {display_label(result.primary.label)}",
        f"Model confidence: {percentage(result.primary.confidence)}",
        f"Needs confirmation: {'Yes' if result.is_uncertain else 'No'}",
        "",
        "What the label means",
        guidance["summary"],
        "",
        "Suggested next checks",
        *[f"{index}. {action}" for index, action in enumerate(guidance["actions"], 1)],
        "",
        "Important: This is an AI screening result, not a laboratory diagnosis. Confirm before treatment and follow local product labels and agricultural guidance.",
    ]
    return "\n".join(lines)


def render_result(crop: str, crop_key: str, result: AnalysisResult) -> None:
    guidance = GUIDANCE[crop_key][result.primary.label]
    diagnosis = html.escape(display_label(result.primary.label))
    certainty_label = "Check recommended" if result.is_uncertain else "Clear model signal"

    st.markdown("<div style='height:1.1rem'></div>", unsafe_allow_html=True)
    left, right = st.columns([1.05, 1], gap="large")
    with left:
        st.markdown(
            f"""
            <div class="result-card">
              <div class="overline">{html.escape(crop)} · {certainty_label}</div>
              <h2>{diagnosis}</h2>
              <div class="confidence"><strong>{percentage(result.primary.confidence)}</strong><span>model confidence</span></div>
              <p class="summary">{html.escape(guidance['summary'])}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if result.is_uncertain:
            st.markdown(
                "<div class='uncertain'><strong>Do not treat from this scan alone.</strong> "
                "The result is low-confidence or close to another class. Retake the photo and seek an agronomist's confirmation.</div>",
                unsafe_allow_html=True,
            )

    with right:
        st.markdown("<div class='step-label'>Next checks</div><h3 class='section-title'>Act with care</h3>", unsafe_allow_html=True)
        for index, action in enumerate(guidance["actions"], 1):
            st.markdown(
                f"<div class='action-card'><span class='action-num'>{index:02}</span>{html.escape(action)}</div>",
                unsafe_allow_html=True,
            )

    with st.expander("See the model's top matches", expanded=False):
        render_rank(result.primary.label, result.primary.confidence)
        for prediction in result.alternatives:
            render_rank(prediction.label, prediction.confidence)

    st.download_button(
        "Download field report",
        report_text(crop, result, guidance),
        file_name=f"leaflens-{crop_key}-{datetime.now().strftime('%Y%m%d-%H%M')}.txt",
        mime="text/plain",
        use_container_width=False,
    )


inject_styles()

st.markdown(
    """
    <div class="topbar">
      <div class="brand"><span class="brand-mark">L</span><span>LeafLens</span></div>
      <div class="status"><span class="status-dot"></span><span>Models ready for field screening</span></div>
    </div>
    <section class="hero">
      <div class="kicker">AI crop health screening</div>
      <h1>See the signal<br>in every <em>leaf.</em></h1>
      <p class="hero-copy">Screen paddy and tea leaves for visible disease patterns, understand the model's confidence, and leave with practical next checks—not a mysterious score.</p>
      <div class="trust-row"><span>18 trained classes</span><span>Real confidence scores</span><span>Private, session-only images</span></div>
    </section>
    """,
    unsafe_allow_html=True,
)

with st.container(key="diagnostic", border=True):
    st.markdown("<div class='scan-label'>FIELD SCAN / 01</div>", unsafe_allow_html=True)
    selector_col, upload_col = st.columns([0.78, 1.35], gap="large")

    with selector_col:
        st.markdown("<div class='step-label'>Step 01</div><h2 class='section-title'>Choose the crop</h2><p class='section-copy'>Select the model that matches the photographed leaf.</p>", unsafe_allow_html=True)
        crop = st.selectbox(
            "Crop model",
            options=list(MODEL_CONFIG),
            label_visibility="collapsed",
        )
        config = MODEL_CONFIG[crop]
        st.caption(f"{config['eyebrow']} · trained model accuracy ≈ 82% on held-out data")
        st.markdown(
            """
            <div class="tip-card">
              <strong>For a useful scan</strong>
              Photograph one leaf in natural light. Keep the symptom sharp, fill most of the frame, and avoid fingers or tools covering the affected area.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with upload_col:
        st.markdown("<div class='step-label'>Step 02</div><h2 class='section-title'>Add a clear leaf photo</h2><p class='section-copy'>JPG or PNG · up to 10 MB recommended</p>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload a leaf photograph",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=False,
            label_visibility="collapsed",
        )
        image = safe_image(uploaded_file)
        if image is not None:
            preview_col, button_col = st.columns([0.58, 1], gap="medium")
            with preview_col:
                st.image(image, caption=f"{image.width} × {image.height} px", use_container_width=True)
            with button_col:
                st.write("Ready to screen")
                st.caption("Analysis runs only after you press the button. The first scan may take a moment while the selected model loads.")
                analyse_clicked = st.button("Analyze leaf", type="primary", use_container_width=True)
        else:
            analyse_clicked = False

if analyse_clicked and image is not None:
    try:
        with st.spinner("Reading leaf patterns…"):
            model, metrics = load_model_and_metrics(config["key"])
            result = analyse(model, metrics["class_names"], image)
        render_result(crop, config["key"], result)
    except FileNotFoundError:
        st.error("The selected model file is not available on this deployment. Check the deployment guide in the README.")
    except Exception as exc:
        st.error("The scan could not be completed. Try a different image or restart the app.")
        with st.expander("Technical details"):
            st.code(str(exc))

st.markdown(
    """
    <div class="model-note">
      <div><strong>10</strong><span>Paddy conditions</span></div>
      <div><strong>8</strong><span>Tea conditions</span></div>
      <div><strong>224px</strong><span>Model input size</span></div>
    </div>
    <p class="disclaimer"><strong>Responsible-use note:</strong> LeafLens is an image-screening aid, not a laboratory test or a replacement for an agronomist. Similar symptoms can have different causes. Confirm uncertain or high-impact results before applying pesticides, and always follow local regulations and product labels.</p>
    """,
    unsafe_allow_html=True,
)
