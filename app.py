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
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,300;0,14..32,400;0,14..32,500;0,14..32,600;0,14..32,700;0,14..32,800;1,14..32,300&display=swap');

:root {
    --bg:       #000000;
    --s1:       #0C0C0C;
    --s2:       #141414;
    --border:   rgba(255,255,255,0.06);
    --border-h: rgba(255,255,255,0.14);
    --text:     #F5F5F7;
    --muted:    #86868B;
    --dim:      #3A3A3C;
    --blue:     #0A84FF;
    --green:    #30D158;
    --red:      #FF453A;
    --purple:   #BF5AF2;
}

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif !important;
    font-feature-settings: "cv02","cv03","cv04","cv11";
    background: var(--bg) !important;
    color: var(--text) !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ─── Animations ──────────────────────────────────── */
@keyframes fadeUp {
    from { opacity:0; transform:translateY(18px); }
    to   { opacity:1; transform:translateY(0); }
}
@keyframes pulse-orb {
    0%,100% { transform: scale(1) translate(0,0); opacity:.7; }
    50%      { transform: scale(1.12) translate(20px,-15px); opacity:1; }
}
@keyframes shimmer {
    0%   { background-position: -200% center; }
    100% { background-position:  200% center; }
}
@keyframes glow-ring {
    0%,100% { box-shadow: 0 0 0 0 rgba(10,132,255,0); }
    50%      { box-shadow: 0 0 0 3px rgba(10,132,255,0.35); }
}

/* ─── Sidebar ─────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--s1) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .block-container {
    padding: 2.2rem 1.4rem !important;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label {
    font-size: 0.72rem !important;
    color: var(--muted) !important;
    font-weight: 500 !important;
}
.brand {
    font-size: 0.95rem;
    font-weight: 700;
    letter-spacing: -0.4px;
    color: var(--text);
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 2rem;
}
.brand-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--blue);
    box-shadow: 0 0 8px rgba(10,132,255,0.6);
}
.sidebar-rule { border:none; border-top:1px solid var(--border); margin:1.4rem 0; }
.sidebar-section {
    font-size: 0.58rem; font-weight: 600;
    letter-spacing: 0.18em; text-transform: uppercase;
    color: var(--dim); margin-bottom: 0.8rem;
}

/* query thumbnail in sidebar */
.q-thumb-wrap {
    border-radius: 14px; overflow: hidden;
    border: 1px solid var(--border); margin-bottom: 1.2rem;
    position: relative;
}
.q-thumb-wrap img { width:100%; display:block; }
.q-thumb-label {
    position: absolute; bottom:0; left:0; right:0;
    padding: 20px 12px 10px 12px;
    background: linear-gradient(to top, rgba(0,0,0,0.7), transparent);
    font-size: 0.6rem; font-weight:600; letter-spacing:0.14em;
    text-transform: uppercase; color: rgba(255,255,255,0.5);
}

