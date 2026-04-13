import tempfile

import streamlit as st
from PIL import Image

from src.retrieval import retrieve_similar_items
from src.preferences import build_preference_schema, summarize_preferences
from src.rerank import rerank_results, summarize_rerank_effect


st.set_page_config(
    page_title="Wardrobe AI",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* Hide default Streamlit header/footer */
#MainMenu, footer { visibility: hidden; }

/* Page title */
.hero-title {
    font-size: 2.4rem;
    font-weight: 700;
    letter-spacing: -0.5px;
    margin-bottom: 0;
    background: linear-gradient(135deg, #C084FC, #818CF8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub {
    font-size: 1rem;
    color: #9CA3AF;
    margin-top: 0.2rem;
    margin-bottom: 2rem;
}

/* Section headers */
.section-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #C084FC;
    margin-bottom: 0.5rem;
}

/* Score pills */
.score-pill {
    display: inline-block;
    background: #2D2D3F;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.75rem;
    color: #D1D5DB;
    margin: 2px 0;
}
.score-pill.final {
    background: linear-gradient(135deg, #7C3AED33, #4F46E533);
    border: 1px solid #7C3AED66;
    color: #C084FC;
    font-weight: 600;
}
.score-pill.boost { color: #6EE7B7; }
.score-pill.penalty { color: #FCA5A5; }

/* Divider */
.styled-divider {
    border: none;
    border-top: 1px solid #2D2D3F;
    margin: 1.5rem 0;
}

/* Preference badge */
.pref-badge {
    display: inline-block;
    background: #2D2D3F;
    border-radius: 8px;
    padding: 4px 12px;
    font-size: 0.82rem;
    color: #C084FC;
    margin: 3px;
}
</style>
""", unsafe_allow_html=True)


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="section-label">Upload</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Clothing image", type=["jpg", "jpeg", "png"], label_visibility="collapsed"
    )

    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, use_container_width=True)

    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)
    st.markdown('<p class="section-label">Style Preferences</p>', unsafe_allow_html=True)

    more_style = st.selectbox(
        "Make it more...",
        ["any", "formal", "casual", "minimal", "sporty"],
    )

    avoid_features = st.multiselect(
        "Avoid...",
        ["cropped", "hood", "skinny fit", "logos"],
    )

    fit_preference = st.selectbox(
        "Fit",
        ["any", "slim", "regular", "relaxed", "oversized"],
    )

    free_text_pref = st.text_input(
        "Other preferences",
        placeholder="e.g. more formal, avoid logos",
    )

    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

    search_btn = st.button("Find Similar Items", use_container_width=True, type="primary")


# ── Main area ─────────────────────────────────────────────────────────────────
st.markdown('<p class="hero-title">Wardrobe AI</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-sub">Upload a clothing item — get visually similar matches ranked by your style preferences.</p>',
    unsafe_allow_html=True,
)

if not uploaded_file:
    st.info("Upload a clothing image in the sidebar to get started.")
    st.stop()

if search_btn:
    preference_schema = build_preference_schema(
        more_style=more_style,
        avoid_features=avoid_features,
        fit_preference=fit_preference,
        free_text=free_text_pref,
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        image.save(tmp.name)
        temp_path = tmp.name

    with st.spinner("Searching catalog..."):
        results = retrieve_similar_items(temp_path, top_k=5)
        reranked_results = rerank_results(results, preference_schema)

    # ── Active preference badges ──
    goals = preference_schema.get("goals", [])
    avoid = preference_schema.get("avoid", [])

    if goals or avoid:
        st.markdown('<p class="section-label">Active Preferences</p>', unsafe_allow_html=True)
        badges = ""
        for g in goals:
            badges += f'<span class="pref-badge">+ {g}</span>'
        for a in avoid:
            badges += f'<span class="pref-badge" style="color:#FCA5A5">- {a}</span>'
        st.markdown(badges, unsafe_allow_html=True)
        st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

    # ── Base results (top) ──
    st.markdown('<p class="section-label">Visual Match (Base)</p>', unsafe_allow_html=True)
    cols = st.columns(5)
    for col, r in zip(cols, results):
        with col:
            st.image(r["image_path"], use_container_width=True)
            st.markdown(
                f'<div class="score-pill">{r["score"]:.3f}</div>',
                unsafe_allow_html=True,
            )

    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

    # ── Reranked results (bottom) ──
    st.markdown('<p class="section-label">Preference-Aware Reranked</p>', unsafe_allow_html=True)
    cols = st.columns(5)
    for col, r in zip(cols, reranked_results):
        with col:
            st.image(r["image_path"], use_container_width=True)
            st.markdown(
                f'<div class="score-pill final">{r["final_score"]:.3f}</div>'
                f'<br><div class="score-pill boost">+{r["goal_bonus"]:.3f}</div>'
                f'<div class="score-pill penalty">-{r["avoid_penalty"]:.3f}</div>',
                unsafe_allow_html=True,
            )

else:
    st.write("Set your preferences in the sidebar and click **Find Similar Items**.")
