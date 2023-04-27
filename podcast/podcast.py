import json
from mako.template import Template

HTML = Template("""
<!DOCTYPE html>
<html>
<head>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-1F5ZFPC2V2"></script>
<script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());

    gtag('config', 'G-1F5ZFPC2V2');
</script>
<meta content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no" name=viewport><meta charset=utf-8>
    <link href="APlayer.min.css" rel="stylesheet">
    <script src="APlayer.min.js"></script>
    <title>最新访谈</title>
    <style>
        .demo {
            min-width: 360px;
            max-width: 500px;
            margin: 60px auto 10px auto;
            font-size: 1rem;
        }
        
        .demo p {
            padding: 10px 0
        }

        iframe {
            overflow: hidden;
            width: 99%;
            margin-left: 20 !important;
        }
        #rss_btn {
            font-family: Arial;
            text-decoration: none;
            font-size: 13px;
            color: #FFF;
            background: #f2853d;
            padding: 1px 5px;
            border: 1px solid #ed6b2a;
        }
    </style>
    <script>
        var fileLocation = document.getElementsByClassName('aplayer-author')[0];
        var text = fileLocation.textContent
        
        function resizeIframe(obj) {
            obj.style.height = (window.innerHeight - 250) + 'px';
        }

        function changeSrc() {
            var fileLocationNew = document.getElementsByClassName('aplayer-author')[0];
            if (text != fileLocationNew.textContent) {
                var file = fileLocationNew.textContent.substr(3, );
                document.getElementsByClassName('iframe-full-height')[0].src = 'https://taizihuang.github.io/wmyblog/html/' + file.replaceAll('/', '').substring(2, ) + '.html ';
                text = fileLocationNew.textContent;
            };
        }
    </script>
</head>

<body>
<center><h2>最新访谈</h2>&nbsp;<span><a href="http://home.ustc.edu.cn/~tz0920/podcast.xml" id="rss_btn">八方论谈</a>&nbsp;</span><span><a href="http://home.ustc.edu.cn/~tz0920/podcast-long.xml" id="rss_btn">龙行天下</a></span></center>
<center><h4>欢迎读者志愿编辑访谈的文字稿（放在Google Docs，本页面自动同步）</h4></center>
<center>手机可用微信打开本页面，PC端参考<a href="https://www.toimc.com/image-google-ssl-limit/">链接中</a>的方案一</center>
    <div class="demo">
        <div id="player" onclick="changeSrc()">
% for lrc in lrc_list:
            <pre class="aplayer-lrc-content">
            ${lrc}
            </pre>
% endfor
        </div>
    </div>
    <iframe src="https://taizihuang.github.io/wmyblog/html/220621.html" class="iframe-full-height" align="middle" scrolling="yes" margin="auto " frameborder="0" onload="resizeIframe(this)" style="margin-left: 20px;"></iframe>
    <script>
        var ap = new APlayer({
            element: document.getElementById('player'),
            narrow: false,
            listFolded: true,
            listMaxHeight: 90,
            autoplay: false,
            showlrc: true,
            audio: ${audio_list}
        });
        ap.init();
    </script>
</body>
""")
with open('podcast.json','r',encoding='utf8') as f:
    podcast_dict = json.loads(f.read())

lrc_list = []
audio_list = []
for date in podcast_dict.keys():
    name, lrc = podcast_dict[date]
    artist = f'20{date[:2]}/{date[2:4]}/{date[4:6]}'
    audio_list.append({'name':name,'artist':artist,'url':f'http://home.ustc.edu.cn/~tz0920/{date}.mp3','pic':'wmy-podcast.jpg'})
    lrc_list.append(lrc)
with open('index.html','w',encoding='utf8') as f:
    f.write(HTML.render(lrc_list=lrc_list,audio_list=audio_list))