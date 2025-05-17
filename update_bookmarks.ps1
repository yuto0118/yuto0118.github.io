# 书签导航系统 - 自动更新与预览
# PowerShell脚本版本
# 确保以UTF-8编码保存

Write-Host "书签导航系统 - 自动更新与预览" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# 设置Python路径
$PYTHON_CMD = "python"

# 检查参数类型
if ($args.Count -gt 0 -and $args[0] -eq "-c") {
    if ($args.Count -lt 4) {
        Write-Host "错误：创建教程页面需要指定目录名称、页面标题和网站URL" -ForegroundColor Red
        Write-Host "`n使用方法:`n  .\update_bookmarks.ps1 -c 目录名称 `"页面标题`" `"网站URL`"`n" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "正在创建教程页面模板..." -ForegroundColor Green
    & $PYTHON_CMD update_bookmarks.py -c -n $args[1] -t $args[2] -u $args[3]
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "创建教程页面模板失败，请检查错误信息。" -ForegroundColor Red
        Read-Host "按任意键退出"
        exit 1
    }
    
    Write-Host "`n教程页面模板创建成功！" -ForegroundColor Green
    Read-Host "按任意键退出"
    exit 0
}

# 检查是否指定了书签文件
$BOOKMARK_FILE = ""

if ($args.Count -eq 0) {
    Write-Host "未指定书签文件，将自动搜索当前目录下的书签文件..." -ForegroundColor Yellow
    
    # 自动查找书签文件的顺序：
    # 1. bookmarks.html (Chrome/Edge标准导出名称)
    # 2. Bookmarks.html (Firefox标准导出名称)
    # 3. 任何包含"bookmark"的html文件
    # 4. 任何包含"书签"的html文件
    
    if (Test-Path "bookmarks.html") {
        Write-Host "找到 Chrome/Edge 书签文件: bookmarks.html" -ForegroundColor Green
        $BOOKMARK_FILE = "bookmarks.html"
    }
    elseif (Test-Path "Bookmarks.html") {
        Write-Host "找到 Firefox 书签文件: Bookmarks.html" -ForegroundColor Green
        $BOOKMARK_FILE = "Bookmarks.html"
    }
    else {
        $bookmarkFiles = Get-ChildItem -Filter "*bookmark*.html"
        if ($bookmarkFiles.Count -gt 0) {
            $BOOKMARK_FILE = $bookmarkFiles[0].Name
            Write-Host "找到书签文件: $BOOKMARK_FILE" -ForegroundColor Green
        }
        else {
            $bookmarkFiles = Get-ChildItem -Filter "*书签*.html"
            if ($bookmarkFiles.Count -gt 0) {
                $BOOKMARK_FILE = $bookmarkFiles[0].Name
                Write-Host "找到书签文件: $BOOKMARK_FILE" -ForegroundColor Green
            }
        }
    }
    
    if ([string]::IsNullOrEmpty($BOOKMARK_FILE)) {
        Write-Host "错误：在当前目录下未找到任何书签文件" -ForegroundColor Red
        Write-Host "请将从浏览器导出的书签文件放在此目录下" -ForegroundColor Yellow
        Write-Host "提示：在Chrome/Edge中可通过「书签管理器」-「导出书签」获取书签文件" -ForegroundColor Yellow
        Read-Host "按任意键退出"
        exit 1
    }
}
else {
    $BOOKMARK_FILE = $args[0]
}

# 检查书签文件是否存在
if (-not (Test-Path $BOOKMARK_FILE)) {
    Write-Host "错误：找不到书签文件 $BOOKMARK_FILE" -ForegroundColor Red
    Read-Host "按任意键退出"
    exit 1
}

# 检查依赖包是否已安装
try {
    Import-Module -Name "BeatifulSoup" -ErrorAction Stop
} 
catch {
    Write-Host "正在安装必要的依赖包..." -ForegroundColor Yellow
    & $PYTHON_CMD -m pip install beautifulsoup4
}

# 运行更新脚本
Write-Host "正在处理书签文件: $BOOKMARK_FILE" -ForegroundColor Green
& $PYTHON_CMD update_bookmarks.py $BOOKMARK_FILE

if ($LASTEXITCODE -ne 0) {
    Write-Host "更新失败，请检查错误信息。" -ForegroundColor Red
    Read-Host "按任意键退出"
    exit 1
}

Write-Host "`n更新成功！正在启动预览服务器..." -ForegroundColor Green

# 检查是否有端口被占用，尝试不同的端口
$PORT = 8088
$portInUse = $null
try {
    $portInUse = Get-NetTCPConnection -LocalPort $PORT -ErrorAction SilentlyContinue
}
catch {
    # 忽略错误
}

if ($portInUse) {
    $PORT = 8089
    $portInUse = $null
    try {
        $portInUse = Get-NetTCPConnection -LocalPort $PORT -ErrorAction SilentlyContinue
    }
    catch {
        # 忽略错误
    }
    
    if ($portInUse) {
        $PORT = 8090
    }
}

# 启动HTTP服务器和浏览器
$server = Start-Process -FilePath $PYTHON_CMD -ArgumentList "-m http.server $PORT" -PassThru -WindowStyle Minimized

# 等待服务器启动
Start-Sleep -Seconds 1

# 启动浏览器
Write-Host "正在启动浏览器..." -ForegroundColor Green
Start-Process "http://localhost:$PORT/"

Write-Host "`n预览服务器已启动，地址: http://localhost:$PORT" -ForegroundColor Green
Write-Host "网页已在浏览器中自动打开" -ForegroundColor Green
Write-Host "`n浏览完成后，按任意键停止服务器并退出..." -ForegroundColor Yellow
Read-Host

# 关闭Python服务器进程
Write-Host "正在关闭服务器..." -ForegroundColor Yellow
Stop-Process -Id $server.Id -Force

Write-Host "服务器已关闭，操作完成。" -ForegroundColor Green
Start-Sleep -Seconds 2 