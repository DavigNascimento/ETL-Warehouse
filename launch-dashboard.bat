@echo off
setlocal

echo Data Warehouse Dashboard Launcher
echo ====================================
echo.

set "PYTHON_CMD="

where python >nul 2>nul
if %ERRORLEVEL%==0 (
    set "PYTHON_CMD=python"
) else (
    where py >nul 2>nul
    if %ERRORLEVEL%==0 (
        set "PYTHON_CMD=py -3"
    )
)

if "%PYTHON_CMD%"=="" (
    echo [ERROR] Python not found. Please install Python 3.8+
    exit /b 1
)

if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call ".venv\Scripts\activate.bat"
)

echo Checking dependencies...
%PYTHON_CMD% -c "import streamlit; import plotly; import pandas; import mysql.connector" 1>nul 2>nul
if not %ERRORLEVEL%==0 (
    echo Installing missing dependencies...
    %PYTHON_CMD% -m pip install -q -r frontend\requirements.txt
    if not %ERRORLEVEL%==0 (
        echo [ERROR] Failed to install dependencies.
        exit /b 1
    )
)

echo Validating database connection...
%PYTHON_CMD% -c "import sys; sys.path.insert(0, 'frontend'); from data.repository import QueryRepository; repo=QueryRepository(); conn=repo._get_connection(); ok=bool(conn); print('Database connection OK' if ok else 'Database connection failed'); repo.close_connection() if conn else None; sys.exit(0 if ok else 1)"
if not %ERRORLEVEL%==0 (
    echo [WARN] Database connection failed. Ensure Docker container is running:
    echo   docker compose up -d
    exit /b 1
)

echo.
echo All checks passed.
echo.
echo Launching Streamlit dashboard...
echo   Open your browser to: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

%PYTHON_CMD% -m streamlit run frontend\main.py

endlocal