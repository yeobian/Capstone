import tempfile

import streamlit as st
from PIL import Image

from src.retrieval import retrieve_similar_items


st.set_page_config(page_title="Wardrobe Visual Similarity", layout="wide")

st.title("Personal Wardrobe Intelligence")
st.write("Upload a clothing image to retrieve visually similar items.")

uploaded_file = st.file_uploader("Upload a clothing image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", width=300)

    if st.button("Find Similar Items"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            image.save(tmp.name)
            temp_path = tmp.name

        with st.spinner("Searching for similar items..."):
            results = retrieve_similar_items(temp_path, top_k=5)

        st.subheader("Top Similar Items")
        cols = st.columns(5)

        for col, result in zip(cols, results):
            with col:
                st.image(result["image_path"], use_container_width=True)
                st.caption(f"Score: {result['score']:.4f}")
else:
    st.warning("Please upload an image to begin.")