from pydantic import BaseModel, EmailStr, constr, validator
from typing import List, Optional
from datetime import datetime

class UserIn(BaseModel):
    email: EmailStr
    fam: constr(strip_whitespace=True, min_length=1)
    name: constr(strip_whitespace=True, min_length=1)
    otc: constr(strip_whitespace=True, min_length=0) = ""
    phone: constr(strip_whitespace=True, min_length=3)

    @property
    def full_name(self) -> str:
        parts = [self.fam, self.name]
        if self.otc:
            parts.append(self.otc)
        return " ".join(parts)

class CoordsIn(BaseModel):
    latitude: constr(strip_whitespace=True, min_length=1)
    longitude: constr(strip_whitespace=True, min_length=1)
    height: constr(strip_whitespace=True, min_length=1)

    @validator("latitude", "longitude")
    def check_float(cls, v):
        float(v)
        return v

    @validator("height")
    def check_int(cls, v):
        int(v)
        return v

class LevelIn(BaseModel):
    winter: str = ""
    summer: str = ""
    autumn: str = ""
    spring: str = ""

class ImageIn(BaseModel):
    data: constr(min_length=1)
    title: constr(strip_whitespace=True, min_length=1)

class SubmitDataIn(BaseModel):
    beauty_title: constr(strip_whitespace=True, min_length=1)
    title: constr(strip_whitespace=True, min_length=1)
    other_titles: str = ""
    connect: str = ""
    add_time: constr(strip_whitespace=True, min_length=1)
    user: UserIn
    coords: CoordsIn
    level: LevelIn
    images: List[ImageIn]

    @validator("add_time")
    def check_dt(cls, v):
        try:
            datetime.fromisoformat(v)
        except Exception:
            datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        return v

class SubmitDataOut(BaseModel):
    status: int
    message: Optional[str] = None
    id: Optional[int] = None
