# Experimental — Not Part of Demo

This folder contains an earlier training/evaluation pipeline that was designed
around a fine-tuned EfficientNet multi-task classifier (category + color labels).

It is **not connected to the running demo** and is preserved here for reference only.

## Why it was moved

- `src/train.py` references `WardrobeNet`, a class that was never fully defined.
- `src/evaluate.py` is fully stubbed with placeholder/dummy logic.
- `src/models/baseline.py` requires `timm`, which is not part of the demo stack.
- The trained classifier model would not be used by the Streamlit app anyway;
  the demo uses CLIP embeddings directly.

## Demo pipeline (in src/)

The working demo uses:
- `src/retrieval.py` — CLIP embedding + cosine similarity retrieval
- `src/preferences.py` — preference schema parsing
- `src/rerank.py` — preference-aware reranking
