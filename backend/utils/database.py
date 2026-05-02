from sqlalchemy import create_engine, Column, Integer, String, Float, text
from sqlalchemy.orm import declarative_base, sessionmaker
import pandas as pd
import os

DATABASE_URL = "sqlite:///./healthguard.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class FoodItem(Base):
    __tablename__ = "foods"
    id = Column(Integer, primary_key=True, index=True)
    food_name = Column(String, index=True)
    calories = Column(Float)
    protein = Column(Float)
    fat = Column(Float)
    carbs = Column(Float)
    fiber = Column(Float, default=0.0)
    category = Column(String)
    region = Column(String, default="global")
    meal_type = Column(String, default="any")

def init_db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    count = session.execute(text("SELECT COUNT(*) FROM foods")).scalar()
    if count == 0:
        csv_path = os.path.join(os.path.dirname(__file__), "../data/nutrition.csv")
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df.fillna(0, inplace=True)
            for _, row in df.iterrows():
                food = FoodItem(
                    food_name=row["food_name"],
                    calories=float(row["calories"]),
                    protein=float(row["protein"]),
                    fat=float(row["fat"]),
                    carbs=float(row["carbs"]),
                    fiber=float(row.get("fiber", 0)),
                    category=row["category"],
                    region=row.get("region", "global"),
                    meal_type=row.get("meal_type", "any")
                )
                session.add(food)
            session.commit()
    session.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()