/* ─── Hero ────────────────────────────────────────── */
.hero {
    position: relative; overflow: hidden;
    background: var(--bg);
    background-image: radial-gradient(rgba(255,255,255,0.025) 1px, transparent 1px);
    background-size: 28px 28px;
    padding: 4rem 3.5rem 3.5rem;
    border-bottom: 1px solid var(--border);
}
.hero-orb {
    position: absolute; border-radius: 50%;
    filter: blur(80px); pointer-events: none;
    animation: pulse-orb 8s ease-in-out infinite;
}
.orb1 { width:520px; height:520px; background:rgba(10,132,255,0.07); top:-180px; left:-80px; }
.orb2 { width:380px; height:380px; background:rgba(191,90,242,0.06); top:-60px; right:80px; animation-delay:-4s; }
.orb3 { width:300px; height:300px; background:rgba(48,209,88,0.04);  bottom:-80px; left:30%; animation-delay:-2s; }
.hero-inner { position:relative; z-index:1; }
.hero-eyebrow {
    display: inline-flex; align-items: center; gap: 8px;
    font-size: 0.65rem; font-weight: 600; letter-spacing: 0.2em;
    text-transform: uppercase; color: var(--blue);
    background: rgba(10,132,255,0.08);
    border: 1px solid rgba(10,132,255,0.2);
    padding: 4px 14px; border-radius: 100px; margin-bottom: 1.5rem;
}
.hero-h1 {
    font-size: 4.5rem; font-weight: 800;
    letter-spacing: -2.5px; line-height: 0.95;
    color: var(--text); margin: 0 0 1.2rem 0;
}
.hero-h1 span {
    background: linear-gradient(135deg, #fff 30%, rgba(255,255,255,0.45));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-sub {
    font-size: 1rem; font-weight: 300; font-style: italic;
    color: var(--muted); line-height: 1.7; max-width: 480px;
    margin-bottom: 1.8rem;
}
.hero-meta { display:flex; align-items:center; gap:1rem; flex-wrap:wrap; }
.stat-badge {
    display:inline-flex; align-items:center; gap:7px;
    background: rgba(255,255,255,0.04);
    border: 1px solid var(--border);
    border-radius: 100px; padding: 5px 14px;
    font-size: 0.7rem; color: var(--muted);
}
.live-dot {
    width:7px; height:7px; border-radius:50%;
    background: var(--green);
    box-shadow: 0 0 6px rgba(48,209,88,0.7);
    animation: pulse-orb 2s ease-in-out infinite;
}

/* ─── Results wrapper ─────────────────────────────── */
.rw { padding: 2.8rem 3.5rem; }

.section-head { margin-bottom: 1.6rem; }
.section-kicker {
    font-size: 0.58rem; font-weight:600; letter-spacing:0.2em;
    text-transform:uppercase; color: var(--dim); margin-bottom:0.35rem;
}
.section-title {
    font-size: 1.4rem; font-weight:700; letter-spacing:-0.6px;
    color: var(--text); margin:0;
}

/* ─── Query row ───────────────────────────────────── */
.q-row {
    display:flex; align-items:center; gap:16px;
    margin-bottom: 2rem;
    padding: 14px 18px;
    background: var(--s1);
    border: 1px solid var(--border);
    border-radius: 16px;
    width: fit-content;
}
.q-img {
    width:52px; height:68px; border-radius:8px;
    overflow:hidden; flex-shrink:0;
    border:1px solid var(--border);
}
.q-img img { width:100%; height:100%; object-fit:cover; display:block; }
.q-arrow { color: var(--dim); font-size:1.1rem; }
.q-text { display:flex; flex-direction:column; gap:3px; }
.q-text-label { font-size:0.6rem; font-weight:600; letter-spacing:0.15em; text-transform:uppercase; color:var(--dim); }
.q-text-val   { font-size:0.88rem; font-weight:500; color:var(--text); }

/* ─── Preference chips ────────────────────────────── */
.pref-row { display:flex; flex-wrap:wrap; gap:7px; margin-bottom:1.8rem; }
.pref-chip {
    font-size:0.72rem; font-weight:500;
    padding:4px 14px; border-radius:100px;
}
.pc-g { background:rgba(48,209,88,.08);  color:var(--green); border:1px solid rgba(48,209,88,.2); }
.pc-a { background:rgba(255,69,58,.08);  color:var(--red);   border:1px solid rgba(255,69,58,.2); }

/* ─── Card grid ───────────────────────────────────── */
.card-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 14px;
}

.p-card {
    position: relative;
    border-radius: 16px;
    overflow: hidden;
    background: var(--s2);
    aspect-ratio: 3 / 4;
    border: 1px solid var(--border);
    cursor: pointer;
    transition:
        transform .35s cubic-bezier(.25,.46,.45,.94),
        box-shadow .35s ease,
        border-color .35s ease;
    animation: fadeUp .55s ease both;
}
/* stagger */
.p-card:nth-child(1){animation-delay:.04s}
.p-card:nth-child(2){animation-delay:.09s}
.p-card:nth-child(3){animation-delay:.14s}
.p-card:nth-child(4){animation-delay:.19s}
.p-card:nth-child(5){animation-delay:.24s}

