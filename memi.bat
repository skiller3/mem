@echo off
call %~dp0.venv-windows\Scripts\activate
python %~dp0memi.py %*
deactivate