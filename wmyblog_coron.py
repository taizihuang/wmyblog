from downloader import Downloader
import asyncio,aiohttp,time,math,os,requests,re,datetime,json,hashlib,sys
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

def pageURL_classic(pno):
    return f"https://classic-blog.udn.com/blog/article/article_list_head_ajax.jsp?uid=MengyuanWang&pno={pno}"

def articleURL_classic(art_id):
    return f"https://classic-blog.udn.com/MengyuanWang/{art_id}"

def commentURL_classic(art_id,pno):
    return f"https://classic-blog.udn.com/blog/article/article_reply_ajax.jsp?uid=MengyuanWang&f_ART_ID={art_id}&pno={pno}"

def getPageNo():
#     url = 'https://blog.udn.com/blog/inc_2011/psn_artcate_new_ajax.jsp?uid=MengyuanWang&totalPageNum=1&curPage=0'
#     nPerPage = 30
#     doc = requests.get(url).content
#     nArticle = int(str(doc).split('(')[1].split(')')[0])
#     nPage = math.ceil(nArticle / nPerPage)
    return 11 #nPage

def updateTag(tagFile='./data/tag.pkl'):

    df_tag = pd.read_pickle(tagFile)

    headers = {
        'Apikey':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNqbG9za2pjb2dya3ZocGtmb296Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODYwMjIyNjIsImV4cCI6MjAwMTU5ODI2Mn0.peYwcTSZcDd3SvG5Rh99jlM7uyHkUjq1klvqRt2vF5c',
        'Authorization':'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNqbG9za2pjb2dya3ZocGtmb296Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODYwMjIyNjIsImV4cCI6MjAwMTU5ODI2Mn0.peYwcTSZcDd3SvG5Rh99jlM7uyHkUjq1klvqRt2vF5c'
    }
    tag_dict = json.loads(requests.get('https://cjloskjcogrkvhpkfooz.supabase.co/rest/v1/tag?select=*&order=created_at.desc&limit=500',headers=headers).content)
    df_tag_new = pd.DataFrame(tag_dict).rename(columns={'id':'md5'})[['md5','tag']]
    df_tag = pd.concat([df_tag_new,df_tag],ignore_index=True).drop_duplicates(keep='first').reset_index(drop=True)
    df_tag.to_pickle(tagFile)
    print('tag table updated')
    return

def extract(doc):
    string_left = 'DOCS_modelChunk = [{'
    string_right = '},{"'
    text = ''
    while string_left in doc:
        loc1 = doc.index(string_left)
        loc2 = doc[loc1:].index(string_right)
        doc_dict = json.loads(doc[loc1+18:loc1+loc2] + '}]')
        loc_idx = 0
        if 's' not in doc_dict[0]:
            loc3 = doc[loc1+loc2+2:].index(string_right)
            doc_dict = json.loads(doc[loc1+18:loc1+loc2+2+loc3] + '}]')
            loc_idx = 1
            if 's' not in doc_dict[1]:
                loc4 = doc[loc1+loc2+2+loc3+2:].index(string_right)
                doc_dict = json.loads(doc[loc1+18:loc1+loc2+loc3+2+loc4+2] + '}]')
                loc_idx = 2
        text += doc_dict[loc_idx]['s']
        doc = doc[loc1+loc2+2:]
    return text

def saveScript(filename, id, proxy=''):
    print(filename, id)
    link = f'https://docs.google.com/document/d/{id}/edit'
    doc = requests.get(link).content.decode("utf8")

    text = extract(doc)
    body = text.replace('\n','<br>')
    html = f"""
    <html><head><meta content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no" name="viewport">
        <meta charset="UTF-8"><link rel="stylesheet" href="./init.css">
        <title>{filename}</title>
    </head>
    <body>
        <div class="BODY"><div class="BACK"><a href="../index.html">返回索引页</a></div>
            <h1>{filename}</h1>
            <h4>编辑地址：<a href="{link}">{link}</a></h4>
            <h4>音频下载地址：<a href="https://drive.tedl.uk/s/kRTG">链接</a></h4><br><br>
            <div class="POST"><div id="article_show_content">{body}</div>
        </div>
    </body>
    </html>
    """
    with open(f'./html/{filename}.html','w',encoding='utf8') as f:
        f.write(html)

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
        if i.has_attr('src'):
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

