"""Drug recommendation engine and AI explanation generator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional, Dict, Any

from app.core.config import settings
from app.schemas import DrugInfo, WarningItem
from app.utils.logger import logger


class DrugDatabase:
    """
    In-memory drug knowledge base loaded from a JSON file.

    Provides disease-to-drug mapping with structured pharmaceutical
    information including dosages, side effects, and contraindications.
    """

    def __init__(self) -> None:
        self._data: Dict[str, Dict[str, Any]] = {}
        self._loaded: bool = False

    def load(self) -> None:
        """Load and parse the drug database from JSON."""
        logger.info("Loading drug database from: %s", settings.DRUGS_JSON)
        try:
            with open(settings.DRUGS_JSON, "r", encoding="utf-8") as f:
                self._data = json.load(f)
            self._loaded = True
            logger.info("Drug database loaded: %d conditions", len(self._data))
        except FileNotFoundError:
            logger.error("Drug database file not found: %s", settings.DRUGS_JSON)
            raise
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in drug database: %s", e)
            raise

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self.load()

    def get_drugs(self, disease: str) -> List[Dict[str, Any]]:
        """
        Retrieve raw drug entries for a given disease.

        Args:
            disease: Canonical disease name.

        Returns:
            List of drug dictionaries, or empty list if disease not found.
        """
        self._ensure_loaded()
        entry = self._data.get(disease, {})
        return entry.get("drugs", [])

    def get_description(self, disease: str) -> str:
        """
        Retrieve the disease description text.

        Args:
            disease: Canonical disease name.

        Returns:
            Description string, or a default fallback message.
        """
        self._ensure_loaded()
        entry = self._data.get(disease, {})
        return entry.get(
            "description",
            "A medical condition that requires professional evaluation and treatment.",
        )

    @property
    def supported_diseases(self) -> List[str]:
        """Return list of diseases in the drug database."""
        self._ensure_loaded()
        return list(self._data.keys())


# ── Module singleton ────────────────────────────────────────────────────
drug_db = DrugDatabase()


def recommend_drugs(
    disease: str,
    allergies: Optional[List[str]] = None,
) -> List[DrugInfo]:
    """
    Generate structured drug recommendations for a predicted disease.

    Each drug is enriched with an allergy warning if the user's reported
    allergies match the drug's allergy flags.

    Args:
        disease: Predicted disease name.
        allergies: Optional list of user-reported drug allergies.

    Returns:
        List of DrugInfo objects with safety annotations.
    """
    raw_drugs = drug_db.get_drugs(disease)

    if not raw_drugs:
        logger.warning("No drugs found in database for: %s", disease)
        return []

    allergy_set = {a.lower().strip() for a in (allergies or []) if a.strip()}
    result: List[DrugInfo] = []

    for drug in raw_drugs:
        # Build allergy warning if applicable
        allergy_warning: Optional[str] = None
        flags = drug.get("allergy_flags", [])
        if flags and allergy_set:
            matched = [
                flag for flag in flags
                if any(a in flag.lower() or flag.lower() in a for a in allergy_set)
            ]
            if matched:
                allergy_warning = ", ".join(matched)

        result.append(DrugInfo(
            name=drug["name"],
            generic_name=drug["generic_name"],
            usage=drug["usage"],
            dosage=drug["dosage"],
            side_effects=drug["side_effects"],
            contraindications=drug["contraindications"],
            drug_class=drug["drug_class"],
            allergy_warning=allergy_warning,
        ))

    logger.info("Recommended %d drugs for %s", len(result), disease)
    return result


def generate_explanation(
    disease: str,
    confidence: float,
    confidence_label: str,
    detected_symptoms: List[str],
    drugs: List[DrugInfo],
    warnings: List[WarningItem],
) -> str:
    """
    Generate a human-readable clinical explanation of the prediction.

    Simulates an LLM-style response using structured templates and
    contextual data from the prediction pipeline.

    Args:
        disease: Predicted disease name.
        confidence: Model confidence score.
        confidence_label: Human-readable confidence level.
        detected_symptoms: Symptoms extracted from user input.
        drugs: Recommended drug list.
        warnings: Generated safety warnings.

    Returns:
        Multi-paragraph explanation string.
    """
    # ── Symptom summary ────────────────────────────────────────────
    if len(detected_symptoms) <= 5:
        symptom_text = ", ".join(detected_symptoms)
    else:
        symptom_text = ", ".join(detected_symptoms[:5]) + f", and {len(detected_symptoms) - 5} other symptom(s)"

    # ── Disease description ────────────────────────────────────────
    description = drug_db.get_description(disease)

    # ── Drug rationale ─────────────────────────────────────────────
    drug_rationales: List[str] = []
    for drug in drugs[:3]:
        drug_rationales.append(f"{drug.name} ({drug.drug_class}) — {drug.usage}")

    drug_text = "\n".join(f"  • {r}" for r in drug_rationales)

    # ── Confidence framing ─────────────────────────────────────────
    confidence_frames = {
        "High": "There is strong alignment between your reported symptoms and the clinical profile of this condition.",
        "Moderate": "Your symptoms show a reasonable match with this condition, though other conditions may present similarly.",
        "Low": "The match is tentative. Additional symptoms or clinical evaluation would help confirm the diagnosis.",
        "Very Low": "The symptom pattern does not clearly match a single condition. A healthcare provider should perform a proper assessment.",
    }
    confidence_note = confidence_frames.get(confidence_label, "")

    # ── Warning summary ────────────────────────────────────────────
    has_allergy_warnings = any("ALLERGY ALERT" in w.message for w in warnings)
    has_severe_warnings = any(w.level in ("emergency", "warning") for w in warnings)
    warning_note = ""
    if has_allergy_warnings:
        warning_note += "\n\nIMPORTANT: Allergy conflicts were detected with one or more recommended medications. Review the warnings above carefully and do not take flagged medications without medical supervision."
    if has_severe_warnings:
        warning_note += "\n\nATTENTION: Serious warnings have been flagged for this prediction. Please review them carefully and consider seeking immediate medical attention if applicable."

    # ── Assemble explanation ───────────────────────────────────────
    explanation = (
        f"Based on the symptoms you reported — {symptom_text} — our clinical decision "
        f"support system predicts {disease} with {confidence_label} confidence "
        f"({confidence * 100:.1f}%).\n\n"
        f"{confidence_note}\n\n"
        f"About {disease}:\n{description}\n\n"
        f"Recommended Medications:\n{drug_text}\n\n"
        f"These medications address the key symptoms associated with {disease}. "
        f"The primary drug targets the underlying cause, while supplementary "
        f"medications help manage specific symptoms and improve comfort during recovery."
        f"{warning_note}"
    )

    return explanation