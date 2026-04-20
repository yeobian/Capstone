# Wardrobe AI

A visual fashion search app. Upload a clothing photo, find visually similar items,
and rerank them by your style preferences.

## Problem

People discover clothing inspiration on Pinterest, Instagram, and TikTok, but
finding similar items to actually buy is hard. Keyword search doesn't help when
you can only describe a visual style. This project tries to solve that by letting
you search with an image instead of text.

## Solution

1. Upload a clothing photo (Pinterest, screenshot, your own photo)
2. FashionCLIP turns the image into a 512-dimensional embedding
3. FAISS searches a catalog of pre-embedded images for the nearest matches
4. Optionally set style preferences (formal, casual, avoid logos, etc.)
5. Results are reranked using text embeddings so items matching your preferences rank higher

Future direction: connect to live retailer catalogs so each result links to a
product page.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Web app | Streamlit |
| Embedding model | FashionCLIP (`patrickjohncyh/fashion-clip`), CLIP ViT-B/32 fine-tuned on fashion data |
| Vector search | FAISS (IndexFlatIP, cosine similarity on L2-normalized vectors) |
| Reranking | FashionCLIP text embeddings, weighted scoring |
| Image processing | Pillow, PyTorch, torchvision |
| Background removal | rembg |
| Dataset | DeepFashion In-Shop Clothes Retrieval (10,000-image subset) |
| Language | Python 3.11 |

## Repository Structure

```
Capstone/
├── app.py                    # Streamlit web application (entry point)
├── requirements.txt          # Pinned Python dependencies
├── README.md
├── src/
│   ├── model.py              # FashionCLIP model loader (cached)
│   ├── retrieval.py          # Embedding, FAISS catalog build, similarity search
│   ├── preferences.py        # Preference schema parsing
│   └── rerank.py             # Preference-aware reranking
├── scripts/
│   └── scrape_catalog.py     # Retailer image scraper (H&M, Uniqlo)
├── memory/
│   └── progress.md           # Baseline test results
├── data/                     # Local catalog images (gitignored)
└── artifacts/                # FAISS index + embeddings cache (gitignored)
```

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

The app samples up to `SAMPLE_SIZE` images (default 10,000) and builds a FAISS
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
