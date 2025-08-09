from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from .db import get_db, Base, engine
from .schemas import SubmitDataIn, SubmitDataOut
from .repository import DataRepository

app = FastAPI(title="FSTR Submit API", version="1.0.0")

Base.metadata.create_all(bind=engine)

@app.post("/submitData", response_model=SubmitDataOut)
async def submit_data(payload: SubmitDataIn, db: Session = Depends(get_db)):
    repo = DataRepository(db)
    try:
        new_id = repo.create_pereval_from_payload(payload.dict())
        return SubmitDataOut(status=200, message=None, id=new_id)
    except ValueError as ve:
        db.rollback()
        return JSONResponse(content={"status": 400, "message": str(ve), "id": None}, status_code=400)
    except Exception as e:
        db.rollback()
        return JSONResponse(content={"status": 500, "message": "Ошибка сервера: " + str(e), "id": None}, status_code=500)
