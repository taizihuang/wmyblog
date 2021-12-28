import requests,os,re,math,json,time,datetime
from bs4 import BeautifulSoup
import pandas as pd
from mako.template import Template
import numpy as np

def today(timezone='Asia/Shanghai'):
    os.environ['TZ'] = timezone
    time.tzset()
    today = pd.to_datetime(datetime.date.today())
    return today

def getPageLink(n=11):
    '''
    Return (id,title) of the nth page.
    '''
    url = "http://blog.udn.com/blog/article/article_list_head_ajax.jsp?uid=MengyuanWang&pno="
    link = []
    r = requests.get(url+str(n))
    doc = BeautifulSoup(r.content,features="lxml")
    docu = doc.findAll(class_="article_topic")
    for i in docu:
        id = i('a')[0].get('href').replace('http://blog.udn.com/MengyuanWang/','')
        title = i.text.replace('\n','')
        link.append((id,title))
    return link

def getPageLinkAll(n=11):
    '''
    Return Dataframe with columns (id,title) from page 1 to n.
    '''
    url = "http://blog.udn.com/blog/article/article_list_head_ajax.jsp?uid=MengyuanWang&pno="
    id = []
    title = []
    for nPage in range(n):
        r = requests.get(url+str(nPage))
        doc = BeautifulSoup(r.content,features="lxml")
        docu = doc.findAll(class_="article_topic")
        for i in docu:
            id.append(i('a')[0].get('href').replace('http://blog.udn.com/MengyuanWang/',''))
            title.append(i.text.replace('\n',''))
    df_link = pd.DataFrame({"id":id,"title":title})
    return df_link

def fetch(art_id):
    '''
    Fetch article metadata/
    Return (art_id,title,art_date,post)
    '''
    url = "http://blog.udn.com/MengyuanWang/"
    response = requests.get(url+art_id)
    doc = BeautifulSoup(response.content,features="lxml")
    title = doc.find(class_="article_topic").text
    art_date = doc.find(class_="article_datatime").text
    post = doc.find(id="article_show_content")

    #save image
    count = 1
    for i in post.findAll('img'):
        url = i.attrs['src']
        img = requests.get(url).content
        imgfile = "/img/"+art_id+"_"+str(count)
        with open("./html%s" % imgfile, "wb") as f:
            f.write(img)
        i.attrs['src'] = "."+imgfile
        count = count+1

    #convert link
    for i in post.findAll('a',{'href': re.compile("MengyuanWang")}):
        t = i.attrs['href'].split('/')
        i.attrs['href'] = t[-1]+'.html'
    
    return (art_id,title,art_date,post)

def updateArticle(articleFile = './data/article_full.pkl'):
    
    # creat pickle backup file
    df_article_old = pd.read_pickle(articleFile)

    # fetech new article list, merge, remove duplicates, then save as pickle file
    df_article_new = pd.DataFrame(columns=['id','title','art_date','post'])
    df_link = getPageLinkAll()   
    for i in df_link.loc[df_link.id > "108908829"].index:
        (art_id,title,art_date,post) = fetch(df_link.iloc[i].id)
        df_article_new = df_article_new.append({'id':art_id,'title':title,'art_date':art_date,'post':str(post)},ignore_index=True)
        print("Fetching article: "+title)
        time.sleep(1)
    df_article_new.art_date = pd.to_datetime(df_article_new.art_date,format="%Y/%m/%d %H:%M")
    df_article = df_article_new.append(df_article_old,ignore_index=True)
    df_article = df_article.drop_duplicates()
    os.rename(articleFile,articleFile+'.bak')
    df_article.to_pickle(articleFile)
    return

def updateComment(commentFile="./data/comment_full.pkl"):
    
    #create pickle backup file
    df_comment_old = pd.read_pickle(commentFile)
    
    
    # fetch new comment list, merge, remove duplicates, then save as pickle file
    df_comment_new = pd.DataFrame(columns = ['comment','reply','nickname','date','id'])
    for n in range(11):
        link = getPageLink(n)
        for i,j in link:
            (npage,df) = getCommentAll(i)
            print("Fetching "+str(len(df))+ " comments in "+j)
            df_comment_new = pd.concat([df_comment_new,df],ignore_index=True)
            time.sleep(1)
    df_comment = df_comment_new.append(df_comment_old,ignore_index=True)
    df_comment = df_comment.drop_duplicates()
    os.rename(commentFile,commentFile+'.bak')
    df_comment.to_pickle(commentFile)
    return

