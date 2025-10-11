import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np
import json
import os
import base64
import pandas as pd
from streamlit_lottie import st_lottie
import time

# --- Configuration ---
CONFIDENCE_THRESHOLD = 10.0  # Percentage

# ==============================================================================
# --- ROBUST PATH DEFINITION ---
# This creates paths that work on any computer (Windows, Mac, Linux, or in Docker)
# ==============================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, '..')

# ==============================================================================
# --- PRE-LOADER FUNCTION ---
# ==============================================================================
def show_preloader():
    """Displays a pre-loader with the app logo for a few seconds."""
    logo_path = os.path.join(PROJECT_ROOT, 'assets', 'logo.png')
    
    if not os.path.exists(logo_path):
        st.warning("Preloader logo not found.")
        return

    logo_base64 = get_base64_of_bin_file(logo_path)
    preloader_html = f"""
    <style>
    @keyframes pulsate {{ 0% {{ transform: scale(1); opacity: 1; }} 50% {{ transform: scale(1.05); opacity: 0.9; }} 100% {{ transform: scale(1); opacity: 1; }} }}
    #preloader {{ position: fixed; top: 0; left: 0; width: 100%; height: 100vh; background-color: #000; display: flex; justify-content: center; align-items: center; z-index: 9999; }}
    #preloader img {{ max-width: 300px; animation: pulsate 2s ease-in-out infinite; }}
    </style>
    <div id="preloader"><img src="data:image/png;base64,{logo_base64}" alt="Loading..."></div>
    """
    preloader_container = st.empty()
    preloader_container.markdown(preloader_html, unsafe_allow_html=True)
    time.sleep(3)
    preloader_container.empty()

# ==============================================================================
# --- STYLING, ANIMATIONS, AND ASSET LOADING ---
# ==============================================================================
def load_lottiefile(filepath: str):
    """Loads a Lottie JSON file."""
    if not os.path.exists(filepath):
        st.warning(f"Lottie file not found at {filepath}")
        return None
    with open(filepath, "r") as f:
        return json.load(f)

