@echo off
REM Find Python and run streamlit. Use from AI Task App folder: run.bat
where python >nul 2>&1 && python -m streamlit run app.py %* && exit /b
where py >nul 2>&1 && py -m streamlit run app.py %* && exit /b
echo Python not found. Install Python and add it to PATH.
exit /b 1
