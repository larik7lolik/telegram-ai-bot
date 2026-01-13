@echo off
chcp 65001 > nul
set "PYTHON_EXE=%~dp0venv\Scripts\python.exe"
set "MAIN_PY=%~dp0main.py"
"%PYTHON_EXE%" "%MAIN_PY%" %*
pause
