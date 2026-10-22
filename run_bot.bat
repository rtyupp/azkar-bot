@echo off
chcp 65001 > nul
title بوت أذكار الصباح والمساء
echo جاري تشغيل بوت أذكار الصباح والمساء...
python bot.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo حدث خطأ أو توقف البوت.
    pause
)
