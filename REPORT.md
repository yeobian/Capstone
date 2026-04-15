# Wardrobe AI — Project Report

**Course:** Capstone Project  
**Project:** Personal Wardrobe Intelligence — Visual Fashion Retrieval with Preference-Aware Reranking  
**Tech Stack:** Python · PyTorch · FashionCLIP · FAISS · Streamlit  
**All tools used are free and open-source.**

---

## 1. Problem Statement

Finding clothing items that visually match something you already own — or that fit a specific personal style — is a hard problem for users of traditional e-commerce search. Keyword search ("blue jacket") fails to capture visual similarity, and generic search engines are not designed for style-aware personalization.

This project asks: **can a system retrieve visually similar clothing items from a catalog, and then re-rank those results based on a user's personal style preferences, without requiring any labeled training data?**

The answer is yes — using a pre-trained vision-language model and a zero-shot preference scoring approach.

---

## 2. System Overview

The system is a full-stack web application with four distinct layers:

```
User uploads image
        ↓
[1] Embed image  →  512-dimensional vector  (FashionCLIP)
        ↓
[2] FAISS search  →  top 20 visually similar items
        ↓
[3] Preference reranking  →  rescore by style goals and avoids
        ↓
[4] Streamlit UI  →  show top 5 visual matches + top 5 reranked
```

The key insight is that all four steps operate in the **same embedding space** — images and text descriptions of style preferences can be compared directly using cosine similarity.

---

## 3. Technical Implementation

### 3.1 Embedding Model — FashionCLIP

The model used is `patrickjohncyh/fashion-clip`, a version of OpenAI's CLIP (Contrastive Language-Image Pretraining) that was **fine-tuned on fashion-specific data**. This matters because generic CLIP does not understand fashion terminology or garment structures as well as a domain-adapted version.

- **Architecture:** Vision Transformer (ViT-B/32)
- **Output:** 512-dimensional embedding vectors, L2-normalized
- **Key property:** Images and text occupy the same vector space — "a formal outfit" as text and a photo of a blazer will be close together

The model is loaded once at startup and shared across all operations via a singleton cache (`src/model.py`), avoiding repeated loading overhead.

### 3.2 Vector Search — FAISS

All catalog images are embedded offline and stored in a FAISS `IndexFlatIP` (exact inner-product search). Because all vectors are L2-normalized, inner product equals cosine similarity.

**Offline index build (`src/retrieval.py`):**
1. Scan `data/catalog_images/` for valid images
2. Embed each image using FashionCLIP in batches of 32
3. Save: `artifacts/catalog_embeddings.npy`, `artifacts/catalog.faiss`, `artifacts/catalog_paths.pkl`

**At query time:**
1. User uploads an image
2. Background is removed (via `rembg`) to isolate the garment
3. Image is embedded to a 512-dim vector
4. FAISS returns the top 20 nearest neighbors from the catalog

The background removal step on the query image was added after observing that busy photo backgrounds (furniture, walls, people) biased the embedding away from the garment itself.

### 3.3 Preference-Aware Reranking (`src/rerank.py`)

This is the core novelty of the project. After retrieving the top 20 candidates by visual similarity, the system re-scores them based on user-specified style preferences.

**How it works:**

User preferences are expressed as natural language text prompts. For example:
- Style goal "formal" → prompt: `"a formal business outfit"`
- Avoid "hood" → prompt: `"a hooded garment"`

These prompts are encoded as text embeddings by FashionCLIP (the same model, same space). Then for each result image, the system computes:

```
goal_bonus    = max(similarity(image, goal_prompt) for each goal)
avoid_penalty = max(similarity(image, avoid_prompt) for each avoid)
final_score   = base_score + α × goal_bonus − α × avoid_penalty
```

Where **α (alpha)** controls how aggressively preferences shift the ranking. It is exposed to the user as a slider (0.1 = subtle nudge, 1.0 = strong re-sort).

