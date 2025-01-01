@echo off

REM Specify the Python file to run
set PYTHON_FILE=ytpyrate.py

REM Ensure the script runs with pythonw to suppress the console window
REM Use "start" to completely detach the process
start "" pythonw "%PYTHON_FILE%"
