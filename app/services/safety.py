"""Safety validation, allergy checks, and warning generation."""

from __future__ import annotations

from typing import List, Optional, Dict, Any

from app.core.config import settings
from app.schemas import WarningItem, DrugInfo
from app.utils.logger import logger


def _classify_severity(
    symptoms: List[str],
    confidence: float,
    duration_days: Optional[int],
) -> str:
    """
    Classify the overall severity of the presented case.

    Args:
        symptoms: List of detected symptom names.
        confidence: Model confidence score (0-1).
        duration_days: How long symptoms have persisted.

    Returns:
        Severity level: "emergency", "severe", "moderate", or "mild".
    """
    symptom_set = set(symptoms)

    # Emergency: red-flag symptoms
    emergency_matches = symptom_set.intersection(settings.EMERGENCY_SYMPTOMS)
    if emergency_matches:
        return "emergency"

    # Severe: high-confidence prediction + concerning combos
    severe_indicators = {
        "shortness of breath", "high fever", "severe back pain",
        "blood in stool", "blood in urine", "rapid heartbeat",
        "severe headache",
    }
    if symptom_set.intersection(severe_indicators) and confidence > 0.6:
        return "severe"

    # Duration-based escalation
    if duration_days is not None and duration_days >= 7:
        return "severe"
    if duration_days is not None and duration_days >= 3:
        return "moderate"

    # Multiple symptoms -> moderate
    if len(symptoms) >= 4:
        return "moderate"

    return "mild"


def _check_allergies(
    drugs: List[DrugInfo],
    allergies: Optional[List[str]],
) -> List[WarningItem]:
    """
    Cross-reference recommended drugs against user-reported allergies.

    Checks drug allergy_flags and drug_class against the allergy list
    using case-insensitive substring matching.

    Args:
        drugs: List of recommended drug objects.
        allergies: User-reported allergy strings (lowercase preferred).

    Returns:
        List of allergy-related WarningItem objects.
    """
    if not allergies:
        return []

    warnings: List[WarningItem] = []
    allergy_set = {a.lower().strip() for a in allergies if a.strip()}

    for drug in drugs:
        # Check explicit allergy flags
        for flag in drug.allergy_warning.split(", ") if drug.allergy_warning else []:
            if any(allergy_val in flag.lower() for allergy_val in allergy_set):
                warnings.append(WarningItem(
                    level="warning",
                    message=f"ALLERGY ALERT: '{drug.name}' may be contraindicated due to reported allergy to '{flag}'. Do NOT take this medication without consulting a doctor.",
                ))
                break

        # Check drug class and name against allergies
        check_targets = [drug.drug_class.lower(), drug.name.lower(), drug.generic_name.lower()]
        for target in check_targets:
            if any(allergy_val in target for allergy_val in allergy_set):
                msg = (
                    f"ALLERGY ALERT: '{drug.name}' ({drug.drug_class}) may conflict "
                    f"with your reported allergies. Consult a healthcare provider before use."
                )
                if not any(w.message == msg for w in warnings):
                    warnings.append(WarningItem(level="warning", message=msg))
                break

        # Check raw allergy flags list from drugs.json (stored in allergy_warning field)
        # We also cross-check the drug's internal allergy flags
        for flag_str in (drug.allergy_warning or "").split(","):
            flag_clean = flag_str.strip().lower()
            if flag_clean and any(flag_clean in a.lower() or a.lower() in flag_clean for a in allergies):
                msg = (
                    f"ALLERGY ALERT: '{drug.name}' carries a '{flag_clean}' flag. "
                    f"This may pose a risk given your allergy history."
                )
                if not any(w.message == msg for w in warnings):
                    warnings.append(WarningItem(level="warning", message=msg))

    return warnings


def _generate_duration_warnings(duration_days: Optional[int]) -> List[WarningItem]:
    """
    Generate warnings based on symptom duration.

    Args:
        duration_days: Number of days symptoms have persisted.

    Returns:
        List of duration-related WarningItem objects.
    """
    if duration_days is None:
        return []

    warnings: List[WarningItem] = []

    if duration_days >= 7:
        warnings.append(WarningItem(
            level="warning",
            message=f"Symptoms persisting for {duration_days} days require medical evaluation. "
                    "Self-treatment is not recommended at this stage.",
        ))
    elif duration_days >= 3:
        warnings.append(WarningItem(
            level="caution",
            message=f"Symptoms have lasted {duration_days} days. If no improvement within 48 hours, "
                    "please consult a healthcare provider.",
        ))
    elif duration_days == 0:
        warnings.append(WarningItem(
            level="info",
            message="Symptoms appeared today. Monitor closely for any worsening.",
        ))

    return warnings


def _generate_confidence_warnings(
    prediction: Dict[str, Any],
) -> List[WarningItem]:
    """
    Generate warnings related to prediction confidence and ambiguity.

    Args:
        prediction: Output dict from DiseasePredictor.predict().

    Returns:
        List of confidence-related WarningItem objects.
    """
    warnings: List[WarningItem] = []
    confidence = prediction["confidence"]

    if confidence < settings.MIN_CONFIDENCE_THRESHOLD:
        warnings.append(WarningItem(
            level="warning",
            message="Very low prediction confidence. The entered symptoms may not match any known condition. "
                    "Please provide more specific symptoms or consult a doctor.",
        ))
    elif confidence < 0.35:
        warnings.append(WarningItem(
            level="caution",
            message="Low prediction confidence. Multiple conditions may present similarly. "
                    "A healthcare provider can perform differential diagnosis.",
        ))

    # Check for close second prediction (ambiguity)
    top = prediction.get("top_predictions", [])
    if len(top) >= 2:
        gap = top[0][1] - top[1][1]
        if gap < 0.10 and top[1][1] > 0.2:
            warnings.append(WarningItem(
                level="caution",
                message=f"Multiple possible conditions detected: '{top[0][0]}' ({top[0][1]:.0%}) "
                        f"and '{top[1][0]}' ({top[1][1]:.0%}). "
                        "Clinical evaluation is recommended to distinguish between them.",
            ))

    return warnings