**This is zero-shot reranking** — no training data or labeled examples are required. The system exploits the pre-trained alignment between fashion images and text descriptions that FashionCLIP already learned.

**Text embedding cache:** The goal and avoid prompt embeddings are constant (they never change between queries). The system caches them on first use, so subsequent queries reuse the cached vectors instead of re-encoding.

### 3.4 Preference Parsing (`src/preferences.py`)

Users express preferences through three channels:
1. **Dropdown** — style goal (formal, casual, minimal, sporty, elegant, streetwear, vintage, colorful)
2. **Multiselect** — features to avoid (cropped, hood, skinny fit, logos, patterns, sheer, embellished)
3. **Free text** — natural language input (e.g., "more formal", "no hood", "relaxed fit")

The free text input is parsed via pattern matching against a dictionary of known phrases and mapped to the same internal representation as the dropdown options. All three channels are merged into a single preference schema dict.

### 3.5 Web Application (`app.py`)

Built with Streamlit. Key UI decisions:

- **Base64 image embedding in HTML** — result images are rendered as inline base64 strings inside custom HTML cards, giving full control over layout and styling that Streamlit's native `st.image()` would not allow
- **Session state** — search results are stored in `st.session_state` so they persist when the user adjusts preferences without re-running the search
- **Dual result sections** — "Visual Matches" (pure similarity) and "Styled for You" (reranked) are shown side by side so users can see the effect of their preferences
- **Expandable results** — "Show all 20" button reveals the full candidate pool beyond the default top 5
- **Reranking stats** — the header shows a live summary: how many items entered the top 5 due to reranking, and the average score delta
- **NEW indicator** — a green dot marks items that appeared in the reranked top 5 but not the original top 5

---

## 4. Software Engineering Decisions

### 4.1 Offline vs. Online Split
Catalog embedding is separated from query-time retrieval. The catalog index is built once and cached to disk. Subsequent runs load from disk in under a second regardless of catalog size. This means the slow step (embedding hundreds of images) only runs once.

### 4.2 Batched Embedding
During catalog build, images are embedded in batches of 32 per model forward pass rather than one at a time. This is approximately 10× faster because it amortizes model loading overhead across the batch.

### 4.3 Device Portability
The model loading code detects the best available compute device at runtime: CUDA (Nvidia GPU) → MPS (Apple Silicon) → CPU. This makes the project runnable on any machine without code changes.

### 4.4 Scraper (`scripts/scrape_catalog.py`)
A polite web scraper is included for expanding the catalog with real product images from H&M and Uniqlo. It respects `robots.txt`, applies 1–2 second random delays between requests, deduplicates images by URL hash, and filters out thumbnails smaller than 100px.

---

## 5. What I Built — Summary

| Component | Description |
|---|---|
| `src/model.py` | FashionCLIP singleton loader with device detection and caching |
| `src/retrieval.py` | Catalog indexer (batched embedding + FAISS), query embedding with background removal |
| `src/preferences.py` | Multi-channel preference parser (dropdowns + multiselect + free text) |
| `src/rerank.py` | Zero-shot preference reranker with text embed cache and score formula |
| `app.py` | Full Streamlit UI with custom CSS, session state, expandable results |
| `scripts/scrape_catalog.py` | Polite catalog scraper for H&M and Uniqlo |

**Lines of code:** ~900 across all files  
**Commits:** 20+ (iterative development documented in git history)  
**External cost:** $0 — all open-source tools and pre-trained models

---

## 6. Observations and Results

Manual testing on 5 query images (light blue shirt, cream sweater, navy jacket, black cardigan, black pants) showed:

- **Strong performance on broad categories:** Searching with a blue t-shirt returns other tops and similar-toned items reliably
- **Preference reranking works visually:** Setting "formal" as a goal pushes items with structured silhouettes higher; "avoid hood" reduces hooded results
- **Weaker on fine-grained garment types:** A puffer jacket query returns generic outerwear instead of other puffer jackets specifically — the model captures broad visual similarity better than exact garment structure
- **Background removal helps:** Queries with complex backgrounds (furniture, outdoor settings) produced noticeably better results after rembg was added