def exportJSON(articleFile,commentFile,jsonFile):
    df_article = pd.read_pickle(articleFile)
    df_comment = pd.read_pickle(commentFile)

    article_list = []
    title_dict = {}
    for i in df_article.index:
        id = df_article.id[i]
        title = df_article.title[i]
        title_dict[id] = title
        art_date = df_article.art_date[i]
        post = df_article.post[i]
        article_list.append({"id":id,"title":title,"date":art_date.strftime('%Y-%m-%d %H:%M:%S'),"post":post})

    comment_list = []
    for i in df_comment.index:
        id = df_comment.id[i]
        title = title_dict[id]
        nickname = df_comment.nickname[i]
        comment = df_comment.comment[i]
        comment_date = df_comment.date[i]
        reply = df_comment.reply[i]
        if reply:
            comment_list.append({"id":id,"title":title,"nickname":nickname,"date":comment_date.strftime('%Y-%m-%d %H:%M:%S'),"comment":comment,"reply":reply})

    wmy = {"article":article_list,"comment":comment_list}
    with open(jsonFile,'w') as f:
        f.write(json.dumps(wmy))

def updateDaily(latest,articleFile='./data/article_full.pkl',commentFile='./data/comment_full.pkl',jsonFile='./search/wmyblog.json'):
    df_article_old = pd.read_pickle(articleFile)
    df_comment_old = pd.read_pickle(commentFile)
    df_article_new = pd.DataFrame(columns = ['id','title','art_date','post'])
    df_comment_new = pd.DataFrame(columns = ['comment','reply','nickname','date','id'])

    url = "http://blog.udn.com/blog/inc_2011/psn_article_ajax.jsp?uid=MengyuanWang&f_FUN_CODE="

    # update article items
    response = requests.get(url+"new_view")
    doc = BeautifulSoup(response.content,features="lxml")
    docu = doc.findAll(class_="main-title")
    for i in docu:
        art_id = i.attrs['href'].replace('http://blog.udn.com/MengyuanWang/','')
        if not art_id in df_article_old.id.values:
            (art_id,title,art_date,post) = fetch(art_id)
            df_article_new = df_article_new.append({'id':art_id,'title':title,'art_date':art_date,'post':str(post)},ignore_index=True)
            df_article_new.art_date = pd.to_datetime(df_article_new.art_date,format="%Y/%m/%d %H:%M")
            print("Fetching article: "+title)
            time.sleep(1)
    df_article = df_article_new.append(df_article_old,ignore_index=True)
    df_article = df_article.drop_duplicates(subset=['id'],keep='first')
    df_article = df_article.reset_index(drop=True)
    art_list = {}
    for i in df_article.index:
        art_list[df_article.id[i]] = df_article.title[i]
    with open('./data/article_list.json','w') as outfile:
        json.dump(art_list, outfile)

    # update comment items
    response = requests.get(url+"new_rep")
    doc = BeautifulSoup(response.content,features="lxml")
    docu = doc.findAll(class_="main-title")
    dict_reply = {'0':'0'}
    for i in docu:
        art_id = i.attrs['href'].replace('http://blog.udn.com/MengyuanWang/','')
        nPage,df = getComment(art_id)
        if nPage > 1:
            nPage,df1 = getComment(art_id,n=1)
            df = df.append(df1,ignore_index=True)
        df_comment_new = df_comment_new.append(df,ignore_index=True)
        dict_reply[art_id] = i.text
    df_comment = df_comment_new.append(df_comment_old, ignore_index=True)
    df_comment = df_comment.drop_duplicates(subset=['comment'],keep='first')
    df_comment = df_comment.reset_index(drop=True)

    # generate htmls that have new comments
    df_comment_today = df_comment.loc[df_comment.date > latest]
    df_comment_today = df_comment_today.sort_values(by='date',ascending=False)
    with open('./data/article_list.json') as infile:
        dict_reply = json.load(infile)
    genLatestComment(df_comment_today,dict_reply)
    for art_id in df_comment_today.id.unique():
        genHTML(art_id,df_article,df_comment)

    os.rename(commentFile,commentFile+'.bak')
    df_comment.to_pickle(commentFile)
    os.rename(articleFile,articleFile+'.bak')
    df_article.to_pickle(articleFile)

    exportJSON(articleFile,commentFile,jsonFile)
    genINDEX()
    return

