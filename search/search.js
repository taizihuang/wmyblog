var cat_dict = {
    "正文": 1,
    "后注": 1,
    "访谈": 1,
    "问答": 1,
};
var tag_cat_dict = {
    "special": ["问答1000", "prognosis", "prescription", "其他", "empty"],
    "stem1": ["基础科研", "应用技术", "学术管理", "能源", "工业", "生物", "医学"],
    "stem2": ["量子技术", "核聚变", "高能物理", "其他理工"],
    "social1": ["金融", "经济", "战略", "政治", "外交", "宣传"],
    "social2": ["历史", "教育", "宗教", "其他社科"],
    "social3": ["逻辑", "哲学", "艺术", "文化", "人生态度"],
    "military": ["军事战略", "军事装备", "军事战术", "其他军事"],
    "region1": ["中国", "中国香港", "中国台湾", "美国", "俄罗斯", "欧洲"],
    "region2": ["法国", "英国", "德国", "日本", "乌克兰", "其他地区"],
}
var tag_dict = {};
var count_dict = {};
var start_date = $("#startDate").val();
var end_date = $("#endDate").val();
var is_online = true;
var search_dir = "https://cdn.jsdmirror.com/gh/taizihuang/wmyblog/search";
var color_off = 'rgb(169, 182, 231)';
var color_on = 'rgb(61, 151, 186)';


function updateDate() {
    start_date = $("#startDate").val();
    end_date = $("#endDate").val();
}

function buildTag() {
    var cat_str = "";
    for (var key in tag_cat_dict) {
        cat_str += `<div class="${key}">`;
        for (var idx in tag_cat_dict[key]) {
            var tag = tag_cat_dict[key][idx];
            cat_str += `<label for="${tag}" id="${tag}-label">${tag}</label>`;
            cat_str += `<input type="checkbox" id="${tag}" onclick="switchTag(this.id)">`;
            tag_dict[tag] = 0;
        }
        cat_str += "</div>";
    }
    $(".category").after(cat_str);
    // $("<div>").appendTo($cat).addClass('tag_list').html(cat_str);
    // $cat.after(cat_str);
}

function formatLabel() {
    for (var key in cat_dict) {
        var cat_label = $('label#'+key+'-label');
        cat_label.text(key);
        if (cat_dict[key] == 1) {
            cat_label[0].style.backgroundColor = color_on;
            cat_label[0].style["margin-bottom"] = "20px";
        } else {
            cat_label[0].style.backgroundColor = color_off;
            cat_label[0].style["margin-bottom"] = "20px";
        }
    }
    for (var key in tag_dict) {
        var tag_label = $('label#'+key+'-label');
        tag_label.text(key);
        if (tag_dict[key] == 1) {
            tag_label[0].style.backgroundColor = color_on;
            tag_label[0].style["margin-right"] = "10px";
        } else {
            tag_label[0].style.backgroundColor = color_off;
            tag_label[0].style["margin-right"] = "10px";
        }
    }
}

function formatInfo() {
    var class_list = [".post_count",
                    ".annotation_count",
                    ".transcript_count",
                    ".comment_count",
                    ".POST_LI",
                    ".ANNOTATION_LI",
                    ".TRANSCRIPT_LI",
                    ".REPLY_LI"
                ]
    class_list.forEach(function(item){$(item).html("")});
}

function formatCount() {
    for (var key in count_dict) {
        var value = count_dict[key]
        var tag_label = $('label#'+key+'-label');
        if (value > 0){
            tag_label.text(key+"["+String(value)+"]");
        }
    }
}

function switchCat(id) {
    cat_dict[id] = Math.abs(cat_dict[id]-1)
    formatLabel();
}

function switchTag(id) {
    tag_dict[id] = Math.abs(tag_dict[id]-1)
    formatLabel();
}

function enter_search(e) {
    if (e.keyCode == 13) {
        search();
    }
};

