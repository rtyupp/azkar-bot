# -*- coding: utf-8 -*-
"""
الملف الرئيسي لبوت أذكار الصباح والمساء
يعمل باستخدام python-telegram-bot v22 بالكامل بأزرار ReplyKeyboardMarkup وتنبيهات مجدولة
"""
import os
import logging
from datetime import time
import pytz

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from azkar_data import AZKAR_DATA, TASBEEH_PRESETS
from storage import get_user, update_user, get_all_subscribers
from keyboards import (
    main_keyboard,
    azkar_reading_keyboard,
    tasbeeh_keyboard,
    alerts_keyboard,
)
from formatter import (
    format_zikr_message,
    format_tasbeeh_message,
    format_stats_message,
    SECTION_TITLES,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("AzkarBot")

HERE = os.path.dirname(os.path.abspath(__file__))


def load_token() -> str:
    tok = os.environ.get("TELEGRAM_TOKEN", "").strip()
    if tok:
        return tok
    # تجربة قراءة من ملف مجاور
    paths = [
        os.path.join(HERE, "token.txt"),
        os.path.join(HERE, ".env"),
        "C:/tmp/token.txt"
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                for line in open(p, encoding="utf-8"):
                    line = line.strip()
                    if line.startswith("TELEGRAM_TOKEN="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
                    if ":" in line and len(line) > 30 and not line.startswith("#"):
                        return line
            except Exception:
                pass
    return ""


# ----------------------------- معالجات الأوامر والرسائل -----------------------------

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = get_user(chat_id)
    update_user(chat_id, active_section=None)

    name = update.effective_user.first_name or "المبارك"
    welcome_text = (
        f"أهلاً وسهلاً بك يا <b>{name}</b> في <b>بوت أذكار الصباح والمساء</b> 🌸\n\n"
        f"حصنك اليومي من الأذكار النبوية الصحيحة، مع عدّاد تفاعلي لكل ذكر وسبحة إلكترونية وتنبيهات يومية.\n\n"
        f"اختر من القائمة بالأسفل للبدء 👇"
    )
    await update.message.reply_text(
        welcome_text,
        reply_markup=main_keyboard(),
        parse_mode=ParseMode.HTML
    )


async def send_section_item(update: Update, chat_id: int, section: str, index: int, repeat_left: int):
    items = AZKAR_DATA.get(section, [])
    if index >= len(items):
        # أنهى الورد
        title = SECTION_TITLES.get(section, "الورد")
        user = get_user(chat_id)
        stats = user.get("stats", {})
        if section == "morning":
            stats["completed_morning"] = stats.get("completed_morning", 0) + 1
        elif section == "evening":
            stats["completed_evening"] = stats.get("completed_evening", 0) + 1

        update_user(chat_id, active_section=None, current_index=0, repeat_left=0, stats=stats)
        done_text = (
            f"🎉 <b>هنيئاً لك! أتممت {title} بحمد الله وفضله.</b>\n\n"
            f"تقبل الله طاعتك وحفظك بحفظه المتين 🤲\n"
            f"اختر ما تريد من القائمة الرئيسية:"
        )
        await update.message.reply_text(
            done_text,
            reply_markup=main_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return

    msg = format_zikr_message(section, index, repeat_left)
    await update.message.reply_text(
        msg,
        reply_markup=azkar_reading_keyboard(repeat_left),
        parse_mode=ParseMode.HTML
    )


async def message_dispatcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    chat_id = update.effective_chat.id
    user = get_user(chat_id)

    # 1. القوائم والتحويلات الرئيسية
    if text == "🌅 أذكار الصباح":
        items = AZKAR_DATA["morning"]
        update_user(chat_id, active_section="morning", current_index=0, repeat_left=items[0]["count"])
        await send_section_item(update, chat_id, "morning", 0, items[0]["count"])
        return

    elif text == "🌙 أذكار المساء":
        items = AZKAR_DATA["evening"]
        update_user(chat_id, active_section="evening", current_index=0, repeat_left=items[0]["count"])
        await send_section_item(update, chat_id, "evening", 0, items[0]["count"])
        return

    elif text == "😴 أذكار النوم":
        items = AZKAR_DATA["sleep"]
        update_user(chat_id, active_section="sleep", current_index=0, repeat_left=items[0]["count"])
        await send_section_item(update, chat_id, "sleep", 0, items[0]["count"])
        return

    elif text == "🕌 أذكار بعد الصلاة":
        items = AZKAR_DATA["prayer"]
        update_user(chat_id, active_section="prayer", current_index=0, repeat_left=items[0]["count"])
        await send_section_item(update, chat_id, "prayer", 0, items[0]["count"])
        return

    elif text == "📿 السبحة الإلكترونية":
        update_user(chat_id, active_section="tasbeeh")
        idx = user.get("tasbeeh_index", 0)
        cnt = user.get("tasbeeh_count", 0)
        preset = TASBEEH_PRESETS[idx % len(TASBEEH_PRESETS)]
        msg = format_tasbeeh_message(idx, cnt)
        await update.message.reply_text(
            msg,
            reply_markup=tasbeeh_keyboard(cnt % preset["target"], preset["target"]),
            parse_mode=ParseMode.HTML
        )
        return

    elif text == "📊 إحصائياتي":
        msg = format_stats_message(user)
        await update.message.reply_text(msg, reply_markup=main_keyboard(), parse_mode=ParseMode.HTML)
        return

    elif text == "🔔 التنبيهات اليومية":
        enabled = user.get("alerts_enabled", True)
        status_str = "مفعّلة ✅" if enabled else "معطّلة ❌"
        msg = (
            f"🔔 <b>إعدادات التنبيهات اليومية التلقائية</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"الحالة الحالية: <b>{status_str}</b>\n\n"
            f"المواعيد المجدولة (بتوقيت مكة المكرمة):\n"
            f"🌅 تذكير أذكار الصباح: <b>06:00 صباحاً</b>\n"
            f"🌙 تذكير أذكار المساء: <b>05:00 مساءً</b>\n\n"
            f"يمكنك التبديل عبر الزر بالأسفل:"
        )
        await update.message.reply_text(msg, reply_markup=alerts_keyboard(enabled), parse_mode=ParseMode.HTML)
        return

    elif text in ["🔕 إيقاف التنبيهات اليومية", "🔔 تفعيل التنبيهات اليومية"]:
        new_status = (text == "🔔 تفعيل التنبيهات اليومية")
        update_user(chat_id, alerts_enabled=new_status)
        action_word = "تفعيل" if new_status else "إيقاف"
        await update.message.reply_text(
            f"✅ تم {action_word} التنبيهات اليومية بنجاح.",
            reply_markup=alerts_keyboard(new_status),
            parse_mode=ParseMode.HTML
        )
        return

    elif text in ["🏠 القائمة الرئيسية", "/start", "/menu"]:
        update_user(chat_id, active_section=None)
        await update.message.reply_text(
            "🏠 عدت إلى القائمة الرئيسية. اختر ما تريد:",
            reply_markup=main_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return

    elif text in ["❓ المساعدة", "/help"]:
        help_text = (
            "📖 <b>دليل استخدام البوت:</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "1. <b>أذكار الصباح والمساء والنوم:</b> تعرض لك الذكر مع عداد تكراره، اضغط زر (تكرار / قرأت) لإنقاص العداد والانتقال تلقائياً.\n"
            "2. <b>السبحة الإلكترونية:</b> تمكنك من التسبيح بالأذكار المأثورة مع حفظ مجموع تسبيحاتك.\n"
            "3. <b>التنبيهات التلقائية:</b> يرسل البوت تذكيراً يومياً بورد الصباح والمساء لتظل في معية الله.\n"
            "4. <b>إحصائياتي:</b> لمعرفة عدد الختمات والتسبيحات المنجزة.\n\n"
            "تقبل الله منا ومنكم صالح الأعمال."
        )
        await update.message.reply_text(help_text, reply_markup=main_keyboard(), parse_mode=ParseMode.HTML)
        return

    # 2. أثناء قراءة الأذكار (الصباح، المساء، النوم، الصلاة)
    section = user.get("active_section")
    if section in ["morning", "evening", "sleep", "prayer"]:
        items = AZKAR_DATA[section]
        curr_idx = user.get("current_index", 0)
        curr_left = user.get("repeat_left", 1)

        # زر النقر على الذكر (تكرار أو تم)
        if text.startswith("✅"):
            if curr_left > 1:
                # تكرار إضافي
                new_left = curr_left - 1
                update_user(chat_id, repeat_left=new_left)
                await send_section_item(update, chat_id, section, curr_idx, new_left)
            else:
                # الذكر اكتمل، الانتقال للتالي
                next_idx = curr_idx + 1
                if next_idx < len(items):
                    next_count = items[next_idx]["count"]
                    update_user(chat_id, current_index=next_idx, repeat_left=next_count)
                    await send_section_item(update, chat_id, section, next_idx, next_count)
                else:
                    await send_section_item(update, chat_id, section, next_idx, 0)
            return

        elif text == "⏭️ الذكر التالي":
            next_idx = curr_idx + 1
            if next_idx < len(items):
                next_count = items[next_idx]["count"]
                update_user(chat_id, current_index=next_idx, repeat_left=next_count)
                await send_section_item(update, chat_id, section, next_idx, next_count)
            else:
                await send_section_item(update, chat_id, section, len(items), 0)
            return

        elif text == "⏮️ الذكر السابق":
            prev_idx = max(0, curr_idx - 1)
            prev_count = items[prev_idx]["count"]
            update_user(chat_id, current_index=prev_idx, repeat_left=prev_count)
            await send_section_item(update, chat_id, section, prev_idx, prev_count)
            return

        elif text == "🔄 إعادة الورد":
            first_count = items[0]["count"]
            update_user(chat_id, current_index=0, repeat_left=first_count)
            await send_section_item(update, chat_id, section, 0, first_count)
            return

    # 3. أثناء السبحة الإلكترونية
    if section == "tasbeeh":
        idx = user.get("tasbeeh_index", 0)
        cnt = user.get("tasbeeh_count", 0)
        stats = user.get("stats", {})
        total_t = stats.get("total_tasbeeh", 0)
        preset = TASBEEH_PRESETS[idx % len(TASBEEH_PRESETS)]

        if text.startswith("🟢 سبّح"):
            cnt += 1
            total_t += 1
            stats["total_tasbeeh"] = total_t
            update_user(chat_id, tasbeeh_count=cnt, stats=stats)

            # فحص إذا أكمل دورة
            if cnt % preset["target"] == 0:
                congrats = (
                    f"🎉 <b>ما شاء الله! أتممت جولة من:</b>\n"
                    f"« <b>{preset['name']}</b> » ({preset['target']} مرة)\n\n"
                    f"تقبل الله ذكرك! تابع التسبيح أو اختر ذكراً آخر."
                )
                await update.message.reply_text(
                    congrats,
                    reply_markup=tasbeeh_keyboard(0, preset["target"]),
                    parse_mode=ParseMode.HTML
                )
            else:
                msg = format_tasbeeh_message(idx, cnt)
                await update.message.reply_text(
                    msg,
                    reply_markup=tasbeeh_keyboard(cnt % preset["target"], preset["target"]),
                    parse_mode=ParseMode.HTML
                )
            return

        elif text == "🔀 تغيير الذكر":
            new_idx = (idx + 1) % len(TASBEEH_PRESETS)
            new_preset = TASBEEH_PRESETS[new_idx]
            update_user(chat_id, tasbeeh_index=new_idx, tasbeeh_count=0)
            msg = format_tasbeeh_message(new_idx, 0)
            await update.message.reply_text(
                msg,
                reply_markup=tasbeeh_keyboard(0, new_preset["target"]),
                parse_mode=ParseMode.HTML
            )
            return

        elif text == "🔄 تصفير العداد":
            update_user(chat_id, tasbeeh_count=0)
            msg = format_tasbeeh_message(idx, 0)
            await update.message.reply_text(
                "تم تصفير العداد الحالي.\n\n" + msg,
                reply_markup=tasbeeh_keyboard(0, preset["target"]),
                parse_mode=ParseMode.HTML
            )
            return

    # رد افتراضي إذا النص غير معروف
    await update.message.reply_text(
        "من فضلك اختر من الأزرار الظاهرة في الأسفل 👇",
        reply_markup=main_keyboard()
    )


# ----------------------------- التنبيهات المجدولة -----------------------------

async def morning_reminder(context: ContextTypes.DEFAULT_TYPE):
    subscribers = get_all_subscribers()
    msg = (
        "🌅 <b>تذكير بأذكار الصباح</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "أشرقت شمس يوم جديد، فابدأ يومك بذكر الله وحفظه وحصنه المنيع 🌸\n\n"
        "«أَصْبَحْنَا وَأَصْبَحَ المُلْكُ لِلَّهِ، وَالحَمْدُ لِلَّهِ...»\n\n"
        "اضغط على زر <b>🌅 أذكار الصباح</b> للبدء بالورد اليومي."
    )
    for cid in subscribers:
        try:
            await context.bot.send_message(
                chat_id=cid,
                text=msg,
                parse_mode=ParseMode.HTML,
                reply_markup=main_keyboard()
            )
        except Exception as e:
            logger.warning(f"Could not send morning alert to {cid}: {e}")


async def evening_reminder(context: ContextTypes.DEFAULT_TYPE):
    subscribers = get_all_subscribers()
    msg = (
        "🌙 <b>تذكير بأذكار المساء</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "أقبل المساء، فحَصّن نفسك وأهلك بأذكار المساء المأثورة 🕯️\n\n"
        "«أَمْسَيْنَا وَأَمْسَى المُلْكُ لِلَّهِ، وَالحَمْدُ لِلَّهِ...»\n\n"
        "اضغط على زر <b>🌙 أذكار المساء</b> لقراءة وردك وحفظ ليلتك."
    )
    for cid in subscribers:
        try:
            await context.bot.send_message(
                chat_id=cid,
                text=msg,
                parse_mode=ParseMode.HTML,
                reply_markup=main_keyboard()
            )
        except Exception as e:
            logger.warning(f"Could not send evening alert to {cid}: {e}")


def main():
    token = load_token()
    if not token:
        print("❌ لم يتم العثور على توكن التيليجرام! يرجى وضع التوكن في TELEGRAM_TOKEN أو في ملف token.txt.")
        return

    # بناء التطبيق
    app = Application.builder().token(token).build()

    # معالجات الأوامر والرسائل
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", start_handler))
    app.add_handler(CommandHandler("menu", start_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_dispatcher))

    # جدولة التنبيهات (بتوقيت مكة المكرمة UTC+3)
    # 06:00 صباحاً بتوقيت مكة = 03:00 UTC
    # 17:00 مساءً بتوقيت مكة = 14:00 UTC
    try:
        tz = pytz.timezone("Asia/Riyadh")
        job_queue = app.job_queue
        if job_queue:
            job_queue.run_daily(morning_reminder, time=time(hour=6, minute=0, tzinfo=tz))
            job_queue.run_daily(evening_reminder, time=time(hour=17, minute=0, tzinfo=tz))
            logger.info("Daily reminder jobs scheduled successfully (06:00 & 17:00 Riyadh time).")
    except Exception as e:
        logger.warning(f"Failed to schedule reminder jobs: {e}")

    logger.info("Bot starting in polling mode...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