def genHTML(art_id,df_article,df_comment):
    
    i = df_article.loc[df_article.id == art_id].index
    title = df_article.title[i[0]]
    art_date = df_article.art_date[i[0]]
    post = df_article.post[i[0]]
    
    reply_li = []
    df_comment_id = df_comment.loc[df_comment.id == art_id].sort_values(by='date')
    for j in df_comment_id.index:
        comment = df_comment_id.comment[j]
        if comment:
            reply = df_comment_id.reply[j].replace("\n\n","\n")
            nickname = df_comment_id.nickname[j]
            comment_date = df_comment_id.date[j]
            uuid = comment_date.strftime('%y%m%d%H%M')
            reply_li.append((uuid,comment,reply,nickname,comment_date))
            
    HTML = Template("""<!DOCTYPE html><html><head>
    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-SN809EL4EQ"></script>
    <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    
    gtag('config', 'G-SN809EL4EQ');
    </script>
    
    <meta content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no" name=viewport><meta charset=utf-8>
    <link rel="stylesheet" href="./init.css">
    <title>${title}</title>
    </head>
    <body><div class="BODY">
    <div class="BACK"><a href="../index.html">返回索引页</a></div>
    <h1>${title}</h1>
    <p class="DATE">${date}</p>
    <h4>原文网址：<a href="http://blog.udn.com/MengyuanWang/${art_id}">http://blog.udn.com/MengyuanWang/${art_id}</a></h4>
    <br><br>
    <div class="POST">${post}</div>
    <div class="REPLY_LI">
    <h2>${len(reply_li)} 条留言</h2>
    %for uuid, say, reply, user, time in reply_li:
    <div class="LI">
    <div class="USER"><span class="NAME" id=${uuid}>${user}</span><div class="TIME">${time}</div></div>
    <div class="SAY">${say}</div>
    %if reply:
    <div class="REPLY">${reply}</div>
    %endif
    </div>
    %endfor
    </div>
    </div>
    <div class="BACK"><a href="../index.html">返回索引页</a></div>
    </body></html>""")
        
    with open('./html/'+art_id+'.html','w') as f:
        f.write(HTML.render(title=title,date=art_date,art_id=art_id,post=post,reply_li=reply_li))
    return

def genHTMLAll(articleFile="./data/article_full.pkl",commentFile="./data/comment_full.pkl"):

    df_article = pd.read_pickle(articleFile)
    df_comment = pd.read_pickle(commentFile)
    
    for art_id in df_article.id:
        genHTML(art_id,df_article,df_comment)
    return

