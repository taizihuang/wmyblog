import asyncio,aiohttp,time,math,os,requests,re,datetime,json
from mako.template import Template
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

def pageURL(pno):
    return f"https://blog.udn.com/blog/article/article_list_head_ajax.jsp?uid=MengyuanWang&pno={pno}"

def articleURL(art_id):
    return f"https://blog.udn.com/MengyuanWang/{art_id}"

def commentURL(art_id,pno):
    return f"https://blog.udn.com/blog/article/article_reply_ajax.jsp?uid=MengyuanWang&f_ART_ID={art_id}&pno={pno}"

def getPageNo():
    url = 'https://blog.udn.com/blog/inc_2011/psn_artcate_new_ajax.jsp?uid=MengyuanWang&totalPageNum=1&curPage=0'
    nPerPage = 30
    doc = requests.get(url).content
    nArticle = int(str(doc).split('(')[1].split(')')[0])
    nPage = math.ceil(nArticle / nPerPage)
    return nPage

class Tasker():

    def __init__(self, nTask=5, tSleep=1):
        self.nTask = nTask
        self.tSleep = tSleep

    def run(self, task_pool):

        async def main(tasks):
            outputs = await asyncio.gather(*tasks)
            return outputs

        s = []
        nTask = self.nTask
        tSleep = self.tSleep

        for i in range(int(np.ceil(len(task_pool)/nTask))):
            tasks = task_pool[i*nTask:(i+1)*nTask]
            outputs = asyncio.run(main(tasks))
            for output in outputs:
                s = s + output
            time.sleep(tSleep)

        return s

async def fetch_async(url, func, args, proxy=''):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, proxy=proxy) as response:
            doc = await response.text()
            doc = BeautifulSoup(doc,features="lxml")
            if type(func) == list:
                output = []
                for i in range(len(func)):
                    output = output + func[i](doc,*args[i])
                output = [tuple(output)]
            else:
                output = func(doc,*args)
            return output

def page2artinfo(doc):
    art_info = []
    for topic in doc('dt')[1:]:
        art_id = topic('a')[0].attrs['href'].split('/')[-1]
        art_nComment = int(topic(class_='article_count_comm')[0].contents[1])
        art_pno = math.ceil(art_nComment/10)
        art_info.append({"art_id": art_id, "art_nComment": art_nComment,'art_pno': art_pno})
    return art_info

def page2article(doc, art_id):

    if doc.find(class_="REPLY_LI"):
        doc.find(class_="REPLY_LI").decompose()

    # title
    title = doc.find(class_="article_topic").text

    # date
    if doc.find(class_="DATE"):
        art_date = doc.find(class_="DATE").text
        art_date = art_date.replace('发表日期 : ','').replace('-','/')
        doc.find(class_="DATE").decompose()
    else:
        art_date = doc.find(class_="article_datatime").text
    art_date = pd.to_datetime(art_date,format="%Y/%m/%d %H:%M")

    # post
    post = doc.find(id="article_show_content")

    # convert link
    for i in post.findAll('a',{'href': re.compile("MengyuanWang")}):
        t = i.attrs['href'].split('/')
        i.attrs['href'] = t[-1]+'.html'

    #save image
    for i in post.findAll('img'):
        url = i.attrs['src'].replace('\r','').replace('\n','')
        imgID = url.split('/')[-1]
        imgfile = f"/img/{imgID}"
        if not os.path.exists(f'./html/img/{imgID}'):
            img = requests.get(url).content
            with open("./html%s" % imgfile, "wb") as f:
                f.write(img)
        i.attrs['src'] = "."+imgfile

    df_article = pd.DataFrame(data={'id':art_id,'title':title,'art_date':art_date,'post':str(post)},index=[0])

    return [df_article]

