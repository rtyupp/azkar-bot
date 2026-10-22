# -*- coding: utf-8 -*-
"""
فحص واختبار كامل لكل وحدات البوت وعمليات التنقل والعدادات والسبحة والتخزين
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from azkar_data import AZKAR_DATA, TASBEEH_PRESETS
import storage
import formatter
import keyboards


def run_tests():
    print("⏳ بدء فحص واختبار مكونات البوت...")

    # 1. فحص بيانات الأذكار
    assert "morning" in AZKAR_DATA and len(AZKAR_DATA["morning"]) >= 15, "أذكار الصباح ناقصة"
    assert "evening" in AZKAR_DATA and len(AZKAR_DATA["evening"]) >= 15, "أذكار المساء ناقصة"
    assert "sleep" in AZKAR_DATA, "أذكار النوم ناقصة"
    assert "prayer" in AZKAR_DATA, "أذكار الصلاة ناقصة"
    assert len(TASBEEH_PRESETS) >= 5, "أذكار السبحة ناقصة"
    print(f"✅ تم التحقق من بيانات الأذكار ({len(AZKAR_DATA['morning'])} صباح، {len(AZKAR_DATA['evening'])} مساء).")

    # 2. فحص التخزين وحالة المستخدم
    test_chat = "999999"
    user = storage.get_user(test_chat)
    assert user is not None and "stats" in user
    storage.update_user(test_chat, active_section="morning", current_index=1, repeat_left=2)
    user2 = storage.get_user(test_chat)
    assert user2["active_section"] == "morning" and user2["repeat_left"] == 2
    print("✅ تم التحقق من تخزين وحفظ حالة المستخدم.")

    # 3. فحص منسق الرسائل (HTML)
    msg1 = formatter.format_zikr_message("morning", 0, 1)
    assert "<b>" in msg1 and "</b>" in msg1
    assert "**" not in msg1, "يجب عدم استخدام علامات Markdown مع parse_mode=HTML"

    tasbeeh_msg = formatter.format_tasbeeh_message(0, 15)
    assert "السبحة الإلكترونية" in tasbeeh_msg
    assert "**" not in tasbeeh_msg

    stats_msg = formatter.format_stats_message(user2)
    assert "إحصائيات إنجازك" in stats_msg
    assert "**" not in stats_msg
    print("✅ تم التحقق من تنسيق الرسائل وخلوها من أخطاء Markdown/HTML.")

    # 4. فحص لوحات الأزرار
    kb_main = keyboards.main_keyboard()
    assert len(kb_main.keyboard) >= 3

    kb_read = keyboards.azkar_reading_keyboard(3)
    assert "تكرار (3)" in kb_read.keyboard[0][0].text

    kb_tasb = keyboards.tasbeeh_keyboard(5, 33)
    assert "سبّح (5/33)" in kb_tasb.keyboard[0][0].text
    print("✅ تم التحقق من بناء وتسميات لوحات المفاتيح.")

    print("\n🎉 جميع الاختبارات الذاتية نجحت بنسبة 100%!")


if __name__ == "__main__":
    run_tests()