def genINDEX(articleFile='./data/article_full.pkl'):
    df_article = pd.read_pickle(articleFile)
    art_li = []
    for i in df_article.index:
        art_id = df_article.id[i]
        title = df_article.title[i]
        art_date = str(df_article.art_date[i]).split(' ')[0]
        art_li.append((art_id,title,art_date))

    INDEX = Template("""
    <!DOCTYPE html><html><head>
    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-SN809EL4EQ"></script>
    <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    
    gtag('config', 'G-SN809EL4EQ');
    </script>
    <meta content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no" name=viewport><meta charset=utf-8>
    <link rel="stylesheet" href="./html/init.css">
    <style>
    .LI li{
    list-style-type: disc;
    }
    .LI li{
    margin-bottom:8px;
    }
    .LI a{
    text-decoration: none;
    }
    .LI .title{
    color:#000;
    }
    .LI .title:hover{
    color:#f40;
    }
    .LI .date{
    font-size:12px;
    color:#999;
    float:right;
    }
    </style>
    <title>王孟源的博客镜像</title>
    </head>
    <body><div class="BODY">
    <h1>王孟源的博客镜像</h1>
    <h4>博客内容搜索：<a href="https://taizihuang.github.io/wmyblog/search/">https://taizihuang.github.io/wmyblog/search/</a></h4>
    <h4>原网址：<a href="http://blog.udn.com/MengyuanWang/article">http://blog.udn.com/MengyuanWang/article</a></h4>
    <h4>Odd Lots文字稿：<a href="https://taizihuang.github.io/OddLots">https://taizihuang.github.io/OddLots</a></h4>
    <h4>经济学人镜像：<a href="https://taizihuang.github.io/TheEconomist/">https://taizihuang.github.io/TheEconomist/</a></h4>
    <h4>外交杂志镜像：<a href="https://taizihuang.github.io/ForeignAffairs/">https://taizihuang.github.io/ForeignAffairs/</a></h4>
    <h4>外交杂志2000-2020：<a href="https://taizihuang.github.io/ForeignAffairs/archive">https://taizihuang.github.io/ForeignAffairs/archive</a></h4>
    <h4>本镜像数据备份: <a href="https://github.com/taizihuang/wmyblog/archive/refs/heads/main.zip">https://github.com/taizihuang/wmyblog/archive/refs/heads/main.zip</a></4>
    <br><br>
    <ul class="LI">
    <li><a class="title" href="./html/new_comment.html">最新回复</a></li>
    %for url, name, time in art_li:
    <li><a class="title" href="./html/${url}.html">[${time}]&emsp;${name}</a></li>
    %endfor
    </ul>
    </div></body></html>
    """)

    with open("index.html", "w") as index:
        index.write(INDEX.render(art_li=art_li))
    return

def genLatestComment(df_comment_today,dict_reply):
    HTML = Template("""<!DOCTYPE html><html><head>
    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-SN809EL4EQ"></script>
    <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    
    gtag('config', 'G-SN809EL4EQ');
    </script>
    <meta content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no" name=viewport><meta charset=utf-8>
    <link rel="stylesheet" href="./init.css">
    <style>
    .REPLY_LI{
    border-top: none;
    margin-top: 0px;
    padding-top: 0px;
    }
    .LI a{
    text-decoration: none;
    color:#000;
    }
    .LI a:hover{
    color:#f40;
    }
    #LATEST {
    font-family: Rajdhani,PingFang SC;
    font-weight: 200;
    font-size: 32px;
    margin: 28px 0 20px;
    }
    #rss_btn {
    font-family: Arial;
    text-decoration: none;
    font-size: 13px;
    color: #FFF;
    background: #f2853d;
    padding: 1px 5px;
    border: 1px solid #ed6b2a;}
    </style>
    <title>${title}</title>
    </head>
    <body><div class="BODY">
    <div class="BACK"><a href="../index.html">返回索引页</a></div>
    <div id="LATEST">最新回复<span>  <a href="https://taizihuang.github.io/wmyblog/rss.xml" id="rss_btn">RSS</a></span></div>
    <p class="DATE">${date}</p>
    <div class="POST">${post}</div>
    <div class="REPLY_LI">
    <h2>${len(reply_li)} 条留言</h2>
    %for source, id, uuid, say, reply, user, time in reply_li:
    <div class="LI">
    <div class="USER"><span class="NAME">${source} | <a href="./${id}.html#${uuid}">${user}</a></span><div class="TIME">${time}</div></div>
    <div class="SAY">${say}</div>
    %if reply:
    <div class="REPLY">${reply}</div>
    %endif
    </div>
    %endfor
    </div>
    </div>
    <div class="BACK"><a href="../index.html">返回索引页</a></div>
    </body></html>""")

    RSS = Template("""
    <rss xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">
    <channel>
    <title><![CDATA[王孟源有新回复]]></title>
    <atom:link href="https://taizihuang.github.io/wmyblog" rel="self" type="application/rss+xml" />
    <description><![CDATA[王孟源有新回复 (https://github.com/taizihuang/wmyblog)]]></description>
    <generator>Github</generator>
    <webMaster>Taizi Huang</webMaster>
    <language>zh-cn</language>
    <lastBuildDate>${date} +0800</lastBuildDate>
    <ttl>5</ttl>
    %for source, id, uuid, say, reply, user, time in reply_li:
    <item>
    <% say = say.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;') %>
    <% reply = reply.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;') %>
    <title><![CDATA[${source} | ${user}]]></title>
    <description><![CDATA[${say} <br><br>----<br><br>${reply}]]></description>
    <author><![CDATA[王孟源部落格]]></author>
    <pubDate>${time} +0800</pubDate>
    <guid isPermaLink="false">${uuid}</guid>
    <link>https://taizihuang.github.io/wmyblog/html/${id}.html#${uuid}</link>
    </item>
    %endfor
    </channel></rss>
    """)
    reply_li = []
    t = today()
    art_date = datetime.datetime.now().strftime('%m-%d %H:%M')
    for i in df_comment_today.index:
        comment = df_comment_today.comment[i] 
        if comment:
            reply = df_comment_today.reply[i].replace("\n\n","\n")       
            nickname = df_comment_today.nickname[i]
            comment_date = df_comment_today.date[i]
            uuid = comment_date.strftime('%y%m%d%H%M')
            art_id = df_comment_today.id[i]
            source = dict_reply[art_id]
            reply_li.append((source,art_id,uuid,comment,reply,nickname,comment_date))
    with open("./html/new_comment.html", "w") as html:
        html.write(HTML.render(title='最新回复',date=art_date,post='',reply_li=reply_li))
    with open("./rss.xml","w") as rss:
        rss.write(RSS.render(date=art_date,reply_li=reply_li))
    return