def page2comment(doc, art_id):
    def rep2dict(rep):

        comment = rep(class_='rp5')[0].text.replace('\xa0','').replace("\r\n","").replace('\n','').replace('<br>','')
        nickname = rep(class_='rp2')[0].text.split('\n')[1]
        comment_date = rep(class_='rp4')[0].text

        reply = ''
        if rep(class_='rp'):
            first_reply_date = rep(class_='prt')[-1].text.replace('王孟源 於 ','').replace('回覆','')
            latest_reply_date = first_reply_date
            for p in rep(class_='prt'):
                p.decompose()
            for irp in rep.findAll(class_='rp'):
                reply = reply + irp.text.replace("\r\n","<br>")
            reply.replace("\n\n","\n").replace("\n","<br>")
        else:
            first_reply_date = ''
            latest_reply_date = ''
        return {'comment':comment,'reply':reply,'nickname':nickname,'comment_date':comment_date,'first_reply_date':first_reply_date,'latest_reply_date':latest_reply_date,'id':art_id}

    if  doc.find(id="response_head"):
        reply_list = []
        for rep in doc.findAll(id=re.compile("rep\d+")):
            reply_list.append(rep2dict(rep))
        df_comment = pd.DataFrame(data=reply_list)
    else:
        df_comment = pd.DataFrame(data={'comment':'','reply':'','nickname':'','comment_date':'','first_reply_date':'','latest_reply_date': '','id':art_id},index=[0])

    l = ['comment_date','first_reply_date','latest_reply_date']
    df_comment[l] = df_comment[l].apply(pd.to_datetime,format="%Y/%m/%d %H:%M")
    
    return [df_comment]

def mergeArticle(df_article_new, articleFile='./data/article_full.pkl'):
    df_article = pd.read_pickle(articleFile)
    df_article_new = pd.concat([df_article_new, df_article],ignore_index=True).drop_duplicates(subset='id',keep='first').reset_index(drop=True)

    os.remove(articleFile+'.bak')
    os.rename(articleFile, articleFile+'.bak')
    df_article_new.to_pickle(articleFile)

def mergeComment(df_comment_new,commentFile='./data/comment_full.pkl',tag=''):

    df_comment = pd.read_pickle(commentFile)
    df_comment1 = df_comment.loc[df_comment.comment_date >= min(df_comment_new.comment_date)]
    df_comment2 = df_comment.loc[df_comment.comment_date < min(df_comment_new.comment_date)]

    id_list = df_comment.id.drop_duplicates()
    for id in id_list:
        d_new = df_comment_new.loc[df_comment_new.id == id]
        if not d_new.empty:
            d = df_comment1.loc[(df_comment1.id == id) & (df_comment1.comment_date >= min(d_new.comment_date))]
            if tag == 'full':
                idx0 = (df_comment1.id == id) & (df_comment1.comment_date < min(d_new.comment_date))
                df_comment1.loc[idx0,'comment'] = '<strike>'+df_comment1.loc[idx0,'comment']+'</strike>'
            d_merge = pd.merge(d_new,d,how='outer',on='comment',indicator=True)
            for idx in d_merge.loc[d_merge['_merge'] == 'right_only'].index:
                comment_date = d_merge.loc[idx,'comment_date_y']
                nickname = d_merge.loc[idx,'nickname_y']
                idx1 = (df_comment1.comment_date == comment_date) & (df_comment1.nickname == nickname)
                df_comment1.loc[idx1,'comment'] = '<strike>'+df_comment1.loc[idx1,'comment']+'</strike>'
            for idx in d_merge.loc[d_merge['_merge'] == 'both'].index:
                comment_date = d_merge.loc[idx,'comment_date_y']
                nickname = d_merge.loc[idx,'nickname_y']
                idx1 = (df_comment_new.comment_date == comment_date) & (df_comment_new.nickname == nickname)
                idx2 = (df_comment1.comment_date == comment_date) & (df_comment1.nickname == nickname)
                if ~ df_comment1['first_reply_date'].isnull()[idx2].iloc[0]:
                    df_comment_new.loc[idx1,'first_reply_date'] = df_comment1.loc[idx2,'first_reply_date'].iloc[0]
    df_comment_new = pd.concat([df_comment_new,df_comment1],ignore_index=True).drop_duplicates(subset=['nickname','comment_date'])
    df_comment_new = pd.concat([df_comment_new,df_comment2],ignore_index=True)
    df_comment_new.comment = df_comment_new.comment.str.replace('<strike><strike>','<strike>').str.replace('</strike></strike>','</strike>')
    df_comment_new = df_comment_new.sort_values('comment_date',ascending=False).reset_index(drop=True)
    
    os.remove(commentFile+'.bak')
    os.rename(commentFile,commentFile+'.bak')
    df_comment_new.to_pickle(commentFile)

