import base64
from datetime import datetime
from sqlalchemy.orm import Session
from . import models

def _norm_email(email: str) -> str:
    return (email or "").strip().lower()

class DataRepository:
    def __init__(self, db: Session):
        self.db = db

    def _get_or_create_user(self, full_name: str, email: str, phone: str) -> models.User:
        user = self.db.query(models.User).filter(models.User.email == _norm_email(email)).one_or_none()
        if user:
            changed = False
            if user.full_name != full_name:
                user.full_name = full_name
                changed = True
            if user.phone != phone:
                user.phone = phone
                changed = True
            if changed:
                self.db.add(user)
            return user
        user = models.User(full_name=full_name, email=_norm_email(email), phone=phone)
        self.db.add(user)
        self.db.flush()
        return user

    def _create_coords(self, lat: str, lon: str, height: str) -> models.Coords:
        coords = models.Coords(
            latitude=float(lat),
            longitude=float(lon),
            height=int(height)
        )
        self.db.add(coords)
        self.db.flush()
        return coords

    def _create_levels(self, level: dict) -> models.Levels:
        levels = models.Levels(
            winter=level.get("winter", "") or "",
            summer=level.get("summer", "") or "",
            autumn=level.get("autumn", "") or "",
            spring=level.get("spring", "") or "",
        )
        self.db.add(levels)
        self.db.flush()
        return levels

    def _create_images(self, pereval_id: int, images: list):
        for img in images:
            raw = img["data"]
            try:
                blob = base64.b64decode(raw, validate=True)
            except Exception as e:
                raise ValueError(f"Некорректная картинка (base64): {e}")
            image = models.Image(pereval_id=pereval_id, title=img["title"], data=blob)
            self.db.add(image)

    def create_pereval_from_payload(self, payload: dict) -> int:
        user_full_name = " ".join(
            [payload["user"]["fam"], payload["user"]["name"]] + (
                [payload["user"]["otc"]] if payload["user"].get("otc") else []
            )
        )
        user = self._get_or_create_user(
            full_name=user_full_name,
            email=payload["user"]["email"],
            phone=payload["user"]["phone"],
        )

        coords = self._create_coords(
            lat=payload["coords"]["latitude"],
            lon=payload["coords"]["longitude"],
            height=payload["coords"]["height"],
        )

        levels = self._create_levels(payload.get("level", {}))

        try:
            try:
                add_dt = datetime.fromisoformat(payload["add_time"])
            except Exception:
                add_dt = datetime.strptime(payload["add_time"], "%Y-%m-%d %H:%M:%S")
        except Exception:
            raise ValueError("Некорректное поле add_time, ожидается 'YYYY-MM-DD HH:MM:SS'")

        pereval = models.Pereval(
            beauty_title=payload["beauty_title"],
            title=payload["title"],
            other_titles=payload.get("other_titles", "") or "",
            connect=payload.get("connect", "") or "",
            add_time=add_dt,
            user_id=user.id,
            coords_id=coords.id,
            levels_id=levels.id,
            status=models.ModerationStatus.new,
            moderator_note="",
        )
        self.db.add(pereval)
        self.db.flush()

        images = payload.get("images", [])
        if not images:
            raise ValueError("Отсутствуют изображения (images)")
        self._create_images(pereval.id, images)

        self.db.commit()
        return int(pereval.id)
