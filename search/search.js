var tag_list = [];
var tag_dict = {};
var last_tag_dict = {};
var is_online = true;
var search_dir = "https://cdn.jsdelivr.net/gh/taizihuang/wmyblog/search";

function enter_search(e) {
    if (e.keyCode == 13) {
        search();
    }
};

function search() {
    searchArticle();
    searchTranscript();
    searchComment();
}

function tag_count(el) {
    if (el != '') {
        if (el in tag_dict){
            tag_dict[el] += 1;
        } else {
            tag_dict[el] = 1;
        }
    }
}

function tagList(id) {
    const index = tag_list.indexOf(id);
    if (index > -1) {
        tag_list.splice(index, 1);
        $('label#'+id+'-label')[0].style.backgroundColor = 'rgb(169, 182, 231)';
    } else {
        tag_list.push(id);
        $('label#'+id+'-label')[0].style.backgroundColor = 'rgb(61, 151, 186)';
    }
}

function searchURL() {
    if (is_online) {
        is_online = false;
        search_dir = ".";
        $('label#offline-label')[0].style.backgroundColor = 'rgb(61, 151, 186)';
    } else {
        is_online = true;
        search_dir = "https://cdn.jsdelivr.net/gh/taizihuang/wmyblog/search"
        $('label#offline-label')[0].style.backgroundColor = 'rgb(169, 182, 231)';
    }
}

function searchArticle() {
    var $input = $('#search-input')
    var $post = $('.POST_LI')
    var $post_count = $('.post_count')

    $.ajax({
        url: search_dir + "/article.json",
        method: 'GET',
        dataType: 'json',
        headers: {
            "accept": "application/json",
            // "Access-Control-Allow-Origin": "*"
        },
        beforeSend: function() {
            $post_count.html('<div id="load"> loading </div>');
        },
        complete: function() {
            $("#load").remove();
        },
        success: function(jsonResponse) {
            var jsonData = JSON.parse(JSON.stringify(jsonResponse));
            if (tag_list.length == 0) {
                var articleData = jsonData.article.map(function(item) {
                    return {
                        title: item.title,
                        content: item.post,
                        url: item.id,
                        date: item.date
                    };
                });
                var post_count = 0;
                var post_str = '';
                var keywords = $input.val().trim().toLowerCase().split(/[\s\-]+/);
            
                articleData.forEach(function(data) {
                    var data_title = data.title.toLowerCase();
                    var data_content = data.content.trim().replace(/<[^>]+>/g, "").toLowerCase();
                    var data_url = data.url;
                    var index_title = -1;
                    var isMatch = true;
                    var first_occur = -1;
                    keywords.forEach(function(keyword, i) {
                        index_title = data_title.indexOf(keyword);
                        index_content = data_content.indexOf(keyword);
                        if (index_title < 0 && index_content < 0) {
                            isMatch = false;
                        } else {
                            if (index_content < 0) {
                                index_content = 0;
                            }
                            if (i == 0) {
                                first_occur = index_content;
                            }
                        }
                    })
                    if (keywords[0]) {
                        if (isMatch) {
                            post_str += "<li class='article-result-item'><a href='../html/" + data_url + ".html' target='_blank' class='search-result-title'>" + post_count + ". " + data_title + "</a>";
                            var content = data.content.trim().replace(/<[^>]+>/g, "");
                            if (first_occur >= 0) {
                                var start = first_occur - 100;
                                if (start < 0) {
                                    start = 0;
                                }
                                var len = content.length - start;
                                //if (start == 0) {
                                //end = 100;
                                //}
                                if (len > 300) {
                                    len = 300;
                                }
                                var match_content = content.substr(start, len);
                                keywords.forEach(function(keyword) {
                                    var regS = new RegExp(keyword, "gi");
                                    match_content = match_content.replace(regS, "<b class=\"search-keyword\">" + keyword + "</b>");
                                });
                                post_str += "<p class=\"search-result\">" + match_content + "...</p>"
                                post_count += 1;
                            }
                            post_str += "</li>";
                        }
                    }
                });
                $post.html(post_str);
                $post_count.html('<a href="#post_li"> 搜索到 ' + post_count + " 篇文章</a>");
            } else {
                $post.html("");
                $post_count.html("");
            }
        }
    });
}

