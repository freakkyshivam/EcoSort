"""
Wraps the teammate's ml/Brain.py so the rest of the backend never has to
know about PyTorch, checkpoints, or tensors directly — it just calls
classify_image(bytes) and gets back a clean result.

The model is loaded ONCE at startup (see get_inference_service below),
not on every request — loading a checkpoint from disk on every API call
would make each request take seconds instead of milliseconds.
"""
from __future__ import annotations

import io
from functools import lru_cache

import torch
from PIL import Image

from app.config import settings
from ml.Brain import get_device, load_model, make_transforms


class InferenceService:
    def __init__(self, checkpoint_path, threshold: float):
        self.device = get_device()
        self.model, self.class_names, self.checkpoint = load_model(checkpoint_path, self.device)
        _, self.transform = make_transforms(self.checkpoint["config"]["image_size"])
        self.threshold = threshold

    @torch.inference_mode()
    def classify_image(self, image_bytes: bytes) -> dict:
        """
        Takes raw image bytes (e.g. straight from an uploaded file),
        returns {label, confidence, should_sort}.
        """
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        tensor = self.transform(image).unsqueeze(0).to(self.device)
        if self.device.type == "cuda":
            tensor = tensor.contiguous(memory_format=torch.channels_last)

        with torch.autocast(device_type=self.device.type, dtype=torch.float16, enabled=self.device.type == "cuda"):
            probabilities = self.model(tensor).softmax(1)[0]

        score, index = probabilities.max(0)
        confidence = round(score.item(), 4)
        label = self.class_names[index.item()]

        return {
            "label": label,
            "confidence": confidence,
            "should_sort": confidence >= self.threshold,
        }


@lru_cache
def get_inference_service() -> InferenceService:
    """
    FastAPI dependency — @lru_cache means this only actually runs once
    (the model loads on the first request), and every request after
    that reuses the same loaded model instead of reloading it.
    """
    return InferenceService(settings.model_checkpoint_path, settings.confidence_threshold)