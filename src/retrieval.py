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


def get_device():
    return "cuda" if torch.cuda.is_available() else "cpu"


def load_clip():
    device = get_device()
    model, preprocess = clip.load("ViT-B/32", device=device)
    model.eval()
    return model, preprocess, device


def get_image_paths():
    exts = {".jpg", ".jpeg", ".png"}
    return sorted([p for p in CATALOG_DIR.iterdir() if p.suffix.lower() in exts and p.is_file()])


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
        raise ValueError("No catalog images found in data/catalog_images")

    embeddings = []
    for path in image_paths:
        emb = embed_image(path, model, preprocess, device)
        embeddings.append(emb)

    embeddings = np.vstack(embeddings)
    np.save(EMBED_PATH, embeddings)

    with open(PATHS_PATH, "wb") as f:
        pickle.dump([str(p) for p in image_paths], f)

    return embeddings, [str(p) for p in image_paths]


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
import pickle

import clip
import numpy as np
import torch
from PIL import Image


CATALOG_DIR = Path("data/catalog_images")
ARTIFACT_DIR = Path("artifacts")
EMBED_PATH = ARTIFACT_DIR / "catalog_embeddings.npy"
PATHS_PATH = ARTIFACT_DIR / "catalog_paths.pkl"


def get_device():
    return "cuda" if torch.cuda.is_available() else "cpu"


def load_clip():
    device = get_device()
    model, preprocess = clip.load("ViT-B/32", device=device)
    model.eval()
    return model, preprocess, device


def get_image_paths():
    exts = {".jpg", ".jpeg", ".png"}
    return sorted([p for p in CATALOG_DIR.iterdir() if p.suffix.lower() in exts and p.is_file()])


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
        raise ValueError("No catalog images found in data/catalog_images")

    embeddings = []
    for path in image_paths:
        emb = embed_image(path, model, preprocess, device)
        embeddings.append(emb)

    embeddings = np.vstack(embeddings)
    np.save(EMBED_PATH, embeddings)

    with open(PATHS_PATH, "wb") as f:
        pickle.dump([str(p) for p in image_paths], f)

    return embeddings, [str(p) for p in image_paths]


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