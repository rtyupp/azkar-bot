@echo off
chcp 65001 > nul
title بوت أذكار الصباح والمساء
echo جاري تشغيل بوت أذكار الصباح والمساء...
py -3.12 bot.py
if %ERRORLEVEL% NEQ 0 (
    python bot.py
)
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo حدث خطأ أو توقف البوت.
    pause
)
