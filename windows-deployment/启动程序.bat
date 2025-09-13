@echo off
title PDF文档脱敏工具
echo.
echo ===============================================
echo           PDF文档脱敏工具 - Windows版
echo ===============================================
echo.
echo 正在启动程序，请稍候...
echo.

REM 检查可执行文件是否存在
if not exist "redactor-windows.exe" (
    echo 错误：未找到 redactor-windows.exe 文件
    echo 请确保文件在同一目录下
    echo.
    pause
    exit /b 1
)

REM 启动程序
echo 启动中...
start "" "redactor-windows.exe"

REM 等待一下再退出
timeout /t 3 /nobreak > nul

echo.
echo 程序已启动！
echo 如果程序未出现，请检查 Windows 安全设置
echo.
echo 按任意键退出...
pause > nul