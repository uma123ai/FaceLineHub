@echo off
chcp 65001 > nul
title  設定 Ngrok Authtoken

echo =======================================
echo  請輸入 Ngrok Authtoken（註冊後取得）
echo  若已設定過，可直接關閉此視窗
echo =======================================
set /p NGROK_TOKEN=請輸入 Ngrok Authtoken：

if not "%NGROK_TOKEN%"=="" (
    ngrok config add-authtoken %NGROK_TOKEN%
    echo  已設定 Ngrok Authtoken！
) else (
    echo  未輸入，未進行任何設定。
)

pause
