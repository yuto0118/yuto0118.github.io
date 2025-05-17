//关键词sug
var hotList = 0;
var bookmarkResults = []; // 存储书签搜索结果
var thisSearch = 'https://www.baidu.com/s?wd='; // 默认使用百度搜索

$(function() {
    // 页面加载完成后初始化
    initBookmarkSearch();
    
    // 搜索按钮点击事件
    $('#search-btn, #modal-search-btn').click(function() {
        var isModalSearch = $(this).attr('id') === 'modal-search-btn';
        var searchText = isModalSearch ? $('#modal-search-text') : $('#search-text');
        var keywords = searchText.val().trim();
        
        if (keywords) {
            // 如果有书签匹配结果，直接跳转到第一个结果
            if (bookmarkResults.length > 0) {
                window.location.href = bookmarkResults[0].url;
                return;
            }
        }
        // 如果无匹配结果，保留默认行为
    });
    
    // 当输入框内容变化时搜索书签
    $('#search-text, #modal-search-text').keyup(function() {
        var keywords = $(this).val().trim();
        var isModalSearch = $(this).attr('id') === 'modal-search-text';
        var wordContainer = isModalSearch ? $('#modal-word') : $('#word');
        
        if (keywords === '') { 
            // 如果输入框为空，则清空搜索结果
            wordContainer.empty();
            bookmarkResults = [];
            return;
        }
        
        // 搜索书签
        bookmarkResults = searchBookmarks(keywords);
        
        // 清空之前的搜索结果
        wordContainer.empty();
        
        if (bookmarkResults.length > 0) {
            // 显示匹配的书签结果
            bookmarkResults.forEach(function(result, index) {
                if (index < 5) { // 最多显示5个结果
                    var newElement = $('<li class="mb-1"><a href="' + result.url + '"><i class="fa fa-bookmark text-info mr-2"></i>' + result.title + '</a></li>');
                    wordContainer.append(newElement);
                }
            });
        } else {
            // 没有书签匹配，显示提示
            var noResultElement = $('<li class="mb-1"><i class="fa fa-info-circle mr-2"></i>没有匹配的书签</li>');
            wordContainer.append(noResultElement);
        }
    });
    
    // 按回车键触发搜索
    $('#search-text, #modal-search-text').keypress(function(e) {
        if (e.which == 13) {
            var keywords = $(this).val().trim();
            if (keywords) {
                // 如果有书签匹配结果，直接跳转到第一个结果
                if (bookmarkResults.length > 0) {
                    window.location.href = bookmarkResults[0].url;
                    return false;
                }
            }
            // 如果无匹配结果，保留默认行为
        }
    });
    
    // 点击搜索结果外的区域时关闭搜索结果
    $(document).on('click', function(e) {
        var target = $(e.target);
        if (!target.is('#search-text') && !target.is('#word') && !target.closest('#word').length &&
            !target.is('#modal-search-text') && !target.is('#modal-word') && !target.closest('#modal-word').length) {
            $('#word, #modal-word').empty();
        }
    });
});

// 初始化书签搜索功能
function initBookmarkSearch() {
    try {
        console.log('初始化书签搜索功能...');
        // 预先加载所有书签
        getAllBookmarks();
    } catch (err) {
        console.error('初始化书签搜索失败:', err);
    }
}

// 获取所有书签
function getAllBookmarks() {
    try {
        var allBookmarks = [];
        
        // 遍历所有书签链接
        $('.bookmark-link').each(function() {
            var title = $(this).data('original-title') || $(this).find('strong').text().trim();
            var url = $(this).attr('href') || $(this).data('url');
            var category = $(this).closest('.row').prev('.bookmark-section').find('h4').text().trim();
            
            if (title && url) {
                allBookmarks.push({
                    title: title,
                    url: url,
                    category: category
                });
            }
        });
        
        // 存储所有书签
        window.allBookmarks = allBookmarks;
        console.log('加载书签完成，共', allBookmarks.length, '个书签');
        
        // 更新搜索框提示文字
        $('#search-text, #modal-search-text').attr('placeholder', '搜索书签内容 (' + allBookmarks.length + '个)');
    } catch (err) {
        console.error('获取书签失败:', err);
    }
}

// 搜索书签
function searchBookmarks(keywords) {
    try {
        if (!keywords || !window.allBookmarks) return [];
        
        var results = [];
        var lowerKeywords = keywords.toLowerCase();
        
        // 在所有书签中搜索匹配的结果
        window.allBookmarks.forEach(function(bookmark) {
            if (bookmark.title.toLowerCase().indexOf(lowerKeywords) > -1 || 
                bookmark.url.toLowerCase().indexOf(lowerKeywords) > -1 ||
                (bookmark.category && bookmark.category.toLowerCase().indexOf(lowerKeywords) > -1)) {
                results.push(bookmark);
            }
        });
        
        return results;
    } catch (err) {
        console.error('搜索书签失败:', err);
        return [];
    }
}

