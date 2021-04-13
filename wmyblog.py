import requests,os,re,math,json,time
from bs4 import BeautifulSoup
import pandas as pd
from mako.template import Template
import numpy as np

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

def updateArticle(articleFile = 'article_full.pkl'):
    
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
    
    # save dataframe file eas json
    article_li = []
    for i in df_article.index:
        id = df_article.id[i]
        title = df_article.title[i]
        art_date = df_article.art_date[i]
        post = df_article.post[i]
        article_li.append([id,title,art_date,post])
    with open(articleFile+'.json','wb') as data:
        for i in range(len(article_li)):
            article_li[i][2] = str(article_li[i][2])
            s = json.dumps(article_li[i]) + "\n"
            data.write(s.encode('utf-8'))
    return

def updateComment(commentFile="comment_full.pkl"):
    
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
    
    #save dataframe as json file
    comment_li = []
    for i in df_comment.index:
        id = df_comment.id[i]
        nickname = df_comment.nickname[i]
        comment = df_comment.comment[i]
        comment_date = df_comment.date[i]
        reply = df_comment.reply[i]
        comment_li.append([id,nickname,comment_date,comment,reply])
    with open(commentFile+'.json','wb') as data:
        for i in range(len(comment_li)):
            comment_li[i][2] = str(comment_li[i][2])
            s = json.dumps(comment_li[i]) + "\n"
            data.write(s.encode('utf-8'))
    return

def genHTML(articleFile="article_full.pkl",commentFile="comment_full.pkl"):
    HTML = Template("""<!DOCTYPE html><html><head><meta content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no" name=viewport><meta charset=utf-8>
<link rel="stylesheet" href="./init.css">
<title>${title}</title>
</head>
<body><div class="BODY">
<div class="BACK"><a href="../index.html">返回索引页</a></div>
<h1>${title}</h1>
<p class="DATE">${date}</p>
<div class="POST">${post}</div>
<div class="REPLY_LI">
<h2>${len(reply_li)} 条留言</h2>
%for say, reply, user, time in reply_li:
<div class="LI">
<div class="USER"><span class="NAME">${user}</span><div class="TIME">${time}</div></div>
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
    # save html
    df_article = pd.read_pickle(articleFile)
    df_comment = pd.read_pickle(commentFile)
    for i in df_article.index:
        id = df_article.id[i]
        title = df_article.title[i]
        art_date = df_article.art_date[i]
        post = df_article.post[i]
        reply_li = []
        df_comment_id = df_comment.loc[df_comment.id==id].sort_values(by='date')
        for j in df_comment_id.index:
            comment = df_comment_id.comment[j]
            if comment:
                reply = df_comment_id.reply[j].replace("\n\n","\n")
                nickname = df_comment_id.nickname[j]
                comment_date = df_comment_id.date[j]
                reply_li.append((comment,reply,nickname,comment_date))
        with open('./html/'+id+'.html','w') as f:
            f.write(HTML.render(title=title,date=art_date,post=post,reply_li=reply_li))
    return

def genINDEX(articleFile="article_full.pkl"):
    INDEX = Template("""
    <!DOCTYPE html><html><head><meta content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no" name=viewport><meta charset=utf-8>
    <link rel="stylesheet" href="/html/init.css">
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
    <title>王孟源的博客</title>
    </head>
    <body><div class="BODY">
    <h1>王孟源的博客</h1>
    <ul class="LI">
    %for url, name, time in li:
    <li><a class="title" href="html/${url}.html">[${time}]&emsp;${name}</a></li>
    %endfor
    </ul>
    </div></body></html>
    """)
    li = []
    df_article = pd.read_pickle(articleFile)
    for i in df_article.index:
        art_id = df_article.id[i]
        title = df_article.title[i]
        art_date = str(df_article.art_date[i]).split(' ')[0]
        li.append((art_id,title,art_date))
    with open("index.html", "w") as index:
            index.write(INDEX.render(li=li))
    return
