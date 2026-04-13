from pathlib import Path
import pickle

import faiss
import numpy as np
import torch
from PIL import Image

from src.model import load_model

try:
    from rembg import remove as rembg_remove
    _REMBG_AVAILABLE = True
except ImportError:
    _REMBG_AVAILABLE = False


def remove_background(image: Image.Image) -> Image.Image:
    """Strip background and composite on white. Falls back to original if rembg not installed."""
    if not _REMBG_AVAILABLE:
        return image
    rgba = rembg_remove(image)
    background = Image.new("RGB", rgba.size, (255, 255, 255))
    background.paste(rgba, mask=rgba.split()[3])
    return background

_catalog_cache = {}

CATALOG_DIR = Path("data/catalog_images")
ARTIFACT_DIR = Path("artifacts")
EMBED_PATH = ARTIFACT_DIR / "catalog_embeddings.npy"
PATHS_PATH = ARTIFACT_DIR / "catalog_paths.pkl"
INDEX_PATH = ARTIFACT_DIR / "catalog.faiss"

# Keep this small for demo speed
SAMPLE_SIZE = 400
RANDOM_SEED = 42
EMBED_BATCH_SIZE = 32  # images per forward pass during catalog build


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
    all_paths = sorted(
        [p for p in CATALOG_DIR.rglob("*") if is_valid_catalog_image(p)]
    )

    if len(all_paths) == 0:
        return []

    if len(all_paths) <= sample_size:
        return all_paths

    rng = np.random.default_rng(seed)
    sampled_indices = rng.choice(len(all_paths), size=sample_size, replace=False)
    sampled_paths = [all_paths[i] for i in sampled_indices]

    return sorted(sampled_paths)


def embed_image(image_path, model, processor, device, remove_bg=False):
    image = Image.open(image_path).convert("RGB")
    if remove_bg:
        image = remove_background(image)
    # Convert to numpy array before passing to processor — avoids PIL/PyTorch
    # memory conflict that causes segfault on macOS
    image_array = np.array(image)
    inputs = processor(images=image_array, return_tensors="pt").to(device)

    with torch.inference_mode():
        features = model.get_image_features(**inputs)
        features = features / features.norm(dim=-1, keepdim=True)

    return features.cpu().float().numpy()[0]


def build_catalog_embeddings():
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    model, processor, device = load_model()
    print(f"Using device: {device}")
    image_paths = get_image_paths()

    if not image_paths:
        raise ValueError("No valid catalog images found in data/catalog_images")

    total = len(image_paths)
    print(f"Building catalog embeddings for {total} images (batch size {EMBED_BATCH_SIZE})...")

    embeddings = []
    valid_paths = []

    for batch_start in range(0, total, EMBED_BATCH_SIZE):
        batch_paths = image_paths[batch_start : batch_start + EMBED_BATCH_SIZE]
        batch_images = []
        batch_valid = []

        for path in batch_paths:
            try:
                img = Image.open(path).convert("RGB")
                batch_images.append(np.array(img))
                batch_valid.append(str(path))
            except Exception as e:
                print(f"  [skip] {path}: {e}")
                continue

        if not batch_images:
            continue

        try:
            inputs = processor(images=batch_images, return_tensors="pt", padding=True).to(device)
            with torch.inference_mode():
                feats = model.get_image_features(**inputs)
                feats = feats / feats.norm(dim=-1, keepdim=True)
            batch_embs = feats.cpu().float().numpy()
            embeddings.extend(batch_embs)
            valid_paths.extend(batch_valid)
            done = min(batch_start + EMBED_BATCH_SIZE, total)
            print(f"  Embedded {done}/{total}")
        except Exception as e:
            print(f"  [batch error] {e} — skipping batch")
            continue

    if not embeddings:
        raise ValueError("No embeddings could be created from catalog images")

    embeddings = np.vstack(embeddings).astype(np.float32)

    np.save(EMBED_PATH, embeddings)
    with open(PATHS_PATH, "wb") as f:
        pickle.dump(valid_paths, f)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    faiss.write_index(index, str(INDEX_PATH))

    print("Saved embeddings, paths, and FAISS index.")

    return index, valid_paths


def load_catalog():
    if "index" in _catalog_cache:
        return _catalog_cache["index"], _catalog_cache["paths"]

    if INDEX_PATH.exists() and PATHS_PATH.exists():
        print("Loading existing FAISS index...")
        index = faiss.read_index(str(INDEX_PATH))
        with open(PATHS_PATH, "rb") as f:
            image_paths = pickle.load(f)
    else:
        print("No saved index found. Building catalog artifacts now...")
        index, image_paths = build_catalog_embeddings()

    _catalog_cache["index"] = index
    _catalog_cache["paths"] = image_paths
    return index, image_paths


def retrieve_similar_items(query_image_path, top_k=5):
    model, processor, device = load_model()
    index, image_paths = load_catalog()

    if len(image_paths) == 0:
        return []

    top_k = min(top_k, len(image_paths))

    query_emb = embed_image(query_image_path, model, processor, device, remove_bg=True)
    query_emb = query_emb.reshape(1, -1).astype(np.float32)

    scores, indices = index.search(query_emb, top_k)

    results = []
    for rank in range(top_k):
        idx = int(indices[0][rank])

        if idx < 0 or idx >= len(image_paths):
            continue

        results.append(
            {
                "image_path": image_paths[idx],
                "score": float(scores[0][rank]),
            }
        )

    return results