def getComment(art_id,n=0):
    '''
    Input: article ID (digits only) & comment page no.
    Return (nPage, df['comment','reply','nickname','date','id']).
    '''
    #art_id = "110576971"
    url = "http://blog.udn.com/blog/article/article_reply_ajax.jsp?uid=MengyuanWang&f_ART_ID="
    response = requests.get(url+art_id+"&pno="+str(n))
    doc = BeautifulSoup(response.content,features="lxml")
    
    #rep_head = re.search('\d+',doc.find(id="response_head").text)
    df = pd.DataFrame(columns = ['comment','reply','nickname','date','id'])
    rep_head = doc.find(id="response_head")    
    if rep_head:
        nComment = int(re.search('\d+',rep_head.text)[0])
        nPage = math.ceil(int(nComment)/10)
        rep = doc.find(id="response_body")
        for i in rep(class_=["prt","icon"]):
            i.extract()
        rep1 = doc.findAll(id=re.compile("rep\d+"))
        for i in range(len(rep1)):
            comment = rep1[i](class_='rp5')[0].text
            nickname = rep1[i](class_='rp2')[0].text.split('\n')[1]
            date = rep1[i](class_='rp4')[0].text
            if rep1[i](class_='rp'):
                reply = "\n"
                for irp in rep1[i].findAll(class_='rp'):
                    reply = reply + irp.text.replace("\r\n","")
                reply.replace("\n\n","\n")
            else:
                reply = "" 
            s = {'comment':comment,'reply':reply,'nickname':nickname,'date':date,'id':art_id}
            df = df.append(s,ignore_index=True)
    else:
        nPage = 0
        df = pd.DataFrame([['','','','',art_id]],columns = ['comment','reply','nickname','date','id'])
    df.date = pd.to_datetime(df.date,format="%Y/%m/%d %H:%M")

    return (nPage,df)

def getCommentAll(art_id):
    '''
    Get all comments for the specified article id
    Return (art_id,title,art_date,post)
    '''
    (nPage, df) = getComment(art_id,0)
    if nPage > 1:
        for i in np.arange(1,nPage):
            (npage, df1) = getComment(art_id,i)
            df = pd.concat([df,df1],ignore_index=True)
    else:
        pass
    return (nPage,df)
