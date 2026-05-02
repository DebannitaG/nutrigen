from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from utils.database import get_db
from utils.mongo import users_collection, feedback_collection
from models.schemas import (
    UserProfile, UserProfileResponse, DietRecommendation,
    ChatRequest, ChatResponse, FeedbackRequest
)
from services.recommendation_service import get_recommendations, compute_bmi, compute_bmr, get_bmi_category
from services.ml_service import predict_goal
from rag.rag_service import chat_with_rag
import logging
from datetime import datetime
from bson import ObjectId

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/profile", response_model=UserProfileResponse)
async def create_profile(profile: UserProfile, db: Session = Depends(get_db)):
    try:
        bmi = compute_bmi(profile.weight_kg, profile.height_cm)
        bmr = compute_bmr(profile.weight_kg, profile.height_cm, profile.age, profile.gender)
        activity_map = {
            "sedentary": 1.2, "lightly_active": 1.375,
            "moderately_active": 1.55, "very_active": 1.725, "extra_active": 1.9
        }
        tdee = bmr * activity_map.get(profile.activity_level, 1.55)
        adjustment = {"weight_loss": -500, "weight_gain": 500, "maintenance": 0}
        target_calories = tdee + adjustment.get(profile.goal, 0)

        user_doc = {
            **profile.dict(),
            "bmi": bmi,
            "bmr": round(bmr, 2),
            "tdee": round(tdee, 2),
            "target_calories": round(target_calories, 2),
            "created_at": datetime.utcnow()
        }
        result = await users_collection.insert_one(user_doc)
        user_id = str(result.inserted_id)

        return UserProfileResponse(
            user_id=user_id,
            name=profile.name,
            bmi=bmi,
            bmi_category=get_bmi_category(bmi),
            bmr=round(bmr, 2),
            tdee=round(tdee, 2),
            target_calories=round(target_calories, 2),
            goal=profile.goal
        )

    except Exception as e:
        logger.error(f"Profile error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend")
async def get_diet_recommendations(profile: UserProfile, db: Session = Depends(get_db)):
    try:
        result = get_recommendations(profile, db)
        return {
            "status": "success",
            "user_name": profile.name,
            "goal": profile.goal,
            **result
        }
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response, sources = chat_with_rag(
            message=request.message,
            conversation_history=request.conversation_history
        )
        return ChatResponse(response=response, sources=sources)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    try:
        doc = {
            **feedback.dict(),
            "created_at": datetime.utcnow()
        }
        result = await feedback_collection.insert_one(doc)
        return {"status": "success", "feedback_id": str(result.inserted_id)}
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "HealthGuard AI"}


@router.get("/foods")
async def list_foods(db: Session = Depends(get_db)):
    from utils.database import FoodItem
    foods = db.query(FoodItem).all()
    return [
        {
            "id": f.id, "food_name": f.food_name,
            "calories": f.calories, "protein": f.protein,
            "fat": f.fat, "carbs": f.carbs,
            "category": f.category, "region": f.region,
            "meal_type": f.meal_type
        }
        for f in foods
    ]