function search() {
    count_dict = {};

    formatInfo();
    formatLabel();

    if (cat_dict["正文"] > 0) {
        searchArticle();
    }
    if (cat_dict["后注"] > 0) {
        searchAnnotation();
    }
    if (cat_dict["访谈"] > 0) {
        searchTranscript();
    }
    if (cat_dict["问答"] > 0) {
        searchComment();
    }

}

function tagCount(el) {
    if (el != '') {
        if (el in count_dict){
            count_dict[el] += 1;
        } else {
            count_dict[el] = 1;
        }
    }
}

function searchURL() {
    if (is_online) {
        is_online = false;
        search_dir = ".";
        $('label#offline-label')[0].style.backgroundColor = color_on; 
    } else {
        is_online = true;
        search_dir = "https://cdn.jsdelivr.net/gh/taizihuang/wmyblog/search"
        $('label#offline-label')[0].style.backgroundColor = color_off;
    }
}

function filterDate(item, start_date, end_date) {
    var matched = true;
    var date = item.date;
    date = date.substr(0, 10);
    date = date.replace("/", "-");

    if ((date < start_date) || (date > end_date)) {
        matched = false
    }
    return matched
}

function filterTag(item, tag_list) {
    var matched = true;
    var index_tag = -1;
    tag_list.forEach(function(t,i){
        index_tag = item.tag.split('/').indexOf(t);
        if (index_tag < 0) {
            matched = false;
        }
    });
    return matched
}

function filterKeywordArticle(item, keywords) {
    var title = item.title.trim().toLowerCase();
    var post = item.post.trim().replace(/<[^>]+>/g, "").toLowerCase();
    var matched = true;

    keywords.forEach(function(keyword, i) {
        match_title = title.match(keyword);
        match_post = post.match(keyword);
        if (match_title == null 
            && match_post == null) {
            matched = false;
        }
    });
    return matched
}

function filterKeywordAnnotation(item, keywords) {
    var title = item.title.trim().toLowerCase();
    var note = item.note.trim().replace(/<[^>]+>/g, "").toLowerCase();
    var matched = true;

    keywords.forEach(function(keyword, i) {
        match_title = title.match(keyword);
        match_note = note.match(keyword);
        if (match_title == null 
            && match_note == null) {
            matched = false;
        }
    });
    return matched
}

function filterKeywordTranscript(item, keywords) {
    var title = item.title.trim().toLowerCase();
    var script = item.content.trim().replace(/<[^>]+>/g, "").toLowerCase();
    var matched = true;

    keywords.forEach(function(keyword, i) {
        match_title = title.match(keyword);
        match_script = script.match(keyword);
        if (match_title == null 
            && match_script == null) {
            matched = false;
        }
    });
    return matched
}

function formatKeywordArticle(item, i, keywords) {
    var id = item.id;
    var title = item.title;
    var date = item.date;
    var tag = item.tag;
    var md5 = `${id}_article`;
    var post = item.post.trim().replace(/<[^>]+>/g, "").toLowerCase();

    var post_str = "";
    var match_content = "";

    var first_occur = -1;
    keywords.forEach(function(keyword, i) {
        match_content = post.match(keyword);
        if (match_content == null) {
            index_content = 0;
        } else {
            index_content = match_content.index;
        }
        if (i == 0) {
            first_occur = index_content;
        }
    })
    if (first_occur >= 0) {
        var start = first_occur - 100;
        if (start < 0) {
            start = 0;
        }
        var len = post.length - start;
        if (len > 300) {
            len = 300;
        }
        match_content = post.substr(start, len);
        keywords.forEach(function(keyword) {
            var regS = new RegExp("("+keyword+")", "gi");
            match_content = match_content.replace(regS, '<b class="search-keyword">$1</b>');
        });
    }

    post_str += "<li class='article-result-item'><div class='LI'><div class='USER'>"
    post_str += `<a href='../html/${id}.html' target='_blank' class='search-result-title'>`
    post_str += `正文 ${i+1}. ${title}</a>`;
    post_str += `<div class='TIME'>${date}</div></div>`;
    post_str += `<span class='tag'><input type='search' value=${tag} data-md5=${md5} onkeydown='enter(event,$(this))'></span></div>`;
    post_str += `<p class="search-result">${match_content}...</p></li>`;
    tag.split('/').forEach(tagCount);
    return post_str
}

