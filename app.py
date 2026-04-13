import base64
import tempfile
from pathlib import Path

import streamlit as st
from PIL import Image

from src.retrieval import retrieve_similar_items, load_catalog
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
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300&display=swap');

html, body, [class*="css"] {
    font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; padding-bottom: 4rem !important; max-width: 100% !important; }

/* ── Sidebar ─────────────────────────────── */
[data-testid="stSidebar"] {
    background: #0A0A0A !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}
[data-testid="stSidebar"] .block-container { padding: 2rem 1.2rem !important; }

.brand {
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: -0.3px;
    color: #FFFFFF;
    margin-bottom: 2rem;
    display: block;
}

.sidebar-label {
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #555;
    margin: 1.5rem 0 0.6rem 0;
}

/* ── Hero strip ──────────────────────────── */
.hero-strip {
    background: #000;
    padding: 3.5rem 3rem 3rem 3rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    margin-bottom: 0;
}
.hero-kicker {
    font-size: 0.62rem;
    font-weight: 600;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #0A84FF;
    margin-bottom: 1rem;
}
.hero-h1 {
    font-size: 3.8rem;
    font-weight: 700;
    letter-spacing: -2px;
    line-height: 1.0;
    color: #fff;
    margin: 0 0 1rem 0;
}
.hero-p {
    font-size: 1rem;
    font-weight: 300;
    color: #555;
    line-height: 1.7;
    max-width: 440px;
    font-style: italic;
}

/* ── Results area ────────────────────────── */
.results-wrap { padding: 2.5rem 3rem; }

.section-eyebrow {
    font-size: 0.58rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #444;
    margin: 0 0 1.2rem 0;
}
.section-title {
    font-size: 1.3rem;
    font-weight: 600;
    letter-spacing: -0.5px;
    color: #F5F5F7;
    margin: 0 0 1.5rem 0;
}

/* ── Product card ────────────────────────── */
.card-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 0.6rem; }

.p-card {
    position: relative;
    border-radius: 14px;
    overflow: hidden;
    background: #111;
    aspect-ratio: 3 / 4;
    cursor: pointer;
    transition: transform 0.3s cubic-bezier(0.25,0.46,0.45,0.94),
                box-shadow 0.3s ease;
}
.p-card:hover {
    transform: translateY(-4px) scale(1.01);
    box-shadow: 0 20px 40px rgba(0,0,0,0.6);
}
.p-card img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}

/* rank badge */
.p-rank {
    position: absolute;
    top: 10px;
    left: 10px;
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: rgba(0,0,0,0.55);
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
    border: 1px solid rgba(255,255,255,0.12);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.65rem;
    font-weight: 700;
    color: #fff;
}

