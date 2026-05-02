from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"

class ActivityLevel(str, Enum):
    sedentary = "sedentary"
    lightly_active = "lightly_active"
    moderately_active = "moderately_active"
    very_active = "very_active"
    extra_active = "extra_active"

class Goal(str, Enum):
    weight_loss = "weight_loss"
    weight_gain = "weight_gain"
    maintenance = "maintenance"

class DietPreference(str, Enum):
    veg = "veg"
    eggetarian = "eggetarian"
    non_veg = "non-veg"
    veg_nonveg = "veg-nonveg"
    jain = "jain"
    sattvic = "sattvic"
    pescatarian = "pescatarian"
    vegan = "vegan"

class Region(str, Enum):
    global_ = "global"
    indian = "indian"
    bengali = "bengali"
    south_indian = "south-indian"

class UserProfile(BaseModel):
    name: str
    age: int = Field(..., ge=10, le=100)
    gender: Gender
    height_cm: float = Field(..., ge=100, le=250)
    weight_kg: float = Field(..., ge=20, le=300)
    activity_level: ActivityLevel
    goal: Goal
    diet_preference: DietPreference = DietPreference.veg
    region: Region = Region.global_
    health_conditions: List[str] = []

class UserProfileResponse(BaseModel):
    user_id: str
    name: str
    bmi: float
    bmi_category: str
    bmr: float
    tdee: float
    target_calories: float
    goal: str

class MealItem(BaseModel):
    food_name: str
    calories: float
    protein: float
    fat: float
    carbs: float
    fiber: float
    category: str
    region: str

class DietRecommendation(BaseModel):
    user_id: str
    goal: str
    target_calories: float
    breakfast: List[MealItem]
    lunch: List[MealItem]
    dinner: List[MealItem]
    snacks: List[MealItem]
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    explanation: str
    ml_predicted_goal: str

class ChatRequest(BaseModel):
    user_id: Optional[str] = None
    message: str
    conversation_history: List[dict] = []

class ChatResponse(BaseModel):
    response: str
    sources: List[str] = []

class FeedbackRequest(BaseModel):
    user_id: str
    meal_name: str
    feedback: str
    comment: Optional[str] = None