function searchTranscript() {
    var $input = $('#search-input')
    var $script = $('.TRANSCRIPT_LI')
    var $script_count = $('.transcript_count')
    $.ajax({
        url: search_dir + "/transcript.json",
        method: 'GET',
        dataType: 'json',
        headers: {
            "accept": "application/json",
            // "Access-Control-Allow-Origin": "*"
        },
        beforeSend: function() {
            // $post_count.html('<div id="load"> loading </div>');
        },
        complete: function() {
            $("#load").remove();
        },
        success: function(jsonResponse) {
            var jsonData = JSON.parse(JSON.stringify(jsonResponse));
            if (tag_list.length == 0) {
                var scriptData = jsonData.transcript.map(function(item) {
                    return {
                        key: item.key,
                        title: item.title,
                        content: item.content,
                    }
                })
                var script_count = 0;
                var script_str = '';
                var keywords = $input.val().trim().toLowerCase().split(/[\s\-]+/);
            
                scriptData.forEach(function(data) {
                    var data_title = data.title;
                    console.log(data.key);
                    var data_content = data.content.trim().replace(/<[^>]+>/g, "").toLowerCase();
                    var data_url = "../html/"+ data.key + ".html";
                    var index_title = -1;
                    var isMatch = true;
                    var first_occurence = -1;
                    keywords.forEach(function(keyword, i) {
                        index_title = data_title.indexOf(keyword);
                        index_content = data_content.indexOf(keyword);
                        if (index_title < 0 && index_content < 0) {
                            isMatch = false;
                        } else {
                            if (index_content < 0) {
                                index_content = 0;
                            }
                            if (i == 0) {
                                first_occurence = index_content;
                            }
                        }
                    })
                    if (keywords[0]) {
                        if (isMatch) {
                            script_str += '<li class="article-result-item"><a href="' + data_url + '" target="_blank" class="search-result-title">' + script_count + ". " + data_title + "</a>";
                            var content = data.content.trim().replace(/<[^>]+>/g, "");
                            if (first_occurence >= 0) {
                                var start = first_occurence - 100;
                                if (start < 0) {
                                    start = 0;
                                }
                                var len = content.length - start;
                                if (len > 300) {
                                    len = 300
                                }
                                var match_content = content.substr(start, len);
                                keywords.forEach(function(keyword) {
                                    var regS = new RegExp(keyword, "gi");
                                    match_content = match_content.replace(regS, '<b class="search-keyword">'+keyword+"</b>");
                                });
                                script_str += '<p class="search-result">' + match_content + "...</p>";
                                script_count += 1;
                            }
                            script_str += "</li>";
                        }
                    }
            });
        $script.html(script_str);
        $script_count.html('<a href="#transcript_li">搜索到 ' + script_count + " 篇访谈</a>");
        } else {
            $script.html("");
            $script_count.html("");
        };
        }
    });
}

function searchComment() {
    var $input = $('#search-input')
    var $comment = $('.REPLY_LI')
    var $comment_count = $('.comment_count')
    last_tag_dict = {...tag_dict};
    tag_dict = {};

    $.ajax({
        url: search_dir + "/comment.json",
        method: 'GET',
        dataType: 'json',
        headers: {
            "accept": "application/json",
            // "Access-Control-Allow-Origin": "*"
        },
        beforeSend: function() {
            // $post_count.html('<div id="load"> loading </div>');
        },
        complete: function() {
            $("#load").remove();
        },
        success: function(jsonResponse) {
            var jsonData = JSON.parse(JSON.stringify(jsonResponse));
            var commentData = jsonData.comment.map(function(item) {
                var isMatch = true;
                var index_tag = -1;
                tag_list.forEach(function(t,i){
                    index_tag = item.tag.split('/').indexOf(t);
                    if (index_tag < 0) {
                        isMatch = false;
                    }
                });
                if (isMatch) {
                return {
                    id: item.id,
                    title: item.title,
                    nickname: item.nickname,
                    date: item.date,
                    comment: item.comment,
                    reply: item.reply,
                    tag: item.tag,
                    md5: item.md5,
                }
            } else {
                return {}
            };}).filter(function(el){return Object.keys(el).length != 0});
            var comment_count = 0
            var reply_str = ''
            var keywords = $input.val().trim().toLowerCase().split(/[\s\-]+/);

            commentData.forEach(function(data) {
                var comment = data.comment.trim().toLowerCase();
                var reply = data.reply.trim().toLowerCase();
                var comment_url = data.id;
                var nickname = data.nickname;
                var tag = data.tag.split('/').join('/');
                var md5 = data.md5;
                var title = data.title;
                var date = data.date
                var index_comment = -1;
                var index_reply = -1;
                var index_nickname = -1;
                var index_md5 = -1;
                var isMatch = true;

                keywords.forEach(function(keyword, i) {
                    index_comment = comment.indexOf(keyword);
                    index_reply = reply.indexOf(keyword);
                    index_nickname = nickname.toLowerCase().indexOf(keyword)
                    index_md5 = md5.indexOf(keyword)
                    if (index_comment < 0 && index_reply < 0 && index_nickname < 0 && index_md5) {
                        isMatch = false;
                    }
                });

                if (tag_list != [] || keywords[0]) {
                    if (isMatch) {
                        keywords.forEach(function(keyword) {
                            if (keyword != ""){
                                var regS = new RegExp(keyword, "gi");
                                comment = comment.replace(regS, "<b class=\"search-keyword\">" + keyword + "</b>");
                                reply = reply.replace(regS, "<b class=\"search-keyword\">" + keyword + "</b>");
                            }
                        });
                        reply_str += "<div class='LI'><div class='USER'>";
                        reply_str += "<span class='NAME'>" + comment_count + "." + title + " | <a href='../html/" + comment_url + ".html#" + md5 + "' target='_blank'>" + nickname + "</a></span>";
                        reply_str += "<div class='TIME'>" + date + "</div></div>";
                        reply_str += "<span class='tag'><input type='search' value=" + tag + " data-md5=" + md5 + " onkeydown='enter(event,$(this))'></span>"
                        reply_str += "<div class='SAY'>" + comment.replace('\n','<br><br>') + "</div>"
                        reply_str += "<div class='REPLY'>" + reply.replace('\n','<br><br>') + "</div>"
                        comment_count += 1
                        tag.split('/').forEach(tag_count);
                    }
                }
                reply_str += "</div></div>";
            });
            $comment.html(reply_str);
            $comment_count.html('<a href="#reply_li">搜索到 ' + comment_count + " 条问答</a>");
            for (var key in last_tag_dict) {
                var value = tag_dict[key]
                var tag_label = $('label#'+key+'-label');
                if (tag_label.length > 0){
                    tag_label.text(key);
                }
            }
            for (var key in tag_dict) {
                var value = tag_dict[key]
                var tag_label = $('label#'+key+'-label');

                if (tag_label.length > 0){
                    tag_label.text(key+"["+String(value)+"]");
                }
            }


        }
    });
}