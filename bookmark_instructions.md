# 书签导航网站使用指南

## 简介

这个工具帮助您将浏览器书签自动转换为美观的导航网站格式。您可以随时导出最新的浏览器书签，然后用这个工具快速更新您的导航页面，无需任何编程知识。

## 使用方法

### 基本使用

1. 从浏览器导出书签HTML文件
   - Chrome/Edge: 书签管理器 -> 三点菜单 -> 导出书签
   - Firefox: 书签 -> 管理书签 -> 导出书签到HTML文件

2. 双击运行 `quick_import.bat` 批处理文件 (推荐)
   - 它会自动查找书签文件
   - 导入并更新网站
   - 启动本地预览服务器
   - 自动在浏览器中打开预览页面

3. 查看预览效果，完成后关闭命令窗口即可停止服务器

### 手动运行 (高级用户)

如果您需要更精确控制，可以使用以下方式手动运行：

```
python update_bookmarks.py your_bookmarks_file.html
```

或者使用PowerShell脚本：

```
.\update_bookmarks.ps1 your_bookmarks_file.html
```

## 高级功能

### 自动书签检测

`quick_import.bat` 会按以下顺序在当前目录中自动查找书签文件：

1. bookmarks.html (Chrome/Edge标准导出名称)
2. Bookmarks.html (Firefox标准导出名称)
3. 任何包含"bookmark"的HTML文件
4. 任何包含"书签"的HTML文件

### 创建教程页面

如果您想为某个书签添加教程页面，可以使用以下命令创建教程模板：

```
python update_bookmarks.py -c -n 目录名称 -t "页面标题" -u "网站URL"
```

例如：
```
python update_bookmarks.py -c -n MusicGen -t "MusicGen音乐生成器教程" -u "https://musicgen.com"
```

这会在`tutorial/MusicGen/`目录下创建一个教程页面模板，您可以编辑该模板添加详细的教程内容。

教程页面创建后，相应的书签卡片右侧会自动显示一个小三角形图标，点击该图标可以跳转到对应的教程页面。

### 脚本参数说明

```
usage: update_bookmarks.py [-h] [-i INDEX] [-v] [-c] [-t TITLE] [-u URL] [-n NAME] [bookmarks_file]

将浏览器书签转换为导航网站格式

positional arguments:
  bookmarks_file        书签文件路径

optional arguments:
  -h, --help            显示帮助信息
  -i INDEX, --index INDEX
                        要更新的index.html文件路径
  -v, --verbose         显示详细信息
  -c, --create-tutorial 创建教程页面模板
  -t TITLE, --title TITLE
                        教程页面标题
  -u URL, --url URL     网站URL
  -n NAME, --name NAME  教程目录名称
```

## 注意事项

1. 书签文件夹结构会被保留，每个顶级文件夹会成为一个导航分类
2. 为了获得最佳效果，建议在浏览器中整理好书签文件夹结构
3. 每次更新会替换网站上之前的所有书签内容
4. 程序默认使用Google的favicon服务获取网站图标

## 故障排除

如果遇到问题，请检查：

1. 确保已安装Python环境（3.6或更高版本）
2. 确保安装了BeautifulSoup4库（脚本会尝试自动安装）
3. 确保index.html文件中有书签区域标记
4. 确保书签文件使用UTF-8编码

## 自定义开发

如果您需要修改或扩展本工具的功能，核心文件如下：

- `update_bookmarks.py`: 主要的书签处理逻辑
- `index.html`: 网站模板文件
- `assets/css/no-blur.css`: 用于修复模糊效果的CSS文件
- `assets/js/update-sidebar-menu.js`: 侧边栏导航逻辑

## 技术支持

如有问题，请通过GitHub提交Issue获取帮助。 