function formatKeywordAnnotation(item, i, keywords) {
    var id = item.id;
    var title = item.title;
    var date = item.date;
    var tag = item.tag;
    var md5 = item.md5;
    var note = item.note.trim().replace(/<[^>]+>/g, "").toLowerCase();

    var note_str = "";
    var match_content = "";

    var first_occur = -1;
    keywords.forEach(function(keyword, i) {
        match_content = note.match(keyword);
        if (match_content == null) {
            index_content = 0;
        } else {
            index_content = match_content.index;
        }
        if (i == 0) {
            first_occur = index_content;
        }
    })
    if (first_occur >= 0) {
        var start = first_occur - 100;
        if (start < 0) {
            start = 0;
        }
        var len = note.length - start;
        if (len > 300) {
            len = 300;
        }
        match_content = note.substr(start, len);
        keywords.forEach(function(keyword) {
            var regS = new RegExp("("+keyword+")", "gi");
            match_content = match_content.replace(regS, '<b class="search-keyword">$1</b>');
        });
    }

    note_str += "<li class='article-result-item'><div class='LI'><div class='USER'>"
    note_str += `<a href='../html/${id}.html#${md5}' target='_blank' class='search-result-title'>`
    note_str += `后注 ${i+1}. ${title}</a>`;
    note_str += `<div class='TIME'>${date}</div></div>`;
    note_str += `<span class='tag'><input type='search' value=${tag} data-md5=${md5} onkeydown='enter(event,$(this))'></span></div>`;
    note_str += `<p class="search-result">${match_content}...</p></li>`;
    tag.split('/').forEach(tagCount);
    return note_str
}

function formatKeywordTranscript(item, i, keywords) {
    var key = item.key;
    var title = item.title;
    var date = item.date;
    var tag = item.tag;
    var md5 = `${key}_${title}`;
    md5 = md5.replace(" ", "");
    var script = item.content.trim().replace(/<[^>]+>/g, "").toLowerCase();

    var script_str = "";
    var match_content = "";

    var first_occur = -1;
    keywords.forEach(function(keyword, i) {
        match_content = script.match(keyword);
        if (match_content == null) {
            index_content = 0;
        } else {
            index_content = match_content.index;
        }
        if (i == 0) {
            first_occur = index_content;
        }
    })
    if (first_occur >= 0) {
        var start = first_occur - 100;
        if (start < 0) {
            start = 0;
        }
        var len = script.length - start;
        if (len > 300) {
            len = 300;
        }
        match_content = script.substr(start, len);
        keywords.forEach(function(keyword) {
            var regS = new RegExp("("+keyword+")", "gi");
            match_content = match_content.replace(regS, '<b class="search-keyword">$1</b>');
        });
    }

    script_str += "<li class='article-result-item'><div class='LI'><div class='USER'>"
    script_str += `<a href='../html/${key}.html#${title}' target='_blank' class='search-result-title'>`
    script_str += `访谈 ${i+1}. ${title}</a>`;
    script_str += `<div class='TIME'>${date}</div></div>`;
    script_str += `<span class='tag'><input type='search' value=${tag} data-md5=${md5} onkeydown='enter(event,$(this))'></span></div>`;
    script_str += `<p class="search-result">${match_content}...</p></li>`;
    tag.split('/').forEach(tagCount);
    return script_str
}

