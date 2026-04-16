# Wardrobe AI — Capstone Presentation Slides

Copy each slide into Google Slides or PowerPoint.
Suggested design: dark background, white text, minimal layout.

---

## Slide 1: Title

**Wardrobe AI**
Visual Fashion Search with Preference-Aware Reranking

[Your Name]
Data Science Capstone | April 2026

---

## Slide 2: The Problem

**You see it. You can't find it.**

- People discover fashion inspiration on Pinterest, Instagram, and TikTok every day
- But the clothes in those photos are often seasonal, sold out, or impossible to search for
- Keyword search fails: typing "beige oversized linen blazer" rarely finds what you saw
- There is no easy way to go from visual inspiration to something you can actually buy

*[Suggestion: show a Pinterest screenshot on one side, and a failed Google search on the other]*

---

## Slide 3: The Solution

**Wardrobe AI: Upload any photo. Find similar clothes.**

1. Upload a clothing photo (Pinterest, screenshot, your own photo)
2. AI encodes it into a visual embedding
3. Searches a catalog of 10,000+ fashion items instantly
4. Returns the most visually similar matches
5. Your style preferences rerank the results

*[Suggestion: simple diagram — photo goes in, similar items come out]*

---

## Slide 4: How It Works — Visual Similarity

**Step 1: FashionCLIP Embedding**

- FashionCLIP is a fashion-tuned version of OpenAI's CLIP model
- Converts any clothing image into a 512-dimensional vector
- Images that look similar end up close together in this vector space
- Works across categories: shirts, pants, jackets, dresses

**Step 2: FAISS Vector Search**

- All catalog images are pre-embedded and stored in a FAISS index
- When you upload a photo, FAISS finds the nearest neighbors by cosine similarity
- Search across 10,000 images completes in milliseconds

*[Suggestion: show embedding space visualization — similar clothes clustered together]*

---

## Slide 5: How It Works — Preference Reranking

**Step 3: Style preferences adjust the results**

- User selects style goals: formal, casual, minimal, sporty, elegant, streetwear, vintage, colorful
- User selects features to avoid: hoods, logos, cropped, patterns, sheer
- User selects preferred fit: slim, regular, relaxed, oversized

**Scoring formula:**

    final_score = similarity + alpha x goal_bonus - alpha x avoid_penalty

- Goal bonus: how well the item matches your desired style (text-to-image similarity)
- Avoid penalty: how much the item looks like something you want to avoid
- Alpha slider: controls how strongly preferences influence results (subtle to aggressive)

*[Suggestion: show a before/after — same query, results change when you set "more formal" + "avoid logos"]*

---

## Slide 6: System Architecture

```
[User uploads photo]
        |
        v
[Background Removal] ---> rembg strips background, composites on white
        |
        v
[FashionCLIP Encoder] --> 512-dim embedding vector
        |
        v
[FAISS Index Search] ---> top-K nearest neighbors from catalog
        |
        v
[Preference Reranking] -> goal bonus + avoid penalty applied
        |
        v
[Streamlit UI] ---------> visual matches + styled results displayed
```

*[Suggestion: recreate this as a clean flow diagram with icons]*

---

## Slide 7: Tech Stack

| Component | Technology |
|-----------|-----------|
| Web App | Streamlit |
| Embedding Model | FashionCLIP (fashion-tuned CLIP ViT-B/32) |
| Vector Search | FAISS (IndexFlatIP) |
| Reranking | FashionCLIP text embeddings |
| Image Processing | Pillow, PyTorch, torchvision |
| Background Removal | rembg |
| Dataset | DeepFashion In-Shop (74,571 images, 10K sampled) |
| Hardware | Apple Silicon (MPS GPU acceleration) |

---

## Slide 8: Evaluation Results

**Baseline testing across 5 query types:**

| Query | Category Match | Style Match | Overall |
|-------|---------------|-------------|---------|
| Light blue shirt | Good | Good | Good |
| Cream cable-knit sweater | Partial-Good | Partial | Okay |
| Black pants | Good | Partial-Good | Good |
| Navy puffer jacket | Weak | Weak | Poor |
| Black cardigan | Weak | Weak | Poor |

**Key finding:** Strong on broad categories (shirts, pants). Weaker on specific
garment types (puffer jackets, cardigans). This is a known CLIP limitation —
it captures general visual similarity better than fine-grained garment structure.

**Preference reranking** measurably shifts results toward desired styles,
demonstrated live in the demo.

---

## Slide 9: Live Demo

**[LIVE DEMO HERE]**

Demo plan:
1. Open Streamlit app (http://localhost:8501)
2. Upload a clothing photo
3. Show baseline visual similarity results
4. Set preferences: "more formal", avoid "logos"
5. Show how reranked results shift toward formal, logo-free items
6. Adjust alpha slider to show subtle vs. aggressive reranking
7. Try a second query with different preferences

---

## Slide 10: Limitations

**Honest assessment:**

- **Static catalog** — results come from a sampled subset, not a live retailer feed
- **No buy links yet** — items are visual matches, not shoppable (requires retailer API partnerships)
- **Soft reranking** — preferences influence order but can't create items that don't exist in the catalog
- **Western fashion bias** — DeepFashion dataset is primarily Western clothing
- **Background removal** — works well for studio photos, less effective for outdoor/natural photos

---

## Slide 11: Future Work

**From proof-of-concept to product:**

- **Live retailer catalogs** — scrape or partner with H&M, Uniqlo, ASOS for real product data with buy links and prices
- **Full catalog embedding** — embed all 74,571 images (or millions) on a GPU server instead of sampling
- **User feedback loop** — learn from likes/dislikes to personalize results over time
- **Multi-item outfits** — upload a full outfit, find similar pieces for each item
- **Mobile app** — bring visual search to iOS/Android with camera integration
- **Cloud deployment** — host on AWS/GCP so anyone can use it without local setup

---

## Slide 12: Summary

**Wardrobe AI bridges the gap between fashion inspiration and finding clothes you can buy.**

- Upload any clothing photo and find visually similar items in seconds
- FashionCLIP + FAISS gives fast, fashion-aware visual search
- Preference reranking personalizes results to your style
- Technical foundation is ready for live retailer integration

**The technology works. The next step is connecting it to real stores.**

Thank you.

---

## Slide 13: Q&A

**Questions?**

GitHub: github.com/yeobian/Capstone
