import base64
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from . import models

def _norm_email(email: str) -> str:
    return (email or "").strip().lower()

class DataRepository:
    def __init__(self, db: Session):
        self.db = db

    # ====== CREATE ======
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

    # ====== READ ======
    def get_pereval(self, pereval_id: int) -> Optional[models.Pereval]:
        return (
            self.db.query(models.Pereval)
            .options(
                joinedload(models.Pereval.user),
                joinedload(models.Pereval.coords),
                joinedload(models.Pereval.levels),
                joinedload(models.Pereval.images),
            )
            .filter(models.Pereval.id == pereval_id)
            .one_or_none()
        )

    def list_perevals_by_email(self, email: str) -> List[models.Pereval]:
        return (
            self.db.query(models.Pereval)
            .join(models.User, models.Pereval.user_id == models.User.id)
            .options(
                joinedload(models.Pereval.user),
                joinedload(models.Pereval.coords),
                joinedload(models.Pereval.levels),
                joinedload(models.Pereval.images),
            )
            .filter(models.User.email == _norm_email(email))
            .order_by(models.Pereval.id.desc())
            .all()
        )

    # ====== UPDATE (только когда status=new; запрещаем менять ФИО/email/phone) ======
    def update_pereval_from_payload(self, pereval_id: int, payload: dict) -> None:
        per = self.get_pereval(pereval_id)
        if not per:
            raise ValueError("Объект не найден")
        if per.status != models.ModerationStatus.new:
            raise ValueError(f"Редактирование запрещено: статус {per.status.value}")

        # Нельзя менять ФИО/email/phone
        incoming_full_name = " ".join(
            [payload["user"]["fam"], payload["user"]["name"]] + (
                [payload["user"]["otc"]] if payload["user"].get("otc") else []
            )
        )
        incoming_email = _norm_email(payload["user"]["email"])
        incoming_phone = payload["user"]["phone"]

        if _norm_email(per.user.email) != incoming_email:
            raise ValueError("Нельзя изменять email пользователя")
        if per.user.phone != incoming_phone:
            raise ValueError("Нельзя изменять телефон пользователя")
        if per.user.full_name != incoming_full_name:
            raise ValueError("Нельзя изменять ФИО пользователя")

        # Обновляем coords
        per.coords.latitude = float(payload["coords"]["latitude"])
        per.coords.longitude = float(payload["coords"]["longitude"])
        per.coords.height = int(payload["coords"]["height"])

        # Обновляем levels
        lvl = payload.get("level", {})
        per.levels.winter = lvl.get("winter", "") or ""
        per.levels.summer = lvl.get("summer", "") or ""
        per.levels.autumn = lvl.get("autumn", "") or ""
        per.levels.spring = lvl.get("spring", "") or ""

        # Основные поля
        per.beauty_title = payload["beauty_title"]
        per.title = payload["title"]
        per.other_titles = payload.get("other_titles", "") or ""
        per.connect = payload.get("connect", "") or ""

        # Дата
        try:
            try:
                per.add_time = datetime.fromisoformat(payload["add_time"])
            except Exception:
                per.add_time = datetime.strptime(payload["add_time"], "%Y-%m-%d %H:%M:%S")
        except Exception:
            raise ValueError("Некорректное поле add_time, ожидается 'YYYY-MM-DD HH:MM:SS'")

        # Полная замена изображений БЕЗ оставления «мертвых» ORM-объектов
        new_images = payload.get("images", [])
        if not new_images:
            raise ValueError("Отсутствуют изображения (images)")

        # 1) удаляем пакетно, минуя коллекцию relationship (иначе висячие ссылки)
        self.db.query(models.Image).filter(models.Image.pereval_id == per.id).delete(synchronize_session=False)
        self.db.flush()  # очистили БД от старых записей

        # 2) создаём новые
        self._create_images(per.id, new_images)

        # Финальный коммит
        self.db.add(per)
        self.db.commit()

    # ====== Утилита: ORM -> dict для ответа ======
    def to_dict(self, per: models.Pereval) -> Dict[str, Any]:
        def b64(data: bytes) -> str:
            return base64.b64encode(data).decode("ascii")
        return {
            "id": int(per.id),
            "status": per.status.value,
            "beauty_title": per.beauty_title,
            "title": per.title,
            "other_titles": per.other_titles,
            "connect": per.connect,
            "add_time": per.add_time.isoformat(sep=" "),
            "user": {
                "email": per.user.email,
                "full_name": per.user.full_name,
                "phone": per.user.phone
            },
            "coords": {
                "latitude": float(per.coords.latitude),
                "longitude": float(per.coords.longitude),
                "height": int(per.coords.height)
            },
            "level": {
                "winter": per.levels.winter,
                "summer": per.levels.summer,
                "autumn": per.levels.autumn,
                "spring": per.levels.spring
            },
            "images": [{"title": im.title, "data": b64(im.data)} for im in per.images]
        }
