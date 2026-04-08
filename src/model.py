import os

# Must be set before torch is imported — prevents OpenMP segfault on macOS
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import torch
from transformers import CLIPModel, CLIPProcessor

MODEL_NAME = "patrickjohncyh/fashion-clip"

_cache = {}


def get_device():
    if torch.cuda.is_available():
        return "cuda"
    # Apple Silicon — MPS is more stable than CPU on macOS for transformer models
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def load_model():
    """Load FashionCLIP and cache it so both retrieval and rerank share one instance."""
    if "model" not in _cache:
        device = get_device()
        torch.set_num_threads(1)  # prevents segfault from threading conflicts on macOS
        model = CLIPModel.from_pretrained(MODEL_NAME).to(device)
        processor = CLIPProcessor.from_pretrained(MODEL_NAME)
        model.eval()
        _cache["model"] = model
        _cache["processor"] = processor
        _cache["device"] = device
    return _cache["model"], _cache["processor"], _cache["device"]