.p-card:hover {
    transform: translateY(-6px) scale(1.015);
    box-shadow: 0 28px 56px rgba(0,0,0,.75);
    border-color: var(--border-h);
}
/* shimmer sweep on hover */
.p-card::after {
    content:""; position:absolute; inset:0;
    background: linear-gradient(105deg, transparent 40%, rgba(255,255,255,0.04) 50%, transparent 60%);
    background-size: 200% 100%;
    opacity:0; transition: opacity .3s;
    pointer-events: none;
}
.p-card:hover::after {
    opacity:1;
    animation: shimmer .8s ease forwards;
}

.p-card img { width:100%; height:100%; object-fit:cover; display:block; }

/* #1 card in reranked — glowing border */
.p-card.top-pick {
    border-color: rgba(10,132,255,0.35);
    animation: fadeUp .55s ease .04s both, glow-ring 3s ease-in-out 1s infinite;
}

/* rank badge */
.p-rank {
    position: absolute; top:10px; left:10px;
    width:27px; height:27px; border-radius:50%;
    background: rgba(0,0,0,0.65);
    backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.14);
    display:flex; align-items:center; justify-content:center;
    font-size:.65rem; font-weight:700; color:#fff;
}

/* rank change badge */
.p-change {
    position:absolute; top:10px; right:10px;
    font-size:.58rem; font-weight:700;
    padding: 3px 8px; border-radius:100px;
    letter-spacing:.04em; backdrop-filter:blur(8px);
    -webkit-backdrop-filter:blur(8px);
}
.pc-up   { background:rgba(48,209,88,.18);  color:var(--green); border:1px solid rgba(48,209,88,.3); }
.pc-down { background:rgba(255,69,58,.15);  color:var(--red);   border:1px solid rgba(255,69,58,.25); }
.pc-same { background:rgba(255,255,255,.06);color:var(--dim);   border:1px solid rgba(255,255,255,.1); }
.pc-new  { background:rgba(10,132,255,.18); color:var(--blue);  border:1px solid rgba(10,132,255,.3); }

/* glass footer overlay */
.p-footer {
    position: absolute; bottom:0; left:0; right:0;
    padding: 36px 12px 13px;
    background: linear-gradient(to top, rgba(0,0,0,.85) 0%, rgba(0,0,0,.3) 60%, transparent 100%);
    backdrop-filter: blur(0px);
    display: flex; flex-direction: column; gap: 4px;
    transition: backdrop-filter .3s;
}
.p-card:hover .p-footer { backdrop-filter: blur(2px); }

.p-score {
    font-size:.73rem; font-weight:600;
    color:rgba(255,255,255,.92); letter-spacing:.02em;
}
.p-meta { display:flex; gap:6px; }
.p-boost   { font-size:.62rem; font-weight:500; color:var(--green); }
.p-penalty { font-size:.62rem; font-weight:500; color:var(--red); }

/* ─── Notice ──────────────────────────────────────── */
.notice {
    background: rgba(255,255,255,.02);
    border: 1px solid rgba(255,255,255,.06);
    border-radius: 12px;
    padding: 11px 18px;
    font-size:.8rem; color:var(--muted);
    margin-bottom:1.6rem;
    display:flex; align-items:center; gap:9px;
}

/* ─── Legend ──────────────────────────────────────── */
.legend {
    display:flex; flex-wrap:wrap; gap:1.4rem;
    margin-top:1.4rem; padding-top:1.2rem;
    border-top:1px solid var(--border);
}
.li { display:flex; align-items:center; gap:6px; font-size:.66rem; color:var(--muted); }
.ld { width:7px; height:7px; border-radius:50%; flex-shrink:0; }

/* ─── Divider ─────────────────────────────────────── */
.rule { border:none; border-top:1px solid var(--border); margin:2.8rem 0; }

