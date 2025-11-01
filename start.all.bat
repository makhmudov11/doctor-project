@echo off
title 🚀 Django + Celery + Redis launcher

echo ==========================================
echo 🚀 Django + Celery + Redis ishga tushmoqda...
echo ==========================================
echo.

:: Virtual environmentni aktivlashtirish
call .venv\Scripts\activate

:: Redis serverni ishga tushirish
echo 🧠 Redis server ishga tushmoqda...
start "Redis Server" cmd /k "redis-server"
timeout /t 3 >nul

:: 5 soniya kutish
timeout /t 5 /nobreak >nul


:: Celery worker’ni ishga tushirish
echo ⚙️ Celery worker ishga tushmoqda...
start "Celery Worker" cmd /k "celery -A config worker -l info"
timeout /t 2 >nul

:: 5 soniya kutish
timeout /t 5 /nobreak >nul

:: Django runserver’ni ishga tushirish
echo 🌍 Django server ishga tushmoqda...
start "Django Server" cmd /k "python manage.py runserver"

echo.
echo ✅ Hammasi ishga tushdi!
echo (Redis, Celery va Django alohida oynalarda ishlayapti)
pause
