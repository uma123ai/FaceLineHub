@echo off
chcp 65001 > nul
title ✅ 安裝環境

echo =======================================
echo 🔧 安裝 Python 套件...
echo =======================================
pip install flask requests openpyxl pyngrok cloudinary python-dateutil
pause