/* ─── Empty state ─────────────────────────────────── */
.empty-state {
    padding: 4rem 3.5rem;
    display: flex; flex-direction: column;
    gap: 1.2rem;
    color: var(--dim);
}
.empty-state-title { font-size:1rem; font-weight:500; color:var(--muted); }
.empty-steps { display:flex; flex-direction:column; gap:.7rem; }
.empty-step {
    display:flex; align-items:center; gap:10px;
    font-size:.82rem; color:var(--dim);
}
.step-num {
    width:22px; height:22px; border-radius:50%;
    background:var(--s2); border:1px solid var(--border);
    display:flex; align-items:center; justify-content:center;
    font-size:.6rem; font-weight:600; flex-shrink:0; color:var(--muted);
}
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
    pil_img.save(buf, format="JPEG", quality=85)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def change_badge(old: int | None, new: int) -> str:
    if old is None:
        return '<span class="p-change pc-new">NEW</span>'
    d = old - new
    if d > 0: return f'<span class="p-change pc-up">↑{d}</span>'
    if d < 0: return f'<span class="p-change pc-down">↓{abs(d)}</span>'
    return '<span class="p-change pc-same">=</span>'


def base_card(rank: int, r: dict) -> str:
    src = img_b64(r["image_path"])
    return (
        f'<div class="p-card">'
        f'<img src="{src}" alt="{rank}" loading="lazy"/>'
        f'<div class="p-rank">{rank}</div>'
        f'<div class="p-footer"><span class="p-score">{r["score"]:.3f}</span></div>'
        f'</div>'
    )


def rerank_card(new_rank: int, r: dict, old: int | None) -> str:
    src = img_b64(r["image_path"])
    top = ' top-pick' if new_rank == 1 else ''
    badge = change_badge(old, new_rank)
    return (
        f'<div class="p-card{top}">'
        f'<img src="{src}" alt="{new_rank}" loading="lazy"/>'
        f'<div class="p-rank">{new_rank}</div>'
        f'{badge}'
        f'<div class="p-footer">'
        f'<span class="p-score">{r["final_score"]:.3f}</span>'
        f'<div class="p-meta">'
        f'<span class="p-boost">+{r["goal_bonus"]:.3f}</span>'
        f'<span class="p-penalty">−{r["avoid_penalty"]:.3f}</span>'
        f'</div></div></div>'
    )


