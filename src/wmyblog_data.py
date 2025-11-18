import math, re, requests, os
import pandas as pd
from downloader import Downloader
from bs4 import BeautifulSoup

def pageURL(pno):
    return f"https://blog.udn.com/blog/article/article_list_head_ajax.jsp?uid=MengyuanWang&pno={pno}"

def articleURL(art_id):
    return f"https://blog.udn.com/MengyuanWang/{art_id}"

def commentURL(art_id,pno):
    return f"https://blog.udn.com/blog/article/article_reply_ajax.jsp?uid=MengyuanWang&f_ART_ID={art_id}&pno={pno}"

# def pageURL_classic(pno):
#     return f"https://classic-blog.udn.com/blog/article/article_list_head_ajax.jsp?uid=MengyuanWang&pno={pno}"

# def articleURL_classic(art_id):
#     return f"https://classic-blog.udn.com/MengyuanWang/{art_id}"

# def commentURL_classic(art_id,pno):
#     return f"https://classic-blog.udn.com/blog/article/article_reply_ajax.jsp?uid=MengyuanWang&f_ART_ID={art_id}&pno={pno}"

# def getPageNo():
#     url = 'https://blog.udn.com/blog/inc_2011/psn_artcate_new_ajax.jsp?uid=MengyuanWang&totalPageNum=1&curPage=0'
#     nPerPage = 30
#     doc = requests.get(url).content
#     nArticle = int(str(doc).split('(')[1].split(')')[0])
#     nPage = math.ceil(nArticle / nPerPage)
    # return 11 #nPage

def page2artinfo(doc):
    art_info = []
    for topic in doc('dt')[1:]:
        art_id = topic('a')[0].attrs['href'].split('/')[-1]
        art_nComment = int(topic(class_='article_count_comm')[0].contents[1])
        art_pno = math.ceil(art_nComment/10)
        art_info.append({"art_id": art_id, "art_nComment": art_nComment,'art_pno': art_pno})
    return art_info

def page2article(doc, art_id, img_dir):

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
    art_date = pd.to_datetime(art_date, format="%Y/%m/%d %H:%M")

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
            img_file = f"{img_dir}/{imgID}"
            img_url = f"./img/{imgID}"
            if not os.path.exists(img_file):
                img = requests.get(url).content
                with open(img_file, "wb") as f:
                    f.write(img)
            i.attrs['src'] = img_url 

    df_article = pd.DataFrame(data={"id": art_id,
                                    "title": title,
                                    "art_date": art_date,
                                    "post": str(post)
                                    },index=[0])

    return [df_article]

def page2article_classic(doc, art_id, img_dir):
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
            img_url = f"./img/{imgID}"
            img_file = f"{img_dir}/{imgID}"
            if not os.path.exists(img_file):
                img = requests.get(url).content
                with open(img_file, "wb") as f:
                    f.write(img)
            i.attrs['src'] = img_url 

    df_article = pd.DataFrame(data={'id': art_id, 
                                    'title': title,
                                    'art_date': art_date,
                                    'post':str(post)
                                    }, index=[0])

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
        return {"comment": comment,
                "reply": reply,
                "nickname": nickname,
                "comment_date": comment_date,
                "first_reply_date": first_reply_date,
                "latest_reply_date": latest_reply_date,
                "id": art_id
                }

    if  doc.find(id="response_head"):
        reply_list = []
        for rep in doc.findAll(id=re.compile(r"rep\d+")):
            reply_list.append(rep2dict(rep))
        df_comment = pd.DataFrame(data=reply_list)
    else:
        df_comment = pd.DataFrame(data={"comment": "",
                                        "reply": "",
                                        "nickname": "",
                                        "comment_date": "",
                                        "first_reply_date": "",
                                        "latest_reply_date": "",
                                        "id": art_id
                                        },index=[0])

    l = ['comment_date', 'first_reply_date', 'latest_reply_date']
    df_comment[l] = df_comment[l].apply(pd.to_datetime,format="%Y/%m/%d %H:%M")
    
    return [df_comment]