/* score overlay at bottom */
.p-footer {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    padding: 28px 12px 12px 12px;
    background: linear-gradient(to top, rgba(0,0,0,0.75) 0%, transparent 100%);
    display: flex;
    flex-direction: column;
    gap: 3px;
}
.p-score {
    font-size: 0.72rem;
    font-weight: 600;
    color: rgba(255,255,255,0.9);
    letter-spacing: 0.02em;
}
.p-meta {
    display: flex;
    gap: 5px;
}
.p-boost  { font-size: 0.62rem; color: #30D158; font-weight: 500; }
.p-penalty{ font-size: 0.62rem; color: #FF453A; font-weight: 500; }

/* ── Preference chips ────────────────────── */
.chips { display: flex; flex-wrap: wrap; gap: 7px; margin-bottom: 2rem; }
.chip {
    font-size: 0.72rem;
    font-weight: 500;
    padding: 4px 13px;
    border-radius: 100px;
}
.chip-g { background: rgba(48,209,88,0.1);  color: #30D158; border: 1px solid rgba(48,209,88,0.25); }
.chip-a { background: rgba(255,69,58,0.1);  color: #FF453A; border: 1px solid rgba(255,69,58,0.25); }

/* ── Divider ─────────────────────────────── */
.rule { border: none; border-top: 1px solid rgba(255,255,255,0.05); margin: 2.5rem 0; }

/* ── Query card (uploaded image) ─────────── */
.query-card {
    border-radius: 16px;
    overflow: hidden;
    background: #111;
    border: 1px solid rgba(255,255,255,0.06);
}
.query-card img { width: 100%; display: block; }
.query-label {
    padding: 10px 14px;
    font-size: 0.62rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #444;
}

/* ── "New" badge on reranked cards ───────── */
.p-new {
    position: absolute;
    top: 10px;
    right: 10px;
    font-size: 0.55rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    background: #0A84FF;
    color: #fff;
    padding: 2px 7px;
    border-radius: 100px;
}

/* ── Score legend ────────────────────────── */
.legend {
    display: flex;
    gap: 1.2rem;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(255,255,255,0.04);
}
.legend-item {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 0.65rem;
    color: #555;
}
.legend-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}

/* ── No-preference notice ────────────────── */
.notice {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 10px 16px;
    font-size: 0.78rem;
    color: #666;
    margin-bottom: 1.5rem;
}

/* ── Catalog stat pill ───────────────────── */
.stat-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 100px;
    padding: 4px 14px;
    font-size: 0.68rem;
    color: #666;
    margin-top: 1.2rem;
}
.stat-dot { width: 6px; height: 6px; border-radius: 50%; background: #30D158; }
</style>
""", unsafe_allow_html=True)


# ── helpers ────────────────────────────────────────────────────────────────────
def img_b64(path: str) -> str:
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    ext = Path(path).suffix.lower().lstrip(".")
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext
    return f"data:image/{mime};base64,{data}"


def pil_b64(pil_img: Image.Image) -> str:
    import io
    buf = io.BytesIO()
    pil_img.save(buf, format="JPEG")
    data = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/jpeg;base64,{data}"


def base_card(rank: int, r: dict) -> str:
    src = img_b64(r["image_path"])
    return f"""
    <div class="p-card">
        <img src="{src}" alt="result {rank}" />
        <div class="p-rank">{rank}</div>
        <div class="p-footer">
            <span class="p-score">{r['score']:.3f}</span>
        </div>
    </div>"""


def rerank_card(rank: int, r: dict, is_new: bool = False) -> str:
    src = img_b64(r["image_path"])
    new_badge = '<span class="p-new">New</span>' if is_new else ""
    return f"""
    <div class="p-card">
        <img src="{src}" alt="result {rank}" />
        <div class="p-rank">{rank}</div>
        {new_badge}
        <div class="p-footer">
            <span class="p-score">{r['final_score']:.3f}</span>
            <div class="p-meta">
                <span class="p-boost">+{r['goal_bonus']:.3f}</span>
                <span class="p-penalty">−{r['avoid_penalty']:.3f}</span>
            </div>
        </div>
    </div>"""


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<span class="brand">Wardrobe AI</span>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload", type=["jpg", "jpeg", "png"], label_visibility="collapsed"
    )

    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        encoded = pil_b64(image)
        st.markdown(
            f'<div class="query-card"><img src="{encoded}" />'
            f'<div class="query-label">Your item</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<p class="sidebar-label">Style</p>', unsafe_allow_html=True)
    more_style = st.selectbox("Make it more...", ["any", "formal", "casual", "minimal", "sporty"])
    avoid_features = st.multiselect("Avoid...", ["cropped", "hood", "skinny fit", "logos"])
    fit_preference = st.selectbox("Fit", ["any", "slim", "regular", "relaxed", "oversized"])
    free_text_pref = st.text_input("", placeholder="other preferences...", label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    search_btn = st.button("Find Similar Items", use_container_width=True, type="primary")


# ── Catalog size (cached, won't re-run unless artifacts change) ────────────────
try:
    _, catalog_paths = load_catalog()
    catalog_count = len(catalog_paths)
    stat_html = (
        f'<div class="stat-pill"><span class="stat-dot"></span>'
        f'{catalog_count:,} items in catalog</div>'
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
        '<div style="padding:2rem 3rem; color:#444; font-size:0.9rem;">Upload a clothing image in the sidebar to begin.</div>',
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

    # ── Step-by-step progress ──
    status = st.empty()
    status.markdown('<p style="color:#555;font-size:0.85rem;">⬡ Removing background…</p>', unsafe_allow_html=True)

    status.markdown('<p style="color:#555;font-size:0.85rem;">⬡ Searching catalog…</p>', unsafe_allow_html=True)
    candidates = retrieve_similar_items(temp_path, top_k=20)
    results = candidates[:5]

    status.markdown('<p style="color:#555;font-size:0.85rem;">⬡ Applying preferences…</p>', unsafe_allow_html=True)
    reranked_results = rerank_results(candidates, preference_schema)[:5]
    status.empty()

    # ── Active chips ──
    goals = preference_schema.get("goals", [])
    avoid = preference_schema.get("avoid", [])

    st.markdown('<div class="results-wrap">', unsafe_allow_html=True)

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
    cards_html = '<div class="card-grid">' + "".join(base_card(i+1, r) for i, r in enumerate(results)) + '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

    st.markdown('<hr class="rule">', unsafe_allow_html=True)

    # ── Reranked grid ──
    st.markdown('<p class="section-eyebrow">Preference Ranking</p><p class="section-title">Styled for You</p>', unsafe_allow_html=True)

    if not goals and not avoid:
        st.markdown(
            '<div class="notice">No style preferences active — results match visual similarity. '
            'Try selecting a style above to see personalized reranking.</div>',
            unsafe_allow_html=True,
        )

    base_paths = {r["image_path"] for r in results}
    cards_html = '<div class="card-grid">' + "".join(
        rerank_card(i+1, r, is_new=(r["image_path"] not in base_paths))
        for i, r in enumerate(reranked_results)
    ) + '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

    # ── Score legend ──
    st.markdown("""
    <div class="legend">
        <span class="legend-item"><span class="legend-dot" style="background:#fff"></span>Base similarity score</span>
        <span class="legend-item"><span class="legend-dot" style="background:#0A84FF"></span>Final score after preferences</span>
        <span class="legend-item"><span class="legend-dot" style="background:#30D158"></span>Goal match bonus</span>
        <span class="legend-item"><span class="legend-dot" style="background:#FF453A"></span>Avoid penalty</span>
        <span class="legend-item"><span class="legend-dot" style="background:#0A84FF"></span>New — not in top 5 base</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown(
        '<div style="padding:2rem 3rem; color:#444; font-size:0.9rem;">Set your preferences and click <strong style="color:#888">Find Similar Items</strong>.</div>',
        unsafe_allow_html=True,
    )
