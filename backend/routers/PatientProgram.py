from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from pydantic import BaseModel
import json

router = APIRouter()

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    import os
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.6)
except Exception:
    llm = None

COLUMN_TRANSLATIONS = {
    "1": "Код карты пациента",
    "2": "Пол пациента",
    "9": "Рост (см)",
    "10": "Вес (кг)",
    "11": "ИМТ (кг/м^2)",
    "30": "Хронические заболевания",
    "854": "Индекс Бартел",
    "FA": "Уровень физической активности",
}

class ProgramResponse(BaseModel):
    patient_code: int
    program: list[str]
    processing_errors: list[str]

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

def safe_get(data, key, is_numeric=False, default=None):
    value = data.get(key)
    if value is None or value == "":
        return default
    if is_numeric:
        try:
            return float(str(value).replace(',', '.'))
        except:
            return default
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)

@router.get("/rehab-program/{patient_code}", response_model=ProgramResponse)
def get_rehabilitation_program(patient_code: int, db: Session = Depends(get_db)):
        processing_errors = []
        stmt_cols = text("SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'fa_numeric'")
        columns = [row[0] for row in db.execute(stmt_cols).fetchall()]
        select_cols_str = ", ".join([f'"{col}"' for col in columns])
        stmt = text(f'SELECT {select_cols_str} FROM fa_numeric WHERE "1" = :code')
        result = db.execute(stmt, {"code": patient_code}).mappings().first()
        if not result:
            raise HTTPException(status_code=404, detail=f"Пациент с кодом {patient_code} не найден.")
        patient_data = dict(result)
        patient_info = [
            {
                "field_id": col,
                "field_name": COLUMN_TRANSLATIONS.get(col, f"Поле {col}"),
                "value": safe_get(patient_data, col, is_numeric=col in ["9", "10", "11", "854"])
            }
            for col, value in patient_data.items() if value is not None and value != ""
        ]
        patient_summary = "Данные пациента:\n" + "\n".join(
            f"- {info['field_name']} (ID: {info['field_id']}): {info['value']}" for info in patient_info
        )
        prompt = f"""
Вы - медицинский эксперт по гериатрической реабилитации. Составьте программу реабилитации на основе данных пациента.
### Данные пациента:
{patient_summary}
### Инструкции:
- Программа должна быть разделена на секции (питание, физическая активность, медикаментозная терапия).
- Каждая секция начинается с заголовка: `## Название секции`.
- Рекомендации внутри секции: `- Рекомендация`.
- Рекомендации должны быть конкретными, основанными на данных пациента.
"""
        if not llm:
            return ProgramResponse(patient_code=patient_code, program=["Ошибка: Модель Gemini не инициализирована"], processing_errors=["Gemini not initialized"])
        response = llm.invoke(prompt)
        program_lines = response.content.strip().split('\n') if response and response.content else ["Ошибка: Пустой ответ от модели"]
        return ProgramResponse(patient_code=patient_code, program=program_lines)