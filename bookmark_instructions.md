# 导航网站书签更新指南

## 简介

这个工具帮助您将浏览器书签自动转换为导航网站的格式，并更新到您的网站中。您可以随时导出最新的浏览器书签，然后用这个工具快速更新您的导航页面。

## 使用方法

1. 从浏览器导出书签HTML文件（Chrome/Edge: 书签管理器 -> 三点菜单 -> 导出书签）
2. 运行更新脚本：`update_bookmarks.bat bookmarks_file.html`
3. 完成后，网站会自动启动预览服务器

## 高级功能

### 创建教程页面

如果您想为某个书签添加教程页面，可以使用以下命令创建教程模板：

```
python update_bookmarks.py -c -n 目录名称 -t "页面标题" -u "网站URL"
```

例如：
```
python update_bookmarks.py -c -n MusicGen -t "MusicGen" -u "https://musicgen.com"
```

这会在`tutorial/MusicGen/`目录下创建一个教程页面模板，您可以编辑该模板添加详细的教程内容。

创建教程页面后，当您运行更新脚本时，相应的书签卡片右侧会自动显示一个小三角形图标，点击该图标可以跳转到对应的教程页面。

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

1. 确保已安装Python环境
2. 确保安装了BeautifulSoup4库（脚本会尝试自动安装）
3. 确保index.html文件中有书签区域标记：`<!-- BOOKMARKS_SECTION_START -->`和`<!-- BOOKMARKS_SECTION_END -->`

## 技术支持

如有问题，请通过以下方式联系：

- Email: aibard123.com@gmail.com 