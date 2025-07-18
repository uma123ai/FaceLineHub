@echo off
chcp 65001 > nul
title 刪除 Ngrok Authtoken 設定

echo =======================================
echo 是否要刪除 Ngrok 的 Authtoken 設定？ (Y/N)
echo =======================================
set /p confirm=請輸入 Y 或 N：

if /i "%confirm%"=="Y" (
    ngrok config reset
    echo 已刪除 Ngrok Authtoken 設定！
) else (
    echo 未刪除，操作取消。
)

pause