def updateBlogData(nTask=20, proxy='',articleUpdate=True,commentFullUpdate=False):

    os.environ['http_proxy'] = proxy #代理的端口
    os.environ['https_proxy'] = proxy

    tasker = Tasker(nTask=nTask)

    artInfo_list = tasker.run([fetch_async(pageURL(pno), page2artinfo, (), proxy=proxy) for pno in range(getPageNo())])
    df_artinfo = pd.DataFrame(data=artInfo_list).set_index('art_id')
    print('article info fetched!')

    if articleUpdate:
        page_list = tasker.run([fetch_async(articleURL(art_id), [page2article,page2comment], [(art_id,), (art_id,)], proxy=proxy) for art_id in df_artinfo.index])
        article_list = [page[0] for page in page_list]
        comment_list = [page[1] for page in page_list]
        df_article = pd.concat(article_list,ignore_index=True)
        df_comment = pd.concat(comment_list,ignore_index=True)
        mergeArticle(df_article)
        mergeComment(df_comment)
        print('articles and latest comments updated')
    else:
        pass

    if commentFullUpdate:
        comment_list = tasker.run([fetch_async(commentURL(art_id,pno), page2comment, (art_id,), proxy=proxy) for art_id in df_artinfo.index for pno in range(df_artinfo.loc[art_id,'art_pno'])])
        df_comment = pd.concat(comment_list,ignore_index=True)
        mergeComment(df_comment)
        print('all comments updated')
    else:
        pass