function searchArticle() {
    var $input = $('#search-input')
    var $post = $('.POST_LI')
    var $post_count = $('.post_count')

    var tag_list = [];

    for (var key in tag_dict) {
        if (tag_dict[key] == 1) {
            tag_list.push(key);
        }
    }

    $.ajax({
        url: search_dir + "/article.json",
        method: 'GET',
        dataType: 'json',
        headers: {
            "accept": "application/json",
            // "Access-Control-Allow-Origin": "*"
        },
        beforeSend: function() {
            $post_count.html('<div id="load"> 文章 loading...</div>');
        },
        complete: function() {
            $("#load").remove();
        },
        success: function(jsonResponse) {
            var jsonData = JSON.parse(JSON.stringify(jsonResponse));
            var keywords = $input.val().trim().toLowerCase().split(/[\s]+/);
            var articleData = jsonData.article.filter(item => filterDate(item, start_date, end_date));
            articleData = articleData.filter(item => filterTag(item, tag_list));
            articleData = articleData.filter(item => filterKeywordArticle(item, keywords));

            var post_str_list = articleData.map((item, idx) => formatKeywordArticle(item, idx, keywords));
            var post_count = post_str_list.length; 
            var post_str = post_str_list.join("");

            $post.html(post_str);
            $post_count.html(`<a href="#post_li">搜索到 ${post_count} 条文章</a>`);
            formatCount();
        }
    });

}

function searchAnnotation() {
    var $input = $('#search-input')
    var $note = $('.ANNOTATION_LI')
    var $note_count = $('.annotation_count')

    var tag_list = [];

    for (var key in tag_dict) {
        if (tag_dict[key] == 1) {
            tag_list.push(key);
        }
    }

    $.ajax({
        url: search_dir + "/annotation.json",
        method: 'GET',
        dataType: 'json',
        headers: {
            "accept": "application/json",
            // "Access-Control-Allow-Origin": "*"
        },
        beforeSend: function() {
            $note_count.html('<div id="load"> 后注 loading...</div>');
        },
        complete: function() {
            $("#load").remove();
        },
        success: function(jsonResponse) {
            var jsonData = JSON.parse(JSON.stringify(jsonResponse));
            var keywords = $input.val().trim().toLowerCase().split(/[\s]+/);
            var noteData = jsonData.annotation.filter(item => filterDate(item, start_date, end_date));
            noteData = noteData.filter(item => filterTag(item, tag_list));
            noteData = noteData.filter(item => filterKeywordAnnotation(item, keywords));

            var note_str_list = noteData.map((item, idx) => formatKeywordAnnotation(item, idx, keywords));
            var note_count = note_str_list.length; 
            var note_str = note_str_list.join("");

            $note.html(note_str);
            $note_count.html(`<a href="#annotation_li">搜索到 ${note_count} 条后注</a>`);
            formatCount();
        }
    });
}

function searchTranscript() {
    var $input = $('#search-input')
    var $script = $('.TRANSCRIPT_LI')
    var $script_count = $('.transcript_count')

    var tag_list = [];

    for (var key in tag_dict) {
        if (tag_dict[key] == 1) {
            tag_list.push(key);
        }
    }

    $.ajax({
        url: search_dir + "/transcript.json",
        method: 'GET',
        dataType: 'json',
        headers: {
            "accept": "application/json",
            // "Access-Control-Allow-Origin": "*"
        },
        beforeSend: function() {
            $script_count.html('<div id="load"> 后注 loading...</div>');
        },
        complete: function() {
            $("#load").remove();
        },
        success: function(jsonResponse) {
            var jsonData = JSON.parse(JSON.stringify(jsonResponse));
            var keywords = $input.val().trim().toLowerCase().split(/[\s]+/);
            var scriptData = jsonData.transcript.filter(item => filterDate(item, start_date, end_date));
            scriptData = scriptData.filter(item => filterTag(item, tag_list));
            scriptData = scriptData.filter(item => filterKeywordTranscript(item, keywords));

            var script_str_list = scriptData.map((item, idx) => formatKeywordTranscript(item, idx, keywords));
            var script_count = script_str_list.length; 
            var script_str = script_str_list.join("");

            $script.html(script_str);
            $script_count.html(`<a href="#transcript_li">搜索到 ${script_count} 条访谈章节</a>`);
            formatCount();
        }
    });

}

