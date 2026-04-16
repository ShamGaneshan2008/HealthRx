"""NLP-based symptom extraction from natural-language input."""

from __future__ import annotations

import re
import string
from typing import List, Set, Optional

from app.utils.logger import logger


# ── Synonym Mapping ──────────────────────────────────────────────────────
# Maps common colloquial or misspelled variations to canonical symptom names.
SYNONYM_MAP: dict[str, str] = {
    # Fever variations
    "temp": "fever",
    "temperature": "fever",
    "high temp": "fever",
    "high temperature": "fever",
    "hot": "fever",
    "febrile": "fever",
    "pyrexia": "fever",
    # Headache variations
    "head pain": "headache",
    "head ache": "headache",
    "headache pain": "headache",
    "head hurts": "headache",
    "head is paining": "headache",
    "migraine": "severe headache",
    # Cough variations
    "coughing": "cough",
    "dry cough": "cough",
    "wet cough": "productive cough",
    "hacking cough": "persistent cough",
    # Breathing
    "breathlessness": "shortness of breath",
    "difficulty breathing": "shortness of breath",
    "hard to breathe": "shortness of breath",
    "can't breathe": "shortness of breath",
    "breathing problem": "shortness of breath",
    "breath short": "shortness of breath",
    # Pain
    "stomach pain": "abdominal pain",
    "stomach ache": "abdominal pain",
    "tummy pain": "abdominal pain",
    "belly pain": "abdominal pain",
    "stomach cramps": "abdominal pain",
    "body ache": "body pain",
    "body aches": "body pain",
    "muscle ache": "muscle pain",
    "muscle aches": "muscle pain",
    "joint ache": "joint pain",
    "joint aches": "joint pain",
    "back ache": "back pain",
    "backache": "back pain",
    "chest ache": "chest pain",
    "flank pain": "severe back pain",
    "eye pain": "eye pain",
    "eyes hurt": "eye pain",
    # GI
    "loose motion": "diarrhea",
    "loose motions": "diarrhea",
    "loose stool": "diarrhea",
    "loose stools": "diarrhea",
    "frequent stool": "diarrhea",
    "passing blood": "blood in stool",
    "blood stool": "blood in stool",
    "blood in poop": "blood in stool",
    "blood urine": "blood in urine",
    "blood in pee": "blood in urine",
    "blood in pee": "blood in urine",
    "throwing up": "vomiting",
    "puking": "vomiting",
    "felt like throwing up": "nausea",
    "feel like vomiting": "nausea",
    "queasy": "nausea",
    "no appetite": "loss of appetite",
    "not eating": "loss of appetite",
    "not hungry": "loss of appetite",
    "bloated": "bloating",
    "constipated": "constipation",
    # Nose
    "blocked nose": "congestion",
    "stuffy nose": "congestion",
    "nose block": "congestion",
    "nasal block": "congestion",
    "nasal blockage": "congestion",
    "runny nose": "runny nose",
    " dripping nose": "runny nose",
    "watery nose": "runny nose",
    "sneezing": "sneezing",
    "sneezes": "sneezing",
    "post nasal drip": "post nasal drip",
    # Throat
    "throat pain": "sore throat",
    "throat ache": "sore throat",
    "throat irritation": "sore throat",
    "painful throat": "sore throat",
    "difficulty swallowing": "sore throat",
    "painful swallowing": "sore throat",
    # Eyes
    "red eye": "red eyes",
    "pink eye": "red eyes",
    "eye redness": "red eyes",
    "itchy eyes": "itchy eyes",
    "eye itching": "itchy eyes",
    "eyes watering": "watery eyes",
    "tearing eyes": "watery eyes",
    "blurry vision": "blurred vision",
    "blurry sight": "blurred vision",
    "light sensitive": "light sensitivity",
    "photosensitivity": "light sensitivity",
    # Skin
    "rashes": "rash",
    "skin rash": "rash",
    "skin rashes": "rash",
    "spots": "rash",
    "itching": "itching",
    "itchy": "itching",
    "itchy skin": "itching",
    "skin irritation": "itching",
    "swelling": "swelling",
    "swollen": "swelling",
    "pale": "pale skin",
    "looking pale": "pale skin",
    "skin redness": "skin redness",
    # Urinary
    "burning urination": "burning sensation",
    "burning pee": "burning sensation",
    "painful urination": "burning sensation",
    "pain while peeing": "burning sensation",
    "frequent pee": "frequent urination",
    "peeing frequently": "frequent urination",
    "peeing a lot": "frequent urination",
    "urgency": "frequent urination",
    "cloudy pee": "cloudy urine",
    "excessive thirst": "excessive thirst",
    "very thirsty": "excessive thirst",
    "always thirsty": "excessive thirst",
    # Energy
    "tired": "fatigue",
    "exhausted": "fatigue",
    "no energy": "fatigue",
    "low energy": "fatigue",
    "lethargic": "fatigue",
    "weak": "weakness",
    "feeling weak": "weakness",
    # Neurological
    "giddy": "dizziness",
    "lightheaded": "dizziness",
    "light headed": "dizziness",
    "room spinning": "dizziness",
    "numb": "numbness",
    "numbness": "numbness",
    "tingling": "tingling",
    "pins and needles": "tingling",
    "shaking": "tremor",
    "trembling": "tremor",
    "can't focus": "concentration difficulty",
    "can't concentrate": "concentration difficulty",
    "poor concentration": "concentration difficulty",
    # Mental health
    "sad": "low mood",
    "feeling low": "low mood",
    "feeling down": "low mood",
    "hopeless": "low mood",
    "worried": "anxiety",
    "nervous": "anxiety",
    "panicking": "anxiety",
    "panic": "anxiety",
    "can't sleep": "insomnia",
    "sleepless": "insomnia",
    "trouble sleeping": "insomnia",
    "difficulty sleeping": "insomnia",
    "sleep disturbance": "insomnia",
    # Other
    "chills": "chills",
    "shivering": "chills",
    "rigors": "chills",
    "sweating": "sweating",
    "night sweats": "sweating",
    "excessive sweating": "sweating",
    "sweaty": "sweating",
    "yellow skin": "yellow skin",
    "jaundice": "yellow skin",
    "yellow eyes": "yellow eyes",
    "rapid heart beat": "rapid heartbeat",
    "fast heartbeat": "rapid heartbeat",
    "heart racing": "rapid heartbeat",
    "heart pounding": "rapid heartbeat",
    "palpitation": "rapid heartbeat",
    "palpitations": "rapid heartbeat",
    "wheezing": "wheezing",
    "whistling breath": "wheezing",
    "chest tightness": "chest tightness",
    "chest heavy": "chest tightness",
    "facial pain": "facial pain",
    "face pain": "facial pain",
    "discharge": "discharge",
    "mucus": "mucus production",
    "phlegm": "mucus production",
    "pus": "pus",
    "weight loss": "weight loss",
    "losing weight": "weight loss",
    "lost weight": "weight loss",
    "slow healing": "slow healing",
    "wound not healing": "slow healing",
    "loss of taste": "loss of taste",
    "can't taste": "loss of taste",
    "no taste": "loss of taste",
    "loss of smell": "loss of smell",
    "can't smell": "loss of smell",
    "no smell": "loss of smell",
    "dehydration": "dehydration",
    "dehydrated": "dehydration",
    "lower abdominal pain": "lower abdominal pain",
}


