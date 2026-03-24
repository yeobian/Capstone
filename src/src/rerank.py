from typing import Dict, List

import clip
import numpy as np
import torch
from PIL import Image


GOAL_PROMPTS = {
    "more_formal": "a formal outfit",
    "more_casual": "a casual outfit",
    "more_minimal": "a minimalist outfit",
    "more_sporty": "a sporty outfit",
}

AVOID_PROMPTS = {
    "cropped": "a cropped top",
    "hood": "a hooded garment",
    "skinny_fit": "skinny fit pants",
    "logos": "a garment with large visible logos",
    "sporty": "a sporty outfit",
}


def get_device():
    return "cuda" if torch.cuda.is_available() else "cpu"


def load_clip_model():
    device = get_device()
    model, preprocess = clip.load("ViT-B/32", device=device)
    model.eval()
    return model, preprocess, device


def encode_text_prompts(prompts: List[str], model, device):
    if not prompts:
        return None

    text_tokens = clip.tokenize(prompts).to(device)

    with torch.no_grad():
        text_features = model.encode_text(text_tokens)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)

    return text_features.cpu().numpy()


def encode_image_path(image_path: str, model, preprocess, device):
    image = Image.open(image_path).convert("RGB")
    image_input = preprocess(image).unsqueeze(0).to(device)

    with torch.no_grad():
        image_features = model.encode_image(image_input)
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)

    return image_features.cpu().numpy()[0]


def rerank_results(results: List[Dict], preference_schema: Dict, alpha: float = 0.15):
    if not results:
        return results

    model, preprocess, device = load_clip_model()

    goal_keys = preference_schema.get("goals", [])
    avoid_keys = preference_schema.get("avoid", [])

    goal_prompts = [GOAL_PROMPTS[g] for g in goal_keys if g in GOAL_PROMPTS]
    avoid_prompts = [AVOID_PROMPTS[a] for a in avoid_keys if a in AVOID_PROMPTS]

    goal_text_features = encode_text_prompts(goal_prompts, model, device)
    avoid_text_features = encode_text_prompts(avoid_prompts, model, device)

    reranked = []

    for result in results:
        image_path = result["image_path"]
        base_score = float(result["score"])

        image_feature = encode_image_path(image_path, model, preprocess, device)

        goal_bonus = 0.0
        avoid_penalty = 0.0

        if goal_text_features is not None:
            goal_scores = goal_text_features @ image_feature
            goal_bonus = float(np.max(goal_scores))

        if avoid_text_features is not None:
            avoid_scores = avoid_text_features @ image_feature
            avoid_penalty = float(np.max(avoid_scores))

        final_score = base_score + alpha * goal_bonus - alpha * avoid_penalty

        reranked.append(
            {
                "image_path": image_path,
                "score": base_score,
                "goal_bonus": goal_bonus,
                "avoid_penalty": avoid_penalty,
                "final_score": final_score,
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