def _generate_disease_specific_warnings(disease: str) -> List[WarningItem]:
    """
    Generate condition-specific safety advisories.

    Args:
        disease: Predicted disease name.

    Returns:
        List of disease-specific WarningItem objects.
    """
    specific_warnings: Dict[str, List[tuple]] = {
        "Dengue Fever": [
            ("warning", "Dengue can progress to severe dengue (dengue hemorrhagic fever). "
             "AVOID aspirin and ibuprofen — they increase bleeding risk. Use only Paracetamol for fever. "
             "Seek immediate medical attention if symptoms worsen."),
        ],
        "Malaria": [
            ("warning", "Malaria is a medical emergency requiring prompt treatment. "
             "Do not delay seeking medical care. Complications can be life-threatening."),
        ],
        "Pneumonia": [
            ("warning", "Pneumonia can be serious, especially in young children, elderly, "
             "and immunocompromised individuals. Medical evaluation and likely antibiotics are needed."),
        ],
        "Appendicitis": [
            ("emergency", "Appendicitis typically requires emergency surgical intervention. "
             "Do NOT take laxatives or enemas. Go to the nearest emergency department immediately."),
        ],
        "Kidney Stones": [
            ("warning", "Large kidney stones may not pass on their own and can cause kidney damage. "
             "Seek medical evaluation to determine stone size and appropriate management."),
        ],
        "Hypertension": [
            ("caution", "Hypertension is a chronic condition that requires proper medical management. "
             "Regular blood pressure monitoring and lifestyle modifications are essential."),
        ],
        "Diabetes": [
            ("caution", "Diabetes requires comprehensive management including diet, exercise, "
             "and medication. Regular blood sugar monitoring is essential. "
             "These medications should only be taken under medical supervision."),
        ],
        "Depression": [
            ("warning", "Antidepressants should only be taken under psychiatric supervision. "
             "They may take 2-4 weeks to show effect. Monitor for any worsening of mood or suicidal thoughts."),
        ],
        "Anxiety Disorder": [
            ("caution", "Anxiety medications should be prescribed by a mental health professional. "
             "Combination with therapy (CBT) is typically most effective."),
        ],
        "COVID-19": [
            ("caution", "If COVID-19 is suspected, get tested and follow local public health guidelines. "
             "Monitor for warning signs like difficulty breathing. Seek emergency care if symptoms worsen."),
        ],
    }

    return [
        WarningItem(level=level, message=msg)
        for level, msg in specific_warnings.get(disease, [])
    ]


def generate_warnings(
    symptoms: List[str],
    drugs: List[DrugInfo],
    prediction: Dict[str, Any],
    allergies: Optional[List[str]] = None,
    duration_days: Optional[int] = None,
) -> List[WarningItem]:
    """
    Aggregate all safety warnings for a given prediction context.

    Combines severity-based, allergy, duration, confidence, and
    disease-specific warnings into a single deduplicated list.

    Args:
        symptoms: Detected symptom names.
        drugs: Recommended drug list.
        prediction: Model prediction output dict.
        allergies: User-reported drug allergies.
        duration_days: Symptom duration in days.

    Returns:
        Ordered list of WarningItem objects (emergency first, then
        warning, caution, info).
    """
    all_warnings: List[WarningItem] = []

    # 1. Severity classification
    severity = _classify_severity(symptoms, prediction["confidence"], duration_days)

    if severity == "emergency":
        all_warnings.append(WarningItem(
            level="emergency",
            message="EMERGENCY: Your symptoms indicate a potentially serious condition. "
                    "Please seek immediate emergency medical attention or call emergency services.",
        ))

    # 2. Disease-specific warnings
    all_warnings.extend(_generate_disease_specific_warnings(prediction["disease"]))

    # 3. Allergy warnings
    all_warnings.extend(_check_allergies(drugs, allergies))

    # 4. Duration warnings
    all_warnings.extend(_generate_duration_warnings(duration_days))

    # 5. Confidence warnings
    all_warnings.extend(_generate_confidence_warnings(prediction))

    # 6. Standard severity note
    if severity in ("severe", "moderate"):
        all_warnings.append(WarningItem(
            level="caution",
            message="Consult a healthcare provider if symptoms persist or worsen. "
                    "Do not self-medicate beyond 2-3 days without medical advice.",
        ))

    # Deduplicate and sort by priority
    seen: set = set()
    unique: List[WarningItem] = []
    priority = {"emergency": 0, "warning": 1, "caution": 2, "info": 3}
    for w in sorted(all_warnings, key=lambda x: priority.get(x.level, 4)):
        if w.message not in seen:
            seen.add(w.message)
            unique.append(w)

    logger.info("Generated %d warnings (severity: %s)", len(unique), severity)
    return unique