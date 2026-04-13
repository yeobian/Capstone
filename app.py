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


# ── Styles ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,300&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif !important;
    -webkit-font-smoothing: antialiased !important;
    -moz-osx-font-smoothing: grayscale !important;
}

#MainMenu, footer { visibility: hidden; }

/* ── Page ── */
.stApp { background: #08080F !important; }
.block-container { max-width: 1160px !important; padding: 3rem 2.2rem 5rem !important; }

/* ── Sidebar shell ── */
[data-testid="stSidebar"] {
    background: #0B0B12 !important;
    border-right: 1px solid rgba(255,255,255,0.045) !important;
}
[data-testid="stSidebar"] .block-container { padding: 2rem 1.6rem !important; }

/* Sidebar native labels */
[data-testid="stSidebar"] label {
    font-size: 0.68rem !important;
    font-weight: 400 !important;
    color: #4B5563 !important;
    letter-spacing: 0.01em !important;
    text-transform: none !important;
}

/* Sidebar button */
[data-testid="stSidebar"] .stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    height: 38px !important;
    letter-spacing: 0.01em !important;
}

/* ── Sidebar brand ── */
.sb-brand {
    display: flex; align-items: center; gap: 9px;
    padding-bottom: 1.4rem;
    margin-bottom: 1.4rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.sb-gem {
    width: 24px; height: 24px; border-radius: 6px; flex-shrink: 0;
    background: linear-gradient(140deg, #C084FC, #818CF8);
}
.sb-name { font-size: 0.85rem; font-weight: 700; color: #F4F3FA; letter-spacing: -0.2px; }

.sb-lbl {
    display: block;
    font-size: 0.6rem; font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; color: #2D3748;
    margin: 1.3rem 0 0.5rem;
}

/* ── Page header ── */
.pg-head { margin-bottom: 2.6rem; }
.pg-title {
    font-size: 1.9rem; font-weight: 800;
    letter-spacing: -0.7px; color: #F4F3FA;
    line-height: 1.1; margin-bottom: 0.45rem;
}
.pg-sub { font-size: 0.85rem; color: #3D4451; font-weight: 400; line-height: 1.6; }
.pg-rule { border: none; border-top: 1px solid rgba(255,255,255,0.045); margin-top: 1.8rem; }

/* ── Section header ── */
.sh { display: flex; align-items: center; gap: 8px; margin-bottom: 1rem; }
.sh-title { font-size: 0.82rem; font-weight: 600; color: #C8C6D6; letter-spacing: -0.1px; }
.sh-dot { width: 3px; height: 3px; border-radius: 50%; background: #2D3748; flex-shrink: 0; }
.sh-meta { font-size: 0.78rem; color: #2D3748; font-weight: 400; }

/* ── Result cards ── */
.cards-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
}
.rcard {
    background: #0F0F18;
    border-radius: 11px;
    overflow: hidden;
    position: relative;
    border: 1px solid rgba(255,255,255,0.05);
    transition: border-color 0.15s, box-shadow 0.15s, transform 0.15s;
}
.rcard:hover {
    border-color: rgba(255,255,255,0.1);
    box-shadow: 0 12px 36px rgba(0,0,0,0.55);
    transform: translateY(-2px);
}
.rcard:hover .rcard-img img { transform: scale(1.04); }

/* rank badge */
.rcard-rank {
    position: absolute; top: 8px; left: 8px; z-index: 2;
    background: rgba(8,8,15,0.72);
    backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 5px; padding: 1px 5px;
    font-size: 0.58rem; font-weight: 700; color: #4B5563; letter-spacing: 0.02em;
}
/* new dot */
.rcard-ndot {
    position: absolute; top: 8px; right: 8px; z-index: 2;
    width: 6px; height: 6px; border-radius: 50%;
    background: #34D399;
    box-shadow: 0 0 7px rgba(52,211,153,0.6);
}
/* image */
.rcard-img {
    width: 100%; aspect-ratio: 2/3;
    overflow: hidden; background: #141420;
}
.rcard-img img {
    width: 100%; height: 100%; object-fit: cover; display: block;
    transition: transform 0.3s ease;
}
/* footer */
.rcard-foot {
    padding: 8px 9px 9px;
    border-top: 1px solid rgba(255,255,255,0.04);
}
.rcard-lbl {
    font-size: 0.55rem; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: #2D3748; margin-bottom: 2px;
}
.rcard-val {
    font-size: 0.8rem; font-weight: 700;
    font-feature-settings: "tnum" 1;
    letter-spacing: -0.2px; line-height: 1;
}
.rv-base  { color: #6B7280; }
.rv-final { color: #C084FC; }
.rcard-delta {
    margin-top: 4px; display: flex; gap: 6px;
}
.rdelta {
    font-size: 0.58rem; font-weight: 500;
    font-feature-settings: "tnum" 1; color: #2D3748;
}

/* ── Empty state ── */
.empty-wrap {
    padding: 6rem 1rem; text-align: center;
}
.empty-title { font-size: 0.9rem; font-weight: 600; color: #2D3748; margin-bottom: 0.4rem; }
.empty-hint { font-size: 0.8rem; color: #1F2937; line-height: 1.75; }
.empty-hint strong { color: #4B5563; font-weight: 500; }

/* ── Active prefs row ── */
.pref-row { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 0.9rem; }
.ptag {
    font-size: 0.67rem; font-weight: 500;
    padding: 3px 9px; border-radius: 5px; letter-spacing: 0.01em;
}
.ptag-goal { background: rgba(192,132,252,0.07); color: #9D72F0; border: 1px solid rgba(192,132,252,0.13); }
.ptag-avoid { background: rgba(255,255,255,0.03); color: #4B5563; border: 1px solid rgba(255,255,255,0.07); }

/* ── Divider ── */
.sec-div { border: none; border-top: 1px solid rgba(255,255,255,0.045); margin: 2.2rem 0; }

/* ── No-prefs hint ── */
.no-pref { font-size: 0.75rem; color: #2D3748; font-style: italic; margin-bottom: 0.9rem; }
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
    return (
        f'<div class="rcard">'
        f'<div class="rcard-rank">{rank}</div>'
        f'<div class="rcard-img"><img src="data:{mime};base64,{b64}" alt="item"></div>'
        f'<div class="rcard-foot">'
        f'<div class="rcard-lbl">Match</div>'
        f'<div class="rcard-val rv-base">{r["score"]:.3f}</div>'
        f'</div></div>'
    )


def _ranked_card(r: dict, rank: int, is_new: bool, has_prefs: bool) -> str:
    b64, mime = _b64(r["image_path"])
    ndot  = '<div class="rcard-ndot"></div>' if is_new else ""
    val   = r["final_score"] if has_prefs else r["score"]
    lbl   = "Ranked" if has_prefs else "Match"
    color = "rv-final" if has_prefs else "rv-base"
    delta = ""
    if has_prefs:
        delta = (
            f'<div class="rcard-delta">'
            f'<span class="rdelta">+{r["goal_bonus"]:.3f}</span>'
            f'<span class="rdelta">−{r["avoid_penalty"]:.3f}</span>'
            f'</div>'
        )
    return (
        f'<div class="rcard">'
        f'<div class="rcard-rank">{rank}</div>'
        f'{ndot}'
        f'<div class="rcard-img"><img src="data:{mime};base64,{b64}" alt="item"></div>'
        f'<div class="rcard-foot">'
        f'<div class="rcard-lbl">{lbl}</div>'
        f'<div class="rcard-val {color}">{val:.3f}</div>'
        f'{delta}'
        f'</div></div>'
    )


def _grid(cards: list[str]) -> str:
    return '<div class="cards-grid">' + "".join(cards) + "</div>"


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div class="sb-brand">'
        '<div class="sb-gem"></div>'
        '<span class="sb-name">Wardrobe AI</span>'
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown('<span class="sb-lbl">Item</span>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload", type=["jpg", "jpeg", "png"], label_visibility="collapsed"
    )
    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, use_container_width=True)

    st.markdown('<span class="sb-lbl">Style goal</span>', unsafe_allow_html=True)
    more_style = st.selectbox(
        "Style", ["any", "formal", "casual", "minimal", "sporty"],
        label_visibility="collapsed",
    )
    fit_preference = st.selectbox(
        "Fit", ["any", "slim", "regular", "relaxed", "oversized"],
        label_visibility="collapsed",
    )

    st.markdown('<span class="sb-lbl">Avoid</span>', unsafe_allow_html=True)
    avoid_features = st.multiselect(
        "Avoid", ["cropped", "hood", "skinny fit", "logos"],
        label_visibility="collapsed",
    )
    free_text_pref = st.text_input(
        "Notes", placeholder="e.g. no patterns, office-ready",
        label_visibility="collapsed",
    )

    st.write("")
    search_btn = st.button("Find Similar Items", use_container_width=True, type="primary")


# ── Main ───────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="pg-head">'
    '<h1 class="pg-title">Wardrobe AI</h1>'
    '<p class="pg-sub">Upload a clothing item and discover visually similar styles,<br>'
    "ranked by your personal preferences.</p>"
    '<hr class="pg-rule">'
    "</div>",
    unsafe_allow_html=True,
)

# Empty state — no image
if not uploaded_file:
    st.markdown(
        '<div class="empty-wrap">'
        '<p class="empty-title">No item uploaded</p>'
        '<p class="empty-hint">'
        "Open the sidebar, upload a clothing photo,<br>"
        "set your style preferences, and click <strong>Find Similar Items</strong>."
        "</p></div>",
        unsafe_allow_html=True,
    )
    st.stop()

# Trigger search
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

    with st.spinner("Searching catalog…"):
        candidates   = retrieve_similar_items(temp_path, top_k=20)
        base_results = candidates[:5]
        reranked     = rerank_results(candidates, pref_schema)[:5]

    st.session_state.update(
        results=base_results,
        reranked=reranked,
        pref_schema=pref_schema,
    )

# No results yet
if "results" not in st.session_state:
    st.markdown(
        '<p style="font-size:0.82rem;color:#2D3748;margin-top:0.2rem;">'
        'Click <strong style="color:#9D72F0">Find Similar Items</strong> '
        "in the sidebar to run a search.</p>",
        unsafe_allow_html=True,
    )
    st.stop()

base_results = st.session_state["results"]
reranked     = st.session_state["reranked"]
pref_schema  = st.session_state["pref_schema"]
goals        = pref_schema.get("goals", [])
avoid        = pref_schema.get("avoid", [])
has_prefs    = bool(goals or avoid)

# ── Section 1: Visual matches ──────────────────────────────────────────────────
st.markdown(
    '<div class="sh">'
    '<span class="sh-title">Visual Matches</span>'
    '<div class="sh-dot"></div>'
    '<span class="sh-meta">top 5 by image similarity</span>'
    "</div>",
    unsafe_allow_html=True,
)
st.markdown(
    _grid([_base_card(r, i + 1) for i, r in enumerate(base_results)]),
    unsafe_allow_html=True,
)

# ── Divider ────────────────────────────────────────────────────────────────────
st.markdown('<hr class="sec-div">', unsafe_allow_html=True)

# ── Section 2: Styled for You ──────────────────────────────────────────────────
sub_meta = "reranked by preferences" if has_prefs else "same order — no preferences active"
st.markdown(
    f'<div class="sh">'
    f'<span class="sh-title">Styled for You</span>'
    f'<div class="sh-dot"></div>'
    f'<span class="sh-meta">{sub_meta}</span>'
    f"</div>",
    unsafe_allow_html=True,
)

# Active preference tags
if has_prefs:
    chips = '<div class="pref-row">'
    for g in goals:
        chips += f'<span class="ptag ptag-goal">+ {g.replace("_", " ")}</span>'
    for a in avoid:
        chips += f'<span class="ptag ptag-avoid">− {a.replace("_", " ")}</span>'
    chips += "</div>"
    st.markdown(chips, unsafe_allow_html=True)

base_paths = {r["image_path"] for r in base_results}
st.markdown(
    _grid([
        _ranked_card(r, i + 1, r["image_path"] not in base_paths, has_prefs)
        for i, r in enumerate(reranked)
    ]),
    unsafe_allow_html=True,
)
