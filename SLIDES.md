# Wardrobe AI - Capstone Presentation

---

## Slide 1: The Problem

People discover fashion inspiration on Pinterest, Instagram, and TikTok, but
finding similar items to actually buy is hard.

- Clothes in inspiration photos are often seasonal, sold out, or hard to search for
- Keyword search fails when you can only describe a visual style
- Typing "beige oversized linen blazer with subtle texture" rarely finds what you saw
- No easy way to go from a visual inspiration to a similar item you can buy

---

## Slide 2: The Solution

Wardrobe AI: upload any photo, find similar clothes.

1. Upload a clothing image (Pinterest screenshot, photo, etc.)
2. FashionCLIP encodes the image into a 512-dimensional visual embedding
3. FAISS searches a catalog of 10,000+ fashion items
4. Top matches returned by visual similarity
5. Style preferences rerank the results using text-image similarity

Scoring formula:
final_score = similarity + alpha * goal_bonus - alpha * avoid_penalty

---

## Slide 3: Tech Stack

| Component | Technology |
|-----------|-----------|
| Web App | Streamlit |
| Embedding Model | FashionCLIP (CLIP ViT-B/32 fine-tuned on fashion data) |
| Vector Search | FAISS (IndexFlatIP, cosine similarity) |
| Preference Reranking | FashionCLIP text embeddings + weighted scoring |
| Image Processing | Pillow, PyTorch |
| Background Removal | rembg |
| Dataset | DeepFashion In-Shop (10,000-image subset of 74,571) |
| Language | Python 3.11 |

---

Then: Live Demo in Streamlit
