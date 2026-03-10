import streamlit as st
import torch
import os
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from PIL import Image
import pandas as pd

import sys
sys.path.append('src')

from src.config import NUM_CLASSES, CLASS_NAMES, DUMMY_MODEL_PATH
from models.baseline import ClothingClassifier
from data.dataset import get_transforms

st.set_page_config(page_title="Wardrobe AI", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

# Load external CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("✨ Wardrobe AI Vision")
st.markdown("<p style='font-size: 1.2rem; color: #A0A0A0;'>Next-generation clothing classification powered by deep learning.</p>", unsafe_allow_html=True)
st.markdown("---")

st.sidebar.markdown("### ⚙️ Engine Settings")
model_path = st.sidebar.text_input("Model Weights", DUMMY_MODEL_PATH)
num_classes_input = st.sidebar.number_input("Output Classes", min_value=1, value=NUM_CLASSES)
st.sidebar.markdown("---")
st.sidebar.markdown("<p style='font-size: 0.9rem; color: #666;'>v2.0.0 - Neural Engine Active</p>", unsafe_allow_html=True)


@st.cache_resource
def load_model(path, expected_num_classes):
    if not os.path.exists(path):
        return None
    try:
        model = ClothingClassifier(num_classes=expected_num_classes, pretrained=False)
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model.load_state_dict(torch.load(path, map_location=device))
        model.eval()
        return model
    except Exception as e:
        st.error(f"Error loading model from {path}: {e}")
        return None

model = load_model(model_path, num_classes_input)

if model is None:
    st.sidebar.error(f"❌ Weights not found or failed to load from {model_path}")
    st.error("System offline: Please ensure the model path is correct and the weights are valid. You can generate dummy weights using `python create_dummy.py`.")
else:
    st.sidebar.success("🟢 Neural Engine Online")
    
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.markdown("### 📤 Input Stream")
        uploaded_file = st.file_uploader("Drop an image of clothing here", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file).convert('RGB')
            st.image(image, use_column_width=True, clamp=True)

    with col2:
        st.markdown("### 🧠 Analysis")
        if uploaded_file is not None:
            if st.button("Initialize Scan 🚀"):
                with st.spinner("Processing image through neural network..."):
                    transforms = get_transforms(train=False)
                    input_tensor = transforms(image).unsqueeze(0)
                    
                    with torch.no_grad():
                        output = model(input_tensor)
                        probabilities = torch.nn.functional.softmax(output[0], dim=0)
                        
                    # Get all predictions sorted
                    probs_np = probabilities.cpu().numpy()
                    indices = np.argsort(probs_np)[::-1]
                    
                    top_class_idx = indices[0]
                    top_class_name = CLASS_NAMES.get(top_class_idx, f"Class {top_class_idx}")
                    confidence = probs_np[top_class_idx]
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("#### Primary Match")
                    st.success(f"**{top_class_name}** • {confidence*100:.2f}% Match")
                    
                    st.markdown("#### Confidence Matrix")
                    
                    # Modern Dark Theme Plot
                    plt.style.use('dark_background')
                    fig, ax = plt.subplots(figsize=(6, 3))
                    fig.patch.set_facecolor('#0E1117')
                    ax.set_facecolor('#0E1117')
                    
                    plot_names = [CLASS_NAMES.get(i, f"Class {i}") for i in range(len(CLASS_NAMES))]
                    
                    # Custom color palette
                    colors = ['#00E5FF' if CLASS_NAMES.get(i) == top_class_name else '#333333' for i in range(len(CLASS_NAMES))]
                    
                    sns.barplot(x=probs_np, y=plot_names, ax=ax, palette=colors)
                    
                    ax.set_xlim(0, 1)
                    ax.set_xlabel("Probability", color='#A0A0A0')
                    ax.set_ylabel("")
                    ax.tick_params(colors='#A0A0A0')
                    
                    # Remove borders
                    for spine in ax.spines.values():
                        spine.set_visible(False)
                        
                    plt.tight_layout()
                    st.pyplot(fig)
        else:
            st.info("Awaiting visual input. Please upload a file to the input stream.")

