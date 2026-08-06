@echo off
REM Cross-platform Python launcher for AI log hooks (Windows cmd.exe).
REM Tries py -3 -> python -> python3 in order, runs the given script with all args.
REM Exits 0 silently if no Python is found - hooks must never block the AI tool.

where py >nul 2>nul
if %ERRORLEVEL%==0 (
  py -3 -c "import sys" >nul 2>nul
  if not errorlevel 1 goto use_py
)

where python >nul 2>nul
if %ERRORLEVEL%==0 (
  python -c "import sys" >nul 2>nul
  if not errorlevel 1 goto use_python
)

where python3 >nul 2>nul
if %ERRORLEVEL%==0 (
  python3 -c "import sys" >nul 2>nul
  if not errorlevel 1 goto use_python3
)

exit /b 0

:use_py
py -3 %*
exit /b %ERRORLEVEL%

:use_python
python %*
exit /b %ERRORLEVEL%

:use_python3
python3 %*
exit /b %ERRORLEVEL%