function filterKeywordComment(item, tag_list, keywords) {
    var comment = item.comment.trim().toLowerCase();
    var reply   = item.reply.trim().toLowerCase();
    var nickname= item.nickname.toLowerCase();
    var md5     = item.md5;
    var matched = true;

    if ((tag_list.length == 0) && (keywords[0] == "") && (end_date == "2027-01-01")) {
        matched = false;
    }

    keywords.forEach(function(keyword, i) {
        match_comment = comment.match(keyword);
        match_reply = reply.match(keyword);
        match_nickname = nickname.match(keyword)
        match_md5 = md5.match(keyword)
        if (match_comment == null 
            && match_reply == null 
            && match_nickname == null 
            && match_md5 == null) {
            matched = false;
        }
    });
    return matched
}

function formatKeywordComment(item, i, keywords) {
    var id = item.id;
    var title = item.title;
    var md5 = item.md5;
    var nickname = item.nickname;
    var comment = item.comment;
    var reply = item.reply;
    var date = item.date;
    var tag = item.tag;
    var reply_str = "";

    keywords.forEach(function(keyword) {
        if (keyword != ""){
            var regS = new RegExp("("+keyword+")", "gi");
            comment = comment.replace(regS, "<b class=\"search-keyword\">$1</b>");
            reply = reply.replace(regS, "<b class=\"search-keyword\">$1</b>");
        }
    });
    comment = comment.replace('\n','<br><br>');
    reply = reply.replace("\n", '<br><br>');
    reply_str += "<div class='LI'><div class='USER'>";
    reply_str += `<span class='NAME'>问答 ${i+1}. ${title} | `;
    reply_str += `<a href='../html/${id}.html#${md5}' target='_blank'>${nickname}</a></span>`;
    reply_str += `<div class='TIME'>${date}</div></div>`;
    reply_str += `<span class='tag'><input type='search' value=${tag} data-md5=${md5} onkeydown='enter(event,$(this))'></span>`;
    reply_str += `<div class='SAY'>${comment}</div>`;
    reply_str += `<div class='REPLY'>${reply}</div></div>`;
    tag.split('/').forEach(tagCount);
    return reply_str
}

function searchComment() {
    var $input = $('#search-input')
    var $comment = $('.REPLY_LI')
    var $comment_count = $('.comment_count')

    var tag_list = [];

    for (var key in tag_dict) {
        if (tag_dict[key] == 1) {
            tag_list.push(key);
        }
    }

    $.ajax({
        url: search_dir + "/comment.json",
        method: 'GET',
        dataType: 'json',
        headers: {
            "accept": "application/json",
            // "Access-Control-Allow-Origin": "*"
        },
        beforeSend: function() {
            $comment_count.html('<div id="load"> 问答 loading...</div>');
        },
        complete: function() {
            $("#load").remove();
        },
        success: function(jsonResponse) {
            var jsonData = JSON.parse(JSON.stringify(jsonResponse));
            var keywords = $input.val().trim().toLowerCase().split(/[\s]+/);
            var commentData = jsonData.comment.filter(item => filterDate(item, start_date, end_date));
            commentData = commentData.filter(item => filterTag(item, tag_list));
            commentData = commentData.filter(item => filterKeywordComment(item, tag_list, keywords));

            var reply_str_list = commentData.map((item, idx) => formatKeywordComment(item, idx, keywords));
            var comment_count = reply_str_list.length; 
            var reply_str = reply_str_list.join("");
            reply_str += "</div></div>";

            $comment.html(reply_str);
            $comment_count.html(`<a href="#reply_li">搜索到 ${comment_count} 条问答</a>`);
            formatCount();
        }
    });
}

window.onload = function() {
    buildTag();
    formatLabel();
};