def page2article_classic(doc, art_id):
    print(art_id)
    print(doc)

    if doc.find(class_="REPLY_LI"):
        doc.find(class_="REPLY_LI").decompose()

    # title
    title = doc.find(class_='article_topic').text

    # date
    if doc.find(class_="DATE"):
        art_date = doc.find(class_="DATE").text
        art_date = art_date.replace('发表日期 : ','').replace('-','/')
        doc.find(class_="DATE").decompose()
    elif doc.find(class_="article_datetime"):
        art_date = doc.find(class_="article_datatime").text
    else:
        for t in doc.findAll(class_="main-text"):
            regex = r'(\d{4}/\d{2}/\d{2} \d{2}:\d{2})'
            if re.search(regex, t.text):
                art_date = re.search(regex, t.text).groups()[0]
                break
    print(art_date)
    art_date = pd.to_datetime(art_date,format="%Y/%m/%d %H:%M")

    # post
    #post = doc.find(id="mainbody")
    post = doc.find(id="article_show_content")

    # convert link
    for i in post.findAll('a',{'href': re.compile("MengyuanWang")}):
        t = i.attrs['href'].split('/')
        i.attrs['href'] = t[-1]+'.html'

    #save image
    for i in post.findAll('img'):
        if i.has_attr('src'):
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

        comment = rep(class_='rp5')[0].text.replace('\xa0','')
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
        for rep in doc.findAll(id=re.compile(r"rep\d+")):
            reply_list.append(rep2dict(rep))
        df_comment = pd.DataFrame(data=reply_list)
    else:
        df_comment = pd.DataFrame(data={'comment':'','reply':'','nickname':'','comment_date':'','first_reply_date':'','latest_reply_date': '','id':art_id},index=[0])

    l = ['comment_date','first_reply_date','latest_reply_date']
    df_comment[l] = df_comment[l].apply(pd.to_datetime,format="%Y/%m/%d %H:%M")
    
    return [df_comment]

def mergeArticle(df_article_new, articleFile='./data/article_full.pkl'):
    df_article = pd.read_pickle(articleFile)
    df_article_new = pd.concat([df_article_new, df_article],ignore_index=True).drop_duplicates(subset='id',keep='first').sort_values('id',ascending=False).reset_index(drop=True)

    os.remove(articleFile+'.bak')
    os.rename(articleFile, articleFile+'.bak')
    df_article_new.to_pickle(articleFile)

def mergeComment(df_comment_new,commentFile='./data/comment_full.pkl',tag=''):

    df_comment = pd.read_pickle(commentFile)
    min_comment_date = min(df_comment_new.comment_date.dropna())
    df_comment1 = df_comment.loc[df_comment.comment_date >= min_comment_date]
    df_comment2 = df_comment.loc[df_comment.comment_date < min_comment_date]

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

def comment2md(comment):
    return hashlib.md5((comment.replace('<strike>','').replace('</strike>','').replace("\r\n","").replace('\n','').replace('<br>','')).encode()).hexdigest()

