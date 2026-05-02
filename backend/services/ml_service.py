import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
import logging

logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../models/rf_model.pkl")
SCALER_PATH = os.path.join(os.path.dirname(__file__), "../models/scaler.pkl")
ENCODER_PATH = os.path.join(os.path.dirname(__file__), "../models/encoders.pkl")
DATA_PATH = os.path.join(os.path.dirname(__file__), "../../data/ml_training.csv")

ACTIVITY_MAP = {
    "sedentary": 0, "lightly_active": 1,
    "moderately_active": 2, "very_active": 3, "extra_active": 4
}
GENDER_MAP = {"male": 0, "female": 1, "other": 2}
HEALTH_MAP = {"none": 0, "diabetes": 1, "hypertension": 2, "both": 3}

def train_model():
    df = pd.read_csv(DATA_PATH)

    df["gender_enc"] = df["gender"].map(GENDER_MAP)
    df["activity_enc"] = df["activity_level"].map(ACTIVITY_MAP)
    df["health_enc"] = df["health_condition"].map(HEALTH_MAP).fillna(0)

    features = ["age", "gender_enc", "bmi", "activity_enc", "health_enc"]
    X = df[features]
    y = df["goal"]

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_enc, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=6)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    logger.info(f"Model Accuracy: {acc:.2f}")
    logger.info(f"\n{classification_report(y_test, y_pred, target_names=le.classes_)}")

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    joblib.dump(le, ENCODER_PATH)

    return acc

def predict_goal(age: int, gender: str, bmi: float, activity_level: str,
                 health_condition: str = "none") -> str:
    try:
        if not os.path.exists(MODEL_PATH):
            train_model()

        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        le = joblib.load(ENCODER_PATH)

        gender_enc = GENDER_MAP.get(gender, 0)
        activity_enc = ACTIVITY_MAP.get(activity_level, 1)
        health_cond = "none"
        if health_condition:
            conds = [c.lower().strip() for c in health_condition] if isinstance(health_condition, list) else [health_condition]
            if "diabetes" in conds and "hypertension" in conds:
                health_cond = "both"
            elif "diabetes" in conds:
                health_cond = "diabetes"
            elif "hypertension" in conds:
                health_cond = "hypertension"
        health_enc = HEALTH_MAP.get(health_cond, 0)

        X = np.array([[age, gender_enc, bmi, activity_enc, health_enc]])
        X_scaled = scaler.transform(X)
        pred = model.predict(X_scaled)
        return le.inverse_transform(pred)[0]

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return "maintenance"