def update_data(data_dir, img_dir):
    article_file = f"{data_dir}/article_full.pkl"
    comment_file = f"{data_dir}/comment_full.pkl"
    df_article = pd.read_pickle(article_file)
    df_comment = pd.read_pickle(comment_file)


    headers = {
               "pragma": "no-cache",
               "cache-control": "no-cache",
               "sec-ch-ua": "\"Chromium\";v=\"142\", \"Microsoft Edge\";v=\"142\", \"Not_A Brand\";v=\"99\"",
               "sec-ch-ua-mobile": "?0",
               "sec-ch-ua-platform": "\"Windows\"",
               "dnt": "1",
               "upgrade-insecure-requests": "1",
               "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0",
               "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
               "sec-fetch-site": "same-origin",
               "sec-fetch-mode": "navigate",
               "sec-fetch-user": "?1",
               "sec-fetch-dest": "document",
               "referer": "https://blog.udn.com/MengyuanWang/article",
               "accept-encoding": "gzip, deflate, br, zstd",
               "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6,en-CA;q=0.5",
               "cookie": "_td=9505f9ed-d13b-4495-b48e-0b09e6caa60a",
               "priority": "u=0, i"
    }

    id_list = []
    url = "https://blog.udn.com/MengyuanWang/article"
    content = requests.get(url, headers=headers).content
    doc = BeautifulSoup(content, features="lxml")
    for d in doc.findAll(class_='article_topic'):
        id_list.append(d('a')[0]['href'].split('/')[-1])
    id_list = id_list[:10]

    url = f'https://classic-blog.udn.com/blog/inc_2011/psn_article_ajax.jsp?uid=MengyuanWang&f_FUN_CODE=new_rep'
    content = requests.get(url, headers=headers).content
    doc = BeautifulSoup(content, features="lxml")
    id_list += [d('a')[0]['href'].split('/')[-1] for d in doc.findAll('dt')]
    id_list += list(df_comment["id"].iloc[:10])
    id_list = list(set(id_list))

    url_list = [articleURL(art_id) for art_id in id_list]
    article_tmp = Downloader(url_list=url_list, nCache=2, headers=headers, outFilename="article_tmp.pkl").run(njob=1)

    article_list = []
    comment_list = []
    for idx in article_tmp.index:
        url, response, status = article_tmp.loc[idx]
        if status == 200:
            doc = BeautifulSoup(response, features="lxml")
            art_id = url.split("/")[-1]
            article_list += page2article(doc, art_id, img_dir)
            comment_list += page2comment(doc, art_id)
        else:
            print(f"[error] {status} {url}")
    
    article_list.append(df_article)
    df_article_new = pd.concat(article_list, ignore_index=True)
    df_article_new = df_article_new.drop_duplicates(subset="id", keep="first")
    df_article_new = df_article_new.sort_values("id", ascending=False).reset_index(drop=True)

    df_comment_new = pd.concat(comment_list, ignore_index=True)
    min_comment_date = min(df_comment_new["comment_date"].dropna())
    df_comment1 = df_comment.loc[df_comment["comment_date"] >= min_comment_date]
    df_comment2 = df_comment.loc[df_comment["comment_date"] < min_comment_date]

    for id in id_list:
        d_new = df_comment_new.loc[df_comment_new.id == id]
        if not d_new.empty:
            d = df_comment1.loc[(df_comment1.id == id) & (df_comment1.comment_date >= min(d_new.comment_date))]
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
    df_comment_new = pd.concat([df_comment_new, df_comment1], ignore_index=True)
    df_comment_new = df_comment_new.drop_duplicates(subset=['nickname','comment_date'], keep="first")
    df_comment_new = pd.concat([df_comment_new, df_comment2],ignore_index=True)
    df_comment_new["comment"] = df_comment_new["comment"].str.replace('<strike><strike>','<strike>')
    df_comment_new["comment"] = df_comment_new["comment"].str.replace('</strike></strike>','</strike>')
    df_comment_new = df_comment_new.sort_values('comment_date',ascending=False).reset_index(drop=True)

    os.remove("article_tmp.pkl")
    os.remove(f"{article_file}.bak")
    os.remove(f"{comment_file}.bak")
    os.rename(article_file, f"{article_file}.bak")
    os.rename(comment_file, f"{comment_file}.bak")
    df_article_new.to_pickle(article_file)
    df_comment_new.to_pickle(comment_file)

if __name__ == "__main__":
    data_dir = "../data"
    img_dir = "../html/img"
    update_data(data_dir, img_dir)
