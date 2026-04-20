from typing import Dict, List

import numpy as np
import torch
from PIL import Image

from src.model import load_model


GOAL_PROMPTS = {
    "more_formal":     "a formal business outfit",
    "more_casual":     "a casual everyday outfit",
    "more_minimal":    "a minimalist outfit with clean lines",
    "more_sporty":     "a sporty athletic outfit",
    "more_elegant":    "an elegant sophisticated outfit",
    "more_streetwear": "a streetwear urban outfit",
    "more_vintage":    "a vintage retro outfit",
    "more_colorful":   "a bold colorful outfit",
}

AVOID_PROMPTS = {
    "cropped":      "a cropped top",
    "hood":         "a hooded garment",
    "skinny_fit":   "skinny fit pants",
    "logos":        "a garment with large visible logos",
    "sporty":       "a sporty athletic outfit",
    "patterns":     "a garment with busy patterns or prints",
    "sheer":        "a sheer or see-through garment",
    "embellished":  "a garment with heavy embellishments or sequins",
}

COLOR_PROMPTS = {
    "black":   "a black clothing item",
    "white":   "a white clothing item",
    "beige":   "a beige or cream colored clothing item",
    "gray":    "a gray clothing item",
    "navy":    "a navy blue clothing item",
    "blue":    "a blue clothing item",
    "red":     "a red clothing item",
    "green":   "a green clothing item",
    "pink":    "a pink clothing item",
    "brown":   "a brown clothing item",
    "yellow":  "a yellow or mustard colored clothing item",
    "orange":  "an orange clothing item",
    "purple":  "a purple clothing item",
}

# Cache: prompt string → normalized embedding vector (populated on first use)
_TEXT_EMBED_CACHE: dict[str, np.ndarray] = {}


def encode_text_prompts(prompts: List[str], model, processor, device):
    if not prompts:
        return None

    inputs = processor(text=prompts, return_tensors="pt", padding=True).to(device)

    with torch.inference_mode():
        text_features = model.get_text_features(**inputs)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)

    return text_features.cpu().float().numpy()


def _get_cached_text_embeddings(
    prompts: List[str], model, processor, device
) -> np.ndarray | None:
    """Return embeddings for prompts, using the module-level cache to avoid
    re-encoding constant strings on every query."""
    if not prompts:
        return None

    uncached = [p for p in prompts if p not in _TEXT_EMBED_CACHE]
    if uncached:
        vecs = encode_text_prompts(uncached, model, processor, device)
        for prompt, vec in zip(uncached, vecs):
            _TEXT_EMBED_CACHE[prompt] = vec

    return np.stack([_TEXT_EMBED_CACHE[p] for p in prompts])


def encode_image_batch(image_paths: List[str], model, processor, device):
    """Encode all result images in one forward pass instead of one at a time."""
    images = [np.array(Image.open(p).convert("RGB")) for p in image_paths]
    inputs = processor(images=images, return_tensors="pt", padding=True).to(device)

    with torch.inference_mode():
        features = model.get_image_features(**inputs)
        features = features / features.norm(dim=-1, keepdim=True)

    return features.cpu().float().numpy()


def rerank_results(results: List[Dict], preference_schema: Dict, alpha: float = 0.4):
    if not results:
        return results

    model, processor, device = load_model()

    goal_keys = preference_schema.get("goals", [])
    avoid_keys = preference_schema.get("avoid", [])

    goal_prompts  = [GOAL_PROMPTS[g]  for g in goal_keys  if g in GOAL_PROMPTS]
    avoid_prompts = [AVOID_PROMPTS[a] for a in avoid_keys if a in AVOID_PROMPTS]

    color_key    = preference_schema.get("color")
    color_prompt = COLOR_PROMPTS.get(color_key) if color_key else None

    # Use cache — constant prompts are only encoded once per session
    goal_text_features  = _get_cached_text_embeddings(goal_prompts,  model, processor, device)
    avoid_text_features = _get_cached_text_embeddings(avoid_prompts, model, processor, device)
    color_text_features = _get_cached_text_embeddings(
        [color_prompt] if color_prompt else [], model, processor, device
    )

    # Encode all result images in one batch
    image_paths = [r["image_path"] for r in results]
    image_features = encode_image_batch(image_paths, model, processor, device)

    reranked = []

    for i, result in enumerate(results):
        base_score = float(result["score"])
        image_feature = image_features[i]

        goal_bonus    = 0.0
        avoid_penalty = 0.0
        color_bonus   = 0.0

        if goal_text_features is not None:
            goal_scores = goal_text_features @ image_feature
            goal_bonus = float(np.max(goal_scores))

        if avoid_text_features is not None:
            avoid_scores = avoid_text_features @ image_feature
            avoid_penalty = float(np.max(avoid_scores))

        if color_text_features is not None:
            color_scores = color_text_features @ image_feature
            color_bonus = float(np.max(color_scores))

        final_score = base_score + alpha * goal_bonus - alpha * avoid_penalty + alpha * color_bonus

        reranked.append(
            {
                "image_path":    result["image_path"],
                "score":         base_score,
                "goal_bonus":    goal_bonus,
                "avoid_penalty": avoid_penalty,
                "color_bonus":   color_bonus,
                "final_score":   final_score,
            }
        )

    reranked.sort(key=lambda x: x["final_score"], reverse=True)
    return reranked


def summarize_rerank_effect(preference_schema: Dict) -> str:
    goals = preference_schema.get("goals", [])
    avoid = preference_schema.get("avoid", [])

    parts = []
    if goals:
        parts.append("Boosted for: " + ", ".join(goals))
    if avoid:
        parts.append("Penalized for: " + ", ".join(avoid))

    if not parts:
        return "No reranking preferences applied."

    return " | ".join(parts)