def genAnno(df):

    def strFind(s,t):
        loc = []
        l = len(t)
        for i in range(len(s)-l):
            if s[i:i+l] == t:
                loc.append(i)
        return loc

    df_anno = pd.DataFrame()
    for idx in df.index:
        id = df.loc[idx,'id']
        s = df.loc[idx,'post']
        d = df.loc[idx,'art_date']
        loc1 = strFind(s,'後註一')+strFind(s,'原後註')
        if loc1 != []:
            ss = s[loc1[0]:].split('<p>【')
            for i in ss:
                loc2 = strFind(i[:7],'，')
                loc3 = strFind(i,'】')[0]
                if loc2 == []:
                    comment = i[:loc3]
                    date = d
                else:
                    comment = i[:loc2[0]]
                    date = pd.to_datetime(i[loc2[0]+1:loc3],format='%Y/%m/%d')+datetime.timedelta(days=1)
                reply = i[loc3+1:]
                if reply[-6:] == '</div>':
                    reply = reply[:-6]
                df_anno = pd.concat([df_anno,pd.DataFrame(data={'comment':comment,'reply':reply,'nickname':comment,'date':date,'id':id},index=[0])],ignore_index=True)
    df_anno = df_anno.sort_values(by='date',ascending=False).reset_index(drop=True)
    return df_anno

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
    .LI .TIME{
    font-size:12px;
    color:#999;
    float:right;
    }
    </style>
    <title>王孟源的博客镜像</title>
    </head>
    <body><div class="BODY">
    <h1><a href="https://blog.udn.com/MengyuanWang/article" style="text-decoration:none;">王孟源的博客镜像</a></h1>
    <br>
    <ul class="LI">
    <li><a class="title" href="./html/new_comment.html">最新回复</a></li>
    <li><a class="title" href="./html/dialogue360.html">王孟源 x 八方论谈</a></li>
    %for url, name, time in art_li:
    <li><a class="title" href="./html/${url}.html">${name}</a><div class="TIME">${time}</div></li>
    %endfor
    </ul>
    </div></body></html>
    """)

    with open("index.html", "w", encoding='utf8') as index:
        index.write(INDEX.render(art_li=art_li))
    return

def genHTML(art_id,df_article,df_comment):
    
    i = df_article.loc[df_article.id == art_id].index
    title = df_article.title[i[0]]
    art_date = df_article.art_date[i[0]]
    post = df_article.post[i[0]]
    
    reply_li = []
    df_comment_id = df_comment.loc[df_comment.id == art_id].sort_values(by=['comment_date','nickname','comment'])
    for j in df_comment_id.index:
        comment = df_comment_id.comment[j]
        if comment:
            reply = re.sub('<br>$','',re.sub('^<br>','',df_comment_id.reply[j])).replace('<br>','<br><br>')

            if reply:
                first_reply_date = df_comment_id.loc[j, 'first_reply_date']
                latest_reply_date = df_comment_id.loc[j, 'latest_reply_date']

                if str(first_reply_date) != 'NaT':
                    if first_reply_date == latest_reply_date:
                        reply = reply + f'<br><div class="TIME">{latest_reply_date.strftime("%Y-%m-%d %H:%M")} 回复</div>'
                    else:
                        reply = reply + f'<br><div class="TIME">{latest_reply_date.strftime("%Y-%m-%d %H:%M")} 修改</div>'

            nickname = df_comment_id.nickname[j]
            comment_date = df_comment_id.comment_date[j].strftime('%Y-%m-%d %H:%M')
            uuid = df_comment_id.comment_date[j].strftime('%y%m%d%H%M')
            striked = '<strike>' in comment
            reply_li.append((uuid,comment,reply,nickname,comment_date,striked))
            
    HTML = Template("""<!DOCTYPE html><html><head>    
    <meta content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no" name=viewport><meta charset=utf-8>
    <link rel="stylesheet" href="./init.css">
    <title>${title}</title>
    </head>
    <body><div class="BODY">
    <div class="BACK"><a href="../index.html">返回索引页</a></div>
    <h1>${title}</h1>
    <p class="DATE">${date}</p>
    <h4>原文网址：<a href="https://blog.udn.com/MengyuanWang/${art_id}">https://blog.udn.com/MengyuanWang/${art_id}</a></h4>
    <br><br>
    <div class="POST">${post}</div>
    <div class="REPLY_LI">
    <h2>${len(reply_li)} 条留言</h2>
    %for uuid, say, reply, user, time, striked in reply_li:
    <div class="LI">
    <div class="USER"><span class="NAME" id=${uuid}>${user}</span><div class="TIME">${time}</div></div>
    %if striked:
    <input type="checkbox" class="exp" id="${uuid}_1">
    <div class="text1"><label class="btn" for="${uuid}_1"></label>
    <div class="SAY">${say}</div>
    </div>
    %else:
    <div class="SAY">${say}</div>
    %endif
    %if reply:
    <div class="REPLY">${reply}</div>
    %endif
    </div>
    %endfor
    </div>
    </div>
    <div class="BACK"><a href="../index.html">返回索引页</a></div>
    <script>
    function click1(link) {
        modal.style.display = "block";
        modalImg.src = link;
    }
    function click2() {
        modal.style.display = "none";
    }</script>
    </body></html>""")
        
    with open('./html/'+art_id+'.html','w',encoding='utf8') as f:
        f.write(HTML.render(title=title,date=art_date,art_id=art_id,post=post,reply_li=reply_li))
    return
def genLatestComment(df_comment_today,article_dict):
    HTML = Template("""<!DOCTYPE html><html><head>
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
    %for source,id,uuid,say,reply,user,time,striked in reply_li:
    <div class="LI">
    <div class="USER"><span class="NAME">${source} | <a href="./${id}.html#${uuid}">${user}</a></span><div class="TIME">${time}</div></div>
    %if striked:
    <input type="checkbox" class="exp" id="${uuid}_1">
    <div class="text1"><label class="btn" for="${uuid}_1"></label>
    <div class="SAY">${say}</div>
    </div>
    %else:
    <div class="SAY">${say}</div>
    %endif
    %if reply:
    <div class="REPLY">${reply}</div>
    %endif
    </div>
    %endfor
    </div>
    </div>
    <div class="BACK"><a href="../index.html">返回索引页</a></div>
    <script>
    function click1(link) {
        modal.style.display = "block";
        modalImg.src = link;
    }
    function click2() {
        modal.style.display = "none";
    }</script>
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
    %for source, id, uuid, say, reply, user, time, striked in reply_li:
    %if reply:
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
    %endif
    %endfor
    </channel></rss>
    """)

    RSS_notify = Template("""
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
    %for source, id, uuid, say, reply, user, time, striked in reply_li:
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
    art_date = datetime.datetime.now().strftime('%m-%d %H:%M')
    for i in df_comment_today.index:
        comment = df_comment_today.comment[i] 
        if comment:
            reply = re.sub('<br>$','',re.sub('^<br>','',df_comment_today.reply[i])).replace('<br>','<br><br>')
            if reply:
                first_reply_date = df_comment_today.loc[i, 'first_reply_date']
                latest_reply_date = df_comment_today.loc[i, 'latest_reply_date']

                if str(first_reply_date) != 'NaT':
                    if first_reply_date == latest_reply_date:
                        reply = reply + f'<br><div class="TIME">{latest_reply_date.strftime("%Y-%m-%d %H:%M")} 回复</div>'
                    else:
                        reply = reply + f'<br><div class="TIME"><a href="https://github.com/taizihuang/wmyblog/commits/main/html/{art_id}.html" style="text-decoration: none;color:black;">{latest_reply_date.strftime("%Y-%m-%d %H:%M")} 修改</a></div>'
            nickname = df_comment_today.nickname[i]
            comment_date = df_comment_today.comment_date[i]
            uuid = comment_date.strftime('%y%m%d%H%M')
            art_id = df_comment_today.id[i]
            source = article_dict[art_id]
            striked = '<strike>' in comment
            reply_li.append((source,art_id,uuid,comment,reply,nickname,comment_date,striked))
    with open("./html/new_comment.html", "w",encoding='utf8') as html:
        html.write(HTML.render(title='最新回复',date=art_date,post='',reply_li=reply_li))
    with open("./rss.xml","w",encoding='utf8') as rss:
        rss.write(RSS.render(date=art_date,reply_li=reply_li))
    with open("./rss_notify.xml","w",encoding='utf8') as rss:
        rss.write(RSS_notify.render(date=art_date,reply_li=reply_li))
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
        comment_date = df_comment.comment_date[i]
        reply = df_comment.reply[i]
        if reply:
            comment_list.append({"id":id,"title":title,"nickname":nickname,"date":comment_date.strftime('%Y-%m-%d %H:%M:%S'),"comment":comment,"reply":reply})

    wmy = {"article":article_list,"comment":comment_list}
    with open(jsonFile,'w') as f:
        f.write(json.dumps(wmy))

