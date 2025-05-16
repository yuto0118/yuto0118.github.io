//关键词sug
var hotList = 0;
var bookmarkResults = []; // 存储书签搜索结果

$(function() {
    // 页面加载完成后初始化
    initBookmarkSearch();
    
    // 搜索按钮点击事件
    $('#search-btn, #modal-search-btn').click(function() {
        var isModalSearch = $(this).attr('id') === 'modal-search-btn';
        var searchText = isModalSearch ? $('#modal-search-text') : $('#search-text');
        var keywords = searchText.val();
        
        if (keywords) {
            window.open(thisSearch + keywords);
        }
    });
    
    //当键盘键被松开时发送Ajax获取数据
    $('#search-text, #modal-search-text').keyup(function() {
        var keywords = $(this).val();
        var isModalSearch = $(this).attr('id') === 'modal-search-text';
        var wordContainer = isModalSearch ? $('#modal-word') : $('#word');
        
        if (keywords == '') { 
            wordContainer.hide(); 
            return 
        };
        
        // 搜索书签
        searchBookmarks(keywords);
        
        // 获取百度搜索建议
        $.ajax({
            url: 'https://suggestion.baidu.com/su?wd=' + keywords,
            dataType: 'jsonp',
            jsonp: 'cb', //回调函数的参数名(键值)key
            // jsonpCallback: 'fun', //回调函数名(值) value
            beforeSend: function() {
                // wordContainer.append('<li>正在加载。。。</li>');
            },
            success: function(res) {
                wordContainer.empty().show();
                hotList = res.s.length + bookmarkResults.length;
                
                // 添加书签结果
                if (bookmarkResults.length > 0) {
                    for (var i = 0; i < bookmarkResults.length; i++) {
                        var item = bookmarkResults[i];
                        wordContainer.append('<li class="bookmark-result"><span class="bookmark-icon"><i class="fas fa-bookmark"></i></span>' + item.title + '<small class="text-muted ml-1">' + item.folder + '</small></li>');
                    }
                    
                    // 添加分隔线
                    if (res.s.length > 0) {
                        wordContainer.append('<li class="divider"></li>');
                    }
                    
                    // 添加点击事件
                    $(".bookmark-result").click(function() {
                        var index = $(this).index();
                        var bookmark = bookmarkResults[index];
                        window.location.href = bookmark.url;
                    });
                }
                
                // 添加百度搜索建议
                if (res.s.length) {
                    for (var i = 0; i < res.s.length; i++) {
                        var indexNum = i + bookmarkResults.length;
                        if (i === res.s.length - 1) {
                            wordContainer.append('<li id="lastHot"><span>' + (indexNum + 1) + "</span>" + res.s[i] + "</li>");
                        } else {
                            wordContainer.append("<li><span>" + (indexNum + 1) + "</span>" + res.s[i] + "</li>");
                        }
                        var suggestionItems = wordContainer.find("li").not('.bookmark-result').not('.divider');
                        suggestionItems.eq(i).click(function() {
                            var searchText = isModalSearch ? $('#modal-search-text') : $('#search-text');
                            searchText.val(this.childNodes[1].nodeValue);
                            window.open(thisSearch + this.childNodes[1].nodeValue);
                            wordContainer.css('display', 'none')
                        });
                        
                        if (i === 0) {
                            suggestionItems.eq(i).css({
                                "border-top": "none"
                            });
                            wordContainer.find("ul span").eq(i).css({
                                "color": "#fff",
                                "background": "#f54545"
                            })
                        } else if (i === 1) {
                            wordContainer.find("ul span").eq(i).css({
                                "color": "#fff",
                                "background": "#ff8547"
                            })
                        } else if (i === 2) {
                            wordContainer.find("ul span").eq(i).css({
                                "color": "#fff",
                                "background": "#ffac38"
                            })
                        }
                    }
                }

                // 没有结果时隐藏
                if (res.s.length === 0 && bookmarkResults.length === 0) {
                    wordContainer.css("display", "none");
                } else {
                    wordContainer.css("display", "block");
                }
            },
            error: function() {
                wordContainer.empty().show();
                // 即使百度API失败，仍然显示书签结果
                if (bookmarkResults.length > 0) {
                    for (var i = 0; i < bookmarkResults.length; i++) {
                        var item = bookmarkResults[i];
                        wordContainer.append('<li class="bookmark-result"><span class="bookmark-icon"><i class="fas fa-bookmark"></i></span>' + item.title + '<small class="text-muted ml-1">' + item.folder + '</small></li>');
                    }
                    
                    // 添加点击事件
                    $(".bookmark-result").click(function() {
                        var index = $(this).index();
                        var bookmark = bookmarkResults[index];
                        window.location.href = bookmark.url;
                    });
                    wordContainer.css("display", "block");
                } else {
                    wordContainer.hide();
                }
            }
        })
    })

    //点击搜索数据复制给搜索框
    $(document).on('click', '#word li, #modal-word li', function() {
        if ($(this).hasClass('bookmark-result') || $(this).hasClass('divider')) {
            return;
        }
        var word = $(this).text().replace(/^[0-9]/, '');
        var isModalSearch = $(this).closest('#modal-word').length > 0;
        var searchText = isModalSearch ? $('#modal-search-text') : $('#search-text');
        var wordContainer = isModalSearch ? $('#modal-word') : $('#word');
        
        searchText.val(word);
        wordContainer.empty();
        wordContainer.hide();
        //$("form").submit();
        $('.submit').trigger('click');//触发搜索事件
    })
    
    //点击其他区域关闭搜索结果
    $(document).on('click', '.io-grey-mode', function(e) {
        if (!$(e.target).closest('#word, #modal-word, #search-text, #modal-search-text').length) {
            $('#word, #modal-word').empty().hide();
        }
    })

})

// 初始化书签搜索功能
function initBookmarkSearch() {
    console.log('初始化书签搜索功能...');
    
    // 检查页面中是否有书签链接
    var bookmarkCount = $('a.bookmark-link').length;
    console.log('找到 ' + bookmarkCount + ' 个书签链接');
    
    // 设置搜索框提示文字
    if (bookmarkCount > 0) {
        $('#search-text, #modal-search-text').attr('placeholder', '支持书签内容搜索');
    }
    
    // 按回车键触发搜索
    $('#search-text, #modal-search-text').keypress(function(e) {
        if (e.which == 13) {
            var keywords = $(this).val();
            if (keywords) {
                window.open(thisSearch + keywords);
            }
            return false;
        }
    });
}

// 搜索书签功能
function searchBookmarks(keyword) {
    if (!keyword || keyword.length < 2) {
        bookmarkResults = [];
        return;
    }
    
    keyword = keyword.toLowerCase();
    bookmarkResults = [];
    
    // 搜索所有书签链接
    $('a.bookmark-link').each(function() {
        var title = $(this).text().toLowerCase();
        var url = $(this).attr('href').toLowerCase();
        var folder = $(this).closest('.bookmark-section').find('h4').text().trim();
        
        if (title.includes(keyword) || url.includes(keyword)) {
            // 限制结果数量为5个
            if (bookmarkResults.length < 5) {
                bookmarkResults.push({
                    title: $(this).text(),
                    url: $(this).attr('href'),
                    folder: folder
                });
            }
        }
    });
}
