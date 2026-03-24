import tempfile

import streamlit as st
from PIL import Image

from src.retrieval import retrieve_similar_items
from src.preferences import build_preference_schema, summarize_preferences
from src.rerank import rerank_results, summarize_rerank_effect


st.set_page_config(page_title="Wardrobe Visual Similarity", layout="wide")

st.title("Personal Wardrobe Intelligence")
st.write("Upload a clothing image to retrieve visually similar items.")
st.caption("For best results, upload a clothing image rather than a portrait.")

uploaded_file = st.file_uploader("Upload a clothing image", type=["jpg", "jpeg", "png"])

st.subheader("Preference Controls")

more_style = st.selectbox(
    "Make it more...",
    ["any", "formal", "casual", "minimal", "sporty"]
)

avoid_features = st.multiselect(
    "Avoid...",
    ["cropped", "hood", "skinny fit", "logos"]
)

fit_preference = st.selectbox(
    "Fit",
    ["any", "slim", "regular", "relaxed", "oversized"]
)

free_text_pref = st.text_input(
    "Optional preference text",
    placeholder="Example: more formal, less sporty, avoid skinny fit"
)

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", width=300)

    if st.button("Find Similar Items"):
        preference_schema = build_preference_schema(
            more_style=more_style,
            avoid_features=avoid_features,
            fit_preference=fit_preference,
            free_text=free_text_pref,
        )

        preference_summary = summarize_preferences(preference_schema)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            image.save(tmp.name)
            temp_path = tmp.name

        with st.spinner("Searching for similar items..."):
            results = retrieve_similar_items(temp_path, top_k=5)

            reranked_results = rerank_results(results, preference_schema)

        st.subheader("Parsed Preference Summary")
        st.write(preference_summary)

        st.subheader("Preference Schema")
        st.json(preference_schema)

        st.subheader("Current Local CLIP Results")
        baseline_cols = st.columns(5)
        for col, result in zip(baseline_cols, results):
            with col:
                st.image(result["image_path"], use_container_width=True)
                st.caption(f"Base score: {result['score']:.4f}")

        st.subheader("Preference-Aware Reranked Results")
        st.write(summarize_rerank_effect(preference_schema))

        rerank_cols = st.columns(5)
        for col, result in zip(rerank_cols, reranked_results):
            with col:
                st.image(result["image_path"], use_container_width=True)
                st.caption(f"Base: {result['score']:.4f}")
                st.caption(f"Goal bonus: {result['goal_bonus']:.4f}")
                st.caption(f"Avoid penalty: {result['avoid_penalty']:.4f}")
                st.caption(f"Final: {result['final_score']:.4f}")

else:
    st.warning("Please upload an image to begin.")