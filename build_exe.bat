@echo off
REM  מסך חכם - Smart Screen  v1.3.0  |  PyQt6 Build
echo.
echo  [מסך חכם v1.3] Building EXE with PyQt6...
echo.
echo [1/3] Installing dependencies...
pip install PyQt6 PyQt6-Qt6 PyQt6-sip pillow pystray pyinstaller --quiet
if errorlevel 1 ( echo ERROR: pip failed. & pause & exit /b 1 )
echo [2/3] Building EXE...
pyinstaller --onefile --windowed --name "MasachChacham" ^
    --hidden-import PyQt6 --hidden-import PyQt6.QtWidgets ^
    --hidden-import PyQt6.QtCore --hidden-import PyQt6.QtGui ^
    --hidden-import PyQt6.QtSvg --hidden-import pystray ^
    --hidden-import PIL --hidden-import PIL.Image ^
    --hidden-import PIL.ImageDraw --hidden-import winreg ^
    masach_chacham.py
if errorlevel 1 ( echo ERROR: build failed. & pause & exit /b 1 )
echo [3/3] Done!  →  dist\MasachChacham.exe
pause
