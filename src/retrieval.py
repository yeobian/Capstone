from pathlib import Path
import pickle

import clip
import numpy as np
import torch
from PIL import Image


CATALOG_DIR = Path("data/catalog_images")
ARTIFACT_DIR = Path("artifacts")
EMBED_PATH = ARTIFACT_DIR / "catalog_embeddings.npy"
PATHS_PATH = ARTIFACT_DIR / "catalog_paths.pkl"

SAMPLE_SIZE = 400
RANDOM_SEED = 42


def get_device():
    return "cuda" if torch.cuda.is_available() else "cpu"


def load_clip():
    device = get_device()
    model, preprocess = clip.load("ViT-B/32", device=device)
    model.eval()
    return model, preprocess, device


def is_valid_catalog_image(path: Path) -> bool:
    exts = {".jpg", ".jpeg", ".png"}
    bad_keywords = ["segment", "mask", "seg", "parse"]

    if not path.is_file():
        return False
    if path.suffix.lower() not in exts:
        return False

    name_lower = path.name.lower()
    if any(keyword in name_lower for keyword in bad_keywords):
        return False

    return True


def get_image_paths(sample_size=SAMPLE_SIZE, seed=RANDOM_SEED):
    all_paths = sorted([p for p in CATALOG_DIR.rglob("*") if is_valid_catalog_image(p)])

    if len(all_paths) <= sample_size:
        return all_paths

    rng = np.random.default_rng(seed)
    sampled_indices = rng.choice(len(all_paths), size=sample_size, replace=False)
    sampled_paths = [all_paths[i] for i in sampled_indices]

    return sorted(sampled_paths)


def embed_image(image_path, model, preprocess, device):
    image = Image.open(image_path).convert("RGB")
    image_input = preprocess(image).unsqueeze(0).to(device)

    with torch.no_grad():
        features = model.encode_image(image_input)
        features = features / features.norm(dim=-1, keepdim=True)

    return features.cpu().numpy()[0]


def build_catalog_embeddings():
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    model, preprocess, device = load_clip()
    image_paths = get_image_paths()

    if not image_paths:
        raise ValueError("No valid catalog images found in data/catalog_images")

    embeddings = []
    valid_paths = []

    for path in image_paths:
        try:
            emb = embed_image(path, model, preprocess, device)
            embeddings.append(emb)
            valid_paths.append(str(path))
        except Exception as e:
            print(f"Skipping {path}: {e}")

    if not embeddings:
        raise ValueError("No embeddings could be created from catalog images")

    embeddings = np.vstack(embeddings)
    np.save(EMBED_PATH, embeddings)

    with open(PATHS_PATH, "wb") as f:
        pickle.dump(valid_paths, f)

    return embeddings, valid_paths


def load_catalog_embeddings():
    if not EMBED_PATH.exists() or not PATHS_PATH.exists():
        return build_catalog_embeddings()

    embeddings = np.load(EMBED_PATH)
    with open(PATHS_PATH, "rb") as f:
        image_paths = pickle.load(f)

    return embeddings, image_paths


def retrieve_similar_items(query_image_path, top_k=5):
    model, preprocess, device = load_clip()
    catalog_embeddings, image_paths = load_catalog_embeddings()

    query_emb = embed_image(query_image_path, model, preprocess, device)

    scores = catalog_embeddings @ query_emb
    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for idx in top_indices:
        results.append(
            {
                "image_path": image_paths[idx],
                "score": float(scores[idx]),
            }
        )

    return results