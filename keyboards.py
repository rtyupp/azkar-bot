# -*- coding: utf-8 -*-
"""
لوحات الأزرار (ReplyKeyboardMarkup) للبوت — تحكم كامل ومريح من أسفل الشاشة
"""
from telegram import ReplyKeyboardMarkup, KeyboardButton


def main_keyboard() -> ReplyKeyboardMarkup:
    """القائمة الرئيسية"""
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("🌅 أذكار الصباح"), KeyboardButton("🌙 أذكار المساء")],
            [KeyboardButton("📿 السبحة الإلكترونية"), KeyboardButton("🕌 أذكار بعد الصلاة")],
            [KeyboardButton("😴 أذكار النوم"), KeyboardButton("📊 إحصائياتي")],
            [KeyboardButton("🔔 التنبيهات اليومية"), KeyboardButton("❓ المساعدة")]
        ],
        resize_keyboard=True
    )


def azkar_reading_keyboard(repeat_left: int) -> ReplyKeyboardMarkup:
    """لوحة التحكم أثناء قراءة الورد مع عداد التكرار"""
    count_label = f"✅ تكرار ({repeat_left})" if repeat_left > 1 else "✅ قرأت الذكر (تم)"
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(count_label)],
            [KeyboardButton("⏭️ الذكر التالي"), KeyboardButton("⏮️ الذكر السابق")],
            [KeyboardButton("🔄 إعادة الورد"), KeyboardButton("🏠 القائمة الرئيسية")]
        ],
        resize_keyboard=True
    )


def tasbeeh_keyboard(current_count: int, target: int) -> ReplyKeyboardMarkup:
    """لوحة السبحة الإلكترونية التفاعلية"""
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(f"🟢 سبّح ({current_count}/{target})")],
            [KeyboardButton("🔀 تغيير الذكر"), KeyboardButton("🔄 تصفير العداد")],
            [KeyboardButton("🏠 القائمة الرئيسية")]
        ],
        resize_keyboard=True
    )


def alerts_keyboard(enabled: bool) -> ReplyKeyboardMarkup:
    """لوحة إعدادات التنبيهات"""
    status_btn = "🔕 إيقاف التنبيهات اليومية" if enabled else "🔔 تفعيل التنبيهات اليومية"
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(status_btn)],
            [KeyboardButton("🏠 القائمة الرئيسية")]
        ],
        resize_keyboard=True
    )
