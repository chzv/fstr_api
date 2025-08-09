from fastapi import FastAPI, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from pydantic import EmailStr

from .db import get_db, Base, engine
from .schemas import SubmitDataIn, SubmitDataOut, PerevalOut, PatchOut
from .repository import DataRepository

app = FastAPI(title="FSTR Submit API", version="2.0.0")

# На проде — Alembic, здесь создаём, если не существует
Base.metadata.create_all(bind=engine)

# ====== Спринт 1: создание ======
@app.post("/submitData", response_model=SubmitDataOut)
async def submit_data(payload: SubmitDataIn, db: Session = Depends(get_db)):
    repo = DataRepository(db)
    try:
        new_id = repo.create_pereval_from_payload(payload.dict())
        return SubmitDataOut(status=200, message=None, id=new_id)
    except ValueError as ve:
        db.rollback()
        return JSONResponse(content={"status": 400, "message": str(ve), "id": None}, status_code=400)
    except IntegrityError as ie:
        db.rollback()
        return JSONResponse(content={"status": 400, "message": "Нарушение уникальности: " + str(ie.orig), "id": None}, status_code=400)
    except Exception as e:
        db.rollback()
        return JSONResponse(content={"status": 500, "message": "Ошибка сервера: " + str(e), "id": None}, status_code=500)

# ====== Спринт 2: чтение одной записи ======
@app.get("/submitData/{pereval_id}", response_model=PerevalOut)
async def get_pereval(pereval_id: int, db: Session = Depends(get_db)):
    repo = DataRepository(db)
    per = repo.get_pereval(pereval_id)
    if not per:
        return JSONResponse(content={"detail": "Not found"}, status_code=404)
    return repo.to_dict(per)

# ====== Спринт 2: правка (только status=new, без изменений ФИО/email/phone) ======
@app.patch("/submitData/{pereval_id}", response_model=PatchOut)
async def patch_pereval(pereval_id: int, payload: SubmitDataIn, db: Session = Depends(get_db)):
    repo = DataRepository(db)
    try:
        repo.update_pereval_from_payload(pereval_id, payload.dict())
        return PatchOut(state=1, message=None)
    except ValueError as ve:
        db.rollback()
        return PatchOut(state=0, message=str(ve))
    except IntegrityError as ie:
        db.rollback()
        return PatchOut(state=0, message="Нарушение уникальности: " + str(ie.orig))
    except Exception as e:
        db.rollback()
        return PatchOut(state=0, message="Ошибка сервера: " + str(e))

# ====== Спринт 2: список пользователя по email ======
@app.get("/submitData/", response_model=List[PerevalOut])
async def list_by_user_email(user__email: EmailStr = Query(..., description="email пользователя"), db: Session = Depends(get_db)):
    repo = DataRepository(db)
    items = repo.list_perevals_by_email(user__email)
    return [repo.to_dict(p) for p in items]
