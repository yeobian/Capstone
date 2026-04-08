import torch
from transformers import CLIPModel, CLIPProcessor

MODEL_NAME = "patrickjohncyh/fashion-clip"

_cache = {}

def get_device():
    return "cpu"

def load_model():
    """Load FashionCLIP and cache it so both retrieval and rerank share one instance."""
    if "model" not in _cache:
        device = get_device()
        model = CLIPModel.from_pretrained(MODEL_NAME).to(device)
        processor = CLIPProcessor.from_pretrained(MODEL_NAME)
        model.eval()
        _cache["model"] = model
        _cache["processor"] = processor
        _cache["device"] = device
    return _cache["model"], _cache["processor"], _cache["device"]