@echo off
chcp 65001 > nul
cd /d "%~dp0linebot"
python linesdk版.py
pause