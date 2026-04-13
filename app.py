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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: "Inter", -apple-system, sans-serif !important;
}
#MainMenu, footer { visibility: hidden; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #13111A !important;
    border-right: 1px solid rgba(192,132,252,0.12) !important;
}
[data-testid="stSidebar"] .block-container {
    padding: 2rem 1.4rem !important;
}
[data-testid="stSidebar"] label {
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    color: #9CA3AF !important;
    letter-spacing: 0.01em !important;
}

.sidebar-brand {
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: -0.4px;
    color: #F1F0F5;
    margin-bottom: 1.8rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.brand-gem {
    width: 22px; height: 22px; border-radius: 6px;
    background: linear-gradient(135deg, #C084FC, #818CF8);
    display: inline-block;
    flex-shrink: 0;
}
.sb-rule {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin: 1.2rem 0;
}
.sb-label {
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #6B7280;
    margin-bottom: 0.7rem;
}

/* ── Main area ── */
.main-title {
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: -1.2px;
    line-height: 1.05;
    margin: 0 0 0.5rem;
    background: linear-gradient(135deg, #C084FC 0%, #818CF8 60%, #C084FC 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.main-sub {
    font-size: 0.92rem;
    color: #6B7280;
    font-weight: 300;
    margin-bottom: 2rem;
}

/* ── Section labels ── */
.sec-label {
    font-size: 0.62rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #9CA3AF;
    margin: 0 0 0.8rem;
}
.sec-title {
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: -0.3px;
    color: #F1F0F5;
    margin: 0 0 1.2rem;
}

/* ── Score pills ── */
.pill {
    display: inline-block;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 0.72rem;
    font-weight: 500;
    margin: 2px 1px;
}
.pill-base   { background: rgba(255,255,255,0.06); color: #9CA3AF; border: 1px solid rgba(255,255,255,0.08); }
.pill-final  { background: rgba(192,132,252,0.15); color: #C084FC; border: 1px solid rgba(192,132,252,0.3); font-weight: 600; }
.pill-boost  { background: rgba(52,211,153,0.1);  color: #34D399; border: 1px solid rgba(52,211,153,0.2); }
.pill-penalty{ background: rgba(248,113,113,0.1); color: #F87171; border: 1px solid rgba(248,113,113,0.2); }

/* ── Preference chips ── */
.pref-chips  { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 1.5rem; }
.pref-chip   { font-size: 0.75rem; font-weight: 500; padding: 4px 12px; border-radius: 100px; }
.pc-goal     { background: rgba(192,132,252,0.12); color: #C084FC; border: 1px solid rgba(192,132,252,0.25); }
.pc-avoid    { background: rgba(248,113,113,0.1);  color: #F87171; border: 1px solid rgba(248,113,113,0.2); }

/* ── Divider ── */
.divider { border: none; border-top: 1px solid rgba(255,255,255,0.06); margin: 1.8rem 0; }

/* ── Notice ── */
.notice {
    background: rgba(192,132,252,0.06);
    border: 1px solid rgba(192,132,252,0.15);
    border-radius: 10px;
    padding: 10px 16px;
    font-size: 0.8rem;
    color: #9CA3AF;
    margin-bottom: 1.2rem;
}
</style>
""", unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div class="sidebar-brand"><span class="brand-gem"></span>Wardrobe AI</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<p class="sb-label">Your Item</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload", type=["jpg", "jpeg", "png"], label_visibility="collapsed"
    )

    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, use_container_width=True)

    st.markdown('<hr class="sb-rule">', unsafe_allow_html=True)
    st.markdown('<p class="sb-label">Style Preferences</p>', unsafe_allow_html=True)

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
        label_visibility="collapsed",
    )

    st.markdown('<hr class="sb-rule">', unsafe_allow_html=True)
    search_btn = st.button("Find Similar Items", use_container_width=True, type="primary")


# ── Main area ──────────────────────────────────────────────────────────────────
st.markdown('<p class="main-title">Find your next outfit.</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="main-sub">Upload a clothing item — get visually similar matches ranked by your style preferences.</p>',
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
        candidates = retrieve_similar_items(temp_path, top_k=20)
        results = candidates[:5]
        reranked_results = rerank_results(candidates, preference_schema)[:5]

    # ── Active preference chips ──
    goals = preference_schema.get("goals", [])
    avoid = preference_schema.get("avoid", [])

    if goals or avoid:
        chips = '<div class="pref-chips">'
        for g in goals:
            chips += f'<span class="pref-chip pc-goal">+ {g.replace("_"," ")}</span>'
        for a in avoid:
            chips += f'<span class="pref-chip pc-avoid">− {a.replace("_"," ")}</span>'
        chips += '</div>'
        st.markdown(chips, unsafe_allow_html=True)

    # ── Base results ──
    st.markdown('<p class="sec-label">Visual Similarity</p><p class="sec-title">Closest Matches</p>', unsafe_allow_html=True)
    cols = st.columns(5, gap="small")
    for col, r in zip(cols, results):
        with col:
            st.image(r["image_path"], use_container_width=True)
            st.markdown(
                f'<div style="margin-top:6px"><span class="pill pill-base">{r["score"]:.3f}</span></div>',
                unsafe_allow_html=True,
            )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Reranked results ──
    st.markdown('<p class="sec-label">Preference Ranking</p><p class="sec-title">Styled for You</p>', unsafe_allow_html=True)

    if not goals and not avoid:
        st.markdown(
            '<div class="notice">💡 No preferences active — select a style or avoid option to see personalized reranking.</div>',
            unsafe_allow_html=True,
        )

    base_paths = {r["image_path"] for r in results}
    cols = st.columns(5, gap="small")
    for col, r in zip(cols, reranked_results):
        with col:
            st.image(r["image_path"], use_container_width=True)
            is_new = r["image_path"] not in base_paths
            new_tag = ' &nbsp;<span class="pill pill-final" style="font-size:0.6rem;padding:2px 7px">NEW</span>' if is_new else ""
            st.markdown(
                f'<div style="margin-top:6px;display:flex;flex-direction:column;gap:3px">'
                f'<span class="pill pill-final">{r["final_score"]:.3f}</span>{new_tag}'
                f'<span class="pill pill-boost">+{r["goal_bonus"]:.3f}</span>'
                f'<span class="pill pill-penalty">−{r["avoid_penalty"]:.3f}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

else:
    st.markdown(
        '<p style="color:#6B7280;font-size:0.9rem;">Set your preferences in the sidebar and click <strong style="color:#C084FC">Find Similar Items</strong>.</p>',
        unsafe_allow_html=True,
    )
