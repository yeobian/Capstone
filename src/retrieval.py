from pathlib import Path
import pickle

import faiss
import numpy as np
import torch
from PIL import Image

from src.model import load_model

CATALOG_DIR = Path("data/catalog_images")
ARTIFACT_DIR = Path("artifacts")
EMBED_PATH = ARTIFACT_DIR / "catalog_embeddings.npy"
PATHS_PATH = ARTIFACT_DIR / "catalog_paths.pkl"
INDEX_PATH = ARTIFACT_DIR / "catalog.faiss"

SAMPLE_SIZE = 400
RANDOM_SEED = 42


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


def embed_image(image_path, model, processor, device):
    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt").to(device)

    with torch.no_grad():
        features = model.get_image_features(**inputs)
        features = features / features.norm(dim=-1, keepdim=True)

    return features.cpu().numpy()[0]


def build_catalog_embeddings():
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    model, processor, device = load_model()
    image_paths = get_image_paths()

    if not image_paths:
        raise ValueError("No valid catalog images found in data/catalog_images")

    embeddings = []
    valid_paths = []

    for path in image_paths:
        try:
            emb = embed_image(path, model, processor, device)
            embeddings.append(emb)
            valid_paths.append(str(path))
        except Exception as e:
            print(f"Skipping {path}: {e}")

    if not embeddings:
        raise ValueError("No embeddings could be created from catalog images")

    embeddings = np.vstack(embeddings).astype(np.float32)

    # Save raw embeddings and paths
    np.save(EMBED_PATH, embeddings)
    with open(PATHS_PATH, "wb") as f:
        pickle.dump(valid_paths, f)

    # Build and save FAISS index (inner product on L2-normalized vectors = cosine similarity)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    faiss.write_index(index, str(INDEX_PATH))

    return index, valid_paths


def load_catalog():
    if not INDEX_PATH.exists() or not PATHS_PATH.exists():
        return build_catalog_embeddings()

    index = faiss.read_index(str(INDEX_PATH))
    with open(PATHS_PATH, "rb") as f:
        image_paths = pickle.load(f)

    return index, image_paths


def retrieve_similar_items(query_image_path, top_k=5):
    model, processor, device = load_model()
    index, image_paths = load_catalog()

    query_emb = embed_image(query_image_path, model, processor, device)
    query_emb = query_emb.reshape(1, -1).astype(np.float32)

    scores, indices = index.search(query_emb, top_k)

    results = []
    for rank in range(top_k):
        idx = indices[0][rank]
        if idx < 0:
            continue
        results.append(
            {
                "image_path": image_paths[idx],
                "score": float(scores[0][rank]),
            }
        )

    return results
