import tempfile

import streamlit as st
from PIL import Image

from src.retrieval import retrieve_similar_items
from src.preferences import build_preference_schema, summarize_preferences
from src.rerank import rerank_results, summarize_rerank_effect


st.set_page_config(
    page_title="Wardrobe AI",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Reset & base ─────────────────────────────── */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Inter", "Helvetica Neue", sans-serif !important;
}
#MainMenu, footer, header { visibility: hidden; }

/* Remove Streamlit's default top padding */
.block-container { padding-top: 2.5rem !important; padding-bottom: 4rem !important; }

/* ── Hero ─────────────────────────────────────── */
.hero {
    padding: 3rem 0 2rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 2.5rem;
}
.hero-eyebrow {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #0A84FF;
    margin-bottom: 0.75rem;
}
.hero-title {
    font-size: 3.2rem;
    font-weight: 700;
    letter-spacing: -1.5px;
    line-height: 1.05;
    color: #F5F5F7;
    margin: 0 0 0.75rem 0;
}
.hero-sub {
    font-size: 1.05rem;
    font-weight: 300;
    color: #86868B;
    max-width: 520px;
    line-height: 1.6;
    margin: 0;
}

/* ── Section label ────────────────────────────── */
.section-label {
    font-size: 0.62rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #86868B;
    margin: 0 0 1rem 0;
}

/* ── Image cards ──────────────────────────────── */
.img-card {
    background: #1C1C1E;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    overflow: hidden;
    transition: border-color 0.25s ease, transform 0.25s ease;
    margin-bottom: 0.5rem;
}
.img-card:hover {
    border-color: rgba(255,255,255,0.18);
    transform: translateY(-2px);
}
.img-card img { width: 100%; display: block; }

/* ── Score tags ───────────────────────────────── */
.tag-row { display: flex; flex-direction: column; gap: 4px; margin-top: 8px; }
.tag {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 0.7rem;
    font-weight: 500;
    padding: 3px 10px;
    border-radius: 20px;
    width: fit-content;
}
.tag-base    { background: rgba(255,255,255,0.06); color: #AEAEB2; }
.tag-final   { background: rgba(10,132,255,0.15);  color: #0A84FF; border: 1px solid rgba(10,132,255,0.3); }
.tag-boost   { background: rgba(48,209,88,0.12);   color: #30D158; }
.tag-penalty { background: rgba(255,69,58,0.12);   color: #FF453A; }

/* ── Preference chips ─────────────────────────── */
.chip-row { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 1.5rem; }
.chip {
    font-size: 0.78rem;
    font-weight: 500;
    padding: 5px 14px;
    border-radius: 100px;
    border: 1px solid rgba(255,255,255,0.1);
    background: rgba(255,255,255,0.04);
    color: #F5F5F7;
}
.chip-goal   { border-color: rgba(48,209,88,0.35); color: #30D158; background: rgba(48,209,88,0.06); }
.chip-avoid  { border-color: rgba(255,69,58,0.35);  color: #FF453A; background: rgba(255,69,58,0.06); }

/* ── Divider ──────────────────────────────────── */
.divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin: 2rem 0;
}

/* ── Sidebar tweaks ───────────────────────────── */
[data-testid="stSidebar"] {
    background: #111111 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] .block-container { padding-top: 2rem !important; }

.sidebar-title {
    font-size: 1rem;
    font-weight: 600;
    color: #F5F5F7;
    letter-spacing: -0.3px;
    margin-bottom: 1.5rem;
}
</style>
""", unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="sidebar-title">Wardrobe AI</p>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload clothing image",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
    )

    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, use_container_width=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.markdown('<p class="section-label">Style</p>', unsafe_allow_html=True)

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
        "Other",
        placeholder="e.g. avoid logos, more minimal",
        label_visibility="collapsed",
    )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    search_btn = st.button(
        "Find Similar Items",
        use_container_width=True,
        type="primary",
    )


# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <p class="hero-eyebrow">Fashion Retrieval</p>
    <h1 class="hero-title">Find your<br>next outfit.</h1>
    <p class="hero-sub">Upload any clothing item and instantly discover visually similar pieces, ranked by your style preferences.</p>
</div>
""", unsafe_allow_html=True)

if not uploaded_file:
    st.markdown(
        '<p style="color:#86868B; font-size:0.95rem;">Upload a clothing image in the sidebar to get started.</p>',
        unsafe_allow_html=True,
    )
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

    with st.spinner(""):
        candidates = retrieve_similar_items(temp_path, top_k=20)
        results = candidates[:5]
        reranked_results = rerank_results(candidates, preference_schema)[:5]

    # ── Active preference chips ──
    goals = preference_schema.get("goals", [])
    avoid = preference_schema.get("avoid", [])
    if goals or avoid:
        chips = '<div class="chip-row">'
        for g in goals:
            chips += f'<span class="chip chip-goal">+ {g.replace("_", " ")}</span>'
        for a in avoid:
            chips += f'<span class="chip chip-avoid">− {a.replace("_", " ")}</span>'
        chips += '</div>'
        st.markdown(chips, unsafe_allow_html=True)

    # ── Base results ──
    st.markdown('<p class="section-label">Visual Match</p>', unsafe_allow_html=True)
    cols = st.columns(5, gap="small")
    for col, r in zip(cols, results):
        with col:
            st.markdown('<div class="img-card">', unsafe_allow_html=True)
            st.image(r["image_path"], use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="tag-row"><span class="tag tag-base">{r["score"]:.3f}</span></div>',
                unsafe_allow_html=True,
            )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Reranked results ──
    st.markdown('<p class="section-label">Preference Ranked</p>', unsafe_allow_html=True)
    cols = st.columns(5, gap="small")
    for col, r in zip(cols, reranked_results):
        with col:
            st.markdown('<div class="img-card">', unsafe_allow_html=True)
            st.image(r["image_path"], use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="tag-row">'
                f'<span class="tag tag-final">{r["final_score"]:.3f}</span>'
                f'<span class="tag tag-boost">+{r["goal_bonus"]:.3f}</span>'
                f'<span class="tag tag-penalty">−{r["avoid_penalty"]:.3f}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

else:
    st.markdown(
        '<p style="color:#86868B; font-size:0.95rem;">Set your preferences and click <strong style="color:#F5F5F7">Find Similar Items</strong>.</p>',
        unsafe_allow_html=True,
    )
