# Personal Wardrobe Intelligence

A machine learning proof-of-concept for visual clothing similarity retrieval
with preference-aware reranking, presented as a live Streamlit web application.

---

## Problem

People struggle to identify what clothing items they already own are similar to
each other, and to find or avoid specific styles when browsing their wardrobe.
Traditional keyword search does not work for visual style matching.

---

## Proposed Solution

A retrieval-based system that uses visual embeddings to find similar clothing
items from a local catalog, then reranks results based on user style preferences.

**Core workflow:**

1. User uploads a clothing image
2. FashionCLIP encodes the image into a 512-dimensional embedding
3. A FAISS index searches pre-computed catalog embeddings for the nearest neighbors
4. The top-5 most similar items are returned
5. User selects style preferences (formal/casual/minimal/sporty, fit, items to avoid)
6. Results are reranked using FashionCLIP text embeddings of preference prompts,
   applying a goal bonus and avoid penalty to each result's base similarity score

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Web application | Streamlit |
| Embedding model | FashionCLIP (fashion-tuned CLIP ViT-B/32) via HuggingFace |
| Vector search | FAISS (IndexFlatIP — exact inner-product search) |
| Preference reranking | FashionCLIP text embeddings + weighted scoring |
| Image processing | Pillow, PyTorch, torchvision |
| Catalog storage | FAISS index + pickle (image paths) |
| Dataset | DeepFashion In-Shop Clothes Retrieval (local subset) |
| Language | Python 3.10+ |

---

## Repository Structure

```
Capstone/
├── app.py                    # Streamlit web application (entry point)
├── requirements.txt          # Python dependencies
├── README.md
├── src/
│   ├── model.py              # Shared FashionCLIP model loader (cached singleton)
│   ├── retrieval.py          # FashionCLIP embedding, FAISS catalog, similarity retrieval
│   ├── preferences.py        # Preference schema parsing (UI controls + free text)
│   ├── rerank.py             # Preference-aware reranking with goal/avoid scoring
│   └── utils/
│       └── logger.py         # Logging utility
├── data/
│   └── catalog_images/       # Local catalog images (not tracked in Git — see below)
├── artifacts/                # Auto-generated embedding cache (not tracked in Git)
└── experimental/             # Earlier training pipeline — not part of the demo
```

---

## Steps to Launch the Demo

### 1. Clone the repository

```bash
git clone https://github.com/yeobian/capstone.git
cd capstone
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> Note: On first run the FashionCLIP model weights (~600 MB) are downloaded from
> HuggingFace Hub and cached locally. Requires an internet connection.

### 4. Add catalog images

Place clothing images inside:

```
data/catalog_images/
```

The app expects `.jpg`, `.jpeg`, or `.png` files. Any subdirectory structure is
supported. On first run, the app builds and caches embeddings automatically
inside `artifacts/`. Subsequent runs load from the cache.

**Recommended:** Use a subset of the
[DeepFashion In-Shop Clothes Retrieval](http://mmlab.ie.cuhk.edu.hk/projects/DeepFashion/InShopRetrieval.html)
dataset (a few hundred images is sufficient for demonstration purposes).

### 5. Run the application

```bash
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`.

---

## How to Use

1. Upload a clothing image (shirt, pants, jacket, etc.)
2. Optionally set style preferences: make it more formal/casual/minimal/sporty,
   select fit, or avoid features like hoods or logos
3. Click **Find Similar Items**
4. View the baseline FashionCLIP results and the preference-reranked results side by side
5. Each reranked result shows: base similarity score, goal bonus, avoid penalty,
   and final score

---

## Known Limitations

- Retrieval quality depends on catalog size and variety. A larger, more diverse
  catalog produces better results.
- FashionCLIP improves fashion-specific retrieval over general-purpose CLIP but
  may still struggle with very specific garment subtypes.
- Preferences apply soft reranking — they influence result order but cannot
  guarantee a result matches the preference if the catalog does not contain it.
- This is a local proof-of-concept. Deployment and persistent feedback storage
  are out of scope for the current version.

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
