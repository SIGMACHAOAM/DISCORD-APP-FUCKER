@echo off
cd /d "%~dp0" 

python --version
if %errorlevel% neq 0 (
    echo Python is not installed or not in the PATH.
    pause
    exit /b
)


python Appspam.py


pause
