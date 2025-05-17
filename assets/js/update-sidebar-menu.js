// 立即执行函数 - 在DOM加载之前阻止模糊效果
(function() {
    // 拦截并阻止所有可能添加模糊的CSS和JS操作
    var originalSetAttribute = Element.prototype.setAttribute;
    Element.prototype.setAttribute = function(name, value) {
        // 阻止设置任何可能导致模糊的样式属性
        if ((name === 'style' && (value.indexOf('blur') !== -1 || value.indexOf('filter') !== -1)) ||
            (name === 'class' && (value.indexOf('blur') !== -1))) {
            console.log('阻止模糊样式: ' + name + '=' + value);
            // 不执行原始操作
            return;
        }
        return originalSetAttribute.call(this, name, value);
    };
    
    // 拦截style属性的setter
    var originalStyleSetter = Object.getOwnPropertyDescriptor(HTMLElement.prototype, 'style').set;
    Object.defineProperty(HTMLElement.prototype, 'style', {
        set: function(value) {
            if (typeof value === 'string' && (value.indexOf('blur') !== -1 || value.indexOf('filter') !== -1)) {
                console.log('阻止模糊样式设置: ' + value);
                // 不设置包含模糊的样式
                return;
            }
            return originalStyleSetter.call(this, value);
        },
        get: Object.getOwnPropertyDescriptor(HTMLElement.prototype, 'style').get
    });
    
    // 拦截classList的add方法
    var originalClassListAdd = DOMTokenList.prototype.add;
    DOMTokenList.prototype.add = function() {
        var args = Array.from(arguments);
        var filtered = args.filter(function(cls) {
            return typeof cls === 'string' && cls.indexOf('blur') === -1;
        });
        if (filtered.length !== args.length) {
            console.log('阻止添加模糊类: ' + args.join(', '));
        }
        if (filtered.length > 0) {
            return originalClassListAdd.apply(this, filtered);
        }
    };
    
    // 拦截可能设置blur的CSS属性
    var originalSetProperty = CSSStyleDeclaration.prototype.setProperty;
    CSSStyleDeclaration.prototype.setProperty = function(propertyName, value, priority) {
        if (propertyName && (
            propertyName.indexOf('filter') !== -1 || 
            propertyName.indexOf('backdrop-filter') !== -1 || 
            value && value.indexOf('blur') !== -1)) {
            console.log('阻止设置模糊CSS属性: ' + propertyName + '=' + value);
            return;
        }
        return originalSetProperty.call(this, propertyName, value, priority);
    };
    
    // 直接清除CSS变量
    document.documentElement.style.setProperty('--blur-value', '0px', 'important');
    document.documentElement.style.setProperty('--filter-blur', 'none', 'important');
    
    console.log('已安装全局模糊拦截器');
})();

