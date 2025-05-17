@echo off
chcp 65001 > nul
title 智能书签导入工具

echo ====================================
echo        书签导航 - 自动导入工具
echo ====================================
echo.

REM 检查Python环境
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python环境！
    echo.
    echo 请安装Python 3.6或更高版本后再运行此工具。
    echo 下载地址: https://www.python.org/downloads/
    echo.
    echo 提示: 安装时请勾选"Add Python to PATH"选项。
    pause
    exit /b 1
)

echo [√] Python环境检测通过

REM 检查必要的Python库
echo 正在检查必要的库...
python -c "import bs4" > nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装必要的库: BeautifulSoup4
    python -m pip install beautifulsoup4
    if %errorlevel% neq 0 (
        echo [错误] 安装BeautifulSoup4失败，请手动运行:
        echo python -m pip install beautifulsoup4
        pause
        exit /b 1
    )
)

echo [√] 环境检查完成
echo.
echo 正在自动检测书签文件...

REM 查找顺序：
REM 1. bookmarks.html (Chrome/Edge标准导出名称)
REM 2. Bookmarks.html (Firefox标准导出名称)
REM 3. bookmarks_*.html (特定模式的书签文件)
REM 4. 任何包含"bookmark"的html文件
REM 5. 任何包含"书签"的html文件

set FOUND_BOOKMARK=0
set BOOKMARK_FILE=

if exist "bookmarks.html" (
    set BOOKMARK_FILE=bookmarks.html
    set FOUND_BOOKMARK=1
    echo 找到Chrome/Edge书签文件: %BOOKMARK_FILE%
) else if exist "Bookmarks.html" (
    set BOOKMARK_FILE=Bookmarks.html
    set FOUND_BOOKMARK=1
    echo 找到Firefox书签文件: %BOOKMARK_FILE%
) else if exist "bookmarks_*.html" (
    for %%f in (bookmarks_*.html) do (
        set BOOKMARK_FILE=%%f
        set FOUND_BOOKMARK=1
        echo 找到书签文件: %%f
        goto FOUND_FILE
    )
) else if exist "*bookmark*.html" (
    for %%f in (*bookmark*.html) do (
        set BOOKMARK_FILE=%%f
        set FOUND_BOOKMARK=1
        echo 找到书签文件: %%f
        goto FOUND_FILE
    )
) else if exist "*书签*.html" (
    for %%f in (*书签*.html) do (
        set BOOKMARK_FILE=%%f
        set FOUND_BOOKMARK=1
        echo 找到书签文件: %%f
        goto FOUND_FILE
    )
)

:FOUND_FILE
if %FOUND_BOOKMARK% equ 0 (
    echo [错误] 当前目录下未找到任何书签文件
    echo.
    echo 请按照以下步骤导出书签:
    echo 1. 打开Chrome/Edge浏览器
    echo 2. 点击右上角三点菜单 -^> 书签 -^> 书签管理器
    echo 3. 在书签管理器中点击三点菜单 -^> 导出书签
    echo 4. 将导出的书签文件 (bookmarks.html) 保存到当前目录
    echo.
    echo 或者将任何包含"bookmark"或"书签"的HTML文件放到当前目录
    pause
    exit /b 1
)

echo.
echo [√] 找到书签文件：%BOOKMARK_FILE%
echo 正在导入...
echo.

REM 运行Python脚本处理书签
python update_bookmarks.py "%BOOKMARK_FILE%"

if %errorlevel% neq 0 (
    echo.
    echo [错误] 导入过程失败，请查看上面的错误信息
    pause
    exit /b 1
)

echo.
echo [√] 书签导入成功！

REM 检查端口占用情况
set PORT=8088
netstat -ano | find ":%PORT% " > nul
if %errorlevel% equ 0 (
    set PORT=8089
    netstat -ano | find ":%PORT% " > nul
    if %errorlevel% equ 0 (
        set PORT=8090
    )
)

echo [√] 已选择可用端口: %PORT%
echo 正在启动预览服务器...
echo.
echo -----------------------------------
echo   🚀 导航网站已准备就绪!
echo   📂 正在浏览器中打开预览...
echo   💡 完成后关闭此窗口即可停止服务器
echo   🔄 如需更新，只需再次运行此文件
echo -----------------------------------
echo.
echo 如遇问题请查看 README.MD 和 bookmark_instructions.md
echo 按 Ctrl+C 可以随时终止预览服务器
echo.

REM 启动浏览器
start http://localhost:%PORT%/

REM 启动HTTP服务器
python -m http.server %PORT%

echo.
echo 服务器已关闭，操作完成
pause 