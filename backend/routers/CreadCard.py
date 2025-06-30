from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
import json
from datetime import date

router = APIRouter()

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

class CardData(BaseModel):
    data: dict

def validate_required_fields(data):
    required_fields = {"1": "Код карты", "2": "Пол", "9": "Рост", "10": "Вес", "11": "ИМТ", "30": "Хронические заболевания"}
    for field_id, field_name in required_fields.items():
        if field_id not in data or data[field_id] is None or data[field_id] == "":
            raise HTTPException(status_code=400, detail=f"Обязательное поле '{field_name}' не заполнено")

def validate_columns(db: Session, field_ids):
    query = text("SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'fa_numeric'")
    valid_columns = {row[0] for row in db.execute(query).fetchall()}
    invalid_fields = [fid for fid in field_ids if fid not in valid_columns]
    if invalid_fields:
        raise HTTPException(status_code=400, detail=f"Следующие поля отсутствуют: {', '.join(invalid_fields)}")

def prepare_sql_value(value, field_id):
    if value is None:
        return None
    date_fields = ["47", "49", "57", "377"]
    if field_id in date_fields and value:
        try:
            return date.fromisoformat(value)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Неверный формат даты для поля {field_id}")
    array_fields = ["108", "121", "125", "374"]
    if field_id in array_fields and isinstance(value, (list, dict)):
        return json.dumps(value)
    return value

@router.post("/create-card")
async def create_card(card_data: CardData, db: Session = Depends(get_db)):
    try:
        validate_required_fields(card_data.data)
        validate_columns(db, card_data.data.keys())
        columns = [f'"{fid}"' for fid in card_data.data if card_data.data[fid] is not None and card_data.data[fid] != ""]
        values = [f':{fid}' for fid in card_data.data if card_data.data[fid] is not None and card_data.data[fid] != ""]
        params = {fid: prepare_sql_value(val, fid) for fid, val in card_data.data.items() if val is not None and val != ""}
        query = text(f"INSERT INTO fa_numeric ({', '.join(columns)}) VALUES ({', '.join(values)}) RETURNING \"1\"")
        result = db.execute(query, params)
        new_card_id = result.fetchone()[0]
        db.commit()
        return {"message": "Карта пациента успешно создана", "card_id": new_card_id}
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при создании карты: {str(e)}")