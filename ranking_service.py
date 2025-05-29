# coding: utf-8
"""Service for scoring and ranking images using multiple models.

This module defines :class:`RankingService` which loads several pre-trained
models for evaluating photographs. Each image can be scored along different
axes such as aesthetics, technical quality, sentiment, novelty with respect to
trends, recency, and whether it was marked as a favorite. Scores are normalized
to the range [0, 1].
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

import numpy as np
from PIL import Image

try:
    import tensorflow as tf
    from tensorflow.keras.models import load_model
except Exception:  # pragma: no cover - TensorFlow is heavy
    tf = None
    load_model = None

try:
    import cv2
except Exception:  # pragma: no cover
    cv2 = None

try:
    from fer import FER
except Exception:  # pragma: no cover
    FER = None

try:
    import clip
    import torch
except Exception:  # pragma: no cover
    clip = None
    torch = None


def _normalize(value: float, min_val: float, max_val: float) -> float:
    """Normalize ``value`` to the 0-1 range given bounds."""
    if max_val - min_val == 0:
        return 0.0
    return max(0.0, min(1.0, (value - min_val) / float(max_val - min_val)))


class RankingService:
    """Score images and rank them by weighted criteria."""

    def __init__(self, trend_embeddings: Optional[Dict[str, np.ndarray]] = None) -> None:
        self.trend_embeddings = trend_embeddings or {}

        # Load models lazily so the module can still be imported without them.
        self.nima = None
        if load_model is not None and os.path.exists("models/nima.h5"):
            try:
                self.nima = load_model("models/nima.h5")
            except Exception:
                self.nima = None

        self.emotion_detector = FER() if FER is not None else None

        if clip is not None and torch is not None:
            try:
                self.clip_model, self.preprocess = clip.load("ViT-B/32")
            except Exception:
                self.clip_model = None
                self.preprocess = None
        else:
            self.clip_model = None
            self.preprocess = None

    # ------------------------------------------------------------------
    # Scoring functions
    # ------------------------------------------------------------------
    def compute_aesthetic_score(self, image: Image.Image) -> float:
        """Return a NIMA aesthetic score in [0, 1]."""
        if self.nima is None:
            return 0.0
        img = image.resize((224, 224))
        arr = np.array(img) / 255.0
        arr = arr.astype(np.float32)
        arr = np.expand_dims(arr, 0)
        try:
            preds = self.nima.predict(arr, verbose=0)[0]
            scores = np.arange(1, 11)
            mean_score = (preds * scores).sum()
            return _normalize(mean_score, 1.0, 10.0)
        except Exception:
            return 0.0

    def compute_technical_score(self, image: Image.Image) -> float:
        """Estimate technical quality using sharpness and brightness."""
        if cv2 is None:
            return 0.0
        arr = np.array(image.convert("RGB"))
        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
        lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        brightness = np.mean(gray)
        sharp_norm = _normalize(lap_var, 0.0, 1000.0)
        bright_norm = _normalize(brightness, 0.0, 255.0)
        return (sharp_norm + bright_norm) / 2.0

    def compute_sentiment_score(self, image: Image.Image) -> float:
        """Return dominant emotion confidence in [0, 1]."""
        if self.emotion_detector is None:
            return 0.0
        arr = np.array(image.convert("RGB"))
        try:
            detections = self.emotion_detector.detect_emotions(arr)
        except Exception:
            detections = []
        if not detections:
            return 0.0
        first = detections[0]
        emotions: Dict[str, float] = first.get("emotions", {})
        if not emotions:
            return 0.0
        return max(emotions.values())

    def compute_novelty_score(self, image: Image.Image) -> float:
        """Compute novelty relative to provided trend embeddings."""
        if self.clip_model is None or self.preprocess is None:
            return 0.0
        if not self.trend_embeddings:
            return 1.0
        img_input = self.preprocess(image).unsqueeze(0)
        try:
            with torch.no_grad():
                img_embed = self.clip_model.encode_image(img_input)
                img_embed = img_embed / img_embed.norm(dim=-1, keepdim=True)
                img_embed = img_embed.cpu().numpy()[0]
        except Exception:
            return 0.0
        similarities = []
        for emb in self.trend_embeddings.values():
            emb = emb / np.linalg.norm(emb)
            similarities.append(float(np.dot(img_embed, emb)))
        if not similarities:
            return 1.0
        max_sim = max(similarities)
        return 1.0 - _normalize(max_sim, -1.0, 1.0)

    def compute_recency_score(self, metadata: Dict[str, Any]) -> float:
        """Map recency (days since creation) to [0,1]; newer means higher."""
        created: Optional[datetime] = metadata.get("creation_time")
        if not isinstance(created, datetime):
            return 0.0
        now = datetime.now(created.tzinfo)
        days = (now - created).days
        return max(0.0, 1.0 - days / 30.0)

    def compute_favorite_score(self, metadata: Dict[str, Any]) -> float:
        """Return 1.0 if item is marked as favorite else 0.0."""
        return 1.0 if metadata.get("is_favorite") else 0.0

    # ------------------------------------------------------------------
    def rank_images(
        self,
        items: Iterable[Dict[str, Any]],
        weights: Optional[Dict[str, float]] = None,
    ) -> List[Dict[str, Any]]:
        """Return items sorted by weighted sum of scores."""

        default_weights = {
            "aesthetic": 0.25,
            "technical": 0.15,
            "sentiment": 0.15,
            "novelty": 0.15,
            "recency": 0.15,
            "favorite": 0.15,
        }
        if weights:
            default_weights.update(weights)
        results = []
        for item in items:
            img = item.get("image")
            metadata = item.get("metadata", {})
            if img is None:
                continue
            score_dict = {
                "aesthetic": self.compute_aesthetic_score(img),
                "technical": self.compute_technical_score(img),
                "sentiment": self.compute_sentiment_score(img),
                "novelty": self.compute_novelty_score(img),
                "recency": self.compute_recency_score(metadata),
                "favorite": self.compute_favorite_score(metadata),
            }
            total = sum(default_weights[k] * score_dict[k] for k in default_weights)
            item_copy = dict(item)
            item_copy["scores"] = score_dict
            item_copy["total_score"] = total
            results.append(item_copy)
        results.sort(key=lambda x: x["total_score"], reverse=True)
        return results

