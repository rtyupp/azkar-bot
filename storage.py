# -*- coding: utf-8 -*-
"""
إدارة حالة المستخدمين (التقدم في الأذكار، السبحة، تفضيلات التنبيهات اليومية)
"""
import json
import os
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(HERE, "users_state.json")
_lock = threading.Lock()


def _load_raw() -> dict:
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_raw(data: dict):
    tmp = DB_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DB_FILE)


def get_user(chat_id: int | str) -> dict:
    chat_id = str(chat_id)
    with _lock:
        db = _load_raw()
        if chat_id not in db:
            db[chat_id] = {
                "active_section": None,
                "current_index": 0,
                "repeat_left": 0,
                "tasbeeh_index": 0,
                "tasbeeh_count": 0,
                "alerts_enabled": True,
                "stats": {
                    "completed_morning": 0,
                    "completed_evening": 0,
                    "total_tasbeeh": 0,
                }
            }
            _save_raw(db)
        return db[chat_id]


def update_user(chat_id: int | str, **kwargs):
    chat_id = str(chat_id)
    with _lock:
        db = _load_raw()
        user = db.setdefault(chat_id, {
            "active_section": None,
            "current_index": 0,
            "repeat_left": 0,
            "tasbeeh_index": 0,
            "tasbeeh_count": 0,
            "alerts_enabled": True,
            "stats": {
                "completed_morning": 0,
                "completed_evening": 0,
                "total_tasbeeh": 0,
            }
        })
        for k, v in kwargs.items():
            if k == "stats" and isinstance(v, dict):
                user.setdefault("stats", {}).update(v)
            else:
                user[k] = v
        _save_raw(db)


def get_all_subscribers() -> list[str]:
    with _lock:
        db = _load_raw()
        return [cid for cid, u in db.items() if u.get("alerts_enabled", True)]
