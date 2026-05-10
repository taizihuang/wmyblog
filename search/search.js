var t2s;
var s2t;

var cat_dict = {
    "正文": 1,
    "后注": 1,
    "访谈": 1,
    "问答": 1,
    "仅回复": 0,
};

var tag_cat_dict = {
    "region1": ["中国", "中国香港", "中国台湾", "美国", "俄罗斯", "欧洲"],
    "region2": ["法国", "英国", "德国", "日本", "乌克兰", "其他地区"],
    "stem1": ["基础科研", "应用技术", "工业"],
    "stem2": ["能源", "气候", "生物", "医学", "其他理工"],
    "focus": ["学术管理", "量子技术", "核聚变", "高能物理"],
    "social1": ["金融", "经济", "政治", "外交", "宣传"],
    "social2": ["历史", "教育", "宗教", "其他社科"],
    "social3": ["哲学", "艺术", "文化", "人生态度"],
    "military": ["军事战略", "军事装备", "军事战术", "其他军事"],
    "special1": ["战略", "管理", "逻辑", "其他", "empty"],
    "special2": ["问答1000", "prognosis", "prescription"],
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
        cat_label[0].style["margin-bottom"] = "10px";
        cat_label[0].style["text-align"] = "center";
        if (cat_dict[key] == 1) {
            cat_label[0].style.backgroundColor = color_on;
        } else {
            cat_label[0].style.backgroundColor = color_off;
        }
    }
    for (var key in tag_dict) {
        var tag_label = $('label#'+key+'-label');
        tag_label.text(key);
        tag_label[0].style["margin-top"] = "3px";
        tag_label[0].style["margin-right"] = "10px";
        tag_label[0].style["text-align"] = "center";
        if (tag_dict[key] == 1) {
            tag_label[0].style.backgroundColor = color_on;
        } else {
            tag_label[0].style.backgroundColor = color_off;
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
    if (cat_dict["问答"] > 0 | cat_dict["仅回复"] > 0) {
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

function filterKeyword(item, keywords) {
    var title = item.title.trim().toLowerCase();
    var content = item.content.trim().replace(/<[^>]+>/g, "").toLowerCase();
    var matched = true;

    keywords.forEach(function(keyword, i) {
        match_title_t = title.match(s2t(keyword));
        match_title_s = title.match(t2s(keyword));
        match_content_t = content.match(s2t(keyword));
        match_content_s = content.match(t2s(keyword));
        if (match_title_t == null 
            && match_title_s == null
            && match_content_t == null
            && match_content_s == null
        ) {
            matched = false;
        }
    });
    return matched
}

function formatKeyword(item, i, keywords, type) {
    var id = item.id;
    var title = item.title;
    var date = item.date;
    var tag = item.tag;
    var md5 = item.md5;
    var content = item.content.trim().replace(/<[^>]+>/g, "").toLowerCase();

    var content_str = "";
    var match_content = "";

    var new_keywords = [];
    for (var j = 0; j < keywords.length; j++) {
        if (keywords[j] != '') {
            new_keywords.push(t2s(keywords[j]));
            new_keywords.push(s2t(keywords[j]));
        }
    }

    var first_occur = -1;
    keywords.forEach(function(keyword, i) {
        match_content_s = content.match(t2s(keyword));
        match_content_t = content.match(s2t(keyword));
        if (match_content_s == null) {
            if (match_content_t == null) {
                index_content = 0;
            } else {
                index_content = match_content_t.index;
            }
        } else {
            index_content = match_content_s.index;
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
        var len = content.length - start;
        if (len > 300) {
            len = 300;
        }
        match_content = content.substr(start, len);
        new_keywords.forEach(function(keyword) {
            var regS = new RegExp("("+keyword+")", "gi");
            match_content = match_content.replace(regS, '<b class="search-keyword">$1</b>');
        });
    }

    content_str += "<ul class='article-result-item'><div class='LI'><div class='USER'>"
    content_str += `<a href='../html/${id}.html#${md5}' target='_blank' class='search-result-title'>`
    content_str += `${type} ${i+1}. ${title}</a>`;
    content_str += `<div class='TIME'>${date}</div></div>`;
    content_str += `<span class='tag'><input type='search' value=${tag} data-md5=${md5} onkeydown='enter(event,$(this))'></span></div>`;
    content_str += `<p class="search-result">${match_content}...</p></ul>`;
    tag.split('/').forEach(tagCount);
    return content_str
}

function searchContent(type_dict) {
    var $input = $('#search-input')
    var $content_li = $(type_dict["li"])
    var $content_count = $(type_dict["count"])

    var tag_list = [];

    for (var key in tag_dict) {
        if (tag_dict[key] == 1) {
            tag_list.push(key);
        }
    }

    $.ajax({
        url: search_dir + `/${type_dict["type"]}.json`,
        method: 'GET',
        dataType: 'json',
        headers: {
            "accept": "application/json",
            // "Access-Control-Allow-Origin": "*"
        },
        beforeSend: function() {
            $content_count.html(`<div id="load"> ${type_dict["type_str"]} loading...</div>`);
        },
        complete: function() {
            $("#load").remove();
        },
        success: function(jsonResponse) {
            var jsonData = JSON.parse(JSON.stringify(jsonResponse));
            var keywords = $input.val().trim().toLowerCase().split(/[\s]+/);
            var data = jsonData[type_dict["type"]].filter(item => filterDate(item, start_date, end_date));
            data = data.filter(item => filterTag(item, tag_list));
            data = data.filter(item => filterKeyword(item, keywords));

            var str_list = data.map((item, idx) => formatKeyword(item, idx, keywords, type_dict["type_str"]));
            var content_count = str_list.length; 
            var content_str = str_list.join("");

            $content_li.html(content_str);
            var anchor = type_dict["li"].replace(".", "").toLowerCase();
            $content_count.html(`<a href="#${anchor}">搜索到 ${content_count} 条${type_dict["type_str"]}</a>`);
            formatCount();
        }
    });
}


function searchArticle() {
    var type_dict = {
        "li": ".POST_LI",
        "count": ".post_count",
        "type": "article",
        "type_str": "正文"
    };
    searchContent(type_dict);
}

function searchAnnotation() {
    var type_dict = {
        "li": ".ANNOTATION_LI",
        "count": ".annotation_count",
        "type": "annotation",
        "type_str": "后注"
    };
    searchContent(type_dict);
}

function searchTranscript() {
    var type_dict = {
        "li": ".TRANSCRIPT_LI",
        "count": ".transcript_count",
        "type": "transcript",
        "type_str": "访谈章节"
    };
    searchContent(type_dict);
}

function filterKeywordComment(item, tag_list, keywords) {
    var comment = item.comment.trim().toLowerCase();
    var reply   = item.reply.replace(/<[^>]+>/g, "").trim().toLowerCase();
    var nickname= item.nickname.toLowerCase();
    var md5     = item.md5;
    var deleted = item.deleted;
    var matched = true;

    if ((tag_list.length == 0) && (keywords[0] == "") && (end_date == "2027-01-01")) {
        matched = false;
    }

    keywords.forEach(function(keyword, i) {
        match_comment_s = comment.match(t2s(keyword));
        match_reply_s = reply.match(t2s(keyword));
        match_nickname_s = nickname.match(t2s(keyword))
        match_comment_t = comment.match(s2t(keyword));
        match_reply_t = reply.match(s2t(keyword));
        match_nickname_t = nickname.match(s2t(keyword))
        match_md5 = md5.match(keyword)
        if (cat_dict["仅回复"] == 0) {
            if (
                match_comment_t == null 
                && match_reply_t == null 
                && match_nickname_t == null 
                && match_comment_s == null 
                && match_reply_s == null 
                && match_nickname_s == null 
                && match_md5 == null
            ) {
                matched = false;
            }
        } else {
            if (
                match_reply_t == null 
                && match_reply_s == null 
            ) {
                matched = false;
            }
        }
    });

    if (reply.length == 0) {
        matched = false;
    }
    return matched
}

function formatKeywordComment(item, i, keywords) {
    var id = item.id;
    var md5 = item.md5;
    var nickname = item.nickname;
    var comment = item.comment;
    var reply = item.reply;
    var date = item.date;
    var tag = item.tag;
    var reply_str = "";

    var new_keywords = [];
    for (var j = 0; j < keywords.length; j++) {
        if (keywords[j] != '') {
            new_keywords.push(t2s(keywords[j]));
            new_keywords.push(s2t(keywords[j]));
        }
    }

    new_keywords.forEach(function(keyword) {
        if (keyword != ""){
            var regS = new RegExp("("+keyword+")", "gi");
            comment = comment.replace(regS, "<b class=\"search-keyword\">$1</b>");
            reply = reply.replace(regS, "<b class=\"search-keyword\">$1</b>");
        }
    });
    comment = comment.replace('\n','<br><br>');
    reply = reply.replace("\n", '<br><br>');
    reply_str += "<div class='LI'><div class='USER'>";
    reply_str += `<span class='NAME'>问答 ${i+1}. `;
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
    s2t = OpenCC.Converter({from: 'cn', to: 'tw'});
    t2s = OpenCC.Converter({from: 'tw', to: 'cn'});
};