// 最简单的侧边栏生成函数 - 完全兼容原网站逻辑
function update_sidebar_menu() {
    console.log('生成侧边栏菜单...');
    
    try {
        // 获取所有书签分类区域
        var bookmarkSections = $('.bookmark-section');
        var sidebarMenuList = $('.sidebar-menu-inner ul');
        
        // 确保菜单列表存在
        if (!sidebarMenuList.length) {
            console.error('找不到侧边栏菜单列表元素');
            return;
        }
        
        // 清空现有菜单内容
        sidebarMenuList.empty();
        
        // 计数检测
        var count = 0;
        
        // 对于每个书签分类区域，添加一个菜单项到侧边栏
        bookmarkSections.each(function() {
            try {
                var sectionTitle = $(this).find('h4').text().trim();
                
                // 重要修改：使用与页面结构匹配的ID获取方式
                // 页面上每个section的ID是在h4下的i标签中定义的
                var iconElement = $(this).find('h4 i');
                var sectionId = iconElement.attr('id');
                
                if (!sectionId) {
                    console.warn('跳过没有ID的分类:', sectionTitle);
                    return;
                }
                
                // 创建与原网站兼容的菜单项，使用最基础的HTML结构
                var menuItem = $('<li class="sidebar-item"></li>');
                
                // 核心修改：添加内部span，并直接使用HTML模式创建链接，确保与原站点生成的结构完全相同
                menuItem.html('<a href="#' + sectionId + '" class="smooth">' + sectionTitle + '</a>');
                
                // 添加到侧边栏
                sidebarMenuList.append(menuItem);
                count++;
            } catch (err) {
                console.error('生成菜单项时出错:', err);
            }
        });
        
        console.log('成功生成侧边栏菜单项: ' + count + '个');
        
        // 确保侧边栏显示
        $('#sidebar').addClass('show');

        // 侧边栏菜单项点击时强力清除模糊效果
        sidebarMenuList.off('click.sidebar').on('click.sidebar', 'a', function(e) {
            e.preventDefault(); // 阻止默认行为，自行处理导航
            
            // 获取目标锚点
            var target = $(this).attr('href');
            
            // 移除自定义遮罩和模态类
            $('.io-bomb-overlay').each(function(){
                $(this).closest('.io-bomb').remove();
            });
            // 移除Bootstrap的modal遮罩
            $('.modal-backdrop').remove();
            // 关闭所有Bootstrap modal
            $('.modal.show').modal('hide');
            $('body').removeClass('modal-open');
            
            // 强力清除模糊效果
            clearAllBlurEffectsImmediate();
            
            // 延迟设置窗口位置，确保在清除模糊后进行导航
            setTimeout(function() {
                window.location.hash = target.substring(1);
                clearAllBlurEffectsImmediate();
            }, 10);
            
            // 额外的延迟清除尝试
            setTimeout(clearAllBlurEffectsImmediate, 100);
            setTimeout(clearAllBlurEffectsImmediate, 300);
            
            return false; // 阻止事件传播
        });
        
        // 确保侧边栏菜单打开时也清除模糊
        $('#sidebar-menu-toggle').off('click.clearbur').on('click.clearblur', function() {
            setTimeout(clearAllBlurEffectsImmediate, 10);
            setTimeout(clearAllBlurEffectsImmediate, 100);
        });
    } catch (err) {
        console.error('更新侧边栏菜单时出错:', err);
    }
}

// 全局变量 - 强力清除模糊效果的函数
function clearAllBlurEffectsImmediate() {
    // 1. 移除所有常见的blur相关类
    $('html, body, .page-container, .main-content, .grid-bg, .big-header-banner, .header-big, #content, #sidebar, *').removeClass('blur blur-layer');
    
    // 2. 直接清除主要容器上的filter和backdrop-filter样式
    $('html, body, .page-container, .main-content, .grid-bg, .big-header-banner, .header-big, #content, #sidebar, div, *').css({
        'filter': 'none',
        'backdrop-filter': 'none',
        '-webkit-backdrop-filter': 'none'
    });
    
    // 3. 查找并清理所有包含blur的内联样式
    $('[style*="blur"]').each(function(){
        var style = $(this).attr('style') || '';
        style = style.replace(/filter\s*:\s*blur\([^)]*\)\s*;?/g, '')
               .replace(/backdrop-filter\s*:\s*blur\([^)]*\)\s*;?/g, '')
               .replace(/-webkit-backdrop-filter\s*:\s*blur\([^)]*\)\s*;?/g, '');
        $(this).attr('style', style);
    });
    
    // 4. 移除模态状态
    if (!$('.modal:visible').length) {
        $('body').removeClass('modal-open');
        $('.modal-backdrop').remove();
    }
    
    // 5. 移除可能的自定义标记类
    $('.io-grey-mode, .io-black-mode').removeClass('modal-is-open has-blur');
    
    // 6. 直接通过CSS变量设置
    document.documentElement.style.setProperty('--blur-value', '0px', 'important');
    document.documentElement.style.setProperty('--filter-blur', 'none', 'important');
    document.documentElement.style.setProperty('--backdrop-blur', 'none', 'important');
    document.documentElement.style.setProperty('--webkit-backdrop-blur', 'none', 'important');
}

