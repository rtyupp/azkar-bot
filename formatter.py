# -*- coding: utf-8 -*-
"""
منطق تنسيق الرسائل وعرض الورد
"""
from azkar_data import AZKAR_DATA, TASBEEH_PRESETS

SECTION_TITLES = {
    "morning": "🌅 أذكار الصباح",
    "evening": "🌙 أذكار المساء",
    "sleep": "😴 أذكار النوم",
    "prayer": "🕌 أذكار بعد الصلاة",
}


def format_zikr_message(section: str, index: int, repeat_left: int) -> str:
    items = AZKAR_DATA.get(section, [])
    if not items or index < 0 or index >= len(items):
        return "لا يوجد ذكر لعرضه."

    item = items[index]
    total_count = item["count"]
    total_items = len(items)
    progress_num = index + 1
    title = SECTION_TITLES.get(section, "📿 الورد")

    text = (
        f"<b>{title}</b>  (<b>{progress_num}</b> من <b>{total_items}</b>)\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"« {item['text']} »\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🔢 <b>التكرار المطلوب:</b> {total_count} مرة\n"
        f"⏳ <b>المتبقي لك:</b> {repeat_left} مرة\n"
    )
    if item.get("reward"):
        text += f"💡 <b>الفضل / المصدر:</b> <i>{item['reward']}</i>\n"

    return text


def format_tasbeeh_message(preset_index: int, current_count: int) -> str:
    preset = TASBEEH_PRESETS[preset_index % len(TASBEEH_PRESETS)]
    target = preset["target"]
    name = preset["name"]
    rounds = current_count // target
    curr_in_round = current_count % target

    text = (
        f"📿 <b>السبحة الإلكترونية</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>الذكر الحالي:</b>\n"
        f"« <b>{name}</b> »\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🎯 <b>الهدف للجولة:</b> {target}\n"
        f"🔢 <b>العدد الحالي:</b> {curr_in_round} / {target}\n"
        f"🏆 <b>الجولات المكتملة:</b> {rounds}\n\n"
        f"<i>اضغط على زر (🟢 سبّح) بالأسفل للعد.</i>"
    )
    return text


def format_stats_message(user_state: dict) -> str:
    stats = user_state.get("stats", {})
    m_done = stats.get("completed_morning", 0)
    e_done = stats.get("completed_evening", 0)
    t_count = stats.get("total_tasbeeh", 0)
    alerts = "مفعّلة 🔔" if user_state.get("alerts_enabled", True) else "معطّلة 🔕"

    text = (
        f"📊 <b>إحصائيات إنجازك في الأذكار</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"🌅 أذكار الصباح المكتملة: <b>{m_done}</b> مرة\n"
        f"🌙 أذكار المساء المكتملة: <b>{e_done}</b> مرة\n"
        f"📿 إجمالي التسبيحات المسجلة: <b>{t_count}</b> تسبيحة\n\n"
        f"⏰ حالة التنبيهات اليومية: <b>{alerts}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<i>«أَحَبُّ الأَعْمَالِ إِلَى اللَّهِ أَدْوَمُهَا وَإِنْ قَلَّ»</i>"
    )
    return text
