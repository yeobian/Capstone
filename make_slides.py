"""Generate capstone presentation slides."""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# -- Colors --
BG_DARK = RGBColor(0x1A, 0x1A, 0x2E)
BG_MED = RGBColor(0x16, 0x21, 0x3E)
ACCENT = RGBColor(0x53, 0x3C, 0xD0)
ACCENT_LIGHT = RGBColor(0x7C, 0x6B, 0xE6)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY = RGBColor(0xBB, 0xBB, 0xCC)
SOFT_GREEN = RGBColor(0x4E, 0xC9, 0xB0)
SOFT_ORANGE = RGBColor(0xE0, 0x9F, 0x3E)
SOFT_RED = RGBColor(0xE0, 0x5E, 0x5E)


def set_slide_bg(slide, color=BG_DARK):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_text_box(slide, left, top, width, height, text, font_size=18,
                 color=WHITE, bold=False, alignment=PP_ALIGN.LEFT, font_name="Calibri"):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.name = font_name
    p.alignment = alignment
    return tf


def add_bullet_list(slide, left, top, width, height, items, font_size=16,
                    color=WHITE, bullet_color=ACCENT_LIGHT):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = item
        p.font.size = Pt(font_size)
        p.font.color.rgb = color
        p.font.name = "Calibri"
        p.space_after = Pt(8)
        p.level = 0
    return tf


def add_accent_bar(slide, left, top, width, height, color=ACCENT):
    shape = slide.shapes.add_shape(1, left, top, width, height)  # rectangle
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()


# ============================================================
# SLIDE 1: Title
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
set_slide_bg(slide)
add_accent_bar(slide, Inches(0), Inches(3.2), Inches(13.333), Inches(0.06))

add_text_box(slide, Inches(1), Inches(1.5), Inches(11), Inches(1.5),
             "Personal Wardrobe Intelligence", font_size=44, bold=True, alignment=PP_ALIGN.CENTER)

add_text_box(slide, Inches(1), Inches(3.5), Inches(11), Inches(1),
             "Visual Clothing Retrieval with FashionCLIP, FAISS, and Preference-Aware Reranking",
             font_size=22, color=LIGHT_GRAY, alignment=PP_ALIGN.CENTER)

add_text_box(slide, Inches(1), Inches(5.2), Inches(11), Inches(0.6),
             "Capstone Project  |  April 2026",
             font_size=18, color=ACCENT_LIGHT, alignment=PP_ALIGN.CENTER)

# ============================================================
# SLIDE 2: Problem
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide)
add_accent_bar(slide, Inches(0.8), Inches(0.8), Inches(0.08), Inches(0.6), ACCENT)
add_text_box(slide, Inches(1.1), Inches(0.7), Inches(10), Inches(0.8),
             "The Problem", font_size=36, bold=True)

add_bullet_list(slide, Inches(1.1), Inches(2.0), Inches(11), Inches(4), [
    "People struggle to find visually similar clothing in their wardrobe",
    "Keyword search doesn't work for visual style matching",
    "No easy way to say \"find me something like this, but more formal\"",
    "Existing tools focus on shopping, not on understanding what you already own",
], font_size=22)

# ============================================================
# SLIDE 3: Proposed Solution
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide)
add_accent_bar(slide, Inches(0.8), Inches(0.8), Inches(0.08), Inches(0.6), ACCENT)
add_text_box(slide, Inches(1.1), Inches(0.7), Inches(10), Inches(0.8),
             "Proposed Solution", font_size=36, bold=True)

add_text_box(slide, Inches(1.1), Inches(1.8), Inches(11), Inches(0.8),
             "A retrieval-based system that uses visual embeddings to find similar clothing,\n"
             "then reranks results based on user style preferences.",
             font_size=20, color=LIGHT_GRAY)

add_bullet_list(slide, Inches(1.1), Inches(3.2), Inches(11), Inches(4), [
    "Upload a clothing image to a web app",
    "FashionCLIP encodes the image into a 512-dimensional embedding",
    "FAISS searches pre-computed catalog embeddings for nearest neighbors",
    "Top-5 most similar items are returned",
    "User selects style preferences (formal, casual, avoid hoods, etc.)",
    "Results are reranked using text-based goal bonuses and avoid penalties",
], font_size=20)

# ============================================================
# SLIDE 4: Architecture
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide)
add_accent_bar(slide, Inches(0.8), Inches(0.8), Inches(0.08), Inches(0.6), ACCENT)
add_text_box(slide, Inches(1.1), Inches(0.7), Inches(10), Inches(0.8),
             "Architecture", font_size=36, bold=True)

