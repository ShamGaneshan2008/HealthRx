"""Pydantic models for request validation and response serialization."""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


# =========================
# INPUT
# =========================

class SymptomInput(BaseModel):
    symptoms: str = Field(..., min_length=2, max_length=2000)
    allergies: Optional[List[str]] = None
    duration_days: Optional[int] = Field(default=None, ge=0, le=365)

    @field_validator("symptoms")
    @classmethod
    def validate_symptoms(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Symptoms cannot be empty")
        return v


# =========================
# DRUG INFO (MATCHES ROUTER)
# =========================

class DrugInfo(BaseModel):
    name: str
    dosage: Optional[str] = None   # ✅ matches your route


# =========================
# WARNINGS (MATCHES ROUTER)
# =========================

class WarningItem(BaseModel):
    message: str
    severity: str = "medium"   # ✅ matches your route


# =========================
# RESPONSE (MATCHES ROUTER)
# =========================

class PredictionResponse(BaseModel):
    disease: str
    confidence: float
    symptoms_detected: List[str]   # ✅ matches your route
    drugs: List[DrugInfo]
    warnings: List[WarningItem]
    explanation: str
    response_time: float


# =========================
# HEALTH
# =========================

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool


# =========================
# ERROR
# =========================

class ErrorResponse(BaseModel):
    detail: str