def updateBlogData(nTask=20, proxy='',articleUpdate=True,gDriveUpdate=True,commentFullUpdate=False):

    os.environ['http_proxy'] = proxy #代理的端口
    os.environ['https_proxy'] = proxy
    headers = {
        'referer' : 'https://blog.udn.com/MengyuanWang',
        'host' : 'blog.udn.com',
        'Origin' : 'https://blog.udn.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh-CN;q=0.7,zh;q=0.6',
        'Dnt': '1',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        'Content-Type': 'application/html'
    }

    # latest article ids
    doc = BeautifulSoup(requests.get(f'https://blog.udn.com/MengyuanWang/article',headers=headers).content, features="lxml")
    id_list = [d('a')[0]['href'].split('/')[-1] for d in doc.findAll(class_='article_topic')][:10]

    # latest comment ids
    doc = BeautifulSoup(requests.get(f'https://classic-blog.udn.com/blog/inc_2011/psn_article_ajax.jsp?uid=MengyuanWang&f_FUN_CODE=new_rep',headers=headers).content, features="lxml")
    id_list += [d('a')[0]['href'].split('/')[-1] for d in doc.findAll('dt')]
    id_list += list(pd.read_pickle('./data/comment_full.pkl').id.iloc[:10])
    id_list = list(set(id_list))
    print(id_list)

    df_artinfo = pd.DataFrame(data=id_list,columns=['art_id']).set_index('art_id')
    print('article info fetched!')
    
    if gDriveUpdate:
        url = 'https://drive.google.com/drive/folders/1eg78LVciM913PhvRtsgtWV3VDLojynDA'
        doc = BeautifulSoup(requests.get(url).content, features="lxml")
        df = pd.DataFrame()
        for i in doc.findAll("div", {'data-target':"doc"}):
            if i.find("div",{'role':"link"}):
                i.find("div",{'role':"link"}).decompose()
            df = pd.concat([df, pd.DataFrame(data={'filename': i.text, 'id': i['data-id']}, index=[0])], ignore_index=True)
        df = df.loc[df.filename.str.contains('龙行天下')]
        for idx in df.index[-2:]:
            saveScript(df.loc[idx, 'filename'][:6], df.loc[idx, 'id'], proxy)
        print('transcript downloaded')

    if articleUpdate:
        article_url = [articleURL(art_id) for art_id in id_list]
        article_tmp = Downloader(url_list=article_url, headers=headers, outFilename="article_tmp.pkl").run(njob=1)
        # article_tmp = pd.read_pickle("article_tmp.pkl")
        article_list = []
        comment_list = []
        for idx in article_tmp.index:
            url, response, status = article_tmp.loc[idx]
            if status == 200:
                doc = BeautifulSoup(response, features="lxml")
                art_id  = url.split("/")[-1]
                article_list += page2article(doc, art_id)
                comment_list += page2comment(doc, art_id)
            else:
                print(f"[error] {status} {url}")

        df_article = pd.concat(article_list, ignore_index=True)
        df_comment = pd.concat(comment_list,ignore_index=True)
        mergeArticle(df_article)
        mergeComment(df_comment)
        print('articles and latest comments updated')
    else:
        pass

    # if commentFullUpdate:
    #     comment_list = tasker.run([fetch_async(commentURL_classic(art_id,pno), page2comment, (art_id,), proxy=proxy) for art_id in df_artinfo.index for pno in range(df_artinfo.loc[art_id,'art_pno'])])
    #     df_comment = pd.concat(comment_list,ignore_index=True)
    #     mergeComment(df_comment)
    #     print('all comments updated')
    # else:
    #     pass

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
                    if '/' in i[loc2[0]+1:loc3]:
                        date = pd.to_datetime(i[loc2[0]+1:loc3],format='%Y/%m/%d')+datetime.timedelta(days=1)
                    else:
                        date = pd.to_datetime(i[loc2[0]+1:loc3],format='%Y%m%d')+datetime.timedelta(days=1)
                reply = i[loc3+1:]
                if reply[-6:] == '</div>':
                    reply = reply[:-6]
                elif reply[-2:] == '<p':
                    reply = reply[:-2]  
                elif reply[-2] == '體':
                    loc4 = strFind(reply,'<p>')
                    reply = reply[:loc4[-1]]              
                df_anno = pd.concat([df_anno,pd.DataFrame(data={'comment':comment,'reply':reply,'nickname':comment,
                                                                'comment_date':date, "first_reply_date": date,
                                                                "latest_reply_date": date, 'id':id},index=[0])],ignore_index=True)
    df_anno = df_anno.sort_values(by='comment_date',ascending=False).reset_index(drop=True)
    return df_anno

