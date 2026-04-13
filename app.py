import base64
import io
import tempfile
from pathlib import Path

import streamlit as st
from PIL import Image

from src.retrieval import retrieve_similar_items, load_catalog
from src.preferences import build_preference_schema
from src.rerank import rerank_results


st.set_page_config(
    page_title="Wardrobe AI",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300&display=swap');

html, body, [class*="css"] {
    font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif !important;
}
#MainMenu, footer { visibility: hidden; }
[data-testid="stToolbar"] { visibility: hidden; }
.block-container { padding-top: 0 !important; padding-bottom: 4rem !important; max-width: 100% !important; }

/* ── Sidebar ─────────────────────────────── */
[data-testid="stSidebar"] {
    background: #0A0A0A !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}
[data-testid="stSidebar"] .block-container { padding: 2rem 1.2rem !important; }
.brand { font-size: 1rem; font-weight: 600; letter-spacing: -0.3px; color: #fff; margin-bottom: 2rem; display: block; }
.sidebar-label { font-size: 0.6rem; font-weight: 600; letter-spacing: 0.18em; text-transform: uppercase; color: #555; margin: 1.5rem 0 0.6rem 0; }

/* ── Hero ────────────────────────────────── */
.hero-strip {
    background: radial-gradient(ellipse at 20% 50%, rgba(10,132,255,0.06) 0%, transparent 60%),
                radial-gradient(ellipse at 80% 20%, rgba(48,209,88,0.04) 0%, transparent 50%),
                #000;
    padding: 3.5rem 3rem 3rem 3rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.hero-kicker { font-size: 0.62rem; font-weight: 600; letter-spacing: 0.22em; text-transform: uppercase; color: #0A84FF; margin-bottom: 1rem; }
.hero-h1 { font-size: 3.8rem; font-weight: 700; letter-spacing: -2px; line-height: 1.0; color: #fff; margin: 0 0 1rem 0; }
.hero-p { font-size: 1rem; font-weight: 300; color: #555; line-height: 1.7; max-width: 440px; font-style: italic; }
.stat-pill { display: inline-flex; align-items: center; gap: 6px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 100px; padding: 4px 14px; font-size: 0.68rem; color: #666; margin-top: 1.2rem; }
.stat-dot { width: 6px; height: 6px; border-radius: 50%; background: #30D158; display: inline-block; }

/* ── Results ─────────────────────────────── */
.results-wrap { padding: 2.5rem 3rem; }
.section-eyebrow { font-size: 0.58rem; font-weight: 600; letter-spacing: 0.2em; text-transform: uppercase; color: #444; margin: 0 0 0.4rem 0; }
.section-title { font-size: 1.3rem; font-weight: 600; letter-spacing: -0.5px; color: #F5F5F7; margin: 0 0 1.5rem 0; }

/* ── Query row ───────────────────────────── */
.query-row { display: flex; align-items: center; gap: 1.5rem; margin-bottom: 2rem; }
.query-thumb { width: 72px; height: 96px; border-radius: 10px; overflow: hidden; background: #111; border: 1px solid rgba(255,255,255,0.08); flex-shrink: 0; }
.query-thumb img { width: 100%; height: 100%; object-fit: cover; display: block; }
.query-meta { display: flex; flex-direction: column; gap: 4px; }
.query-meta-label { font-size: 0.6rem; font-weight: 600; letter-spacing: 0.18em; text-transform: uppercase; color: #444; }
.query-meta-title { font-size: 0.95rem; font-weight: 500; color: #F5F5F7; }
.arrow-right { color: #333; font-size: 1.4rem; }

/* ── Card grid ───────────────────────────── */
.card-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 0.6rem; }
.p-card {
    position: relative; border-radius: 14px; overflow: hidden;
    background: #111; aspect-ratio: 3 / 4; cursor: pointer;
    transition: transform 0.3s cubic-bezier(0.25,0.46,0.45,0.94), box-shadow 0.3s ease;
    border: 1px solid rgba(255,255,255,0.04);
}
.p-card:hover { transform: translateY(-5px) scale(1.015); box-shadow: 0 24px 48px rgba(0,0,0,0.7); border-color: rgba(255,255,255,0.1); }
.p-card img { width: 100%; height: 100%; object-fit: cover; display: block; }

/* rank */
.p-rank { position: absolute; top: 10px; left: 10px; width: 26px; height: 26px; border-radius: 50%; background: rgba(0,0,0,0.6); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.12); display: flex; align-items: center; justify-content: center; font-size: 0.65rem; font-weight: 700; color: #fff; }

/* rank change badge (top-right) */
.p-change { position: absolute; top: 10px; right: 10px; font-size: 0.58rem; font-weight: 700; padding: 2px 7px; border-radius: 100px; letter-spacing: 0.04em; }
.p-change-up   { background: rgba(48,209,88,0.2);  color: #30D158; border: 1px solid rgba(48,209,88,0.3); }
.p-change-down { background: rgba(255,69,58,0.15); color: #FF453A; border: 1px solid rgba(255,69,58,0.25); }
.p-change-same { background: rgba(255,255,255,0.06); color: #666; border: 1px solid rgba(255,255,255,0.1); }
.p-change-new  { background: rgba(10,132,255,0.2); color: #0A84FF; border: 1px solid rgba(10,132,255,0.3); }

/* footer overlay */
.p-footer { position: absolute; bottom: 0; left: 0; right: 0; padding: 32px 12px 12px 12px; background: linear-gradient(to top, rgba(0,0,0,0.8) 0%, transparent 100%); display: flex; flex-direction: column; gap: 3px; }
.p-score { font-size: 0.72rem; font-weight: 600; color: rgba(255,255,255,0.9); letter-spacing: 0.02em; }
.p-meta { display: flex; gap: 5px; }
.p-boost   { font-size: 0.62rem; color: #30D158; font-weight: 500; }
.p-penalty { font-size: 0.62rem; color: #FF453A; font-weight: 500; }

/* ── Misc ────────────────────────────────── */
.chips { display: flex; flex-wrap: wrap; gap: 7px; margin-bottom: 1.5rem; }
.chip { font-size: 0.72rem; font-weight: 500; padding: 4px 13px; border-radius: 100px; }
.chip-g { background: rgba(48,209,88,0.1);  color: #30D158; border: 1px solid rgba(48,209,88,0.25); }
.chip-a { background: rgba(255,69,58,0.1);  color: #FF453A; border: 1px solid rgba(255,69,58,0.25); }
.rule { border: none; border-top: 1px solid rgba(255,255,255,0.05); margin: 2.5rem 0; }
.notice { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 10px 16px; font-size: 0.78rem; color: #555; margin-bottom: 1.5rem; }
.legend { display: flex; flex-wrap: wrap; gap: 1rem; margin-top: 1.2rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.04); }
.legend-item { display: flex; align-items: center; gap: 5px; font-size: 0.65rem; color: #555; }
.legend-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }

/* ── Query card (sidebar) ────────────────── */
.query-card { border-radius: 14px; overflow: hidden; background: #111; border: 1px solid rgba(255,255,255,0.06); margin-bottom: 1rem; }
.query-card img { width: 100%; display: block; }
.query-card-label { padding: 8px 12px; font-size: 0.6rem; font-weight: 600; letter-spacing: 0.15em; text-transform: uppercase; color: #444; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def img_b64(path: str) -> str:
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    ext = Path(path).suffix.lower().lstrip(".")
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext
    return f"data:image/{mime};base64,{data}"


def pil_b64(pil_img: Image.Image) -> str:
    buf = io.BytesIO()
    pil_img.save(buf, format="JPEG")
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def change_badge(old_rank: int | None, new_rank: int) -> str:
    if old_rank is None:
        return '<span class="p-change p-change-new">NEW</span>'
    diff = old_rank - new_rank
    if diff > 0:
        return f'<span class="p-change p-change-up">↑{diff}</span>'
    if diff < 0:
        return f'<span class="p-change p-change-down">↓{abs(diff)}</span>'
    return '<span class="p-change p-change-same">=</span>'


def base_card(rank: int, r: dict) -> str:
    src = img_b64(r["image_path"])
    return f"""<div class="p-card">
        <img src="{src}" alt="{rank}" />
        <div class="p-rank">{rank}</div>
        <div class="p-footer"><span class="p-score">{r['score']:.3f}</span></div>
    </div>"""


def rerank_card(new_rank: int, r: dict, old_rank: int | None) -> str:
    src = img_b64(r["image_path"])
    badge = change_badge(old_rank, new_rank)
    return f"""<div class="p-card">
        <img src="{src}" alt="{new_rank}" />
        <div class="p-rank">{new_rank}</div>
        {badge}
        <div class="p-footer">
            <span class="p-score">{r['final_score']:.3f}</span>
            <div class="p-meta">
                <span class="p-boost">+{r['goal_bonus']:.3f}</span>
                <span class="p-penalty">−{r['avoid_penalty']:.3f}</span>
            </div>
        </div>
    </div>"""


# ── Session state init ─────────────────────────────────────────────────────────
for key in ("candidates", "results", "reranked", "query_b64", "pref_schema"):
    if key not in st.session_state:
        st.session_state[key] = None


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<span class="brand">Wardrobe AI</span>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        encoded = pil_b64(image)
        st.markdown(
            f'<div class="query-card"><img src="{encoded}" /><div class="query-card-label">Your item</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<p class="sidebar-label">Style</p>', unsafe_allow_html=True)
    more_style     = st.selectbox("Make it more...", ["any", "formal", "casual", "minimal", "sporty"])
    avoid_features = st.multiselect("Avoid...", ["cropped", "hood", "skinny fit", "logos"])
    fit_preference = st.selectbox("Fit", ["any", "slim", "regular", "relaxed", "oversized"])
    free_text_pref = st.text_input("", placeholder="other preferences...", label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    search_btn  = st.button("Find Similar Items", use_container_width=True, type="primary")
    rerank_btn  = st.button(
        "Re-rank with New Preferences",
        use_container_width=True,
        disabled=(st.session_state.candidates is None),
    )

    if st.session_state.candidates:
        st.markdown(
            '<p style="font-size:0.65rem;color:#333;text-align:center;margin-top:0.5rem;">'
            'Re-rank is instant — no re-search needed</p>',
            unsafe_allow_html=True,
        )


# ── Catalog count ──────────────────────────────────────────────────────────────
try:
    _, catalog_paths = load_catalog()
    stat_html = (
        f'<div class="stat-pill"><span class="stat-dot"></span>'
        f'{len(catalog_paths):,} items indexed</div>'
    )
except Exception:
    stat_html = ""


# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-strip">
    <p class="hero-kicker">AI-Powered Fashion Retrieval</p>
    <h1 class="hero-h1">Find your<br>next outfit.</h1>
    <p class="hero-p">Upload any clothing piece and discover visually similar items, intelligently ranked by your personal style preferences.</p>
    {stat_html}
</div>
""", unsafe_allow_html=True)

if not uploaded_file:
    st.markdown(
        '<div style="padding:2rem 3rem;color:#333;font-size:0.9rem;">'
        'Upload a clothing image in the sidebar to begin.</div>',
        unsafe_allow_html=True,
    )
    st.stop()


# ── Full search ────────────────────────────────────────────────────────────────
if search_btn:
    pref = build_preference_schema(
        more_style=more_style, avoid_features=avoid_features,
        fit_preference=fit_preference, free_text=free_text_pref,
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        image.save(tmp.name)
        temp_path = tmp.name

    status = st.empty()
    status.markdown('<p style="padding:1rem 3rem;color:#444;font-size:0.82rem;">Removing background…</p>', unsafe_allow_html=True)
    candidates = retrieve_similar_items(temp_path, top_k=20)

    status.markdown('<p style="padding:1rem 3rem;color:#444;font-size:0.82rem;">Applying preferences…</p>', unsafe_allow_html=True)
    reranked = rerank_results(candidates, pref)[:5]
    status.empty()

    st.session_state.candidates  = candidates
    st.session_state.results     = candidates[:5]
    st.session_state.reranked    = reranked
    st.session_state.query_b64   = pil_b64(image)
    st.session_state.pref_schema = pref


# ── Re-rank only ───────────────────────────────────────────────────────────────
if rerank_btn and st.session_state.candidates:
    pref = build_preference_schema(
        more_style=more_style, avoid_features=avoid_features,
        fit_preference=fit_preference, free_text=free_text_pref,
    )
    st.session_state.reranked    = rerank_results(st.session_state.candidates, pref)[:5]
    st.session_state.pref_schema = pref


# ── Render results ─────────────────────────────────────────────────────────────
if st.session_state.results is None:
    st.markdown(
        '<div style="padding:2rem 3rem;color:#333;font-size:0.9rem;">'
        'Set your preferences and click <strong style="color:#666">Find Similar Items</strong>.</div>',
        unsafe_allow_html=True,
    )
    st.stop()

results         = st.session_state.results
reranked_results = st.session_state.reranked
pref_schema     = st.session_state.pref_schema
goals           = pref_schema.get("goals", [])
avoid           = pref_schema.get("avoid", [])

# base rank lookup: position in full 20-candidate list
base_rank_map = {r["image_path"]: i + 1 for i, r in enumerate(st.session_state.candidates)}

st.markdown('<div class="results-wrap">', unsafe_allow_html=True)

# ── Query row ──
st.markdown(
    f'<div class="query-row">'
    f'<div class="query-thumb"><img src="{st.session_state.query_b64}" /></div>'
    f'<span class="arrow-right">→</span>'
    f'<div class="query-meta">'
    f'<span class="query-meta-label">Searching for</span>'
    f'<span class="query-meta-title">Similar items in catalog</span>'
    f'</div></div>',
    unsafe_allow_html=True,
)

# ── Active preference chips ──
if goals or avoid:
    chips = '<div class="chips">'
    for g in goals:
        chips += f'<span class="chip chip-g">+ {g.replace("_"," ")}</span>'
    for a in avoid:
        chips += f'<span class="chip chip-a">− {a.replace("_"," ")}</span>'
    chips += '</div>'
    st.markdown(chips, unsafe_allow_html=True)

# ── Base grid ──
st.markdown('<p class="section-eyebrow">Visual Similarity</p><p class="section-title">Closest Matches</p>', unsafe_allow_html=True)
st.markdown(
    '<div class="card-grid">' +
    "".join(base_card(i+1, r) for i, r in enumerate(results)) +
    '</div>',
    unsafe_allow_html=True,
)

st.markdown('<hr class="rule">', unsafe_allow_html=True)

# ── Reranked grid ──
st.markdown('<p class="section-eyebrow">Preference Ranking</p><p class="section-title">Styled for You</p>', unsafe_allow_html=True)

if not goals and not avoid:
    st.markdown(
        '<div class="notice">No preferences active — both rows show visual similarity only. '
        'Select a style goal or something to avoid to see personalized reranking.</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="card-grid">' +
    "".join(
        rerank_card(new_rank + 1, r, base_rank_map.get(r["image_path"]))
        for new_rank, r in enumerate(reranked_results)
    ) +
    '</div>',
    unsafe_allow_html=True,
)

# ── Legend ──
st.markdown("""
<div class="legend">
    <span class="legend-item"><span class="legend-dot" style="background:#30D158"></span>↑ Moved up</span>
    <span class="legend-item"><span class="legend-dot" style="background:#FF453A"></span>↓ Moved down</span>
    <span class="legend-item"><span class="legend-dot" style="background:#0A84FF"></span>NEW — surfaced by preferences</span>
    <span class="legend-item"><span class="legend-dot" style="background:#555"></span>= Same position</span>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
