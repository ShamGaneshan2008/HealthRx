"""
ML model training and inference for disease prediction.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MultiLabelBinarizer, LabelEncoder
from sklearn.model_selection import cross_val_score
from typing import List, Tuple, Optional, Dict, Any

from app.core.config import settings
from app.utils.logger import logger


class DiseasePredictor:
    """
    Symptom-based disease prediction using Random Forest.
    """

    def __init__(self) -> None:
        self._model: Optional[RandomForestClassifier] = None
        self._mlb: Optional[MultiLabelBinarizer] = None
        self._le: Optional[LabelEncoder] = None
        self._symptom_vocab: Optional[List[str]] = None
        self._trained: bool = False

    # ── TRAINING ─────────────────────────────────────

    def train(self) -> None:
        logger.info("📂 Loading training data from: %s", settings.SYMPTOMS_CSV)

        try:
            df = pd.read_csv(settings.SYMPTOMS_CSV, header=None)
        except FileNotFoundError:
            logger.error("❌ File not found: %s", settings.SYMPTOMS_CSV)
            raise

        records: List[Tuple[List[str], str]] = []

        for _, row in df.iterrows():
            values = [
                str(v).strip()
                for v in row.values
                if pd.notna(v) and str(v).strip()
            ]

            if len(values) >= 2:
                symptoms = [s.lower() for s in values[:-1]]
                disease = values[-1]
                records.append((symptoms, disease))

        if not records:
            raise ValueError("No valid training data found.")

        X_symptoms = [r[0] for r in records]
        y_diseases = [r[1] for r in records]

        # Convert symptoms → binary matrix
        self._mlb = MultiLabelBinarizer()
        X = self._mlb.fit_transform(X_symptoms)
        self._symptom_vocab = list(self._mlb.classes_)

        # Encode disease labels
        self._le = LabelEncoder()
        y = self._le.fit_transform(y_diseases)

        # Train model
        self._model = RandomForestClassifier(
            n_estimators=settings.N_ESTIMATORS,
            max_depth=settings.MAX_DEPTH,
            min_samples_split=settings.MIN_SAMPLES_SPLIT,
            min_samples_leaf=settings.MIN_SAMPLES_LEAF,
            class_weight="balanced",
            random_state=settings.RANDOM_STATE,
            n_jobs=-1,
        )

        self._model.fit(X, y)

        # Cross-validation
        try:
            cv_scores = cross_val_score(self._model, X, y, cv=3)
            logger.info(
                "✅ Model trained | Classes: %d | Features: %d | Accuracy: %.3f",
                len(self._le.classes_),
                X.shape[1],
                cv_scores.mean(),
            )
        except Exception:
            logger.warning("⚠️ CV skipped (dataset too small)")

        self._trained = True

    def _ensure_trained(self) -> None:
        if not self._trained:
            self.train()

    # ── PREDICTION ───────────────────────────────────

    def predict(self, symptoms: List[str]) -> Dict[str, Any]:
        self._ensure_trained()

        if not symptoms:
            raise ValueError("No symptoms provided")

        symptom_set = set(symptoms)
        X = self._mlb.transform([list(symptom_set)])

        pred_idx = self._model.predict(X)[0]
        disease = self._le.inverse_transform([pred_idx])[0]

        probs = self._model.predict_proba(X)[0]
        confidence = float(probs[pred_idx])

        # Top predictions
        top_idx = np.argsort(probs)[::-1][:3]
        top_predictions = [
            (self._le.inverse_transform([i])[0], float(probs[i]))
            for i in top_idx
        ]

        # Confidence label
        if confidence >= 0.75:
            label = "High"
        elif confidence >= 0.45:
            label = "Moderate"
        else:
            label = "Low"

        logger.info(
            "🧠 Prediction: %s (%.2f%%)",
            disease,
            confidence * 100,
        )

        return {
            "disease": disease,
            "confidence": confidence,
            "confidence_label": label,
            "top_predictions": top_predictions,
        }

    # ── ACCESSORS ────────────────────────────────────

    @property
    def symptom_vocab(self) -> List[str]:
        self._ensure_trained()
        return self._symptom_vocab or []

    @property
    def supported_diseases(self) -> List[str]:
        self._ensure_trained()
        return list(self._le.classes_) if self._le else []

    @property
    def is_trained(self) -> bool:
        return self._trained


# ✅ SINGLE GLOBAL INSTANCE (IMPORTANT)
predictor = DiseasePredictor()