def updateBlogPage(days=7,articleFile="./data/article_full.pkl",commentFile="./data/comment_full.pkl"):

    def today(timezone='Asia/Shanghai'):
        os.environ['TZ'] = timezone
        time.tzset()
        today = pd.to_datetime(datetime.date.today())
        return today

    df_article = pd.read_pickle(articleFile)
    df_comment = pd.read_pickle(commentFile)
    
    for art_id in df_article.id:
        genHTML(art_id,df_article,df_comment)

    genINDEX(articleFile=articleFile)
    print('index page generated')

    latest = today() - datetime.timedelta(days=days)
    df_anno = genAnno(df_article)
    df_comment1 = pd.concat([df_comment,df_anno],ignore_index=True)
    df_comment_today = df_comment1.loc[df_comment1.comment_date > latest]
    df_comment_today = df_comment_today.sort_values(by='comment_date',ascending=False)
    article_dict = {}
    for index in df_article.index:
        article_dict[df_article.id[index]] = df_article.title[index]
    genLatestComment(df_comment_today,article_dict)
    print('latest page generated')

    exportJSON(articleFile,commentFile,jsonFile='./search/wmyblog.json')
    print('search data generated')

if __name__ == "__main__":
    updateBlogData(proxy='')
    updateBlogPage(days=7)
