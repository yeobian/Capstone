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

try:
    from models.baseline import ClothingClassifier
    from data.dataset import get_transforms
except ImportError:
    st.warning("Could not import model or transforms. Please ensure you are running this from the Capstone directory.")

st.set_page_config(page_title="Wardrobe AI", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

# Modern Dark/Light Theme Support with Custom CSS
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
        font-family: 'Inter', sans-serif;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #00E5FF !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    /* Custom Button */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        color: #121212;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 229, 255, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 229, 255, 0.5);
    }
    
    /* Image Container */
    .uploaded-img {
        border-radius: 12px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.5);
        border: 2px solid #262730;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1E1E1E;
        border-right: 1px solid #333;
    }
    
    /* Success/Info Boxes */
    .stSuccess, .stInfo {
        background-color: #1A1A1A !important;
        border: 1px solid #333 !important;
        color: #E0E0E0 !important;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("✨ Wardrobe AI Vision")
st.markdown("<p style='font-size: 1.2rem; color: #A0A0A0;'>Next-generation clothing classification powered by deep learning.</p>", unsafe_allow_html=True)
st.markdown("---")

st.sidebar.markdown("### ⚙️ Engine Settings")
model_path = st.sidebar.text_input("Model Weights", "models/dummy_model.pth")
num_classes = st.sidebar.number_input("Output Classes", min_value=1, value=3)
st.sidebar.markdown("---")
st.sidebar.markdown("<p style='font-size: 0.9rem; color: #666;'>v2.0.0 - Neural Engine Active</p>", unsafe_allow_html=True)


# Define class mapping based on SETUP.md
CLASS_NAMES = {
    0: "👕 Tops",
    1: "👖 Bottoms",
    2: "👟 Shoes"
}

@st.cache_resource
def load_model(path, classes):
    if not os.path.exists(path):
        return None
    model = ClothingClassifier(num_classes=classes, pretrained=False)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.load_state_dict(torch.load(path, map_location=device))
    model.eval()
    return model

model = load_model(model_path, num_classes)

if model is None:
    st.sidebar.error(f"❌ Weights not found at {model_path}")
    st.error("System offline: Please train the model and generate valid `.pth` weights to initialize the AI engine.")
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
                    
                    plot_names = [CLASS_NAMES.get(i, f"Class {i}") for i in range(num_classes)]
                    
                    # Custom color palette
                    colors = ['#00E5FF' if i == top_class_idx else '#333333' for i in range(num_classes)]
                    
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
