import requests, logging, os, re
import pandas as pd
from bs4 import BeautifulSoup
from downloader import Downloader

proxy_url = ""
proxies = {
    "http": proxy_url,
    "https": proxy_url
}

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
    art_date = pd.to_datetime(art_date, format="%Y/%m/%d %H:%M")

    # post
    post = doc.find(id="article_show_content")

    # convert link
    for i in post.findAll('a',{'href': re.compile("MengyuanWang")}):
        t = i.attrs['href'].split('/')
        i.attrs['href'] = t[-1]+'.html'

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

    if doc.find(id="response_head"):
        reply_list = []
        for rep in doc.findAll(id=re.compile(r"rep\d+")):
            reply_list.append(rep2dict(rep))
        df_comment = pd.DataFrame(data=reply_list)
    else:
        data_dict = {"comment": "",
                    "reply": "",
                    "nickname": "",
                    "comment_date": "",
                    "first_reply_date": "",
                    "latest_reply_date": "",
                    "id": art_id
        }
        df_comment = pd.DataFrame(data=data_dict, index=[0])

    l = ['comment_date', 'first_reply_date', 'latest_reply_date']
    df_comment[l] = df_comment[l].apply(pd.to_datetime,format="%Y/%m/%d %H:%M")
    
    return [df_comment]

class Wmyblog:
    def __init__(self, data_dir, html_dir):
        self.data_dir = data_dir
        self.html_dir = html_dir

        article_file = f"{data_dir}/article.pkl"
        comment_file = f"{data_dir}/comment.pkl"
        transcript_file = f"{data_dir}/transcript.pkl"
        log_file = f"{data_dir}/wmyblog.log"

        # 全部按照正序排列
        self.df_article = pd.read_pickle(article_file)
        self.df_comment = pd.read_pickle(comment_file)
        self.df_transcript = pd.read_pickle(transcript_file)

        # logging
        formatter = logging.Formatter(
                    fmt='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y/%m/%d %I:%M:%S')
        file_handle = logging.FileHandler(log_file)
        file_handle.setLevel(logging.INFO)
        file_handle.setFormatter(formatter)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(self.file_handle)
    
    def get_id_list(self):

        id_list = []

        # 新文章或者新后注都会置顶
        url = "https://blog.udn.com/MengyuanWang/article"
        response = requests.get(url, headers=headers, proxies=proxies)
        status_code = response.status_code
        if status_code == 200:
            doc = BeautifulSoup(response.content, features="lxml")
            for d in doc.findAll(class_='article_topic'):
                id_list.append(d('a')[0]['href'].split('/')[-1])
            id_list = id_list[:10]
        else:
            self.logger.error(f"status {status_code} from {url}")

        # 最近有新评论的五篇文章
        url = f'https://classic-blog.udn.com/blog/inc_2011/psn_article_ajax.jsp?uid=MengyuanWang&f_FUN_CODE=new_rep'
        response = requests.get(url, headers=headers, proxies=proxies)
        status_code = response.status_code
        if status_code == 200:
            doc = BeautifulSoup(response.content, features="lxml")
            id_list += [d('a')[0]['href'].split('/')[-1] for d in doc.findAll('dt')]
        else:
            self.logger.error(f"status {status_code} from {url}")

        # 评论时间更老但未回复的文章 
        df_comment_noreply = self.df_comment.loc[self.df_comment["reply"].empty()
                                                 & (self.df_comment["deleted"] == False)]
        id_list += df_comment_noreply["id"].iloc[-10:]

        # 去重 
        id_list = list(set(id_list))

        return id_list

    def download_page(self, art_id):

        url = f"https://blog.udn.com/MengyuanWang/{art_id}"
        response = requests.get(url, headers=headers, proxies=proxies)
        status_code = response.status_code

        if status_code != 200:
            self.logger.error(f"status {status_code} from {url}")
            content = ""
        else:
            content = response.content
        doc = BeautifulSoup(content, features="lxml")

        # 下载图片，修改图片src为本地地址
        for img in doc.find(id="article_show_content").findAll('img'):
            if img.has_attr('src'):
                src = img.attrs['src'].replace('\r','').replace('\n','')
                imgID = src.split('/')[-1]
                img_file = f"{self.html_dir}/img/{imgID}"
                img_src = f"./img/{imgID}"
                if not os.path.exists(img_file):
                    img_content = requests.get(url, proxies=proxies).content
                    with open(img_file, "wb") as f:
                        f.write(img_content)
                    img.attrs['src'] = img_src 
        
        return status_code, doc
    
    def download_pages(self, id_list):
        article_list = [self.df_article]
        comment_list = []

        for art_id in id_list:
            status, doc = self.download_page(art_id)
            if status == 200:
                article_list += page2article(doc, art_id)
                comment_list += page2comment(doc, art_id)
        
        df_article = pd.concat(article_list, ignore_index=True)
        df_article = df_article.drop_duplicates(subset="id", keep="last")
        df_article = df_article.sort_values("id").reset_index(drop=True)

        df_comment_new = pd.concat(comment_list, ignore_index=True)
        min_comment_date = min(df_comment_new["comment_date"].dropna())
        df_comment1 = df_comment.loc[df_comment["comment_date"] >= min_comment_date]
        df_comment2 = df_comment.loc[df_comment["comment_date"] < min_comment_date]
        
        

    

    

    
