function search() {
    var $input = $('#search-input')
    var $post = $('.POST_LI')
    var $comment = $('.REPLY_LI')
    var $post_count = $('.post_count')
    var $comment_count = $('.comment_count')

    $.ajax({
        url: 'wmyblog.json',
        dataType: 'json',
        headers: {
            "accept": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        beforeSend: function() {
            $post_count.html('<div id="load"> loading </div>');
        },
        complete: function() {
            $("#load").remove();
        },
        success: function(jsonResponse) {
            var jsonData = JSON.parse(JSON.stringify(jsonResponse));
            var articleData = jsonData.article.map(function(item) {
                return {
                    title: item.title,
                    content: item.post,
                    url: item.id,
                    date: item.date
                };
            });
            var commentData = jsonData.comment.map(function(item) {
                return {
                    id: item.id,
                    title: item.title,
                    nickname: item.nickname,
                    date: item.date,
                    comment: item.comment,
                    reply: item.reply
                }
            })
            var post_count = 0
            var comment_count = 0
            var post_str = ''
            var reply_str = ''
            var keywords = $input.val().trim().toLowerCase().split(/[\s\-]+/);
            var dict = { "and": 1, "or": -1, "not": 0 };
            var keyword_list = [];
            var logic_list = [];

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
                        post_str += "<li class='article-result-item'><a href='../html/" + data_url + ".html' target='_blank' class='search-result-title'>" + data_title + "</a>";
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
            $post.html(post_str)
            $post_count.html("搜索到 " + post_count + " 篇文章")

            commentData.forEach(function(data) {
                var comment = data.comment.trim().replace(/<[^>]+>/g, "").toLowerCase();
                var reply = data.reply.trim().replace(/<[^>]+>/g, "").toLowerCase();
                var comment_url = data.id;
                var nickname = data.nickname;
                var title = data.title;
                var date = data.date
                var uuid = date.replace(/[- :]/g, '').substr(2, 10)
                var index_comment = -1;
                var index_reply = -1;
                var isMatch = true;
                keywords.forEach(function(keyword, i) {
                    index_comment = comment.indexOf(keyword);
                    index_reply = reply.indexOf(keyword);
                    index_nickname = nickname.toLowerCase().indexOf(keyword)
                    if (index_comment < 0 && index_reply < 0 && index_nickname < 0) {
                        isMatch = false;
                    }
                });
                if (keywords[0]) {
                    if (isMatch) {
                        keywords.forEach(function(keyword) {
                            var regS = new RegExp(keyword, "gi");
                            comment = comment.replace(regS, "<b class=\"search-keyword\">" + keyword + "</b>");
                            reply = reply.replace(regS, "<b class=\"search-keyword\">" + keyword + "</b>");
                        });
                        reply_str += "<div class='LI'><div class='USER'><span class='NAME'>" + title + " | <a href='../html/" + comment_url + ".html#" + uuid + "' target='_blank'>" + nickname + "</a></span><div class='TIME'>" + date + "</div></div>";
                        reply_str += "<div class='SAY'>" + comment + "</div>"
                        reply_str += "<div class='REPLY'>" + reply + "</div>"
                        comment_count += 1
                    }
                }
                reply_str += "</div></div>";

            });
            $comment.html(reply_str);
            $comment_count.html("搜索到 " + comment_count + " 条问答");

        }
    });
}