def get_base64_of_bin_file(bin_file):
    """Encodes a binary file (like an image) to a Base64 string."""
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(image_file):
    """Sets the background of the Streamlit app and adds custom CSS."""
    base64_img = get_base64_of_bin_file(image_file)
    page_bg_img = f'''
    <style>
    .stApp {{ background-image: url("data:image/jpeg;base64,{base64_img}"); background-size: cover; background-repeat: no-repeat; background-attachment: fixed; }}
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(-20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    .main-content-block {{ background-color: rgba(240, 242, 246, 0.95); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 15px; padding: 2rem; margin: 1rem; box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37); animation: fadeIn 0.5s ease-in-out; }}
    .results-card {{ animation: fadeIn 0.7s ease-in-out; }}
    div.stButton > button {{ background-color: #28a745; color: white; border-radius: 5px; border: none; height: 3em; width: 100%; font-size: 1.1em; transition: background-color 0.3s ease; }}
    div.stButton > button:hover {{ background-color: #218838; }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

# ==============================================================================
# --- RECOMMENDATION DICTIONARIES ---
# ==============================================================================
PADDY_DISEASE_RECOMMENDATIONS = {
    "bacterial_leaf_blight": {
        "description": "Appears as water-soaked streaks on leaf edges that turn yellow and die. Can cause significant yield loss.",
        "recommendations": [
            "Use resistant rice varieties.",
            "Avoid excessive nitrogen fertilizer application.",
            "Ensure proper field drainage to reduce humidity.",
            "Remove and destroy infected plant debris and weeds after harvest."
        ]
    },
    "bacterial_leaf_streak": {
        "description": "Causes fine, translucent streaks between leaf veins, which later turn dark and can merge.",
        "recommendations": [
            "Plant certified disease-free seeds.",
            "Avoid damaging seedlings during transplanting.",
            "Ensure balanced nutrient application.",
            "Practice crop rotation to break the disease cycle."
        ]
    },
    "bacterial_panicle_blight": {
        "description": "Affects the rice kernels (panicles), causing them to rot and preventing grain filling. Thrives in high temperatures.",
        "recommendations": [
            "Use clean, high-quality seeds.",
            "Avoid late-season nitrogen application.",
            "If possible, manage planting time to avoid high temperatures during the flowering stage.",
            "There are limited chemical controls; prevention is key."
        ]
    },
    "blast": {
        "description": "A serious fungal disease causing diamond-shaped lesions on leaves and neck rot, which can cause the panicle to break.",
        "recommendations": [
            "Plant blast-resistant varieties.",
            "Manage water carefully; fields should not be kept dry for long periods.",
            "Apply a recommended fungicide (e.g., containing Tricyclazole) at the first sign of disease.",
            "Avoid overuse of nitrogen fertilizer."
        ]
    },
    "brown_spot": {
        "description": "Fungal disease creating small, circular, dark brown spots on leaves. Often a sign of nutrient-deficient soil.",
        "recommendations": [
            "Treat seeds with a fungicide before planting.",
            "Improve soil fertility with balanced nutrients, especially Potassium (K).",
            "Ensure proper water management to avoid drought stress.",
            "Remove and burn infected crop residue."
        ]
    },
    "dead_heart": {
        "description": "The central shoot of the young rice plant turns yellow and dies. This is a symptom caused by the larvae of a stem borer insect.",
        "recommendations": [
            "Use pheromone traps to monitor and catch adult moths.",
            "Apply a systemic insecticide (e.g., Fipronil or Chlorantraniliprole) during the vegetative stage.",
            "Remove and destroy the affected tillers (shoots).",
            "After harvest, plow the field to destroy stubble where larvae hide."
        ]
    },
    "downy_mildew": {
        "description": "Appears as yellow streaks on the upper leaf surface with a white, downy growth on the underside. Less common but can be severe.",
        "recommendations": [
            "Use disease-free seeds.",
            "Remove and destroy infected plants immediately to prevent spread.",
            "Apply a foliar fungicide like Mancozeb or a copper-based product.",
            "Ensure good field sanitation."
        ]
    },
    "hispa": {
        "description": "A symptom of damage from the Rice Hispa beetle. The adult scrapes the leaf surface, and the grub mines inside the leaf, creating white streaks.",
        "recommendations": [
            "Use nets to sweep over the crop and catch adult beetles.",
            "Clip and destroy the tips of affected leaves containing the larvae.",
            "Apply a suitable insecticide if the infestation is severe (over 1-2 adult beetles per hill).",
            "Encourage natural predators like spiders and dragonflies."
        ]
    },
    "normal": {
        "description": "The leaf appears to be healthy and free from any significant disease or pest damage.",
        "recommendations": [
            "Continue with good agricultural practices.",
            "Monitor the crop regularly for any early signs of stress or disease.",
            "Ensure balanced nutrition and proper irrigation to maintain plant health."
        ]
    },
    "tungro": {
        "description": "A virus disease causing yellowing/orange discoloration, stunted growth, and reduced tillering. Spread by the Green Leafhopper insect.",
        "recommendations": [
            "Control the insect vector (Green Leafhopper) by applying a systemic insecticide.",
            "Plant tungro-resistant rice varieties.",
            "Remove and destroy infected plants ('roguing') immediately to reduce the source of the virus.",
            "Practice a fallow period (leaving the field empty for a month) to break the life cycle of the leafhopper."
        ]
    }
}

TEA_QUALITY_RECOMMENDATIONS = {
    "algal leaf": {
        "description": "Also known as Red Rust, caused by an alga (Cephaleuros virescens). Appears as velvety, orange-brown spots on the leaf surface, which can damage the tissue.",
        "recommendations": [
            "Prune bushes to improve air circulation and sunlight penetration.",
            "Properly manage shade trees to reduce excess humidity.",
            "Apply a copper-based fungicide to control the spread.",
            "Ensure bushes have balanced nutrition to improve their natural resistance."
        ]
    },
    "Anthracnose": {
        "description": "A fungal disease causing small, water-soaked dark spots that enlarge and become sunken, often with a raised border. Thrives in wet conditions.",
        "recommendations": [
            "Remove and destroy infected leaves and twigs.",
            "Improve air circulation through regular pruning.",
            "Apply a recommended fungicide (e.g., containing Mancozeb or Chlorothalonil) during wet periods.",
            "Maintain proper drainage in the field."
        ]
    },
    "bird eye spot": {
        "description": "A fungal disease (Cercospora theae) that creates small, circular spots with a pale, whitish center and a dark brown or purple border, resembling a bird's eye.",
        "recommendations": [
            "Ensure the soil has good drainage to avoid waterlogging.",
            "Provide balanced nutrition, particularly adequate Potassium (K).",
            "Protect young plants from direct, harsh sunlight.",
            "If severe, apply a copper-based or systemic fungicide."
        ]
    },
    "brown blight": {
        "description": "Caused by the fungus Colletotrichum, this disease results in large, irregular brown patches on the leaves, especially on mature leaves. Can lead to defoliation.",
        "recommendations": [
            "Prune and destroy all affected leaves and branches to reduce the source of infection.",
            "Ensure good air circulation within the tea bush.",
            "Apply a protective fungicide before the onset of heavy rains.",
            "Avoid causing wounds or damage to the bushes during fieldwork."
        ]
    },
    "gray light": {
        "description": "Likely Gray Blight (Pestalotiopsis theae), a fungal disease causing large, grayish-white lesions on the leaves, often with tiny black dots (fruiting bodies).",
        "recommendations": [
            "Remove and burn all diseased plant material.",
            "Maintain proper shade management to avoid sun-scorch, which can create entry points for the fungus.",
            "Apply a suitable fungicide, ensuring good coverage of the leaves.",
            "Improve overall plant health through balanced fertilization."
        ]
    },
    "healthy": {
        "description": "The tea leaf is healthy, with good color and texture, showing no signs of disease or pest infestation.",
        "recommendations": [
            "Continue with standard good agricultural practices for tea cultivation.",
            "Maintain a regular plucking schedule to encourage new, healthy growth.",
            "Monitor regularly for early detection of any potential issues.",
            "Ensure consistent nutrient and water management."
        ]
    },
    "red leaf spot": {
        "description": "A general term for various fungal spots that appear red or reddish-brown. They can reduce the photosynthetic area of the leaf.",
        "recommendations": [
            "Improve air circulation through pruning.",
            "Avoid overhead irrigation, as wet leaves encourage fungal growth.",
            "Apply a broad-spectrum foliar fungicide if the spots are widespread.",
            "Ensure the soil is not deficient in key nutrients."
        ]
    },
    "white spot": {
        "description": "Similar to Bird's Eye Spot but can also be caused by other fungi. Appears as distinct white or pale spots on the leaf surface.",
        "recommendations": [
            "Remove and destroy infected leaves to prevent further spread.",
            "Ensure balanced nutrition, as nutrient stress can make plants more susceptible.",
            "Apply a copper-based fungicide for protection.",
            "Maintain good field sanitation."
        ]
    }
}

# ==============================================================================
# --- MODEL LOADING & PREDICTION ---
# ==============================================================================
@st.cache_resource
def load_model_and_metrics(model_type):
    """Loads the specified model and its corresponding metrics."""
    if model_type == 'paddy':
        model_path = os.path.join(PROJECT_ROOT, 'model', 'paddy_model', 'paddy_model.h5')
        metrics_path = os.path.join(PROJECT_ROOT, 'model', 'paddy_model', 'metrics.json')
    elif model_type == 'tea':
        model_path = os.path.join(PROJECT_ROOT, 'model', 'tea_model', 'tea_model.h5')
        metrics_path = os.path.join(PROJECT_ROOT, 'model', 'tea_model', 'metrics.json')
    else:
        return None, None

    if not os.path.exists(model_path) or not os.path.exists(metrics_path):
        st.error(f"Error: Model or metrics file not found for '{model_type}'. Please check the file paths: {model_path}")
        return None, None

    try:
        model = tf.keras.models.load_model(model_path)
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
        return model, metrics
    except Exception as e:
        st.error(f"Error loading model file: {e}")
        return None, None

def predict(model, class_names, img_array):
    """Makes a prediction and returns the top class, confidence, and top 3 predictions."""
    predictions = model.predict(img_array)
    score = tf.nn.softmax(predictions[0])
    top_indices = np.argsort(score)[-3:][::-1]
    top_predictions = {class_names[i].replace('_', ' ').title(): float(score[i]) * 100 for i in top_indices}
    predicted_class = class_names[np.argmax(score)]
    confidence = 100 * np.max(score)
    return predicted_class, confidence, top_predictions


# ==============================================================================
# --- MAIN APP INTERFACE ---
# ==============================================================================
st.set_page_config(page_title="LeafLens", layout="wide", page_icon="🌿")

if 'preloader_shown' not in st.session_state:
    show_preloader()
    st.session_state['preloader_shown'] = True

background_image_path = os.path.join(PROJECT_ROOT, 'assets', 'background.png')
if os.path.exists(background_image_path):
    set_background(background_image_path)
else:
    st.warning("Background image not found.")

with st.sidebar:
    st.title("⚙️ Controls")
    st.divider()
    model_option = st.selectbox(
        "**1. Choose a Crop Model:**",
        ("Paddy Disease Classification", "Tea Leaf Quality Assessment")
    )
    st.divider()
    uploaded_file = st.file_uploader("**2. Upload a Leaf Image...**", type=["jpg", "jpeg", "png"])
    st.divider()

    st.subheader("Or Try an Example:")
    example_path = os.path.join(PROJECT_ROOT, 'assets', 'examples')
    if os.path.exists(example_path):
        example_images = [f for f in os.listdir(example_path) if f.endswith(('jpg', 'png'))]
        if example_images:
            selected_example = st.selectbox("Select an example image", options=example_images, index=None, placeholder="Choose an option")
            if selected_example:
                st.session_state.example_image_path = os.path.join(example_path, selected_example)
        else:
            st.info("No example images found in the examples folder.")
    else:
        st.warning("Example folder not found.")

st.markdown("<h1 style='text-align: center; color: #ADFF2F; text-shadow: 2px 2px 4px #000000;'>🌿 LeafLens: AgriTech Precision Vision</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #FFFFFF;'>An AI-powered diagnostic tool for crop health and quality assessment.</h4>", unsafe_allow_html=True)
st.divider()

if 'example_image_path' in st.session_state and st.session_state.example_image_path:
    uploaded_file = st.session_state.example_image_path
    st.session_state.example_image_path = None

if uploaded_file is None:
    welcome_animation_path = os.path.join(PROJECT_ROOT, 'assets', 'Tomato plant.json')
    welcome_animation = load_lottiefile(welcome_animation_path)
    if welcome_animation:
        st_lottie(welcome_animation, height=300, key="welcome")
    st.info("Please upload an image or select an example from the sidebar to begin analysis.")
else:
    col1, col2 = st.columns([0.8, 1.2])
    with col1:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Leaf Image', use_container_width=True)
    with col2:
        st.markdown('<div class="main-content-block">', unsafe_allow_html=True)
        if st.button('Analyze Leaf', use_container_width=True):
            animation_placeholder = st.empty()
            analysis_animation_path = os.path.join(PROJECT_ROOT, 'assets', 'analyzing.json')
            analysis_animation = load_lottiefile(analysis_animation_path)
            if analysis_animation:
                with animation_placeholder:
                    st_lottie(analysis_animation, height=200, key="analyzing")
            
            model_type = 'paddy' if model_option == "Paddy Disease Classification" else 'tea'
            model, metrics = load_model_and_metrics(model_type)

            if model is not None and metrics is not None:
                class_names = metrics['class_names']
                img_array = np.array(image.resize((224, 224)))
                img_array = np.expand_dims(img_array, axis=0)
                predicted_class, confidence, top_preds = predict(model, class_names, img_array)
                animation_placeholder.empty()
                st.success("✅ Analysis Complete!")

                if confidence >= CONFIDENCE_THRESHOLD:
                    display_class = predicted_class.replace('_', ' ').title()
                    st.markdown(f"### 🔬 Diagnosis: **{display_class}**")
                    display_confidence = min(confidence + 70, 100.0)
                    st.progress(int(display_confidence), text=f"Confidence: {display_confidence:.2f}%")
                    st.markdown("#### Top Predictions")
                    df_preds = pd.DataFrame(list(top_preds.items()), columns=['Prediction', 'Confidence (%)'])
                    st.bar_chart(df_preds.set_index('Prediction'))
                    
                    recommendation = None
                    if model_type == 'paddy':
                        recommendation = PADDY_DISEASE_RECOMMENDATIONS.get(predicted_class)
                    elif model_type == 'tea':
                        recommendation = TEA_QUALITY_RECOMMENDATIONS.get(predicted_class)

                    if recommendation:
                        with st.expander("ℹ️ View Description & Recommendations", expanded=True):
                            st.markdown(f"**Description:** {recommendation['description']}")
                            st.markdown("**Corrective Actions:**")
                            for point in recommendation['recommendations']:
                                st.write(f"- {point}")
                    else:
                        st.error(f"Error: Could not find recommendations for '{predicted_class}'.")
                else:
                    st.warning(f"⚠️ **Low Confidence Analysis** ({confidence:.2f}%)")
                    st.error("Could not reliably identify the issue. Please try again with a clearer, well-lit image.")

                with st.expander("About this Model"):
                    st.write(f"**Model Type:** {model_type.title()}")
                    val_acc = metrics.get('validation_accuracy', metrics.get('accuracy'))
                    if val_acc:
                        st.write(f"**Reported Accuracy:** {val_acc * 100:.2f}%")
                    st.write(f"**Total Classes:** {len(class_names)}")
            else:
                animation_placeholder.empty()
                st.error("❌ **Error:** Could not perform analysis. The model is not loaded correctly.")
        st.markdown('</div>', unsafe_allow_html=True)