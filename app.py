import base64
import os
import tempfile
from pathlib import Path

import numpy as np
import streamlit as st
from PIL import Image

from src.retrieval import retrieve_similar_items
from src.preferences import build_preference_schema
from src.rerank import rerank_results


# page setup
st.set_page_config(
    page_title="Wardrobe AI",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded",
)


# custom app styling
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
.stApp { background: #FAFAFB !important; }
.block-container { max-width: 1160px !important; padding: 3rem 2.2rem 5rem !important; }

/* ── Sidebar shell ── */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid rgba(15,23,42,0.06) !important;
}
[data-testid="stSidebar"] .block-container { padding: 2rem 1.6rem !important; }

/* Sidebar native labels */
[data-testid="stSidebar"] label {
    font-size: 0.68rem !important;
    font-weight: 400 !important;
    color: #6B7280 !important;
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
    border-bottom: 1px solid rgba(15,23,42,0.07);
}
.sb-gem {
    width: 24px; height: 24px; border-radius: 6px; flex-shrink: 0;
    background: linear-gradient(140deg, #7C3AED, #4F46E5);
}
.sb-name { font-size: 0.85rem; font-weight: 700; color: #0F172A; letter-spacing: -0.2px; }

.sb-lbl {
    display: block;
    font-size: 0.6rem; font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; color: #94A3B8;
    margin: 1.3rem 0 0.5rem;
}

/* ── Page header ── */
.pg-head { margin-bottom: 2.6rem; }
.pg-title {
    font-size: 1.9rem; font-weight: 800;
    letter-spacing: -0.7px; color: #0F172A;
    line-height: 1.1; margin-bottom: 0.45rem;
}
.pg-sub { font-size: 0.85rem; color: #475569; font-weight: 400; line-height: 1.6; }
.pg-rule { border: none; border-top: 1px solid rgba(15,23,42,0.07); margin-top: 1.8rem; }

/* ── Section header ── */
.sh { display: flex; align-items: center; gap: 8px; margin-bottom: 1rem; }
.sh-title { font-size: 0.82rem; font-weight: 600; color: #0F172A; letter-spacing: -0.1px; }
.sh-dot { width: 3px; height: 3px; border-radius: 50%; background: #94A3B8; flex-shrink: 0; }
.sh-meta { font-size: 0.78rem; color: #6B7280; font-weight: 400; }

/* ── Cards ── */
.cards-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
}
.cards-grid-wide {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
}
@media (min-width: 1200px) {
    .cards-grid-wide { grid-template-columns: repeat(10, 1fr); }
}
.rcard {
    background: #FFFFFF;
    border-radius: 11px;
    overflow: hidden;
    position: relative;
    border: 1px solid rgba(15,23,42,0.08);
    box-shadow: 0 1px 2px rgba(15,23,42,0.04);
    transition: border-color 0.15s, box-shadow 0.15s, transform 0.15s;
}
.rcard:hover {
    border-color: rgba(15,23,42,0.16);
    box-shadow: 0 12px 28px rgba(15,23,42,0.10);
    transform: translateY(-2px);
}
.rcard:hover .rcard-img img { transform: scale(1.04); }

/* rank badge */
.rcard-rank {
    position: absolute; top: 8px; left: 8px; z-index: 2;
    background: rgba(255,255,255,0.85);
    backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
    border: 1px solid rgba(15,23,42,0.08);
    border-radius: 5px; padding: 1px 5px;
    font-size: 0.58rem; font-weight: 700; color: #475569; letter-spacing: 0.02em;
}
/* new dot */
.rcard-ndot {
    position: absolute; top: 8px; right: 8px; z-index: 2;
    width: 6px; height: 6px; border-radius: 50%;
    background: #10B981;
    box-shadow: 0 0 7px rgba(16,185,129,0.55);
}
/* image */
.rcard-img {
    width: 100%; aspect-ratio: 2/3;
    overflow: hidden; background: #F1F5F9;
}
.rcard-img img {
    width: 100%; height: 100%; object-fit: cover; display: block;
    transition: transform 0.3s ease;
}
/* footer */
.rcard-foot {
    padding: 8px 9px 9px;
    border-top: 1px solid rgba(15,23,42,0.06);
}
.rcard-lbl {
    font-size: 0.55rem; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: #94A3B8; margin-bottom: 2px;
}
.rcard-val {
    font-size: 0.8rem; font-weight: 700;
    font-feature-settings: "tnum" 1;
    letter-spacing: -0.2px; line-height: 1;
}
.rv-base  { color: #475569; }
.rv-final { color: #7C3AED; }
.rcard-delta {
    margin-top: 4px; display: flex; gap: 6px;
}
.rdelta {
    font-size: 0.58rem; font-weight: 500;
    font-feature-settings: "tnum" 1; color: #94A3B8;
}

/* ── Show more button ── */
.show-more-wrap { margin-top: 10px; }

/* ── Empty state ── */
.empty-wrap {
    padding: 6rem 1rem; text-align: center;
}
.empty-title { font-size: 0.9rem; font-weight: 600; color: #475569; margin-bottom: 0.4rem; }
.empty-hint { font-size: 0.8rem; color: #94A3B8; line-height: 1.75; }
.empty-hint strong { color: #475569; font-weight: 500; }

/* ── Active prefs row ── */
.pref-row { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 0.9rem; }
.ptag {
    font-size: 0.67rem; font-weight: 500;
    padding: 3px 9px; border-radius: 5px; letter-spacing: 0.01em;
}
.ptag-goal { background: rgba(124,58,237,0.08); color: #7C3AED; border: 1px solid rgba(124,58,237,0.20); }
.ptag-avoid { background: rgba(15,23,42,0.04); color: #475569; border: 1px solid rgba(15,23,42,0.08); }

/* ── Divider ── */
.sec-div { border: none; border-top: 1px solid rgba(15,23,42,0.07); margin: 2.2rem 0; }

/* ── Alpha hint ── */
.alpha-hint {
    font-size: 0.62rem; color: #94A3B8;
    margin-top: 3px; font-style: italic;
}
</style>
""", unsafe_allow_html=True)


# helper: encode an image file to base64 so it can be embedded in HTML
def _b64(path: str) -> tuple[str, str]:
    p = Path(path)
    ext = p.suffix.lower().lstrip(".")
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode(), mime


# helper: build a card for the Visual Matches section
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


# helper: build a card for the Styled for You section (shows score delta)
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


# helper: wrap a list of cards in a CSS grid
def _grid(cards: list[str], wide: bool = False) -> str:
    cls = "cards-grid-wide" if wide else "cards-grid"
    return f'<div class="{cls}">' + "".join(cards) + "</div>"


# sidebar: upload image and set style preferences
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
        "Upload", type=["jpg", "jpeg", "png", "webp"], label_visibility="collapsed"
    )
    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        # show a preview of the uploaded image
        st.image(image, width="stretch")

    st.markdown('<span class="sb-lbl">Style goal</span>', unsafe_allow_html=True)
    more_style = st.selectbox(
        "Style",
        ["any", "formal", "casual", "minimal", "sporty",
         "elegant", "streetwear", "vintage", "colorful"],
        label_visibility="collapsed",
    )
    fit_preference = st.selectbox(
        "Fit", ["any", "slim", "regular", "relaxed", "oversized"],
        label_visibility="collapsed",
    )

    st.markdown('<span class="sb-lbl">Color</span>', unsafe_allow_html=True)
    color_preference = st.selectbox(
        "Color",
        ["any", "black", "white", "beige", "gray", "navy", "blue",
         "red", "green", "pink", "brown", "yellow", "orange", "purple"],
        label_visibility="collapsed",
    )

    st.markdown('<span class="sb-lbl">Avoid</span>', unsafe_allow_html=True)
    avoid_features = st.multiselect(
        "Avoid",
        ["cropped", "hood", "skinny fit", "logos", "patterns", "sheer", "embellished"],
        label_visibility="collapsed",
    )
    free_text_pref = st.text_input(
        "Notes", placeholder="e.g. no patterns, office-ready",
        label_visibility="collapsed",
    )

    st.markdown('<span class="sb-lbl">Preference strength</span>', unsafe_allow_html=True)
    alpha = st.slider(
        "Alpha", min_value=0.1, max_value=1.0, value=0.4, step=0.05,
        label_visibility="collapsed",
        help="How aggressively preferences re-order results. Low = subtle nudge, High = strong re-sort.",
    )
    st.markdown(
        f'<p class="alpha-hint">α = {alpha:.2f} &nbsp;·&nbsp; '
        f'{"subtle" if alpha < 0.3 else "balanced" if alpha < 0.7 else "aggressive"}</p>',
        unsafe_allow_html=True,
    )

    st.write("")
    search_btn = st.button("Find Similar Items", width="stretch", type="primary")


# main page header
st.markdown(
    '<div class="pg-head">'
    '<h1 class="pg-title">Wardrobe AI</h1>'
    '<p class="pg-sub">Upload a clothing item and discover visually similar styles,<br>'
    "ranked by your personal preferences.</p>"
    '<hr class="pg-rule">'
    "</div>",
    unsafe_allow_html=True,
)

# show empty state if no image has been uploaded yet
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

# run search when the button is clicked
if search_btn:
    pref_schema = build_preference_schema(
        more_style=more_style,
        avoid_features=avoid_features,
        fit_preference=fit_preference,
        free_text=free_text_pref,
        color_preference=color_preference,
    )

    # save uploaded image to a temp file so retrieval can read it from disk
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        image.save(tmp.name)
        temp_path = tmp.name

    try:
        with st.spinner("Searching catalog…"):
            # get similar items from the catalog, then rerank by preferences
            candidates      = retrieve_similar_items(temp_path, top_k=20)
            base_results    = candidates[:5]
            reranked        = rerank_results(candidates, pref_schema, alpha=alpha)
            reranked_top5   = reranked[:5]
    finally:
        os.unlink(temp_path)

    # compute how much reranking changed the top 5
    base_set = {r["image_path"] for r in base_results}
    moved_in = sum(1 for r in reranked_top5 if r["image_path"] not in base_set)
    if pref_schema.get("goals") or pref_schema.get("avoid") or pref_schema.get("color"):
        avg_delta = float(np.mean([r["final_score"] - r["score"] for r in reranked_top5]))
        rerank_meta = f"{moved_in} new · avg Δ {avg_delta:+.3f}"
    else:
        rerank_meta = "no preferences active"

    # store results in session state so they persist across rerenders
    st.session_state.update(
        results=base_results,
        reranked=reranked_top5,
        all_candidates=candidates,
        all_reranked=reranked,
        pref_schema=pref_schema,
        rerank_meta=rerank_meta,
        show_all_base=False,
        show_all_reranked=False,
    )

# nothing to show yet — user hasn't searched
if "results" not in st.session_state:
    st.markdown(
        '<p style="font-size:0.82rem;color:#475569;margin-top:0.2rem;">'
        'Click <strong style="color:#7C3AED">Find Similar Items</strong> '
        "in the sidebar to run a search.</p>",
        unsafe_allow_html=True,
    )
    st.stop()

base_results     = st.session_state["results"]
reranked_top5    = st.session_state["reranked"]
all_candidates   = st.session_state["all_candidates"]
all_reranked     = st.session_state["all_reranked"]
pref_schema      = st.session_state["pref_schema"]
rerank_meta      = st.session_state["rerank_meta"]
goals            = pref_schema.get("goals", [])
avoid            = pref_schema.get("avoid", [])
has_prefs        = bool(goals or avoid or pref_schema.get("color"))

show_all_base     = st.session_state.get("show_all_base", False)
show_all_reranked = st.session_state.get("show_all_reranked", False)

# visual matches section — pure image similarity, no preference applied
n_base = len(all_candidates) if show_all_base else 5
st.markdown(
    f'<div class="sh">'
    f'<span class="sh-title">Visual Matches</span>'
    f'<div class="sh-dot"></div>'
    f'<span class="sh-meta">top {n_base} by image similarity</span>'
    f"</div>",
    unsafe_allow_html=True,
)

display_base = all_candidates if show_all_base else base_results
base_cards = [_base_card(r, i + 1) for i, r in enumerate(display_base)]
st.markdown(_grid(base_cards, wide=show_all_base), unsafe_allow_html=True)

col_expand_base, _ = st.columns([1, 4])
with col_expand_base:
    btn_label = "Show top 5" if show_all_base else f"Show all {len(all_candidates)} →"
    if st.button(btn_label, key="btn_base"):
        st.session_state["show_all_base"] = not show_all_base
        st.rerun()

st.markdown('<hr class="sec-div">', unsafe_allow_html=True)

# styled for you section — reranked by user preferences
n_ranked = len(all_reranked) if show_all_reranked else 5
st.markdown(
    f'<div class="sh">'
    f'<span class="sh-title">Styled for You</span>'
    f'<div class="sh-dot"></div>'
    f'<span class="sh-meta">{rerank_meta}</span>'
    f"</div>",
    unsafe_allow_html=True,
)

# show active preference chips above the results
if has_prefs:
    chips = '<div class="pref-row">'
    for g in goals:
        chips += f'<span class="ptag ptag-goal">+ {g.replace("_", " ")}</span>'
    for a in avoid:
        chips += f'<span class="ptag ptag-avoid">− {a.replace("_", " ")}</span>'
    color = pref_schema.get("color")
    if color:
        chips += f'<span class="ptag ptag-goal">color: {color}</span>'
    chips += "</div>"
    st.markdown(chips, unsafe_allow_html=True)

base_paths = {r["image_path"] for r in base_results}
display_reranked = all_reranked if show_all_reranked else reranked_top5
rerank_cards = [
    _ranked_card(r, i + 1, r["image_path"] not in base_paths, has_prefs)
    for i, r in enumerate(display_reranked)
]
st.markdown(_grid(rerank_cards, wide=show_all_reranked), unsafe_allow_html=True)

col_expand_ranked, _ = st.columns([1, 4])
with col_expand_ranked:
    btn_label2 = "Show top 5" if show_all_reranked else f"Show all {len(all_reranked)} →"
    if st.button(btn_label2, key="btn_reranked"):
        st.session_state["show_all_reranked"] = not show_all_reranked
        st.rerun()
