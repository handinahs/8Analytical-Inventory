@echo off
title 8Analytical Inventory
cd /d "%~dp0"
echo Iniciando 8Analytical Inventory...
echo.
python -m streamlit run app.py
pause
