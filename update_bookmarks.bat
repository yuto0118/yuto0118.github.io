@echo off
chcp 936 > nul
echo 正在更新书签导航...

rem 设置 Python 路径
set PYTHON_CMD=python

rem 检查参数类型
if "%~1"=="-c" (
  if "%~2"=="" (
    echo 错误：创建教程页面需要指定目录名称
    goto :usage
  )
  if "%~3"=="" (
    echo 错误：创建教程页面需要指定页面标题
    goto :usage
  )
  if "%~4"=="" (
    echo 错误：创建教程页面需要指定网站URL
    goto :usage
  )
  
  echo 正在创建教程页面模板...
  %PYTHON_CMD% update_bookmarks.py -c -n "%~2" -t "%~3" -u "%~4"
  if %errorlevel% neq 0 (
    echo 创建教程页面模板失败，请检查错误信息。
    pause
    exit /b 1
  )
  
  echo.
  echo 教程页面模板创建成功！
  pause
  exit /b 0
)

rem 检查是否有参数传入（书签文件）
if "%~1"=="" (
  echo 未指定书签文件，将使用默认文件 bookmarks_2025_5_16.html
  set BOOKMARK_FILE=bookmarks_2025_5_16.html
) else (
  set BOOKMARK_FILE=%~1
)

rem 检查书签文件是否存在
if not exist "%BOOKMARK_FILE%" (
  echo 错误：找不到书签文件 %BOOKMARK_FILE%
  pause
  exit /b 1
)

rem 检查依赖包是否已安装
%PYTHON_CMD% -c "import bs4" >nul 2>&1
if %errorlevel% neq 0 (
  echo 正在安装必要的依赖包...
  %PYTHON_CMD% -m pip install beautifulsoup4
)

rem 运行更新脚本
echo 正在处理书签文件: %BOOKMARK_FILE%
%PYTHON_CMD% update_bookmarks.py "%BOOKMARK_FILE%"

if %errorlevel% neq 0 (
  echo 更新失败，请检查错误信息。
  pause
  exit /b 1
)

echo.
echo 更新成功！正在启动预览服务器...

rem 检查是否有端口被占用，尝试不同的端口
set PORT=8088
netstat -ano | findstr ":%PORT% " >nul
if %errorlevel% equ 0 (
  set PORT=8089
  netstat -ano | findstr ":%PORT% " >nul
  if %errorlevel% equ 0 (
    set PORT=8090
  )
)

rem 在后台启动HTTP服务器
start "" %PYTHON_CMD% -m http.server %PORT%

echo 预览服务器已启动，请访问 http://localhost:%PORT% 查看效果
echo 在浏览器中查看后，按任意键退出...
pause >nul
taskkill /f /im python.exe >nul 2>&1
exit /b 0

:usage
echo.
echo 使用方法:
echo.
echo 更新书签导航:
echo   update_bookmarks.bat [书签文件路径]
echo.
echo 创建教程页面模板:
echo   update_bookmarks.bat -c 目录名称 "页面标题" "网站URL"
echo.
echo 示例:
echo   update_bookmarks.bat bookmarks.html
echo   update_bookmarks.bat -c MusicGen "MusicGen AI音乐生成" "https://musicgen.com"
echo.
pause 
exit /b 0 