def genINDEX(articleFile, df_comment_tag):
    df_article = pd.read_pickle(articleFile)
    art_li = []
    for i in df_article.index:
        art_id = df_article.id[i]
        title = df_article.title[i]
        art_date = str(df_article.art_date[i]).split(' ')[0]
        df_reply = df_comment_tag.loc[df_comment_tag.id == art_id].drop_duplicates(subset=['comment'],keep='first') 
        tagged = df_reply.loc[df_reply['tag'] != 'empty/']
        replied = df_reply.loc[df_reply['reply'] != '']
        tagRate = f'{len(tagged)}/{len(replied)}'
        art_li.append((art_id,title,art_date,tagRate))

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
    <br><br>
    <ul class="LI">
    <li><a class="title" href="./html/new_comment.html">最新回复</a></li>
    <li><a class="title" href="./podcast/index.html">最新访谈</a></li>
    <li><a class="title" href="./search/index.html">网页搜索</a></li>
    %for url, name, time, tagRate in art_li:
    <li><a class="title" href="./html/${url}.html">${name} [${tagRate}]</a><div class="TIME">${time}</div></li>
    %endfor
    </ul>
    </div></body></html>
    """)

    with open("index.html", "w", encoding='utf8') as index:
        index.write(INDEX.render(art_li=art_li))
    return

def genHTML(art_id,df_article,df_comment_tag):
    
    i = df_article.loc[df_article.id == art_id].index
    title = df_article.title[i[0]]
    art_date = df_article.art_date[i[0]]
    post = df_article.post[i[0]]
    
    reply_li = []
    df_comment_id = df_comment_tag.loc[df_comment_tag.id == art_id].sort_values(by=['comment_date','nickname','comment']).drop_duplicates(subset=['comment'],keep='first')
    for j in df_comment_id.index:
        comment = df_comment_id.comment[j]
        if comment:
            comment = comment.replace('\n','<br><br>').replace('<br><br><br>','<br>').replace('<br><br><br>','<br>')
            reply = df_comment_id.reply[j].replace('\n','<br>') 
            reply = re.sub('<br>$','',re.sub('^<br>','', reply)).replace('<br>','<br><br>')

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
            uuid = df_comment_id.md5[j]
            tag_list = df_comment_id.tag[j].replace('。','/').replace('、','/') #' '.join([f'#{t}' for t in  df_comment_id.tag[j].split('/')])
            striked = '<strike>' in comment
            reply_li.append((uuid,comment,reply,nickname,comment_date,tag_list,striked))
            
    HTML = Template("""<!DOCTYPE html><html><head>    
    <meta content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no" name=viewport><meta charset=utf-8>
    <script src="./blog.js"></script>
    <script src="jquery-1.11.3.min.js"></script>
    <link href="fSelect.css" rel="stylesheet" type="text/css">
    <script src="supabase.js"></script>
    <script src="tag.js"></script>
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
    %for uuid, say, reply, user, time, tag_list, striked in reply_li:
    <div class="LI">
    <div class="USER"><span class="NAME" id=${uuid}>${user}</span>
    <div class="TIME">${time}</div></div>
    <span class="tag"><input type="search" value=${tag_list} data-md5=${uuid} onkeydown="enter(event,$(this))"></span>
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
    #search_btn {
        font-family: Arial;
        text-decoration: none;
        font-size: 13px;
        color: #FFF;
        background: #24a2e0b9;
        padding: 1px 5px;
        border: 1px solid #24a2e0b9;
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
    <title>${title}</title>
    </head>
    <body><div class="BODY">
    <div class="BACK"><a href="../index.html">返回索引页</a></div>
    <div id="LATEST">最新回复
        <span><a href="https://taizihuang.github.io/wmyblog/rss.xml" id="rss_btn">RSS</a></span>
        <span><a href="../search/index.html" id="search_btn">搜索</a></span>
    </div>
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
            comment = comment.replace('\n','<br><br>').replace('<br><br><br>','<br>').replace('<br><br><br>','<br>')
            nickname = df_comment_today.nickname[i].replace('\u3000',' ')
            comment_date = df_comment_today.comment_date[i]
            uuid = comment2md(comment) #comment_date.strftime('%y%m%d%H%M')
            art_id = df_comment_today.id[i]
            source = article_dict[art_id]
            striked = '<strike>' in comment
            reply = df_comment_today.reply[i].replace('\n','<br>').replace('src="./img/','src="https://wmyblog.site/html/img/') 
            reply = re.sub('<br>$','',re.sub('^<br>','', reply)).replace('<br>','<br><br>')
            if reply:
                first_reply_date = df_comment_today.loc[i, 'first_reply_date']
                latest_reply_date = df_comment_today.loc[i, 'latest_reply_date']

                if str(first_reply_date) != 'NaT':
                    if first_reply_date == latest_reply_date:
                        reply = reply + f'<br><div class="TIME">{latest_reply_date.strftime("%Y-%m-%d %H:%M")} 回复</div>'
                    else:
                        reply = reply + f'<br><div class="TIME"><a href="https://github.com/taizihuang/wmyblog/commits/main/html/{art_id}.html" style="text-decoration: none;color:black;">{latest_reply_date.strftime("%Y-%m-%d %H:%M")} 修改</a></div>'
            reply_li.append((source,art_id,uuid,comment,reply,nickname,comment_date,striked))
    with open("./html/new_comment.html", "w",encoding='utf8') as html:
        html.write(HTML.render(title='最新回复',date=art_date,post='',reply_li=reply_li))
    with open("./rss.xml","w",encoding='utf8') as rss:
        rss.write(RSS.render(date=art_date,reply_li=reply_li).replace('&lt;br&gt;','<br>').replace('&lt;','<').replace('&gt;','>'))
    with open("./rss_notify.xml","w",encoding='utf8') as rss:
        rss.write(RSS_notify.render(date=art_date,reply_li=reply_li).replace('&lt;br&gt;','<br>'))
    return