# ── Session state ──────────────────────────────────────────────────────────────
for k in ("candidates", "results", "reranked", "query_b64", "pref_schema"):
    if k not in st.session_state:
        st.session_state[k] = None


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div class="brand"><span class="brand-dot"></span>Wardrobe AI</div>',
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Drop your clothing image here",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
    )

    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        encoded = pil_b64(image)
        st.markdown(
            f'<div class="q-thumb-wrap">'
            f'<img src="{encoded}" />'
            f'<div class="q-thumb-label">Your item</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="sidebar-rule">', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-section">Style Preferences</p>', unsafe_allow_html=True)

    more_style     = st.selectbox("Make it more...", ["any","formal","casual","minimal","sporty"])
    avoid_features = st.multiselect("Avoid...", ["cropped","hood","skinny fit","logos"])
    fit_preference = st.selectbox("Fit", ["any","slim","regular","relaxed","oversized"])
    free_text_pref = st.text_input("Free text", placeholder="e.g. more minimal, avoid logos...", label_visibility="collapsed")

    st.markdown('<hr class="sidebar-rule">', unsafe_allow_html=True)

    search_btn = st.button("Find Similar Items", use_container_width=True, type="primary")
    rerank_btn = st.button(
        "Re-rank with New Preferences",
        use_container_width=True,
        disabled=(st.session_state.candidates is None),
    )


# ── Catalog count ──────────────────────────────────────────────────────────────
try:
    _, cpaths = load_catalog()
    stat_html = (
        f'<span class="stat-badge"><span class="live-dot"></span>'
        f'{len(cpaths):,} items indexed</span>'
    )
except Exception:
    stat_html = ""


# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
    <div class="hero-orb orb1"></div>
    <div class="hero-orb orb2"></div>
    <div class="hero-orb orb3"></div>
    <div class="hero-inner">
        <div class="hero-eyebrow">AI-Powered Fashion Retrieval</div>
        <h1 class="hero-h1">
            <span>Find your<br>next outfit.</span>
        </h1>
        <p class="hero-sub">Upload any clothing piece and instantly discover visually similar items, ranked intelligently by your personal style preferences.</p>
        <div class="hero-meta">{stat_html}</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Empty state ────────────────────────────────────────────────────────────────
if not uploaded_file:
    st.markdown("""
    <div class="empty-state">
        <p class="empty-state-title">Get started in 3 steps</p>
        <div class="empty-steps">
            <div class="empty-step"><span class="step-num">1</span>Upload a clothing image in the sidebar</div>
            <div class="empty-step"><span class="step-num">2</span>Set your style preferences</div>
            <div class="empty-step"><span class="step-num">3</span>Click Find Similar Items</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
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

    prog = st.empty()
    prog.markdown('<p style="padding:1rem 3.5rem;color:var(--dim,#444);font-size:.82rem;font-family:Inter,sans-serif">Removing background…</p>', unsafe_allow_html=True)
    candidates = retrieve_similar_items(temp_path, top_k=20)
    prog.markdown('<p style="padding:1rem 3.5rem;color:var(--dim,#444);font-size:.82rem;font-family:Inter,sans-serif">Applying preferences…</p>', unsafe_allow_html=True)
    reranked = rerank_results(candidates, pref)[:5]
    prog.empty()

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


# ── Render ─────────────────────────────────────────────────────────────────────
if st.session_state.results is None:
    st.markdown(
        '<div style="padding:2rem 3.5rem;color:#3A3A3C;font-size:.9rem;font-family:Inter,sans-serif">'
        'Set your preferences and click <strong style="color:#666">Find Similar Items</strong>.</div>',
        unsafe_allow_html=True,
    )
    st.stop()

results          = st.session_state.results
reranked_results = st.session_state.reranked
pref_schema      = st.session_state.pref_schema
goals            = pref_schema.get("goals", [])
avoid            = pref_schema.get("avoid", [])
base_rank_map    = {r["image_path"]: i + 1 for i, r in enumerate(st.session_state.candidates)}

st.markdown('<div class="rw">', unsafe_allow_html=True)

# query row
qb = st.session_state.query_b64
st.markdown(
    f'<div class="q-row">'
    f'<div class="q-img"><img src="{qb}"/></div>'
    f'<span class="q-arrow">→</span>'
    f'<div class="q-text">'
    f'<span class="q-text-label">Searching for</span>'
    f'<span class="q-text-val">Similar items in catalog</span>'
    f'</div></div>',
    unsafe_allow_html=True,
)

# preference chips
if goals or avoid:
    chips = '<div class="pref-row">'
    for g in goals: chips += f'<span class="pref-chip pc-g">+ {g.replace("_"," ")}</span>'
    for a in avoid: chips += f'<span class="pref-chip pc-a">− {a.replace("_"," ")}</span>'
    chips += '</div>'
    st.markdown(chips, unsafe_allow_html=True)

# base results
st.markdown(
    '<div class="section-head">'
    '<p class="section-kicker">Visual Similarity</p>'
    '<p class="section-title">Closest Matches</p>'
    '</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="card-grid">' +
    "".join(base_card(i+1, r) for i, r in enumerate(results)) +
    '</div>',
    unsafe_allow_html=True,
)

st.markdown('<hr class="rule">', unsafe_allow_html=True)

# reranked results
st.markdown(
    '<div class="section-head">'
    '<p class="section-kicker">Preference Ranking</p>'
    '<p class="section-title">Styled for You</p>'
    '</div>',
    unsafe_allow_html=True,
)

if not goals and not avoid:
    st.markdown(
        '<div class="notice">💡 No style preferences set — both rows show visual similarity. '
        'Select a goal or something to avoid to see personalized reranking.</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="card-grid">' +
    "".join(
        rerank_card(i+1, r, base_rank_map.get(r["image_path"]))
        for i, r in enumerate(reranked_results)
    ) +
    '</div>',
    unsafe_allow_html=True,
)

# legend
st.markdown("""
<div class="legend">
    <span class="li"><span class="ld" style="background:var(--green)"></span>↑ Moved up by preferences</span>
    <span class="li"><span class="ld" style="background:var(--red)"></span>↓ Moved down</span>
    <span class="li"><span class="ld" style="background:var(--blue)"></span>NEW — surfaced from outside top 5</span>
    <span class="li"><span class="ld" style="background:#3A3A3C"></span>= Unchanged</span>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
