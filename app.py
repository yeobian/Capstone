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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif !important;
    background: #000 !important;
    color: #F5F5F7 !important;
}
#MainMenu, footer { visibility: hidden; }
[data-testid="stToolbar"] { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stSidebar"] {
    background: #0C0C0C !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] .block-container { padding: 2rem 1.4rem !important; }
[data-testid="stSidebar"] label { font-size: 0.72rem !important; color: #86868B !important; font-weight: 500 !important; }

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes glowPulse {
    0%,100% { box-shadow: 0 0 0 1px rgba(10,132,255,0.3), 0 0 20px rgba(10,132,255,0.1); }
    50%      { box-shadow: 0 0 0 1px rgba(10,132,255,0.6), 0 0 32px rgba(10,132,255,0.25); }
}

/* ── sidebar brand ── */
.brand { display:flex; align-items:center; gap:8px; margin-bottom:1.8rem; }
.brand-name { font-size:.95rem; font-weight:700; letter-spacing:-.3px; color:#F5F5F7; }
.brand-dot  { width:8px; height:8px; border-radius:50%; background:#0A84FF; box-shadow:0 0 8px rgba(10,132,255,.7); }
.sb-rule    { border:none; border-top:1px solid rgba(255,255,255,.06); margin:1.4rem 0; }
.sb-label   { font-size:.58rem; font-weight:600; letter-spacing:.18em; text-transform:uppercase; color:#3A3A3C; margin-bottom:.7rem; }

/* ── query thumbnail (sidebar) ── */
.qt { border-radius:12px; overflow:hidden; border:1px solid rgba(255,255,255,.07); margin-bottom:1.2rem; position:relative; }
.qt img { width:100%; display:block; }
.qt-label { position:absolute; bottom:0; left:0; right:0; padding:20px 10px 8px;
    background:linear-gradient(to top,rgba(0,0,0,.65),transparent);
    font-size:.58rem; font-weight:600; letter-spacing:.14em; text-transform:uppercase; color:rgba(255,255,255,.45); }

/* ── hero ── */
.hero {
    padding: 4rem 3.5rem 3.2rem;
    border-bottom: 1px solid rgba(255,255,255,.05);
    background:
        radial-gradient(ellipse 550px 380px at 8% 55%, rgba(10,132,255,.08) 0%, transparent 70%),
        radial-gradient(ellipse 420px 300px at 88% 15%, rgba(191,90,242,.06) 0%, transparent 65%),
        radial-gradient(rgba(255,255,255,.022) 1px, transparent 1px),
        #000;
    background-size: 100% 100%, 100% 100%, 28px 28px, auto;
}
.hero-eyebrow {
    display:inline-flex; align-items:center; gap:7px;
    font-size:.62rem; font-weight:600; letter-spacing:.2em; text-transform:uppercase;
    color:#0A84FF; background:rgba(10,132,255,.1); border:1px solid rgba(10,132,255,.2);
    padding:4px 14px; border-radius:100px; margin-bottom:1.4rem;
}
.hero-h1 { font-size:4.2rem; font-weight:800; letter-spacing:-2.5px; line-height:.95; color:#F5F5F7; margin:0 0 1.1rem; }
.hero-sub { font-size:.98rem; font-weight:300; font-style:italic; color:#86868B; line-height:1.7; max-width:460px; margin:0 0 1.6rem; }
.hero-stat {
    display:inline-flex; align-items:center; gap:7px;
    background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.08);
    border-radius:100px; padding:5px 14px; font-size:.7rem; color:#86868B;
}
.live-dot { width:7px; height:7px; border-radius:50%; background:#30D158; box-shadow:0 0 6px rgba(48,209,88,.7); }

/* ── results section ── */
.rblock { padding: 2.8rem 3.5rem 0; }
.sec-kicker { font-size:.58rem; font-weight:600; letter-spacing:.2em; text-transform:uppercase; color:#3A3A3C; margin:0 0 .35rem; }
.sec-title  { font-size:1.35rem; font-weight:700; letter-spacing:-.6px; color:#F5F5F7; margin:0 0 1.5rem; }

/* ── query row ── */
.qrow {
    display:inline-flex; align-items:center; gap:14px;
    background:#0C0C0C; border:1px solid rgba(255,255,255,.07);
    border-radius:14px; padding:12px 18px; margin-bottom:1.8rem;
}
.qrow-img { width:50px; height:66px; border-radius:8px; overflow:hidden; border:1px solid rgba(255,255,255,.08); flex-shrink:0; }
.qrow-img img { width:100%; height:100%; object-fit:cover; display:block; }
.qrow-arrow { color:#3A3A3C; font-size:1rem; }
.qrow-label { font-size:.58rem; font-weight:600; letter-spacing:.15em; text-transform:uppercase; color:#3A3A3C; margin-bottom:3px; }
.qrow-val   { font-size:.88rem; font-weight:500; color:#F5F5F7; }

/* ── chips ── */
.chips { display:flex; flex-wrap:wrap; gap:7px; margin-bottom:1.6rem; }
.chip  { font-size:.72rem; font-weight:500; padding:4px 13px; border-radius:100px; }
.chip-g { background:rgba(48,209,88,.08);  color:#30D158; border:1px solid rgba(48,209,88,.2); }
.chip-a { background:rgba(255,69,58,.08);  color:#FF453A; border:1px solid rgba(255,69,58,.2); }

/* ── card grid ── */
.cgrid { display:grid; grid-template-columns:repeat(5,1fr); gap:14px; margin-bottom:1rem; }

.pcard {
    position:relative; border-radius:16px; overflow:hidden;
    background:#141414; aspect-ratio:3/4;
    border:1px solid rgba(255,255,255,.06);
    cursor:pointer;
    transition: transform .3s cubic-bezier(.25,.46,.45,.94), box-shadow .3s ease, border-color .3s ease;
    animation: fadeUp .5s ease both;
}
.pcard:nth-child(1){animation-delay:.05s}
.pcard:nth-child(2){animation-delay:.10s}
.pcard:nth-child(3){animation-delay:.15s}
.pcard:nth-child(4){animation-delay:.20s}
.pcard:nth-child(5){animation-delay:.25s}
.pcard:hover { transform:translateY(-5px) scale(1.012); box-shadow:0 24px 50px rgba(0,0,0,.75); border-color:rgba(255,255,255,.13); }
.pcard.top1  { border-color:rgba(10,132,255,.35); animation:fadeUp .5s ease .05s both, glowPulse 3s ease 1s infinite; }
.pcard img   { width:100%; height:100%; object-fit:cover; display:block; }

.prank {
    position:absolute; top:10px; left:10px;
    width:26px; height:26px; border-radius:50%;
    background:rgba(0,0,0,.65); border:1px solid rgba(255,255,255,.14);
    display:flex; align-items:center; justify-content:center;
    font-size:.64rem; font-weight:700; color:#fff;
}
.pbadge {
    position:absolute; top:10px; right:10px;
    font-size:.58rem; font-weight:700; padding:3px 8px; border-radius:100px; letter-spacing:.03em;
}
.b-up   { background:rgba(48,209,88,.18);  color:#30D158; border:1px solid rgba(48,209,88,.3); }
.b-down { background:rgba(255,69,58,.15);  color:#FF453A; border:1px solid rgba(255,69,58,.25); }
.b-same { background:rgba(255,255,255,.06);color:#3A3A3C; border:1px solid rgba(255,255,255,.1); }
.b-new  { background:rgba(10,132,255,.18); color:#0A84FF; border:1px solid rgba(10,132,255,.3); }

.pfooter {
    position:absolute; bottom:0; left:0; right:0;
    padding:32px 12px 12px;
    background:linear-gradient(to top,rgba(0,0,0,.82) 0%,rgba(0,0,0,.2) 70%,transparent 100%);
}
.pscore { font-size:.72rem; font-weight:600; color:rgba(255,255,255,.9); display:block; margin-bottom:3px; }
.pmeta  { display:flex; gap:6px; }
.pboost   { font-size:.62rem; font-weight:500; color:#30D158; }
.ppenalty { font-size:.62rem; font-weight:500; color:#FF453A; }

/* ── misc ── */
.hrule  { border:none; border-top:1px solid rgba(255,255,255,.05); margin:2.8rem 0 2.8rem; }
.notice { background:rgba(255,255,255,.02); border:1px solid rgba(255,255,255,.06); border-radius:12px; padding:11px 16px; font-size:.8rem; color:#86868B; margin-bottom:1.5rem; }
.legend { display:flex; flex-wrap:wrap; gap:1.2rem; padding-top:1.2rem; border-top:1px solid rgba(255,255,255,.05); margin-top:1.2rem; }
.li { display:flex; align-items:center; gap:6px; font-size:.65rem; color:#86868B; }
.ld { width:7px; height:7px; border-radius:50%; flex-shrink:0; }

/* ── empty state ── */
.estate { padding:4rem 3.5rem; }
.estate-title { font-size:1rem; font-weight:500; color:#86868B; margin-bottom:1.2rem; }
.estep { display:flex; align-items:center; gap:10px; font-size:.85rem; color:#3A3A3C; margin-bottom:.75rem; }
.estep-n { width:22px; height:22px; border-radius:50%; background:#141414; border:1px solid rgba(255,255,255,.08); display:flex; align-items:center; justify-content:center; font-size:.6rem; font-weight:600; color:#86868B; flex-shrink:0; }
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

def change_badge(old, new):
    if old is None: return '<span class="pbadge b-new">NEW</span>'
    d = old - new
    if d > 0: return f'<span class="pbadge b-up">↑{d}</span>'
    if d < 0: return f'<span class="pbadge b-down">↓{abs(d)}</span>'
    return '<span class="pbadge b-same">=</span>'

def base_card(rank, r):
    src = img_b64(r["image_path"])
    return (f'<div class="pcard"><img src="{src}" loading="lazy"/>'
            f'<div class="prank">{rank}</div>'
            f'<div class="pfooter"><span class="pscore">{r["score"]:.3f}</span></div></div>')

def rerank_card(rank, r, old):
    src = img_b64(r["image_path"])
    cls = ' top1' if rank == 1 else ''
    return (f'<div class="pcard{cls}"><img src="{src}" loading="lazy"/>'
            f'<div class="prank">{rank}</div>{change_badge(old, rank)}'
            f'<div class="pfooter"><span class="pscore">{r["final_score"]:.3f}</span>'
            f'<div class="pmeta"><span class="pboost">+{r["goal_bonus"]:.3f}</span>'
            f'<span class="ppenalty">−{r["avoid_penalty"]:.3f}</span></div></div></div>')


# ── Session state ──────────────────────────────────────────────────────────────
for k in ("candidates","results","reranked","query_b64","pref_schema"):
    if k not in st.session_state: st.session_state[k] = None


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="brand"><span class="brand-dot"></span><span class="brand-name">Wardrobe AI</span></div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload clothing image", type=["jpg","jpeg","png"], label_visibility="collapsed")

    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        enc = pil_b64(image)
        st.markdown(f'<div class="qt"><img src="{enc}"/><div class="qt-label">Your item</div></div>', unsafe_allow_html=True)

    st.markdown('<hr class="sb-rule"><p class="sb-label">Style Preferences</p>', unsafe_allow_html=True)
    more_style     = st.selectbox("Make it more...", ["any","formal","casual","minimal","sporty"])
    avoid_features = st.multiselect("Avoid...", ["cropped","hood","skinny fit","logos"])
    fit_preference = st.selectbox("Fit", ["any","slim","regular","relaxed","oversized"])
    free_text_pref = st.text_input("Other", placeholder="e.g. avoid logos, more minimal...", label_visibility="collapsed")
    st.markdown('<hr class="sb-rule">', unsafe_allow_html=True)
    search_btn = st.button("Find Similar Items", use_container_width=True, type="primary")
    rerank_btn = st.button("Re-rank with New Preferences", use_container_width=True, disabled=(st.session_state.candidates is None))


# ── Catalog count ──────────────────────────────────────────────────────────────
try:
    _, cpaths = load_catalog()
    stat_html = f'<span class="hero-stat"><span class="live-dot"></span>{len(cpaths):,} items indexed</span>'
except Exception:
    stat_html = ""


# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
    <div class="hero-eyebrow">AI-Powered Fashion Retrieval</div>
    <h1 class="hero-h1">Find your<br>next outfit.</h1>
    <p class="hero-sub">Upload any clothing piece and instantly discover visually similar items, ranked by your personal style preferences.</p>
    {stat_html}
</div>
""", unsafe_allow_html=True)


# ── Empty / waiting states ─────────────────────────────────────────────────────
if not uploaded_file:
    st.markdown("""<div class="estate">
        <p class="estate-title">Get started in 3 steps</p>
        <div class="estep"><span class="estep-n">1</span>Upload a clothing image in the sidebar</div>
        <div class="estep"><span class="estep-n">2</span>Set your style preferences</div>
        <div class="estep"><span class="estep-n">3</span>Click Find Similar Items</div>
    </div>""", unsafe_allow_html=True)
    st.stop()


# ── Full search ────────────────────────────────────────────────────────────────
if search_btn:
    pref = build_preference_schema(more_style=more_style, avoid_features=avoid_features,
                                   fit_preference=fit_preference, free_text=free_text_pref)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        image.save(tmp.name); temp_path = tmp.name

    prog = st.empty()
    prog.markdown('<p style="padding:1.5rem 3.5rem;color:#3A3A3C;font-size:.82rem;font-family:Inter,sans-serif">Removing background…</p>', unsafe_allow_html=True)
    candidates = retrieve_similar_items(temp_path, top_k=20)
    prog.markdown('<p style="padding:1.5rem 3.5rem;color:#3A3A3C;font-size:.82rem;font-family:Inter,sans-serif">Applying preferences…</p>', unsafe_allow_html=True)
    reranked = rerank_results(candidates, pref)[:5]
    prog.empty()

    st.session_state.candidates  = candidates
    st.session_state.results     = candidates[:5]
    st.session_state.reranked    = reranked
    st.session_state.query_b64   = pil_b64(image)
    st.session_state.pref_schema = pref


# ── Re-rank only ───────────────────────────────────────────────────────────────
if rerank_btn and st.session_state.candidates:
    pref = build_preference_schema(more_style=more_style, avoid_features=avoid_features,
                                   fit_preference=fit_preference, free_text=free_text_pref)
    st.session_state.reranked    = rerank_results(st.session_state.candidates, pref)[:5]
    st.session_state.pref_schema = pref


# ── Render results (all in ONE markdown block so divs work correctly) ──────────
if st.session_state.results is None:
    st.markdown('<p style="padding:2rem 3.5rem;color:#3A3A3C;font-size:.9rem;font-family:Inter,sans-serif">Set your preferences and click <strong style="color:#555">Find Similar Items</strong>.</p>', unsafe_allow_html=True)
    st.stop()

results          = st.session_state.results
reranked_results = st.session_state.reranked
pref_schema      = st.session_state.pref_schema
goals            = pref_schema.get("goals", [])
avoid            = pref_schema.get("avoid", [])
base_rank_map    = {r["image_path"]: i+1 for i, r in enumerate(st.session_state.candidates)}

# Build chips HTML
chips_html = ""
if goals or avoid:
    chips_html = '<div class="chips">'
    for g in goals: chips_html += f'<span class="chip chip-g">+ {g.replace("_"," ")}</span>'
    for a in avoid: chips_html += f'<span class="chip chip-a">− {a.replace("_"," ")}</span>'
    chips_html += '</div>'

# Build base grid
base_grid = '<div class="cgrid">' + "".join(base_card(i+1, r) for i, r in enumerate(results)) + '</div>'

# Build reranked grid
notice = '' if (goals or avoid) else '<div class="notice">💡 No style preferences set — select a goal or something to avoid to see personalized reranking.</div>'
rerank_grid = '<div class="cgrid">' + "".join(
    rerank_card(i+1, r, base_rank_map.get(r["image_path"]))
    for i, r in enumerate(reranked_results)
) + '</div>'

qb = st.session_state.query_b64

# Render everything in ONE call
st.markdown(f"""
<div style="padding:2.8rem 3.5rem 3rem;">

    <div class="qrow">
        <div class="qrow-img"><img src="{qb}"/></div>
        <span class="qrow-arrow">→</span>
        <div>
            <div class="qrow-label">Searching for</div>
            <div class="qrow-val">Similar items in catalog</div>
        </div>
    </div>

    {chips_html}

    <p class="sec-kicker">Visual Similarity</p>
    <p class="sec-title">Closest Matches</p>
    {base_grid}

    <div class="hrule"></div>

    <p class="sec-kicker">Preference Ranking</p>
    <p class="sec-title">Styled for You</p>
    {notice}
    {rerank_grid}

    <div class="legend">
        <span class="li"><span class="ld" style="background:#30D158"></span>↑ Moved up</span>
        <span class="li"><span class="ld" style="background:#FF453A"></span>↓ Moved down</span>
        <span class="li"><span class="ld" style="background:#0A84FF"></span>NEW — surfaced by preferences</span>
        <span class="li"><span class="ld" style="background:#3A3A3C"></span>= Same position</span>
    </div>
</div>
""", unsafe_allow_html=True)