def exportJSON(df_article,df_comment_tag, jsonFile):
    
    article_list = []
    title_dict = {}
    for i in df_article.index:
        id = df_article.id[i]
        title = df_article.title[i]
        title_dict[id] = title
        art_date = df_article.art_date[i]
        post = df_article.post[i]
        article_list.append({"id":id,"title":title,"date":art_date.strftime('%Y-%m-%d %H:%M:%S'),"post":post})

    df_comment_tag = df_comment_tag.drop_duplicates(subset=['comment'],keep='first')
    comment_list = []
    for i in df_comment_tag.index:
        id = df_comment_tag.id[i]
        title = title_dict[id]
        nickname = df_comment_tag.nickname[i]
        comment = df_comment_tag.comment[i]
        comment_date = df_comment_tag.comment_date[i]
        reply = df_comment_tag.reply[i]
        tag = df_comment_tag.tag[i].replace('。','/').replace('、','/')
        md5 = df_comment_tag.md5[i]
        if reply:
            comment_list.append({"id":id,"title":title,"nickname":nickname,"date":comment_date.strftime('%Y-%m-%d %H:%M:%S'),"comment":comment,"reply":reply,"tag":tag, "md5":md5})

    wmy = {"article":article_list,"comment":comment_list}
    with open(jsonFile,'w') as f:
        f.write(json.dumps(wmy))

def updateBlogPage(days=7,articleFile="./data/article_full.pkl",commentFile="./data/comment_full.pkl",tagFile="./data/tag.pkl"):

    def today(timezone='Asia/Shanghai'):
        os.environ['TZ'] = timezone
        if sys.platform == 'linux':
            time.tzset()
        today = pd.to_datetime(datetime.date.today())
        return today

    updateTag()
    
    df_article = pd.read_pickle(articleFile)
    df_comment = pd.read_pickle(commentFile)
    df_comment = df_comment.loc[~((df_comment['first_reply_date'] >= datetime.datetime(2023,11,24,11,0,0)) & (df_comment    ['first_reply_date'] <= datetime.datetime(2023,11,25,2,0,0)))]
    df_comment['md5'] = df_comment['comment'].apply(lambda x: comment2md(x))
    df_tag = pd.read_pickle(tagFile)
    df_comment_tag = pd.merge(df_comment, df_tag, on='md5',how='left')
    df_comment_tag.loc[df_comment_tag.tag.isna(),'tag'] = 'empty/'
    
    for art_id in df_article.id:
        genHTML(art_id,df_article,df_comment_tag)

    genINDEX(articleFile, df_comment_tag)
    print('index page generated')

    latest = today() - datetime.timedelta(days=days)
    df_anno = genAnno(df_article)
    df_comment1 = pd.concat([df_comment,df_anno],ignore_index=True)
    df_comment_today = df_comment1.loc[df_comment1.comment_date > latest]
    df_comment_today = df_comment_today.sort_values(by='latest_reply_date',ascending=False)
    article_dict = {}
    for index in df_article.index:
        article_dict[df_article.id[index]] = df_article.title[index]
    genLatestComment(df_comment_today, article_dict)
    print('latest page generated')

    exportJSON(df_article,df_comment_tag,jsonFile='./search/wmyblog.json')
    print('search data generated')

if __name__ == "__main__":
    updateBlogData(nTask=1, proxy='' ,gDriveUpdate=False)
    updateBlogPage(days=50)
    os.remove("article_tmp.pkl")
