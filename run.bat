@echo off
echo ==========================================
echo   个股排雷扫描仪 - 启动中
echo ==========================================
cd /d "%~dp0"
python -m pip install -r requirements.txt
python app.py
pause