# Flow boxes
boxes = [
    ("Upload Image", ACCENT),
    ("FashionCLIP Encoder", RGBColor(0x3A, 0x50, 0x8F)),
    ("FAISS Index Search", RGBColor(0x3A, 0x50, 0x8F)),
    ("Preference Reranking", RGBColor(0x3A, 0x50, 0x8F)),
    ("Results Display", SOFT_GREEN),
]
box_w = Inches(2.0)
box_h = Inches(1.0)
start_x = Inches(0.9)
y = Inches(3.2)
gap = Inches(0.5)

for i, (label, color) in enumerate(boxes):
    x = start_x + i * (box_w + gap)
    shape = slide.shapes.add_shape(1, x, y, box_w, box_h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = label
    p.font.size = Pt(16)
    p.font.color.rgb = WHITE
    p.font.bold = True
    p.font.name = "Calibri"
    p.alignment = PP_ALIGN.CENTER
    tf.paragraphs[0].space_before = Pt(14)

    # Arrow
    if i < len(boxes) - 1:
        arrow_x = x + box_w + Inches(0.05)
        add_text_box(slide, arrow_x, y + Inches(0.2), Inches(0.4), Inches(0.6),
                     "→", font_size=28, color=ACCENT_LIGHT, alignment=PP_ALIGN.CENTER)

# Labels below boxes
sublabels = [
    "Streamlit UI",
    "512-dim embedding",
    "Top-5 neighbors",
    "Goal/Avoid scoring",
    "Baseline + Reranked",
]
for i, sub in enumerate(sublabels):
    x = start_x + i * (box_w + gap)
    add_text_box(slide, x, y + box_h + Inches(0.2), box_w, Inches(0.5),
                 sub, font_size=13, color=LIGHT_GRAY, alignment=PP_ALIGN.CENTER)

# ============================================================
# SLIDE 5: Tech Stack
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide)
add_accent_bar(slide, Inches(0.8), Inches(0.8), Inches(0.08), Inches(0.6), ACCENT)
add_text_box(slide, Inches(1.1), Inches(0.7), Inches(10), Inches(0.8),
             "Tech Stack", font_size=36, bold=True)

stack_items = [
    ("Web Application", "Streamlit"),
    ("Embedding Model", "FashionCLIP (ViT-B/32 fine-tuned on fashion data)"),
    ("Vector Search", "FAISS (IndexFlatIP — exact inner-product search)"),
    ("Preference Reranking", "FashionCLIP text embeddings + weighted scoring"),
    ("Image Processing", "Pillow, PyTorch, torchvision"),
    ("Dataset", "DeepFashion In-Shop Clothes Retrieval (local subset)"),
    ("Language", "Python 3.10+"),
]

for i, (label, value) in enumerate(stack_items):
    row_y = Inches(2.0) + Inches(i * 0.65)
    # Label
    add_text_box(slide, Inches(1.5), row_y, Inches(3.5), Inches(0.5),
                 label, font_size=18, color=ACCENT_LIGHT, bold=True)
    # Value
    add_text_box(slide, Inches(5.0), row_y, Inches(7), Inches(0.5),
                 value, font_size=18, color=WHITE)


# ============================================================
# SLIDE 6: Development Stages
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide)
add_accent_bar(slide, Inches(0.8), Inches(0.8), Inches(0.08), Inches(0.6), ACCENT)
add_text_box(slide, Inches(1.1), Inches(0.7), Inches(10), Inches(0.8),
             "Development Stages", font_size=36, bold=True)

# Stage 1
add_text_box(slide, Inches(1.1), Inches(1.9), Inches(3.5), Inches(0.5),
             "Stage 1: Baseline Retrieval", font_size=20, bold=True, color=SOFT_GREEN)
add_bullet_list(slide, Inches(1.1), Inches(2.5), Inches(3.5), Inches(2), [
    "OpenAI CLIP embeddings",
    "Brute-force cosine similarity",
    "Streamlit web demo",
    "Good on broad categories",
], font_size=15, color=LIGHT_GRAY)

# Stage 2
add_text_box(slide, Inches(5.0), Inches(1.9), Inches(3.5), Inches(0.5),
             "Stage 2: Preference Reranking", font_size=20, bold=True, color=SOFT_ORANGE)
add_bullet_list(slide, Inches(5.0), Inches(2.5), Inches(3.5), Inches(2), [
    "Style/fit/avoid UI controls",
    "Free-text preference parsing",
    "Text-based reranking scores",
    "Users can steer results",
], font_size=15, color=LIGHT_GRAY)

# Stage 3
add_text_box(slide, Inches(8.9), Inches(1.9), Inches(3.8), Inches(0.5),
             "Stage 3: FashionCLIP + FAISS", font_size=20, bold=True, color=ACCENT_LIGHT)
