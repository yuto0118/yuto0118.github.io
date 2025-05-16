#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from bs4 import BeautifulSoup
import re
import urllib.parse
import hashlib
import argparse

# 常量定义
CHROME_BOOKMARK_FOLDER_PATTERN = r'<H3.*?>(.*?)</H3>\s*<DL><p>(.*?)</DL>'
DEFAULT_ICON = 'assets/images/logos/default.webp'

def generate_id(text):
    """生成一个唯一的ID，用于锚点链�?""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def get_favicon_url(url):
    """从URL获取网站域名，用于生成favicon链接"""
    try:
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc
        return f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
    except:
        return "assets/images/logos/default.webp"  # 使用相对路径而非绝对路径

def parse_bookmarks(bookmarks_file):
    """解析书签文件，返回分层结构的书签数据"""
    print(f"开始解析书签文�? {bookmarks_file}")
    
    with open(bookmarks_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"文件大小: {len(content)} 字节")
    
    # 使用正则表达式查找所有文件夹和链�?    bookmarks_data = []
    parsed_folders = set()  # 跟踪已解析的文件夹名�?    
    # 尝试多种模式来识别文件夹结构
    patterns = [
        # 模式1: 标准的文件夹结构 <DL><p><DT><H3>文件夹名</H3><DL><p>内容</DL>
        r'<DL><p>\s*<DT><H3[^>]*>([^<]+)</H3>\s*<DL><p>(.*?)</DL>',
        
        # 模式2: 另一种常见结�?<DT><H3>文件夹名</H3><DL><p>内容</DL>
        r'<DT><H3[^>]*>([^<]+)</H3>\s*<DL><p>(.*?)</DL>',
        
        # 模式3: 更宽松的书签栏内部结�?        r'<H3[^>]*>([^<]+)</H3>\s*<DL><p>(.*?)</DL>'
    ]
    
    # 针对不同的模式尝试解�?    for pattern_idx, pattern in enumerate(patterns, 1):
        folders = re.findall(pattern, content, re.DOTALL)
        print(f"模式{pattern_idx}: 找到 {len(folders)} 个可能的文件�?)
        
        for folder_name, folder_content in folders:
            folder_name = folder_name.strip()
            
            # 跳过已经解析过的文件�?            if folder_name in parsed_folders:
                continue
                
            # 处理收藏�?书签栏特殊情�?            if folder_name in ["收藏�?, "书签�?]:
                # 在书签栏内部查找子文件夹
                sub_patterns = [
                    r'<DT><H3[^>]*>([^<]+)</H3>\s*<DL><p>(.*?)</DL>',  # 标准模式
                    r'<H3[^>]*>([^<]+)</H3>\s*<DL><p>(.*?)</DL>'       # 宽松模式
                ]
                
                sub_folders = []
                for sub_pattern in sub_patterns:
                    sub_folders.extend(re.findall(sub_pattern, folder_content, re.DOTALL))
                
                print(f"  '{folder_name}'中找�?{len(sub_folders)} 个子文件�?)
                
                for sub_folder_name, sub_folder_content in sub_folders:
                    sub_folder_name = sub_folder_name.strip()
                    
                    # 跳过已解析的文件�?                    if sub_folder_name in parsed_folders:
                        continue
                        
                    folder = {
                        'type': 'folder',
                        'name': sub_folder_name,
                        'items': []
                    }
                    
                    # 查找子文件夹中的链接
                    links_pattern = r'<DT><A[^>]*HREF="([^"]*)"[^>]*>([^<]*)</A>'
                    links = re.findall(links_pattern, sub_folder_content, re.DOTALL)
                    
                    for link_url, link_name in links:
                        link_name = link_name.strip()
                        if not link_name:
                            link_name = link_url
                        
                        link_item = {
                            'type': 'link',
                            'name': link_name,
                            'url': link_url,
                            'icon': get_favicon_url(link_url)
                        }
                        folder['items'].append(link_item)
                    
                    if folder['items']:
                        print(f"    子文件夹 '{sub_folder_name}' �?{len(folder['items'])} 个项�?)
                        bookmarks_data.append(folder)
                        parsed_folders.add(sub_folder_name)
            else:
                # 普通文件夹处理
                folder = {
                    'type': 'folder',
                    'name': folder_name,
                    'items': []
                }
                
                # 查找文件夹中的链�?                links_pattern = r'<DT><A[^>]*HREF="([^"]*)"[^>]*>([^<]*)</A>'
                links = re.findall(links_pattern, folder_content, re.DOTALL)
                
                for link_url, link_name in links:
                    link_name = link_name.strip()
                    if not link_name:
                        link_name = link_url
                    
                    link_item = {
                        'type': 'link',
                        'name': link_name,
                        'url': link_url,
                        'icon': get_favicon_url(link_url)
                    }
                    folder['items'].append(link_item)
                
                if folder['items']:
                    print(f"  文件�?'{folder_name}' �?{len(folder['items'])} 个项�?)
                    bookmarks_data.append(folder)
                    parsed_folders.add(folder_name)
    
    # 如果没有找到任何书签，创建一个默认的"我的书签"文件�?    if not bookmarks_data:
        print("警告: 没有找到任何书签分类，创建默�?我的书签'文件�?)
        
        # 查找所有链�?        links_pattern = r'<DT><A[^>]*HREF="([^"]*)"[^>]*>([^<]*)</A>'
        links = re.findall(links_pattern, content, re.DOTALL)
        
        if links:
            default_folder = {
                'type': 'folder',
                'name': '我的书签',
                'items': []
            }
            
            for link_url, link_name in links:
                link_name = link_name.strip()
                if not link_name:
                    link_name = link_url
                
                link_item = {
                    'type': 'link',
                    'name': link_name,
                    'url': link_url,
                    'icon': get_favicon_url(link_url)
                }
                default_folder['items'].append(link_item)
            
            if default_folder['items']:
                bookmarks_data.append(default_folder)
                print(f"  添加�?{len(default_folder['items'])} 个未分类链接�?我的书签'")
    
    # 只输出一次解析完成信�?    print(f"解析完成，找�?{len(bookmarks_data)} 个顶级文件夹")
    for folder in bookmarks_data:
        print(f"  - 文件�? {folder['name']}, 包含 {len(folder['items'])} 个项�?)
    
    return bookmarks_data

def process_folder_content(dl_tag):
    """处理文件夹内�?""
    items = []
    
    if not dl_tag:
        print("警告: 传入的DL标签为空")
        return items
    
    # 查找所有直接子DT标签
    dt_tags = dl_tag.find_all('dt', recursive=False)
    print(f"  正在处理文件夹，找到 {len(dt_tags)} 个DT标签")
    
    for dt in dt_tags:
        # 检查是否是子文件夹
        h3 = dt.find('h3')
        if h3:
            folder_name = h3.text.strip()
            print(f"    处理子文件夹: {folder_name}")
            
            folder = {
                'type': 'folder',
                'name': folder_name,
                'items': []
            }
            
            # 处理子文件夹内容
            sub_dl = dt.find('dl')
            if sub_dl:
                sub_items = process_folder_content(sub_dl)
                if sub_items:
                    folder['items'].extend(sub_items)
                    print(f"    子文件夹 '{folder_name}' �?{len(sub_items)} 个项�?)
                else:
                    print(f"    子文件夹 '{folder_name}' 没有找到有效项目")
            else:
                print(f"    子文件夹 '{folder_name}' 没有DL标签")
            
            items.append(folder)
        else:
            # 检查是否是链接
            a = dt.find('a')
            if a:
                link_name = a.text.strip() or "未命名链�?
                link_url = a.get('href', '')
                if link_url and link_name:
                    link_item = {
                        'type': 'link',
                        'name': link_name,
                        'url': link_url,
                        'icon': get_favicon_url(link_url)
                    }
                    items.append(link_item)
    
    return items

def generate_html(bookmarks_data):
    """生成HTML代码"""
    html_output = []
    
    # 为每个顶级文件夹创建一个部�?    for folder in bookmarks_data:
        if folder['type'] == 'folder':
            folder_name = folder['name'\]
            section_id = generate_id(folder_name)
            
            # 添加分类标题，使用与网站原有样式一致的格式
            html_output.append(f'''
<!-- {folder_name} 部分开�?-->
<div class="d-flex flex-fill bookmark-section">
    <h4 class="text-gray text-lg mb-4">
        <i class="fas fa-folder fa-lg icon-fw icon-lg mr-2" id="{section_id}"></i>
        {folder_name}
    </h4>
</div>
<div class="row">
''')
            
            # 添加该文件夹中的链接
            for item in folder['items']:
                if item['type'] == 'link':
                    link_name = item['name']
                    link_url = item['url']
                    link_icon = item['icon']
                    
                    # 检查是否有相应的教程页�?                    # 从链接URL中提取域名作为可能的教程目录�?                    tutorial_path = None
                    try:
                        domain = urllib.parse.urlparse(link_url).netloc
                        possible_names = []
                        
                        # 尝试从域名中提取可能的名�?                        if domain:
                            parts = domain.split('.')
                            for part in parts:
                                if part and part.lower() not in ['www', 'com', 'cn', 'org', 'net', 'io', 'ai']:
                                    # 首字母大�?                                    possible_names.append(part.capitalize())
                        
                        # 也尝试以链接名称作为可能的路�?                        if link_name:
                            # 移除链接名称中的空格和特殊字�?                            clean_name = ''.join(c for c in link_name if c.isalnum())
                            possible_names.append(clean_name)
                        
                        # 检查是否存在对应的教程目录
                        for name in possible_names:
                            check_path = os.path.join('tutorial', name)
                            if os.path.exists(check_path) and os.path.isdir(check_path):
                                tutorial_path = f"/tutorial/{name}/"
                                break
                                
                    except Exception as e:
                        print(f"检查教程路径时出错: {str(e)}")
                        tutorial_path = None
                    
                    # 使用网站原有的卡片样式，添加教程链接支持
                    if tutorial_path:
                        html_output.append(f'''
    <div class="url-card col-6 col-sm-6 col-md-4 col-xl-5a col-xxl-6a">
        <div class="url-body default">
        <a class="card no-c mb-4 bookmark-link" data-html="true" data-original-title="{link_name} &lt;br&gt;  右边的箭头查看教�? data-placement="bottom" data-toggle="tooltip" data-url="{link_url}" href="{link_url}" target="_blank">
                <div class="card-body">
                    <div class="url-content d-flex align-items-center">
                        <div class="url-img mr-2 d-flex align-items-center justify-content-center">
                        <img alt="{link_name}" class="lazy" data-src="{link_icon}" onerror="javascript:this.src='assets/images/logos/default.webp'" src="{link_icon}"/>
                    </div>
                    <div class="url-info flex-fill">
                        <div class="text-sm overflowClip_1">
                            <strong>{link_name}</strong>
                        </div>
                        <p class="overflowClip_1 m-0 text-muted text-xs">{link_name}</p>
                    </div>
                </div>
            </div>
        </a>
        <a class="togo text-center text-muted is-views" data-placement="right" data-toggle="tooltip" href="{tutorial_path}" rel="nofollow" target="_blank" title="教程">
            <i class="iconfont icon-goto"></i>
        </a>
        </div>
    </div>
''')
                    else:
                        # 没有教程的普通卡�?                        html_output.append(f'''
    <div class="url-card col-6 col-sm-6 col-md-4 col-xl-5a col-xxl-6a">
        <div class="url-body default">
            <a class="card no-c mb-4 bookmark-link" data-original-title="{link_name}" data-placement="bottom" data-toggle="tooltip" data-url="{link_url}" href="{link_url}" target="_blank">
                <div class="card-body">
                    <div class="url-content d-flex align-items-center">
                        <div class="url-img mr-2 d-flex align-items-center justify-content-center">
                            <img alt="{link_name}" class="lazy" data-src="{link_icon}" onerror="javascript:this.src='assets/images/logos/default.webp'" src="{link_icon}"/>
                        </div>
                        <div class="url-info flex-fill">
                            <div class="text-sm overflowClip_1">
                                <strong>{link_name}</strong>
                            </div>
                            <p class="overflowClip_1 m-0 text-muted text-xs">{link_name}</p>
                        </div>
                    </div>
                </div>
            </a>
        </div>
    </div>
''')
                elif item['type'] == 'folder':
                    # 处理子文件夹
                    if 'items' in item and item['items']:
                        subfolder_name = item['name']
                        subfolder_id = generate_id(subfolder_name)
                        
                        # 子文件夹结束上一个div.row，创建新的子文件夹部�?                        html_output.append(f'''
</div>
<!-- {subfolder_name} 子文件夹开�?-->
<div class="d-flex flex-fill bookmark-section">
    <h4 class="text-gray text-lg mb-4 ml-3">
        <i class="fas fa-folder-open fa-lg icon-fw icon-lg mr-2" id="{subfolder_id}"></i>
        {subfolder_name}
    </h4>
</div>
<div class="row">
''')
                        
                        # 添加子文件夹中的链接
                        for subitem in item['items']:
                            if subitem['type'] == 'link':
                                link_name = subitem['name']
                                link_url = subitem['url']
                                link_icon = subitem['icon']
                                
                                # 检查是否有相应的教程页�?                                tutorial_path = None
                                try:
                                    domain = urllib.parse.urlparse(link_url).netloc
                                    possible_names = []
                                    
                                    # 尝试从域名中提取可能的名�?                                    if domain:
                                        parts = domain.split('.')
                                        for part in parts:
                                            if part and part.lower() not in ['www', 'com', 'cn', 'org', 'net', 'io', 'ai']:
                                                # 首字母大�?                                                possible_names.append(part.capitalize())
                                    
                                    # 也尝试以链接名称作为可能的路�?                                    if link_name:
                                        # 移除链接名称中的空格和特殊字�?                                        clean_name = ''.join(c for c in link_name if c.isalnum())
                                        possible_names.append(clean_name)
                                    
                                    # 检查是否存在对应的教程目录
                                    for name in possible_names:
                                        check_path = os.path.join('tutorial', name)
                                        if os.path.exists(check_path) and os.path.isdir(check_path):
                                            tutorial_path = f"/tutorial/{name}/"
                                            break
                                            
                                except Exception as e:
                                    print(f"检查子文件夹教程路径时出错: {str(e)}")
                                    tutorial_path = None
                                
                                # 使用与主文件夹相同的卡片样式
                                if tutorial_path:
                                    html_output.append(f'''
    <div class="url-card col-6 col-sm-6 col-md-4 col-xl-5a col-xxl-6a">
        <div class="url-body default">
        <a class="card no-c mb-4 bookmark-link" data-html="true" data-original-title="{link_name} &lt;br&gt;  右边的箭头查看教�? data-placement="bottom" data-toggle="tooltip" data-url="{link_url}" href="{link_url}" target="_blank">
                <div class="card-body">
                    <div class="url-content d-flex align-items-center">
                        <div class="url-img mr-2 d-flex align-items-center justify-content-center">
                        <img alt="{link_name}" class="lazy" data-src="{link_icon}" onerror="javascript:this.src='assets/images/logos/default.webp'" src="{link_icon}"/>
                        </div>
                        <div class="url-info flex-fill">
                            <div class="text-sm overflowClip_1">
                            <strong>{link_name}</strong>
                        </div>
                        <p class="overflowClip_1 m-0 text-muted text-xs">{link_name}</p>
                    </div>
                </div>
            </div>
        </a>
        <a class="togo text-center text-muted is-views" data-placement="right" data-toggle="tooltip" href="{tutorial_path}" rel="nofollow" target="_blank" title="教程">
            <i class="iconfont icon-goto"></i>
            </a>
        </div>
    </div>
''')
                                else:
                                    # 没有教程的普通卡�?                                    html_output.append(f'''
    <div class="url-card col-6 col-sm-6 col-md-4 col-xl-5a col-xxl-6a">
        <div class="url-body default">
            <a class="card no-c mb-4 bookmark-link" data-original-title="{link_name}" data-placement="bottom" data-toggle="tooltip" data-url="{link_url}" href="{link_url}" target="_blank">
                <div class="card-body">
                    <div class="url-content d-flex align-items-center">
                        <div class="url-img mr-2 d-flex align-items-center justify-content-center">
                            <img alt="{link_name}" class="lazy" data-src="{link_icon}" onerror="javascript:this.src='assets/images/logos/default.webp'" src="{link_icon}"/>
                        </div>
                        <div class="url-info flex-fill">
                            <div class="text-sm overflowClip_1">
                                <strong>{link_name}</strong>
                            </div>
                            <p class="overflowClip_1 m-0 text-muted text-xs">{link_name}</p>
                        </div>
                    </div>
                </div>
            </a>
        </div>
    </div>
''')
            
            # 关闭行div
            html_output.append('</div>')
            html_output.append(f'<!-- {folder_name} 部分结束 -->\n')
    
    return '\n'.join(html_output)

def update_sidebar_menu(bookmarks_data, html_content):
    """更新侧边栏菜单，使用书签文件夹结�?""
    print("更新侧边栏菜�?..")
    
        # 创建新的侧边栏菜单内�?    sidebar_menu_html = []
    
    # 为每个顶级文件夹创建菜单�?    for folder in bookmarks_data:
        if folder['type'] == 'folder':
            folder_name = folder['name'\]
            section_id = generate_id(folder_name)
            
            # 为每个文件夹创建一个图�?- 使用FontAwesome图标
            icon_class = "fa-folder"  # 默认图标
            
            # 根据文件夹名称尝试匹配合适的图标
            lower_name = folder_name.lower()
            if "视频" in lower_name or "影片" in lower_name or "movie" in lower_name:
                icon_class = "fa-video"
            elif "音乐" in lower_name or "歌曲" in lower_name or "music" in lower_name:
                icon_class = "fa-music"
            elif "购物" in lower_name or "商城" in lower_name or "shop" in lower_name:
                icon_class = "fa-shopping-cart"
            elif "游戏" in lower_name or "game" in lower_name:
                icon_class = "fa-gamepad"
            elif "工具" in lower_name or "tool" in lower_name:
                icon_class = "fa-tools"
            elif "学习" in lower_name or "教育" in lower_name or "edu" in lower_name:
                icon_class = "fa-book"
            elif "社交" in lower_name or "社区" in lower_name or "社会" in lower_name or "social" in lower_name:
                icon_class = "fa-users"
            elif "新闻" in lower_name or "资讯" in lower_name or "news" in lower_name:
                icon_class = "fa-newspaper"
            elif "金融" in lower_name or "财务" in lower_name or "理财" in lower_name or "finance" in lower_name:
                icon_class = "fa-money-bill-alt"
            
            # 添加侧边栏菜单项
            sidebar_menu_html.append(f'''
<li class="sidebar-item">
    <a class="smooth" href="#{section_id}">
        <i class="fas {icon_class} fa-lg icon-fw icon-lg mr-2"></i>
        <span>{folder_name}</span>
    </a>
</li>''')
    
    # 将侧边栏菜单项组合起�?    sidebar_menu = "".join(sidebar_menu_html)
    
    # 更新侧边栏菜�?    sidebar_pattern = r'<div class="sidebar-menu-inner">\s*<ul>(.*?)</ul>\s*</div>'
    new_sidebar = f'''<div class="sidebar-menu-inner">
    <ul>
    {sidebar_menu}
    </ul>
    </div>'''
    
    # 替换侧边栏菜�?    html_content = re.sub(sidebar_pattern, new_sidebar, html_content, flags=re.DOTALL)
    print("侧边栏菜单更新完�?)
    
    return html_content

def update_index_html(index_file, bookmarks_content, bookmarks_data):
    """更新index.html文件，替换书签部分内�?""
    try:
        # 创建index.html的备�?        import shutil
        backup_file = index_file + '.bak'
        shutil.copy2(index_file, backup_file)
        print(f"已创建备份文�? {backup_file}")
        
        # 读取原始文件内容
        with open(index_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print(f"读取index.html文件，大�? {len(html_content)} 字节")
        
        # 清理教程目录
        print("清理教程目录...")
        tutorial_dir = "tutorial"
        if os.path.exists(tutorial_dir) and os.path.isdir(tutorial_dir):
            for item in os.listdir(tutorial_dir):
                item_path = os.path.join(tutorial_dir, item)
                if os.path.isdir(item_path) and item != ".git" and item != ".gitkeep":
                    try:
                        import shutil
                        shutil.rmtree(item_path)
                        print(f"  已删除教程目�? {item_path}")
                    except Exception as e:
                        print(f"  删除目录时出�?{item_path}: {str(e)}")
        
        # 更新侧边栏菜�?        print("更新侧边栏菜�?..")
        html_content = update_sidebar_menu(bookmarks_data, html_content)
        
        # 保留页面的基本结构并只显示书签内容和搜索�?        print("修改网站结构，只保留搜索框和书签内容...")
        
        # 提取头部内容（包含必要的CSS和JavaScript�?        head_start = html_content.find('<head>')
        head_end = html_content.find('</head>') + 7  # 包含</head>标签
        head_content = html_content[head_start:head_end]
        
        # 提取搜索相关的JavaScript
        search_js = '<script id="content-search-js" src="/assets/js/content-search.js" type="text/javascript"></script>'
        if search_js not in head_content:
            head_content = head_content.replace('</head>', f'{search_js}</head>')
        
        # 提取底部脚本内容（保留必要的JavaScript�?        footer_scripts_start = html_content.rfind('<script id="jqueryui-touch-js"')
        footer_scripts_end = html_content.rfind('</body>')
        footer_scripts = html_content[footer_scripts_start:footer_scripts_end]
        
        # 构建简化版的HTML结构，只包含搜索框和书签内容
        simplified_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
{head_content}
<body class="io-grey-mode">
<div class="page-container">
    <div class="sticky sidebar-nav fade animate-nav" id="sidebar" style="width: 170px">
        <div class="modal-dialog h-100 sidebar-nav-inner">
            <div class="sidebar-logo border-bottom border-color">
                <div class="logo overflow-hidden">
                    <a class="logo-expanded" href="">
                        <img alt="书签导航" class="logo-light" height="40" src="/assets/images/bt8-expand-light.png"/>
                        <img alt="书签导航" class="logo-dark d-none" height="40" src="/assets/images/bt8-expand-dark.png"/>
                    </a>
                    <a class="logo-collapsed" href="">
                        <img alt="书签导航" class="logo-light" height="40" src="/assets/images/bt.png"/>
                        <img alt="书签导航" class="logo-dark d-none" height="40" src="/assets/images/bt.png"/>
                    </a>
                </div>
            </div>
            <div class="sidebar-menu flex-fill">
                <div class="sidebar-scroll">
                    <div class="sidebar-menu-inner">
                        <ul>
                        <!-- 侧边栏内容将由update_sidebar_menu函数填充 -->
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="main-content flex-fill grid-bg">
        <div class="big-header-banner">
            <div class="page-header sticky" id="header">
                <div class="navbar navbar-expand-md">
                    <div class="container-fluid p-0">
                        <a class="navbar-brand d-md-none" href="" title="书签导航">
                            <img alt="书签导航" class="logo-light" src="/assets/images/bt.png"/>
                            <img alt="书签导航" class="logo-dark d-none" src="/assets/images/bt.png"/>
                        </a>
                        <div class="collapse navbar-collapse order-2 order-md-1">
                            <div class="header-mini-btn">
                                <label>
                                    <input id="mini-button" type="checkbox"/>
                                    <svg viewbox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                                        <path class="line--1" d="M0 40h62c18 0 18-20-17 5L31 55"></path>
                                        <path class="line--2" d="M0 50h80"></path>
                                        <path class="line--3" d="M0 60h62c18 0 18 20-17-5L31 45"></path>
                                    </svg>
                                </label>
                            </div>
                        </div>
                        <ul class="nav navbar-menu text-xs order-1 order-md-2">
                            <li class="nav-search ml-3 ml-md-4">
                                <a data-target="#search-modal" data-toggle="modal" href="javascript:"><i class="iconfont icon-search icon-2x"></i></a>
                            </li>
                            <li class="nav-item d-md-none mobile-menu ml-3 ml-md-4">
                                <a data-target="#sidebar" data-toggle="modal" href="javascript:" id="sidebar-switch"><i class="iconfont icon-classification icon-2x"></i></a>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
            <div class="placeholder" style="height:74px"></div>
        </div>
        
        <div class="header-big post-top css-color mb-4" id="search-bg" style=""></div>
        
        <div class="content-site customize-site" id="content">
            <!-- 搜索框部�?-->
            <div class="container-fluid">
                <div class="d-flex flex-fill">
                    <div class="flex-fill">
                        <div class="card">
                            <div class="card-body">
                                <div class="d-flex">
                                    <div class="flex-fill">
                                        <div class="input-group">
                                            <div class="input-group-prepend">
                                                <button class="btn btn-search" type="button" id="search-btn"><i class="iconfont icon-search"></i></button>
                                            </div>
                                            <input id="search-text" class="form-control" type="text" placeholder="支持书签内容搜索" aria-label="搜索" data-toggle="tooltip" data-placement="bottom" title="输入关键词搜�? autocomplete="off">
                                        </div>
                                        <div id="word" class="above"></div>
                                    </div>
                                </div>
                                <div class="card search-smart-tips search-hot-text" style="display:none"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 书签内容部分 -->
            <div class="container-fluid">
<!-- BOOKMARKS_SECTION_START -->

{bookmarks_content}

<!-- BOOKMARKS_SECTION_END -->
            </div>
        </div>
    </div>
</div>

<!-- 搜索模态框 -->
<div class="modal fade search" id="search-modal">
    <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-body">
                <div id="search-body">
                    <div class="card">
                        <div class="card-body">
                            <div class="d-flex flex-fill">
                                <div class="flex-fill">
                                    <div class="input-group">
                                        <div class="input-group-prepend">
                                            <button class="btn btn-search" type="button" id="modal-search-btn"><i class="iconfont icon-search"></i></button>
                                        </div>
                                        <input id="modal-search-text" class="form-control" type="text" placeholder="搜索书签内容" aria-label="搜索" data-toggle="tooltip" data-placement="bottom" title="输入关键词搜�? autocomplete="off">
                                    </div>
                                    <div id="modal-word" class="above"></div>
                                </div>
                            </div>
                            <div class="card search-smart-tips search-hot-text" style="display:none"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

{footer_scripts}
</body>
</html>'''
        
        # 写回更新后的文件
        print("写入文件...")
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(simplified_html)
        
        print(f"更新成功，写�?{len(simplified_html)} 字节�?index.html")
        return True
    except Exception as e:
        print(f"更新index.html时出�? {str(e)}")
        import traceback
        traceback.print_exc()
            
        # 如果出错，恢复备�?        if 'backup_file' in locals():
            print("出错，恢复备份文�?..")
            shutil.copy2(backup_file, index_file)
            print("已恢复原始文�?)
        
        return False

def create_tutorial_template(tutorial_name, title, url):
    """创建一个教程页面模�?""
    try:
        tutorial_dir = os.path.join('tutorial', tutorial_name)
        
        # 如果目录不存在，创建目录
        if not os.path.exists(tutorial_dir):
            os.makedirs(tutorial_dir)
        
        # 创建index.html文件
        tutorial_file = os.path.join(tutorial_dir, 'index.html')
        
        # 如果文件已存在，不覆�?        if os.path.exists(tutorial_file):
            print(f"教程文件已存�? {tutorial_file}")
            return False
        
        # 创建教程模板内容
        template_content = f'''<!DOCTYPE html>
<html lang="zh-CN">

<head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge, chrome=1" />
    <meta name="viewport"
        content="width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no" />
    <meta name="theme-color" content="#f9f9f9" />
\t<title>{title} 教程 | AiBard123| ai工具网址导航,ai最新产�?/title>
\t<link rel="shortcut icon" href="/assets/images/favicon.png" />
    <meta name="keywords" content="chatgpt,AI,AI聊天,AI文本生成,AI绘画,AI编程,AI电商" />
\t<meta name="description" content="AiBard123 网址导航 | 免费chatgpt 汇集各类先进的人工智能产品，旨在帮助用户更快速地了解和使用这些产�?轻松地浏览不同领域的AI产品，包括语音识别、图像处理、自然语言处理�? />
    
    <link rel="stylesheet" id="block-library-css"
        href="/assets/css/block-library.min-5.6.2.css" type="text/css" media="all" />
    <link rel="stylesheet" id="iconfont-css" href="/assets/css/iconfont-3.03029.1.css"
        type="text/css" media="all" />
    <link rel="stylesheet" id="bootstrap-css" href="/assets/css/bootstrap.min-4.3.1.css"
        type="text/css" media="all" />
    <link rel="stylesheet" id="fancybox-css" href="/assets/css/fancybox.min-3.5.7.css"
        type="text/css" media="all" />
    <link rel="stylesheet" id="iowen-css" href="/assets/css/style-3.03029.1.css"
        type="text/css" media="all" />
    <link rel="stylesheet" id="custom-css" href="/assets/css/custom-style.css"
        type="text/css" media="all" />
    <link rel="stylesheet" id="fortawesome-css" href="/assets/fontawesome-5.15.4/css/all.min.css" type="text/css" />
\t<link rel="stylesheet" id="custom-css" href="/assets/css/github-markdown.css"
        type="text/css" media="all" />
    <script type="text/javascript" src="/assets/js/jquery.min-3.2.1.js" id="jquery-js"></script>
    <script type="text/javascript" src="/assets/js/content-search.js"  id="content-search-js"></script>
</head>


<div class="flex-fill grid-bg">
    <div class="big-header-banner">
        <div id="header" class="page-header sticky">
            <div class="navbar navbar-expand-md">
                <div class="container-fluid p-0">

                    <a href="" class="navbar-brand d-md-none" title="AiBard123| ai工具网址导航,ai最新产�?>
                        <img src="/assets/images/bt.png" class="logo-light"
                            alt="AiBard123| ai工具网址导航,ai最新产�?>
                        <img src="/assets/images/bt.png" class="logo-dark d-none"
                            alt="AiBard123| ai工具网址导航,ai最新产�?>
                    </a>

                    <div class="collapse navbar-collapse order-2 order-md-1">
                        <div class="header-mini-btn">
                            <label>
                                <input id="mini-button" type="checkbox">
                                <svg viewbox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                                    <path class="line--1" d="M0 40h62c18 0 18-20-17 5L31 55"></path>
                                    <path class="line--2" d="M0 50h80"></path>
                                    <path class="line--3" d="M0 60h62c18 0 18 20-17-5L31 45"></path>
                                </svg>
                            </label>

                        </div>

                        <ul class="navbar-nav site-menu" style="margin-right: 16px;">
                        
\t\t\t<li >
\t\t\t\t<a href="/">
                                    <i class="fa fa-home fa-lg mr-2"></i>
                                    <span>首页</span>
                                </a>
\t\t\t\t<ul class="sub-menu">
\t\t\t\t
\t\t\t\t</ul>
\t\t\t    </li>
\t\t\t
\t\t\t</ul>
                    </div>
                </div>
            </div>
        </div>
        <div class="placeholder" style="height:74px"></div>
    </div>


<body class="page-body boxed-container">
    <main role="main" class="flex-shrink-0">
    <div class="container">
        <h1 class="mt-5">{title} 教程</h1>
        <div class="content">
            <style>
    body{{
\t    background:#fff;
\t}}
\t

\t@media (max-width: 767px) {{
\t\t.markdown-body {{
\t\t\tpadding: 15px;
\t\t}}
\t}}
</style>
<article class="markdown-body">
<br/>
<h3 id="{tutorial_name.lower()}">{title}</h3>
<br/>
<p>这是{title}的使用教程页面。您可以在这里添加{title}的详细使用说明、功能介绍、使用技巧等内容�?/p>

<p>网站链接�?a href="{url}" target="_blank">{url}</a></p>

<h4>主要功能介绍</h4>
<ul>
    <li>在这里添加主要功�?的介�?/li>
    <li>在这里添加主要功�?的介�?/li>
    <li>在这里添加主要功�?的介�?/li>
</ul>

<h4>使用步骤</h4>
<ol>
    <li>第一步：在这里描述第一步操�?/li>
    <li>第二步：在这里描述第二步操作</li>
    <li>第三步：在这里描述第三步操作</li>
</ol>

<h4>实用技�?/h4>
<p>在这里分享一些使用技巧和注意事项�?/p>

</article>
        </div>
    </div>
    </main>
    <footer class="main-footer footer-type-1 text-xs">
<div id="footer-tools" class="d-flex flex-column">
    <a href="javascript:" id="go-to-up" class="smoothscroll" title="返回顶部" uk-tooltip="pos: left">
        <i class="iconfont icon-top icon-2x"></i>
    </a>
</div>
<div class="footer-inner">
    <div class="footer-text">Copyright © 2023-2025 </div>
</div>
</footer>
    <!-- 自定义js -->
<script type='text/javascript' src='/assets/js/popper.min-2.4.4.js' id='popper-js'></script>
<script type='text/javascript' src='/assets/js/bootstrap.min-4.3.1.js' id='bootstrap-js'></script>
<script type='text/javascript' src='/assets/js/theia-sticky-sidebar-1.5.0.js' id='sidebar-js'></script>
<script type='text/javascript' src='/assets/js/lazyload.min-12.4.0.js' id='lazyload-js'></script>
<script type='text/javascript' src='/assets/js/app-3.03029.1.js' id='appjs-js'></script>
</body>
</html>'''
        
        # 写入文件
        with open(tutorial_file, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        print(f"成功创建教程模板: {tutorial_file}")
        return True
    except Exception as e:
        print(f"创建教程模板时出�? {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='将浏览器书签转换为导航网站格�?)
    parser.add_argument('bookmarks_file', nargs='?', help='书签文件路径')
    parser.add_argument('-i', '--index', default='index.html', help='要更新的index.html文件路径')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细信息')
    parser.add_argument('-c', '--create-tutorial', action='store_true', help='创建教程页面模板')
    parser.add_argument('-t', '--title', help='教程页面标题')
    parser.add_argument('-u', '--url', help='网站URL')
    parser.add_argument('-n', '--name', help='教程目录名称')
    
    args = parser.parse_args()
    
    # 创建教程页面模板
    if args.create_tutorial:
        if not args.name or not args.title or not args.url:
            print("错误: 创建教程页面需要指�?--name, --title �?--url 参数")
            return 1
        
        if create_tutorial_template(args.name, args.title, args.url):
            print(f"教程模板创建成功。后续使用时，卡片会自动链接�?/tutorial/{args.name}/ 页面�?)
            return 0
        else:
            return 1
    
    # 正常处理书签文件
    if not args.bookmarks_file:
        print("错误: 请指定书签文件路�?)
        return 1
    
    if not os.path.exists(args.bookmarks_file):
        print(f"错误: 找不到书签文�?{args.bookmarks_file}")
        return 1
    
    if not os.path.exists(args.index):
        print(f"错误: 找不到索引文�?{args.index}")
        return 1
    
    print("正在解析书签文件...")
    try:
        bookmarks_data = parse_bookmarks(args.bookmarks_file)
        if not bookmarks_data:
            print("错误: 未能从书签文件中解析出任何内容！")
            return 1
    except Exception as e:
        print(f"解析书签文件时出�? {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("正在生成 HTML 代码...")
    html_content = generate_html(bookmarks_data)
    if not html_content.strip():
        print("错误: 生成的HTML为空�?)
        return 1
    
    print(f"生成的HTML大小: {len(html_content)} 字节")
    
    print("正在更新 index.html...")
    try:
        if update_index_html(args.index, html_content, bookmarks_data):
            print("更新完成!")
        else:
            print("更新失败.")
            return 1
    except Exception as e:
        print(f"更新 index.html 时出�? {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
