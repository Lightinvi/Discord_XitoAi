@echo off
set /p packet="python packet name:"
set /p version="python packet version(Default:None):"
cd "C:\Program Files\Python312"
if not defined version (
    python -m pip install %packet%
) else (
    python -m pip install %packet%==%version%
)
pause