// 初始化函数 - 只处理侧边栏
function initSidebar() {
    try {
        console.log('初始化侧边栏...');
        
        // 立即清除模糊
        clearAllBlurEffectsImmediate();
        
        // 重要：查找并替换网站原有的可能导致模糊的函数
        if (typeof window.jQuery !== 'undefined') {
            // 尝试覆盖原网站的一些可能导致模糊的函数
            if (typeof $.fn.modal === 'function') {
                var originalModal = $.fn.modal;
                $.fn.modal = function(action) {
                    var result = originalModal.apply(this, arguments);
                    // 在任何模态操作后清除模糊
                    setTimeout(clearAllBlurEffectsImmediate, 10);
                    setTimeout(clearAllBlurEffectsImmediate, 100);
                    return result;
                };
            }
        }
        
        // 更新侧边栏菜单
        update_sidebar_menu();
        
        // 移除可能存在的"清除模糊"按钮
        $('#fix-blur-button').remove();
        
        // 全局点击事件监听
        $(document).off('click.clearblur').on('click.clearblur', function(e) {
            // 点击任意地方都尝试清除模糊（除非是在模态框内点击）
            if (!$(e.target).closest('.modal-dialog').length) {
                clearAllBlurEffectsImmediate();
            }
        });
        
        // 添加额外的事件监听，确保在任何可能导致模糊的操作后清除模糊
        $(window).off('focus.clearblur').on('focus.clearblur', clearAllBlurEffectsImmediate);
        $(window).off('scroll.clearblur').on('scroll.clearblur', clearAllBlurEffectsImmediate);
        $(window).off('resize.clearblur').on('resize.clearblur', clearAllBlurEffectsImmediate);
        $(document).off('mousemove.clearblur').on('mousemove.clearblur', function() {
            // 减少鼠标移动时的频繁调用
            if (!window._blurClearMouseTimeout) {
                window._blurClearMouseTimeout = setTimeout(function() {
                    clearAllBlurEffectsImmediate();
                    window._blurClearMouseTimeout = null;
                }, 100);
            }
        });
        
        // 添加更多事件监听器
        $(window).off('load.clearblur').on('load.clearblur', clearAllBlurEffectsImmediate);
        $(document).off('DOMContentLoaded.clearblur').on('DOMContentLoaded.clearblur', clearAllBlurEffectsImmediate);
        
        // 监听hash变化，确保在内部导航时也清除模糊
        $(window).off('hashchange.clearblur').on('hashchange.clearblur', function() {
            clearAllBlurEffectsImmediate();
            setTimeout(clearAllBlurEffectsImmediate, 100);
        });
        
        // 观察DOM变化，当有新元素添加时清除模糊
        if (typeof MutationObserver !== 'undefined') {
            if (window._blurClearObserver) {
                window._blurClearObserver.disconnect();
            }
            window._blurClearObserver = new MutationObserver(function(mutations) {
                // 只在有新元素添加时尝试清除模糊
                var shouldClear = false;
                for (var i = 0; i < mutations.length; i++) {
                    if (mutations[i].addedNodes.length > 0) {
                        shouldClear = true;
                        break;
                    }
                }
                if (shouldClear) {
                    clearAllBlurEffectsImmediate();
                }
            });
            window._blurClearObserver.observe(document.body, { 
                childList: true, 
                subtree: true 
            });
        }
        
        // 页面加载后立即清除模糊
        clearAllBlurEffectsImmediate();
        
        // 定时清除模糊，可以应对延迟加载或动态变化的情况
        var clearBlurIntervals = [10, 50, 100, 300, 500, 1000, 2000, 3000];
        clearBlurIntervals.forEach(function(interval) {
            setTimeout(clearAllBlurEffectsImmediate, interval);
        });
        
        // 初始化周期性监测与清除
        setInterval(clearAllBlurEffectsImmediate, 2000);
    } catch (err) {
        console.error('侧边栏初始化失败:', err);
    }
}

// 页面加载完成后执行初始化，同时尝试在更早阶段执行
(function() {
    // 尝试尽早清除模糊
    clearAllBlurEffectsImmediate();
    
    // 尝试在不同阶段初始化
    var initSidebarIfReady = function() {
        if (document.readyState === 'interactive' || document.readyState === 'complete') {
            initSidebar();
            clearAllBlurEffectsImmediate();
        }
    };
    
    // 立即尝试执行
    initSidebarIfReady();
    
    // 在DOM内容加载完成时执行
    document.addEventListener('DOMContentLoaded', function() {
        initSidebar();
        clearAllBlurEffectsImmediate();
    });
    
    // 确保在jQuery ready时执行
    if (typeof jQuery !== 'undefined') {
        jQuery(document).ready(function() {
            console.log('jQuery加载完成，准备初始化侧边栏...');
            initSidebar();
            clearAllBlurEffectsImmediate();
        });
    }
    
    // 页面完全加载后再执行一次
    window.addEventListener('load', function() {
        initSidebar();
        clearAllBlurEffectsImmediate();
        
        // 额外的延迟初始化，确保在页面完全加载后再次尝试
        setTimeout(initSidebar, 500);
        setTimeout(clearAllBlurEffectsImmediate, 1000);
    });
})(); 