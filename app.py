import streamlit as st
from PIL import Image

st.set_page_config(page_title="Wardrobe Visual Similarity", layout="wide")

st.title("Personal Wardrobe Intelligence")
st.write("Upload a clothing image to retrieve visually similar items.")

uploaded_file = st.file_uploader("Upload a clothing image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", width=300)

    if st.button("Find Similar Items"):
        st.info("Retrieval pipeline will run here.")
        st.write("Top similar items will be displayed here.")
else:
    st.warning("Please upload an image to begin.")