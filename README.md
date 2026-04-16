# Wardrobe AI

A visual fashion search engine that finds similar clothing items from a catalog
using AI-powered image embeddings and preference-aware reranking.

---

## Problem

People discover fashion inspiration everywhere — Pinterest boards, Instagram feeds,
street style photos — but acting on that inspiration is frustrating. The clothes in
aesthetic photos are often seasonal, unavailable, or impossible to find by keyword
search. Typing "beige oversized linen blazer with subtle texture" into a search bar
rarely surfaces what you actually saw.

**The gap:** Visual inspiration is abundant. Shoppable matches are hard to find.

---

## Solution

Wardrobe AI lets you upload any clothing photo and instantly find visually similar
items from a fashion catalog, ranked by how well they match your personal style
preferences.

**Core workflow:**

1. Upload a clothing photo (from Pinterest, a screenshot, or your own photos)
2. FashionCLIP encodes the image into a 512-dimensional visual embedding
3. A FAISS index searches pre-computed catalog embeddings for the nearest neighbors
4. Top results are returned ranked by visual similarity
5. Optionally set style preferences (formal/casual/minimal/sporty, fit, items to avoid)
6. Results are reranked using FashionCLIP text embeddings — goal styles get a bonus,
   avoided features get a penalty

**Future direction:** Connect to live retailer catalogs (H&M, Uniqlo, ASOS, etc.)
so every result links directly to a product page where users can buy what they find.
The technical foundation is already in place for this.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Web application | Streamlit |
| Embedding model | FashionCLIP (`patrickjohncyh/fashion-clip`) — fashion-tuned CLIP ViT-B/32 |
| Vector search | FAISS (IndexFlatIP — exact inner-product search on L2-normalized vectors) |
| Preference reranking | FashionCLIP text embeddings + weighted scoring |
| Image processing | Pillow, PyTorch, torchvision |
| Background removal | rembg (removes background from query image before embedding) |
| Catalog storage | FAISS index + pickle (image paths) |
| Dataset | DeepFashion In-Shop Clothes Retrieval (10,000-image local subset) |
| Language | Python 3.11 |

---

## Repository Structure

```
Capstone/
├── app.py                    # Streamlit web application (entry point)
├── requirements.txt          # Pinned Python dependencies
├── README.md
├── REPORT.md                 # Project report
├── src/
│   ├── model.py              # FashionCLIP model loader (cached singleton)
│   ├── retrieval.py          # Embedding, FAISS catalog build, similarity retrieval
│   ├── preferences.py        # Preference schema parsing (UI controls + free text)
│   ├── rerank.py             # Preference-aware reranking with goal/avoid scoring
│   └── utils/
│       └── logger.py
├── scripts/
│   └── scrape_catalog.py     # Retailer image scraper (H&M, Uniqlo)
├── data/
│   └── catalog_images/       # Local catalog images (not tracked in Git)
├── artifacts/                # Auto-generated FAISS index + embeddings cache (not tracked in Git)
└── experimental/             # Training pipeline experiments — not part of the demo
```

---

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

> On first run, FashionCLIP model weights (~600 MB) download from HuggingFace Hub
> and cache locally. Internet connection required.

### 3. Add catalog images

Place clothing images in `data/catalog_images/` or point to the DeepFashion
`img_highres/` directory. The app auto-detects both locations.

The app samples up to `SAMPLE_SIZE` images (default: 10,000) for the FAISS index.
On first launch it builds and saves the index to `artifacts/`. Every subsequent
launch loads from cache instantly.

**To rebuild the index** (e.g. after adding new images):

```bash
rm -rf artifacts/
streamlit run app.py
```

### 4. Run

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`.

---

## How to Use

1. Upload a clothing photo — anything you want to find a match for
2. Optionally set style preferences in the sidebar:
   - **Style goal** — make results more formal, casual, minimal, sporty, etc.
   - **Fit** — slim, regular, relaxed, or oversized
   - **Avoid** — exclude hoods, logos, cropped tops, patterns, etc.
   - **Free text** — type anything (e.g. "no patterns", "more elegant")
3. Click **Find Similar Items**
4. Browse **Visual Matches** (pure similarity) and **Styled for You** (preference-reranked) side by side
5. Each reranked result shows how much it was boosted or penalized by your preferences

---

## Known Limitations

- Results are drawn from a static sampled catalog, not a live retailer feed.
  Real-time shoppability requires retailer API integration (out of scope for this version).
- Catalog quality directly affects result quality — DeepFashion covers common Western
  fashion categories well but may miss niche styles.
- Preference reranking is soft — it influences ranking but cannot surface items that
  don't exist in the catalog.
- Background removal (rembg) improves query accuracy for studio-style images but may
  not help for natural outdoor photos.

---

## Dataset Reference

DeepFashion In-Shop Clothes Retrieval:

```bibtex
@inproceedings{liuLQWTcvpr16DeepFashion,
  author    = {Liu, Ziwei and Luo, Ping and Qiu, Shi and Wang, Xiaogang and Tang, Xiaoou},
  title     = {DeepFashion: Powering Robust Clothes Recognition and Retrieval with Rich Annotations},
  booktitle = {Proceedings of IEEE Conference on Computer Vision and Pattern Recognition (CVPR)},
  month     = {June},
  year      = {2016}
}
```
