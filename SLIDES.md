# Wardrobe AI — Capstone Presentation

---

## Slide 1: The Problem

**You see it. You can't find it.**

- People discover fashion inspiration on Pinterest, Instagram, and TikTok daily
- But the actual clothes are seasonal, sold out, or impossible to search for
- Keyword search fails — "beige oversized linen blazer with subtle texture" returns nothing useful
- No easy way to go from a visual inspiration photo to a similar item you can actually buy

---

## Slide 2: The Solution

**Wardrobe AI: Upload any photo. Find similar clothes.**

1. Upload a clothing image (Pinterest screenshot, photo, anything)
2. FashionCLIP encodes the image into a 512-dimensional visual embedding
3. FAISS searches a catalog of 10,000+ fashion items in milliseconds
4. Top matches returned ranked by visual similarity
5. Style preferences (formal/casual, fit, features to avoid) rerank the results

**Scoring:** `final_score = similarity + alpha x goal_bonus - alpha x avoid_penalty`

---

## Slide 3: Tech Stack

| Component | Technology |
|-----------|-----------|
| Web App | Streamlit |
| Embedding Model | FashionCLIP (fashion-tuned CLIP ViT-B/32) |
| Vector Search | FAISS (IndexFlatIP — cosine similarity) |
| Preference Reranking | FashionCLIP text embeddings + weighted scoring |
| Image Processing | Pillow, PyTorch |
| Background Removal | rembg |
| Dataset | DeepFashion In-Shop (10,000-image subset of 74,571) |
| Language | Python 3.11 |

---

Then: **Live Demo** in Streamlit
