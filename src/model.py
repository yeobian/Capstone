import os

# prevent crash on macOS from OpenMP and tokenizer conflicts
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import torch
from transformers import CLIPModel, CLIPProcessor

MODEL_NAME = "patrickjohncyh/fashion-clip"

# in-memory cache so the model is only loaded once per session
_cache = {}


# pick the best available device: GPU > Apple Silicon > CPU
def get_device():
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


# load FashionCLIP once and reuse it — avoids re-downloading on every search
def load_model():
    if "model" not in _cache:
        device = get_device()
        torch.set_num_threads(1)
        model = CLIPModel.from_pretrained(MODEL_NAME).to(device)
        processor = CLIPProcessor.from_pretrained(MODEL_NAME)
        model.eval()
        _cache["model"] = model
        _cache["processor"] = processor
        _cache["device"] = device
    return _cache["model"], _cache["processor"], _cache["device"]
