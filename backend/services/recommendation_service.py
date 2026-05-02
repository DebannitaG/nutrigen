import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from utils.database import FoodItem
from models.schemas import UserProfile, MealItem
from services.ml_service import predict_goal
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

ACTIVITY_MULTIPLIER = {
    "sedentary": 1.2,
    "lightly_active": 1.375,
    "moderately_active": 1.55,
    "very_active": 1.725,
    "extra_active": 1.9
}

GOAL_CALORIE_ADJUSTMENT = {
    "weight_loss": -500,
    "weight_gain": +500,
    "maintenance": 0
}

MEAL_CALORIE_SPLIT = {
    "breakfast": 0.25,
    "lunch": 0.35,
    "dinner": 0.30,
    "snacks": 0.10
}

def compute_bmi(weight_kg: float, height_cm: float) -> float:
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 2)

def compute_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    if gender == "male":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

def get_bmi_category(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def filter_foods_by_preference(foods: List[FoodItem], diet_pref: str, region: str) -> List[FoodItem]:
    JAIN_EXCLUDED = ["onion", "garlic", "potato", "carrot", "radish", "beetroot"]
    SATTVIC_EXCLUDED = ["onion", "garlic", "egg", "meat", "fish", "chicken"]

    filtered = []
    for food in foods:
        food_name_lower = food.food_name.lower()

        # Vegetarian — no meat or fish
        if diet_pref == "veg" and food.category == "non-veg":
            continue

        # Eggetarian — veg + eggs only
        if diet_pref == "eggetarian":
            if food.category == "non-veg" and "egg" not in food_name_lower:
                continue

        # Pescatarian — veg + fish only
        if diet_pref == "pescatarian":
            if food.category == "non-veg":
                if not any(word in food_name_lower for word in ["fish", "salmon", "tuna", "maach", "ilish", "chingri"]):
                    continue

        # Jain — veg, no root vegetables or onion/garlic
        if diet_pref == "jain":
            if food.category == "non-veg":
                continue
            if any(word in food_name_lower for word in JAIN_EXCLUDED):
                continue

        # Sattvic — pure veg, no onion/garlic/eggs
        if diet_pref == "sattvic":
            if food.category == "non-veg":
                continue
            if any(word in food_name_lower for word in SATTVIC_EXCLUDED):
                continue

        # Vegan — no animal products
        if diet_pref == "vegan":
            if food.category == "non-veg":
                continue
            if any(word in food_name_lower for word in ["egg", "milk", "yogurt", "curd", "paneer", "ghee", "honey", "doi"]):
                continue

        # Veg + Non-Veg and Non-Veg — everything allowed
        # No filtering needed

        # Region filter
        if region != "global" and food.region not in ["global", region]:
            continue

        filtered.append(food)
    return filtered

def apply_health_constraints(foods: List[FoodItem], health_conditions: List[str]) -> List[FoodItem]:
    HIGH_SUGAR = ["Mishti Doi (Sweet Yogurt)", "Sandesh", "Mango", "Banana", "Watermelon", "Luchi (Fried Bread)"]
    HIGH_SODIUM = ["Chicken Curry", "Fish Curry", "Kosha Mangsho (Mutton)"]
    HIGH_FAT = ["Luchi (Fried Bread)", "Begun Bhaja (Fried Eggplant)", "Sandesh", "Kosha Mangsho (Mutton)"]
    HIGH_PURINE = ["Kosha Mangsho (Mutton)", "Chicken Breast", "Shorshe Ilish", "Tuna (canned)"]
    HIGH_CHOLESTEROL = ["Boiled Eggs", "Egg White", "Kosha Mangsho (Mutton)", "Chicken Curry"]
    HIGH_FIBER = ["Oats", "Brown Rice", "Quinoa", "Chickpeas", "Rajma", "Lentil Soup"]
    GLUTEN_FOODS = ["Whole Wheat Bread", "Roti (Wheat)", "Luchi (Fried Bread)", "Upma", "Poha"]
    DAIRY_FOODS = ["Milk (whole)", "Greek Yogurt", "Paneer", "Cottage Cheese", "Mishti Doi (Sweet Yogurt)", "Curd Rice"]

    filtered = []
    for food in foods:
        # Diabetes — avoid high sugar foods
        if "diabetes" in health_conditions and food.food_name in HIGH_SUGAR:
            continue

        # Hypertension — avoid high sodium foods
        if "hypertension" in health_conditions and food.food_name in HIGH_SODIUM:
            continue

        # Heart disease — avoid high fat foods
        if "heart disease" in health_conditions and food.food_name in HIGH_FAT:
            continue

        # High cholesterol — avoid cholesterol rich foods
        if "cholesterol" in health_conditions and food.food_name in HIGH_CHOLESTEROL:
            continue

        # Kidney disease — avoid high protein foods
        if "kidney disease" in health_conditions and food.protein > 20:
            continue

        # Uric acid / gout — avoid high purine foods
        if "uric acid / gout" in health_conditions and food.food_name in HIGH_PURINE:
            continue

        # IBS — avoid high fiber foods
        if "ibs" in health_conditions and food.food_name in HIGH_FIBER:
            continue

        # Celiac disease — avoid gluten foods
        if "celiac disease" in health_conditions and food.food_name in GLUTEN_FOODS:
            continue

        # Lactose intolerance — avoid dairy foods
        if "lactose intolerance" in health_conditions and food.food_name in DAIRY_FOODS:
            continue

        # Obesity — avoid high calorie foods
        if "obesity" in health_conditions and food.calories > 350:
            continue

        # Fatty liver — avoid high fat foods
        if "fatty liver" in health_conditions and food.fat > 15:
            continue

        filtered.append(food)
    return filtered

def select_meals_for_slot(foods: List[FoodItem], meal_type: str,
                           target_calories: float, n: int = 3) -> List[MealItem]:
    slot_foods = [f for f in foods if f.meal_type == meal_type or f.meal_type == "any"]

    if not slot_foods:
        slot_foods = foods

    per_item_cal = target_calories / n
    scored = sorted(slot_foods, key=lambda f: abs(f.calories - per_item_cal))
    selected = scored[:n]

    return [
        MealItem(
            food_name=f.food_name,
            calories=f.calories,
            protein=f.protein,
            fat=f.fat,
            carbs=f.carbs,
            fiber=f.fiber,
            category=f.category,
            region=f.region
        )
        for f in selected
    ]

def generate_explanation(profile: UserProfile, bmi: float, goal: str,
                          target_calories: float, ml_goal: str) -> str:
    bmi_cat = get_bmi_category(bmi)
    explanation = (
        f"Based on your profile — {profile.age} years old, {bmi_cat} (BMI: {bmi}), "
        f"{profile.activity_level.replace('_', ' ')} lifestyle — "
        f"your daily calorie target is set at {target_calories:.0f} kcal for {goal.replace('_', ' ')}. "
    )
    if ml_goal != goal:
        explanation += (
            f"Our ML model also suggests '{ml_goal.replace('_', ' ')}' based on your metabolic profile. "
        )
    if "diabetes" in profile.health_conditions:
        explanation += "High-sugar foods have been excluded due to diabetes. "
    if "hypertension" in profile.health_conditions:
        explanation += "High-sodium foods have been excluded due to hypertension. "
    if "heart disease" in profile.health_conditions:
        explanation += "High-fat foods have been excluded due to heart disease. "
    if "kidney disease" in profile.health_conditions:
        explanation += "High-protein foods have been limited due to kidney disease. "
    if "celiac disease" in profile.health_conditions:
        explanation += "Gluten-containing foods have been excluded due to celiac disease. "
    if "lactose intolerance" in profile.health_conditions:
        explanation += "Dairy foods have been excluded due to lactose intolerance. "
    if profile.region != "global":
        explanation += f"Meals are customized with {profile.region} regional foods for cultural familiarity. "
    return explanation

def get_recommendations(profile: UserProfile, db: Session) -> Dict:
    bmi = compute_bmi(profile.weight_kg, profile.height_cm)
    bmr = compute_bmr(profile.weight_kg, profile.height_cm, profile.age, profile.gender)
    tdee = bmr * ACTIVITY_MULTIPLIER.get(profile.activity_level, 1.55)
    adjustment = GOAL_CALORIE_ADJUSTMENT.get(profile.goal, 0)
    target_calories = tdee + adjustment

    ml_goal = predict_goal(
        age=profile.age,
        gender=profile.gender,
        bmi=bmi,
        activity_level=profile.activity_level,
        health_condition=profile.health_conditions[0] if profile.health_conditions else "none"
    )

    all_foods = db.query(FoodItem).all()
    filtered = filter_foods_by_preference(all_foods, profile.diet_preference, profile.region)
    filtered = apply_health_constraints(filtered, profile.health_conditions)

    breakfast = select_meals_for_slot(
        filtered, "breakfast",
        target_calories * MEAL_CALORIE_SPLIT["breakfast"], n=3
    )
    lunch = select_meals_for_slot(
        filtered, "lunch",
        target_calories * MEAL_CALORIE_SPLIT["lunch"], n=3
    )
    dinner = select_meals_for_slot(
        filtered, "dinner",
        target_calories * MEAL_CALORIE_SPLIT["dinner"], n=3
    )
    snacks = select_meals_for_slot(
        filtered, "snack",
        target_calories * MEAL_CALORIE_SPLIT["snacks"], n=2
    )

    all_meals = breakfast + lunch + dinner + snacks
    total_cal = sum(m.calories for m in all_meals)
    total_prot = sum(m.protein for m in all_meals)
    total_carbs = sum(m.carbs for m in all_meals)
    total_fat = sum(m.fat for m in all_meals)

    explanation = generate_explanation(
        profile, bmi, profile.goal, target_calories, ml_goal
    )

    return {
        "bmi": bmi,
        "bmi_category": get_bmi_category(bmi),
        "bmr": round(bmr, 2),
        "tdee": round(tdee, 2),
        "target_calories": round(target_calories, 2),
        "breakfast": breakfast,
        "lunch": lunch,
        "dinner": dinner,
        "snacks": snacks,
        "total_calories": round(total_cal, 2),
        "total_protein": round(total_prot, 2),
        "total_carbs": round(total_carbs, 2),
        "total_fat": round(total_fat, 2),
        "explanation": explanation,
        "ml_predicted_goal": ml_goal
    }