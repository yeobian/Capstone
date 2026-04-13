import base64
import tempfile
from pathlib import Path

import streamlit as st
from PIL import Image

from src.retrieval import retrieve_similar_items
from src.preferences import build_preference_schema
from src.rerank import rerank_results


# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Wardrobe AI",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Global styles ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
    font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer { visibility: hidden; }

/* ── Background ── */
.stApp { background: #0C0C10 !important; }
.block-container { max-width: 1200px !important; padding: 2.5rem 2rem !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0F0F16 !important;
    border-right: 1px solid rgba(255,255,255,0.04) !important;
}
[data-testid="stSidebar"] .block-container {
    padding: 2rem 1.5rem !important;
}
[data-testid="stSidebar"] label {
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    color: #4B5563 !important;
    text-transform: uppercase !important;
}
[data-testid="stSidebar"] .stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.01em !important;
    padding: 0.65rem 1rem !important;
}

/* ── Sidebar brand ── */
.sb-brand {
    display: flex; align-items: center; gap: 10px;
    padding-bottom: 1.6rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    margin-bottom: 1.6rem;
}
.sb-gem {
    width: 30px; height: 30px; border-radius: 9px; flex-shrink: 0;
    background: linear-gradient(135deg, #C084FC 0%, #818CF8 100%);
}
.sb-name { font-size: 0.95rem; font-weight: 700; color: #F1F0F5; letter-spacing: -0.3px; }

.sb-sec {
    font-size: 0.58rem; font-weight: 700; letter-spacing: 0.18em;
    text-transform: uppercase; color: #374151;
    margin: 1.4rem 0 0.7rem;
}

/* ── Main header ── */
.page-header {
    display: flex; align-items: center; gap: 12px;
    margin-bottom: 0.4rem;
}
.header-gem {
    width: 38px; height: 38px; border-radius: 11px; flex-shrink: 0;
    background: linear-gradient(135deg, #C084FC 0%, #818CF8 100%);
}
.header-title {
    font-size: 1.6rem; font-weight: 800; letter-spacing: -0.6px; color: #F1F0F5;
}
.header-badge {
    font-size: 0.58rem; font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; color: #C084FC;
    background: rgba(192,132,252,0.1);
    border: 1px solid rgba(192,132,252,0.2);
    border-radius: 20px; padding: 2px 9px;
}
.header-sub {
    font-size: 0.875rem; color: #4B5563; font-weight: 400;
    margin: 0.35rem 0 2.2rem;
}

/* ── Empty state ── */
.empty-wrap {
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; gap: 0;
    padding: 5rem 2rem; text-align: center;
    border: 1.5px dashed rgba(255,255,255,0.06);
    border-radius: 20px;
    background: rgba(255,255,255,0.01);
}
.empty-icon { font-size: 2.8rem; opacity: 0.25; margin-bottom: 1rem; }
.empty-title { font-size: 1rem; font-weight: 600; color: #374151; margin-bottom: 0.4rem; }
.empty-hint { font-size: 0.82rem; color: #374151; line-height: 1.6; }
.empty-hint b { color: #9CA3AF; font-weight: 500; }

/* ── Section header ── */
.sec-wrap { margin: 0 0 1.2rem; }
.sec-eyebrow {
    font-size: 0.58rem; font-weight: 700; letter-spacing: 0.2em;
    text-transform: uppercase; color: #374151; margin-bottom: 0.35rem;
}
.sec-title-text {
    font-size: 1rem; font-weight: 700; letter-spacing: -0.3px; color: #E5E3EE;
}
.sec-sub-text { font-size: 0.78rem; color: #4B5563; margin-top: 3px; }

/* ── Result cards ── */
.cards-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin-bottom: 0.5rem;
}
.rcard {
    background: #141420;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    overflow: hidden;
    position: relative;
    transition: border-color 0.18s, transform 0.18s;
}
.rcard:hover {
    border-color: rgba(192,132,252,0.3);
    transform: translateY(-3px);
}
.rcard-rank {
    position: absolute; top: 10px; left: 10px;
    width: 22px; height: 22px; border-radius: 50%;
    background: rgba(0,0,0,0.6);
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.6rem; font-weight: 700; color: #6B7280;
    border: 1px solid rgba(255,255,255,0.08);
    z-index: 2;
}
.rcard-img {
    width: 100%; aspect-ratio: 3/4;
    overflow: hidden; background: #1A1A24;
}
.rcard-img img {
    width: 100%; height: 100%; object-fit: cover;
    display: block;
}
.rcard-body { padding: 10px 11px 11px; }
.rcard-label {
    font-size: 0.58rem; font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; color: #374151; margin-bottom: 3px;
}
.rcard-score {
    font-size: 0.88rem; font-weight: 700; color: #C084FC; letter-spacing: -0.2px;
}
.rcard-top-row {
    display: flex; align-items: flex-start;
    justify-content: space-between; margin-bottom: 6px;
}
.rcard-pills { display: flex; gap: 4px; flex-wrap: wrap; margin-top: 5px; }
.mpill {
    font-size: 0.6rem; font-weight: 600; padding: 2px 7px;
    border-radius: 20px; display: inline-block;
}
.mpill-boost {
    background: rgba(52,211,153,0.08); color: #34D399;
    border: 1px solid rgba(52,211,153,0.15);
}
.mpill-penalty {
    background: rgba(248,113,113,0.08); color: #F87171;
    border: 1px solid rgba(248,113,113,0.15);
}
.badge-new {
    font-size: 0.56rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #34D399;
    background: rgba(52,211,153,0.1);
    border: 1px solid rgba(52,211,153,0.2);
    border-radius: 20px; padding: 2px 7px;
    white-space: nowrap;
}

/* ── Preference chips ── */
.pref-row { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 1.3rem; }
.pref-chip {
    font-size: 0.7rem; font-weight: 500;
    padding: 4px 12px; border-radius: 100px;
}
.pc-goal {
    background: rgba(192,132,252,0.1); color: #C084FC;
    border: 1px solid rgba(192,132,252,0.2);
}
.pc-avoid {
    background: rgba(248,113,113,0.08); color: #F87171;
    border: 1px solid rgba(248,113,113,0.18);
}

/* ── Notice ── */
.notice {
    display: flex; align-items: flex-start; gap: 10px;
    background: rgba(192,132,252,0.04);
    border: 1px solid rgba(192,132,252,0.1);
    border-radius: 10px; padding: 11px 15px;
    font-size: 0.78rem; color: #6B7280;
    margin-bottom: 1.2rem; line-height: 1.5;
}

/* ── Divider ── */
.fancy-div {
    display: flex; align-items: center; gap: 12px;
    margin: 2.2rem 0;
}
.fd-line { flex: 1; height: 1px; background: rgba(255,255,255,0.05); }
.fd-pip {
    width: 5px; height: 5px; border-radius: 50%;
    background: rgba(192,132,252,0.25);
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def _b64(path: str) -> tuple[str, str]:
    p = Path(path)
    ext = p.suffix.lower().lstrip(".")
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode(), mime


def _base_card(r: dict, rank: int) -> str:
    b64, mime = _b64(r["image_path"])
    return f"""<div class="rcard">
  <div class="rcard-rank">#{rank}</div>
  <div class="rcard-img"><img src="data:{mime};base64,{b64}" alt="item"></div>
  <div class="rcard-body">
    <div class="rcard-label">Similarity</div>
    <div class="rcard-score">{r['score']:.3f}</div>
  </div>
</div>"""


def _rerank_card(r: dict, rank: int, is_new: bool) -> str:
    b64, mime = _b64(r["image_path"])
    new_html = '<span class="badge-new">NEW</span>' if is_new else ""
    return f"""<div class="rcard">
  <div class="rcard-rank">#{rank}</div>
  <div class="rcard-img"><img src="data:{mime};base64,{b64}" alt="item"></div>
  <div class="rcard-body">
    <div class="rcard-top-row">
      <div>
        <div class="rcard-label">Final Score</div>
        <div class="rcard-score">{r['final_score']:.3f}</div>
      </div>
      {new_html}
    </div>
    <div class="rcard-pills">
      <span class="mpill mpill-boost">+{r['goal_bonus']:.3f}</span>
      <span class="mpill mpill-penalty">−{r['avoid_penalty']:.3f}</span>
    </div>
  </div>
</div>"""


def _cards_grid(cards: list[str]) -> str:
    return '<div class="cards-grid">' + "".join(cards) + "</div>"


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div class="sb-brand"><div class="sb-gem"></div>'
        '<span class="sb-name">Wardrobe AI</span></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<p class="sb-sec">Your Item</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload image", type=["jpg", "jpeg", "png"], label_visibility="collapsed"
    )

    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, use_container_width=True)

    st.markdown('<p class="sb-sec">Style Goal</p>', unsafe_allow_html=True)
    more_style = st.selectbox(
        "Make it more...", ["any", "formal", "casual", "minimal", "sporty"],
        label_visibility="collapsed",
    )
    fit_preference = st.selectbox(
        "Fit preference", ["any", "slim", "regular", "relaxed", "oversized"],
        label_visibility="collapsed",
    )

    st.markdown('<p class="sb-sec">Avoid</p>', unsafe_allow_html=True)
    avoid_features = st.multiselect(
        "Avoid", ["cropped", "hood", "skinny fit", "logos"],
        label_visibility="collapsed",
    )
    free_text_pref = st.text_input(
        "Other", placeholder="e.g. no patterns, office-ready",
        label_visibility="collapsed",
    )

    st.write("")
    search_btn = st.button("Find Similar Items", use_container_width=True, type="primary")


# ── Main area ──────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="page-header">'
    '<div class="header-gem"></div>'
    '<span class="header-title">Wardrobe AI</span>'
    '<span class="header-badge">AI Powered</span>'
    "</div>"
    '<p class="header-sub">Upload a clothing item — discover visually similar styles ranked by your preferences.</p>',
    unsafe_allow_html=True,
)

# ── Empty state ──
if not uploaded_file:
    st.markdown(
        '<div class="empty-wrap">'
        '<div class="empty-icon">👗</div>'
        '<p class="empty-title">No item uploaded yet</p>'
        '<p class="empty-hint">'
        'Use the <b>sidebar on the left</b> to upload a clothing image,<br>'
        "set your style preferences, and click <b>Find Similar Items</b>."
        "</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.stop()

# ── Session state: persist results ──
if search_btn:
    pref_schema = build_preference_schema(
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
        base_results = candidates[:5]
        reranked_results = rerank_results(candidates, pref_schema)[:5]

    st.session_state["results"] = base_results
    st.session_state["reranked"] = reranked_results
    st.session_state["pref_schema"] = pref_schema

# ── Show results if available ──
if "results" not in st.session_state:
    st.markdown(
        '<p style="color:#374151;font-size:0.88rem;margin-top:0.5rem;">'
        "Set your preferences in the sidebar and click "
        '<strong style="color:#C084FC">Find Similar Items</strong> to search.</p>',
        unsafe_allow_html=True,
    )
    st.stop()

base_results    = st.session_state["results"]
reranked_results = st.session_state["reranked"]
pref_schema     = st.session_state["pref_schema"]

# ── Section 1: Visual matches ──
st.markdown(
    '<div class="sec-wrap">'
    '<p class="sec-eyebrow">Step 1</p>'
    '<p class="sec-title-text">Visual Matches</p>'
    '<p class="sec-sub-text">Closest items by image similarity</p>'
    "</div>",
    unsafe_allow_html=True,
)

base_cards = [_base_card(r, i + 1) for i, r in enumerate(base_results)]
st.markdown(_cards_grid(base_cards), unsafe_allow_html=True)

# ── Divider ──
st.markdown(
    '<div class="fancy-div">'
    '<div class="fd-line"></div>'
    '<div class="fd-pip"></div>'
    '<div class="fd-line"></div>'
    "</div>",
    unsafe_allow_html=True,
)

# ── Section 2: Reranked ──
goals = pref_schema.get("goals", [])
avoid = pref_schema.get("avoid", [])

st.markdown(
    '<div class="sec-wrap">'
    '<p class="sec-eyebrow">Step 2</p>'
    '<p class="sec-title-text">Styled for You</p>'
    '<p class="sec-sub-text">Reranked by your style preferences</p>'
    "</div>",
    unsafe_allow_html=True,
)

# Active preference chips
if goals or avoid:
    chips = '<div class="pref-row">'
    for g in goals:
        chips += f'<span class="pref-chip pc-goal">+ {g.replace("_", " ")}</span>'
    for a in avoid:
        chips += f'<span class="pref-chip pc-avoid">− {a.replace("_", " ")}</span>'
    chips += "</div>"
    st.markdown(chips, unsafe_allow_html=True)
else:
    st.markdown(
        '<div class="notice">'
        '<span>💡</span>'
        "<span>No preferences selected — results match visual similarity only. "
        "Set a style goal or avoid option in the sidebar to see personalized reranking.</span>"
        "</div>",
        unsafe_allow_html=True,
    )

base_paths = {r["image_path"] for r in base_results}
rerank_cards = [
    _rerank_card(r, i + 1, r["image_path"] not in base_paths)
    for i, r in enumerate(reranked_results)
]
st.markdown(_cards_grid(rerank_cards), unsafe_allow_html=True)
