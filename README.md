# Wardrobe AI

A visual fashion search app. Upload a clothing photo, find visually similar items,
and rerank them by your style preferences.

## Problem Addressed

People often struggle to understand what clothing they already own, what styles they repeatedly choose, and what similar items they may want to buy or avoid buying again. This project explores how machine learning can support that process through visual similarity retrieval.

## Proposed Solution

The system uses a retrieval-based approach rather than a traditional classification pipeline.

### Core workflow
1. User uploads a clothing image
2. The system generates an image embedding using **FashionCLIP** (CLIP ViT-B/32 fine-tuned on fashion data)
3. The embedding is compared to 20,000+ catalog embeddings using cosine similarity via **FAISS**
4. The system returns the top visually similar clothing items
5. Optional style, color, and fit preferences **rerank** the results using text-image similarity

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Web app | Streamlit |
| Embedding model | FashionCLIP (`patrickjohncyh/fashion-clip`), CLIP ViT-B/32 fine-tuned on fashion data |
| Vector search | FAISS (IndexFlatIP, cosine similarity on L2-normalized vectors) |
| Reranking | FashionCLIP text embeddings, weighted scoring |
| Image processing | Pillow, PyTorch, torchvision |
| Background removal | rembg |
| Dataset | DeepFashion In-Shop Clothes Retrieval (20,000-image subset) |
| Language | Python 3.11 |

## Repository Structure

```
Capstone/
├── app.py                    # Streamlit web application (entry point)
├── requirements.txt          # Pinned Python dependencies
├── README.md
├── SLIDES.md                 # Capstone presentation outline
├── AGENT.md                  # Project rules for AI-assisted development
├── presentation.html         # Slide deck for capstone presentation
├── src/
│   ├── model.py              # FashionCLIP model loading and caching
│   ├── retrieval.py          # FAISS index build and similarity search
│   ├── rerank.py             # Preference-based result reranking
│   └── preferences.py        # Sidebar input parsing and schema
├── scripts/
│   └── scrape_catalog.py     # Future: retailer catalog scraper (not used by app)
├── memory/
│   └── progress.md           # Development test notes
├── data/        # local only, not tracked in Git
└── artifacts/   # local only, not tracked in Git
````

## Setup

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/yeobian/Capstone.git
cd Capstone
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

On first run, FashionCLIP weights (~600 MB) download from HuggingFace. Needs internet.

### 3. Add catalog images

Place clothing images in `data/catalog_images/` or point to a DeepFashion
`img_highres/` directory. The app scans both locations automatically.

The app samples up to `SAMPLE_SIZE` images (default 20,000) and builds a FAISS
index in `artifacts/` on first launch. Later launches load the cache instantly.

To rebuild the index after adding new images:

```bash
rm -rf artifacts/
streamlit run app.py
```

### 4. Run

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`.

## How to Use

1. Upload a clothing photo (jpg, png, or webp)
2. Optionally set style preferences in the sidebar:
   - Style goal (formal, casual, minimal, etc.)
   - Fit (slim, regular, relaxed, oversized)
   - Color (black, white, beige, navy, and more)
   - Features to avoid (hoods, logos, cropped, patterns, etc.)
   - Free text notes
3. Click "Find Similar Items"
4. Compare the "Visual Matches" section (pure similarity) with "Styled for You"
   (preference-reranked)

## Known Limitations

- Catalog is a static sampled subset, not a live retailer feed. Real-time
  shoppability would require retailer API integration.
- DeepFashion covers common Western clothing well but may miss niche styles.
- Preference reranking only reorders existing results. It can't surface items
  that don't exist in the catalog.
- Background removal works best on studio-style images.

## Dataset Reference

Liu, Z., Luo, P., Qiu, S., Wang, X., & Tang, X. (2016). DeepFashion: Powering
robust clothes recognition and retrieval with rich annotations. CVPR.
