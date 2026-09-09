@echo off
rem ============================================================
rem  GameReview AI Platform - One-Click Launcher
rem  Double-click (or use desktop shortcut) to start & open.
rem  To STOP the server: close the minimized "GameReviewAI-Server" window.
rem ============================================================
cd /d "C:\Users\ABC\Documents\trae_projects\1"
set SQLALCHEMY_SILENCE_UBER_WARNING=1

rem --- Already running? Just open the site. ---
netstat -ano | findstr LISTENING | findstr ":8000" >nul 2>&1
if %errorlevel%==0 (
  start "" "http://127.0.0.1:8000/static/index.html"
  exit /b 0
)

echo Starting GameReview AI platform, please wait...

rem --- Start server in a minimized window (stays alive) ---
start "GameReviewAI-Server" /min cmd /c "python -m uvicorn main:app --host 127.0.0.1 --port 8000"

rem --- Wait until health check passes (max 60s) ---
set /a tries=0
:waitloop
timeout /t 1 /nobreak >nul
curl.exe -s -o nul http://127.0.0.1:8000/api/health
if %errorlevel%==0 goto ready
set /a tries+=1
if %tries% lss 60 goto waitloop
echo.
echo Startup timed out after 60 seconds.
echo Please check: python is in PATH, port 8000 is free.
pause
exit /b 1

:ready
start "" "http://127.0.0.1:8000/static/index.html"
exit /b 0