---

## 7. Limitations

**Catalog size:** The current catalog contains 20 hand-curated images. This is sufficient to demonstrate the system architecture and retrieval mechanics, but too small for meaningful evaluation or diversity in results.

**No quantitative evaluation:** Without a labeled ground-truth dataset (e.g., "these 5 items are similar to this query"), it is not possible to compute standard information retrieval metrics like Precision@k, Recall@k, or NDCG. Results are assessed qualitatively.

**Reranking formula is hand-crafted:** The formula `base + α × goal − α × avoid` was chosen based on intuition and manual observation. It has not been compared against a learned ranking model (e.g., LambdaMART) or validated with a user study.

**Fit constraint parsed but not enforced:** The system parses "slim fit" or "relaxed" from user input but does not currently use it in the reranking score — this is planned future work.

**Free-text parsing is brittle:** The free-text input relies on substring pattern matching against a fixed dictionary. It handles common phrases ("more formal", "no hood") but will miss paraphrases or typos.

---

## 8. What I Can Do to Improve This

### Short-term (technical improvements)

| Improvement | Impact | Effort |
|---|---|---|
| **Run the scraper** — expand catalog to 300–500 images | High — more diverse results, more realistic demo | Low |
| **Apply background removal to catalog images** — currently only query gets rembg | Medium — fixes preprocessing inconsistency | Low |
| **Wire up fit constraint** — use "slim/relaxed" in reranking text prompts | Medium — activates a feature that's already parsed | Low |
| **Result diversity (MMR)** — penalize results too similar to each other | Medium — top 5 often show near-identical items | Medium |
| **Better error handling** — graceful failure on corrupt images, missing catalog | Low — user experience | Low |

### Medium-term (research improvements)

| Improvement | Impact | Effort |
|---|---|---|
| **Quantitative evaluation** — create a small ground-truth test set, compute Precision@5 and NDCG | High — provides evidence the system works | Medium |
| **Prompt ensembling** — average multiple text prompts per style goal instead of one | Medium — more robust style representation | Low |
| **User feedback collection** — thumbs up/down on results, stored in session | Medium — enables preference learning over time | Medium |
| **Ablation study** — compare with/without reranking, with/without background removal | Medium — validates design decisions | Medium |

### Long-term (research extensions)

| Improvement | Impact | Effort |
|---|---|---|
| **Fine-tune FashionCLIP** on domain-specific data with user preferences | High — direct accuracy improvement | High |
| **Learned reranking** — replace hand-crafted formula with a trained ranking model | High — replaces heuristic with data-driven approach | High |
| **Outfit completion** — given a top, recommend a matching bottom | High — extends use case beyond single-item search | High |
| **Deployment** — Streamlit Cloud or Hugging Face Spaces for a public URL | Medium — shareable portfolio piece | Low |

---

## 9. Key Takeaways

1. **Pre-trained vision-language models** like FashionCLIP enable zero-shot fashion retrieval without any labeled training data — the model's pre-trained knowledge is sufficient for the core task.

2. **The same embedding space for images and text** is the fundamental mechanism that makes preference-aware reranking possible. A photo of a blazer and the text "a formal outfit" are close in this space — that proximity is the signal the system uses.

3. **Separation of offline and online steps** is critical for a usable system. Embedding 400 images takes minutes; retrieving from a FAISS index takes milliseconds. The offline/online split makes the demo feel instant.

4. **Iterative development matters.** The project went through multiple architecture changes (retrieval-only → +reranking → +background removal → +scraper → +UI redesign) documented in 20+ git commits. Each change was motivated by a specific observed weakness.

5. **The hardest part was not the ML — it was data.** Getting a meaningful catalog, cleaning images, and maintaining embedding quality proved more challenging than implementing the retrieval or reranking logic itself.