def _normalize_text(text: str) -> str:
    """
    Lowercase and strip punctuation from input text.

    Args:
        text: Raw user input string.

    Returns:
        Cleaned lowercase string without punctuation.
    """
    text = text.lower().strip()
    text = text.translate(str.maketrans("", "", string.punctuation))
    # Normalize multiple spaces to single space
    text = re.sub(r"\s+", " ", text)
    return text


def _resolve_synonyms(tokens: List[str]) -> List[str]:
    """
    Replace colloquial/misspelled tokens with canonical symptom names.

    Also attempts multi-token phrase matching (longest match first).

    Args:
        tokens: List of normalized word tokens.

    Returns:
        List of resolved symptom names (may contain duplicates).
    """
    resolved: List[str] = []

    # Build phrase lookup sorted by length descending for greedy matching
    phrases = sorted(SYNONYM_MAP.keys(), key=len, reverse=True)
    i = 0
    while i < len(tokens):
        matched = False
        # Try multi-word matches first
        for phrase_len in range(min(4, len(tokens) - i), 1, -1):
            candidate = " ".join(tokens[i : i + phrase_len])
            if candidate in SYNONYM_MAP:
                resolved.append(SYNONYM_MAP[candidate])
                i += phrase_len
                matched = True
                break
        if not matched:
            # Try single-word match
            word = tokens[i]
            if word in SYNONYM_MAP:
                resolved.append(SYNONYM_MAP[word])
            i += 1

    return resolved


def extract_symptoms(
    text: str,
    known_symptoms: Optional[Set[str]] = None,
) -> List[str]:
    """
    Extract recognized symptoms from free-text user input.

    Uses a multi-pass strategy:
      1. Normalize text (lowercase, remove punctuation).
      2. Resolve synonyms and colloquial expressions.
      3. Match against the known symptom vocabulary.

    Args:
        text: Raw natural-language symptom description.
        known_symptoms: Set of canonical symptom names from the training
            dataset. If None, returns all resolved synonyms without filtering.

    Returns:
        Deduplicated, ordered list of recognized symptom names found in input.

    Example:
        >>> extract_symptoms("I have fever and head ache for 2 days")
        ['fever', 'headache']
    """
    if not text or not text.strip():
        logger.warning("Received empty symptom text for extraction.")
        return []

    normalized = _normalize_text(text)
    tokens = normalized.split()
    resolved = _resolve_synonyms(tokens)

    # Also try direct phrase matching on the normalized text
    for phrase in SYNONYM_MAP:
        if phrase in normalized:
            canonical = SYNONYM_MAP[phrase]
            if canonical not in resolved:
                resolved.append(canonical)

    # Filter against known vocabulary if provided
    if known_symptoms is not None:
        filtered: List[str] = []
        for symptom in resolved:
            if symptom in known_symptoms:
                filtered.append(symptom)
            # Partial match fallback (e.g., "severe headache" -> "headache")
            else:
                for known in known_symptoms:
                    if known in symptom or symptom in known:
                        if known not in filtered:
                            filtered.append(known)
                        break
        result = list(dict.fromkeys(filtered))  # deduplicate preserving order
    else:
        result = list(dict.fromkeys(resolved))

    logger.info("Extracted symptoms: %s from input: '%s'", result, text[:80])
    return result