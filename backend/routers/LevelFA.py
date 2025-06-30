from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
import pandas as pd
from pydantic import BaseModel
from catboost import CatBoostClassifier
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

try:
    second_model = CatBoostClassifier()
    second_model.load_model('/home/user/RehabilitationProject_FA/catboost_physical_activity_model_2.cbm')
    logger.info("Second CatBoost model loaded successfully")
except Exception as e:
    second_model = None
    logger.error(f"Failed to load second CatBoost model: {str(e)}")

second_model_features = [
    "Интерпретация.динамометрии.(0.-.16.кг.и.более.у.женщин/.27.и.более.у.мужчин.(саркопении.нет);.1.-.менее.16.кг.у.женщин/.менее.27.у.мужчин.(саркопения)).(Динамометрия.(2.попытки))",
    "Положение.«стопы.вместе».(Время,.секунды).(Кратка)",
    "Ходьба.на.4.м.(Время,.секунды).(Кратка)",
    "Шкала.Бартел,.общий.балл.(Оценка.гериатрического.индекса.здоровья)",
]

class SinglePredictionRequest(BaseModel):
    code: int

class ManualPredictionRequest(BaseModel):
    dynamometry: float
    feet_together: float
    walk_4m: float
    barthel_score: float

class SinglePredictionResponse(BaseModel):
    message: str
    activity_level: str

def get_db():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    DATABASE_URL = "данные авторизации и подключение к БД"
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def extract_numeric_value(value):
    if isinstance(value, str):
        import re
        match = re.search(r'[\d,.]+', value.replace(',', '.'))
        return float(match.group()) if match else 0
    return float(value) if value is not None else 0

@router.get("/patients")
def get_all_patients(db: Session = Depends(get_db)):
    try:
        stmt = text('SELECT "1" AS code, "2" AS gender FROM fa_numeric')
        result = db.execute(stmt).fetchall()
        return [{"code": row.code, "gender": row.gender or "N/A"} for row in result]
    except Exception as e:
        logger.error(f"Error fetching patients: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.get("/patients/{code}")
def get_patient_by_code(code: int, db: Session = Depends(get_db)):
    try:
        stmt = text('SELECT "1" AS code, "2" AS gender, "FA" AS activity_level FROM fa_numeric WHERE "1" = :code')
        result = db.execute(stmt, {"code": code}).fetchone()
        if not result:
            raise HTTPException(status_code=404, detail=f"Patient with code {code} not found")
        return {"code": result.code, "patient_info": f"{result.gender or 'N/A'}, {result.activity_level or 'Не оценено'}"}
    except Exception as e:
        logger.error(f"Error fetching patient {code}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.post("/predict-activity-manual", response_model=SinglePredictionResponse)
def predict_activity_manual(request: ManualPredictionRequest, db: Session = Depends(get_db)):
    if second_model is None:
        raise HTTPException(status_code=500, detail="Second model not loaded. Check path and server logs.")
    try:
        input_data = {
            second_model_features[0]: request.dynamometry,
            second_model_features[1]: request.feet_together,
            second_model_features[2]: request.walk_4m,
            second_model_features[3]: request.barthel_score,
        }
        df_predict = pd.DataFrame([input_data], columns=second_model_features)
        for col in second_model_features:
            df_predict[col] = df_predict[col].astype(float)
        prediction = second_model.predict(df_predict)
        activity_str = {0: "Низкий", 1: "Средний", 2: "Высокий"}.get(prediction.flatten()[0], "Ошибка предсказания")
        return SinglePredictionResponse(
            message="Уровень физической активности успешно оценён.",
            activity_level=activity_str
        )
    except Exception as e:
        logger.error(f"Error predicting with manual input: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")