add_bullet_list(slide, Inches(8.9), Inches(2.5), Inches(3.8), Inches(2), [
    "Fashion-specific embeddings",
    "FAISS vector search index",
    "Shared model loader",
    "Production-grade retrieval",
], font_size=15, color=LIGHT_GRAY)

# ============================================================
# SLIDE 7: Reranking Explained
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide)
add_accent_bar(slide, Inches(0.8), Inches(0.8), Inches(0.08), Inches(0.6), ACCENT)
add_text_box(slide, Inches(1.1), Inches(0.7), Inches(10), Inches(0.8),
             "How Preference Reranking Works", font_size=36, bold=True)

add_text_box(slide, Inches(1.5), Inches(2.2), Inches(10), Inches(0.6),
             "final_score  =  base_score  +  0.15 × goal_bonus  −  0.15 × avoid_penalty",
             font_size=24, color=SOFT_GREEN, bold=True, alignment=PP_ALIGN.CENTER,
             font_name="Consolas")

add_bullet_list(slide, Inches(1.5), Inches(3.5), Inches(10), Inches(3.5), [
    "Base score: cosine similarity between query and result (from FAISS search)",
    "Goal bonus: similarity between result image and goal text prompt (e.g., \"a formal outfit\")",
    "Avoid penalty: similarity between result image and avoid text prompt (e.g., \"a hooded garment\")",
    "Alpha = 0.15 controls how much preferences shift the ranking",
    "Results are re-sorted by final score — order changes, not the items themselves",
], font_size=18)

# ============================================================
# SLIDE 8: Live Demo
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide)

add_text_box(slide, Inches(1), Inches(2.5), Inches(11), Inches(1.2),
             "Live Demo", font_size=48, bold=True, alignment=PP_ALIGN.CENTER)

add_text_box(slide, Inches(1), Inches(4.0), Inches(11), Inches(0.8),
             "streamlit run app.py", font_size=28, color=SOFT_GREEN,
             alignment=PP_ALIGN.CENTER, font_name="Consolas")

add_text_box(slide, Inches(1), Inches(5.2), Inches(11), Inches(0.8),
             "Upload image  →  Retrieve similar items  →  Apply preferences  →  See reranked results",
             font_size=18, color=LIGHT_GRAY, alignment=PP_ALIGN.CENTER)

# ============================================================
# SLIDE 9: Known Limitations & Future Work
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide)
add_accent_bar(slide, Inches(0.8), Inches(0.8), Inches(0.08), Inches(0.6), ACCENT)
add_text_box(slide, Inches(1.1), Inches(0.7), Inches(10), Inches(0.8),
             "Limitations & Future Work", font_size=36, bold=True)

add_text_box(slide, Inches(1.1), Inches(1.9), Inches(5), Inches(0.5),
             "Current Limitations", font_size=22, bold=True, color=SOFT_RED)
add_bullet_list(slide, Inches(1.1), Inches(2.6), Inches(5), Inches(3), [
    "Retrieval depends on catalog size and variety",
    "Preferences are per-session, not persisted",
    "Local only — no cloud deployment",
    "May still struggle with very niche garment types",
], font_size=17, color=LIGHT_GRAY)

add_text_box(slide, Inches(7.0), Inches(1.9), Inches(5), Inches(0.5),
             "Future Improvements", font_size=22, bold=True, color=SOFT_GREEN)
add_bullet_list(slide, Inches(7.0), Inches(2.6), Inches(5), Inches(3), [
    "Persistent feedback storage (learn from likes/dislikes)",
    "API backend (FastAPI) for separation of concerns",
    "Cloud deployment (Streamlit Cloud or Render)",
    "Larger, curated catalog for better coverage",
], font_size=17, color=LIGHT_GRAY)

# ============================================================
# SLIDE 10: Thank You
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide)
add_accent_bar(slide, Inches(0), Inches(3.2), Inches(13.333), Inches(0.06))

add_text_box(slide, Inches(1), Inches(2.2), Inches(11), Inches(1.2),
             "Thank You", font_size=48, bold=True, alignment=PP_ALIGN.CENTER)

add_text_box(slide, Inches(1), Inches(3.6), Inches(11), Inches(0.8),
             "Questions?", font_size=28, color=LIGHT_GRAY, alignment=PP_ALIGN.CENTER)

add_text_box(slide, Inches(1), Inches(5.0), Inches(11), Inches(0.6),
             "github.com/yeobian/Capstone", font_size=18, color=ACCENT_LIGHT,
             alignment=PP_ALIGN.CENTER, font_name="Consolas")

# Save
prs.save("Capstone_Presentation.pptx")
print("Saved Capstone_Presentation.pptx")
