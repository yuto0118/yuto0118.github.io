@echo off
title Bookmark Import

echo ====================================
echo        Bookmark Import Tool
echo ====================================
echo.

echo Searching for bookmark files...

REM Try to find bookmark files in order of priority
set BOOKMARK_FILE=

REM First priority - standard Chrome/Edge export name
if exist "bookmarks.html" (
    set BOOKMARK_FILE=bookmarks.html
    echo Found: bookmarks.html
    goto FOUND_FILE
)

REM Second priority - standard Firefox export name
if exist "Bookmarks.html" (
    set BOOKMARK_FILE=Bookmarks.html
    echo Found: Bookmarks.html
    goto FOUND_FILE
)

REM Third priority - bookmark_YYYY_MM_DD.html pattern (common in this project)
if exist "bookmarks_*.html" (
    for %%f in (bookmarks_*.html) do (
        set BOOKMARK_FILE=%%f
        echo Found: %%f
        goto FOUND_FILE
    )
)

REM Fourth priority - any HTML with bookmark in name
for %%f in (*bookmark*.html) do (
    set BOOKMARK_FILE=%%f
    echo Found: %%f
    goto FOUND_FILE
)

:FOUND_FILE
if "%BOOKMARK_FILE%"=="" (
    echo No bookmark files found!
    echo.
    echo Please export bookmarks from your browser first.
    echo Tips:
    echo - In Chrome/Edge: Bookmarks menu -^> Bookmark manager -^> ... -^> Export bookmarks
    echo - Save as "bookmarks.html" in this folder
    echo.
    pause
    exit /b 1
)

echo.
echo Using: %BOOKMARK_FILE%
echo.

REM Import bookmarks
python update_bookmarks.py "%BOOKMARK_FILE%"

if %errorlevel% neq 0 (
    echo.
    echo Import failed!
    pause
    exit /b 1
)

echo.
echo Bookmarks imported successfully!
echo Starting preview server...
echo.
echo Close this window when finished viewing.

REM Start browser
start http://localhost:8088/

REM Start HTTP server
python -m http.server 8088

pause 