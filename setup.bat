@echo off
echo Installing Image-to-Label dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.
echo Setup complete! Run run.bat to start the app.
pause
