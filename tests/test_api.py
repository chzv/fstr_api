# tests/test_api.py
import copy
import requests

BASE = "http://localhost:8000"

def make_payload():
    return {
        "beauty_title": "пер.",
        "title": "Пхия",
        "other_titles": "Триев",
        "connect": "",
        "add_time": "2021-09-22 13:18:13",
        "user": {
            "email": "qwerty@mail.ru",
            "fam": "Пупкин",
            "name": "Василий",
            "otc": "Иванович",
            "phone": "+7 555 55 55"
        },
        "coords": {"latitude": "45.3842", "longitude": "7.1525", "height": "1200"},
        "level": {"winter": "", "summer": "1А", "autumn": "1А", "spring": ""},
        "images": [
            {
                "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMB/ek9nYQAAAAASUVORK5CYII=",
                "title": "Седловина",
            },
            {
                "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMB/ek9nYQAAAAASUVORK5CYII=",
                "title": "Подъём",
            },
        ],
    }

def test_submit_get_list_and_patch():
    # 1) POST
    payload = make_payload()
    r = requests.post(f"{BASE}/submitData", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == 200
    pid = data["id"]
    assert isinstance(pid, int)

    # 2) GET by id
    r = requests.get(f"{BASE}/submitData/{pid}")
    assert r.status_code == 200
    got = r.json()
    assert got["id"] == pid
    assert got["status"] == "new"

    # 3) LIST by email
    r = requests.get(f"{BASE}/submitData/", params={"user__email": payload["user"]["email"]})
    assert r.status_code == 200
    items = r.json()
    assert any(x["id"] == pid for x in items)

    # 4) PATCH (разрешённые изменения) — ВАЖНО: deepcopy!
    patch = copy.deepcopy(payload)
    patch["title"] = "Пхия (апдейт)"
    patch["coords"] = {"latitude": "45.38", "longitude": "7.15", "height": "1300"}
    patch["images"] = [{
        "data": payload["images"][0]["data"],
        "title": "Новая"
    }]

    r = requests.patch(f"{BASE}/submitData/{pid}", json=patch)
    assert r.status_code == 200
    out = r.json()
    assert out["state"] == 1, out

    # 5) GET и проверим обновления
    r = requests.get(f"{BASE}/submitData/{pid}")
    assert r.status_code == 200
    got2 = r.json()
    assert got2["title"] == "Пхия (апдейт)"
    assert got2["coords"]["height"] == 1300
    assert len(got2["images"]) == 1
    assert got2["images"][0]["title"] == "Новая"

def test_patch_forbidden_on_user_fields_change():
    # Создадим свежую запись (status=new)
    payload = make_payload()
    payload["title"] = "Для проверки запрета"
    r = requests.post(f"{BASE}/submitData", json=payload)
    assert r.status_code == 200
    pid = r.json()["id"]

    # Пытаемся изменить email — это запрещено по ТЗ
    bad_patch = copy.deepcopy(payload)
    bad_patch["user"]["email"] = "other@mail.ru"  # запрет

    r = requests.patch(f"{BASE}/submitData/{pid}", json=bad_patch)
    # PATCH у тебя всегда возвращает 200 с {state:0|1}, поэтому проверяем содержимое
    assert r.status_code == 200
    out = r.json()
    assert out["state"] == 0
    assert "email" in (out.get("message") or "").lower()
