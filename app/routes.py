from fastapi import APIRouter, HTTPException
from typing import List
import time
from pydantic import BaseModel

from app.schemas import (
    SymptomInput,
    PredictionResponse,
    DrugInfo,
    WarningItem,
    ErrorResponse,
)
from app.ml.preprocess import extract_symptoms
from app.ml.model import predictor
from app.services.drug_service import recommend_drugs, generate_explanation
from app.services.safety import generate_warnings


router = APIRouter()

# =========================
# 💬 CHAT ENDPOINT
# =========================

class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
async def chat(req: ChatRequest):
    try:
        user_msg = req.message.lower()

        if "fever" in user_msg:
            reply = "You may have a fever-related illness like Flu. Stay hydrated and rest."
        elif "headache" in user_msg:
            reply = "Headache could be due to stress, dehydration, or migraine."
        elif "cough" in user_msg:
            reply = "Cough may indicate a cold or respiratory infection."
        else:
            reply = "Please describe your symptoms more clearly."

        # ✅ FIXED (frontend expects 'reply')
        return {"reply": reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# 🩺 HEALTH CHECK
# =========================
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": predictor.is_trained
    }


# =========================
# 📋 LIST DISEASES
# =========================
@router.get("/diseases", response_model=List[str])
async def list_diseases():
    return predictor.supported_diseases


# =========================
# 🤖 PREDICT
# =========================
@router.post("/predict", response_model=PredictionResponse)
async def predict_disease(input_data: SymptomInput):

    start_time = time.perf_counter()

    try:
        detected_symptoms = extract_symptoms(
            text=input_data.symptoms,
            known_symptoms=set(predictor.symptom_vocab),
        )

        if not detected_symptoms:
            raise HTTPException(
                status_code=400,
                detail="No valid symptoms detected"
            )

        prediction = predictor.predict(detected_symptoms)

        drugs = recommend_drugs(prediction["disease"], input_data.allergies)

        warnings = generate_warnings(
            prediction["disease"],
            drugs,
            input_data.allergies
        )

        explanation = generate_explanation(
            prediction["disease"],
            detected_symptoms
        )

        response_time = round(time.perf_counter() - start_time, 3)

        return PredictionResponse(
            disease=prediction["disease"],
            confidence=prediction["confidence"],
            symptoms_detected=detected_symptoms,
            drugs=[DrugInfo(name=d["name"], dosage=d.get("dosage")) for d in drugs],
            warnings=[WarningItem(message=w["message"]) for w in warnings],
            explanation=explanation,
            response_time=response_time,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))