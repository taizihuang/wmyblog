import requests, logging, os, re, hashlib, json, datetime, time
import pandas as pd
from bs4 import BeautifulSoup
from mako.template import Template
from downloader import Downloader
from article_merger import ArticleMerger

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

def comment2md(comment):
    return hashlib.md5((comment.replace("\r\n","").replace('\n','').replace('<br>','')).encode()).hexdigest()
# def comment2md(comment):
#     return hashlib.md5((comment.replace('<strike>','').replace('</strike>','').replace("\r\n","").replace('\n','').replace('<br>','')).encode()).hexdigest()

def rep2dict(rep, art_id):

    comment = rep(class_='rp5')[0].text.replace('\xa0','')
    nickname = rep(class_='rp2')[0].text.split('\n')[1]
    comment_date = rep(class_='rp4')[0].text

    reply = ''
    if rep(class_='rp'):
        first_reply_date = rep(class_='prt')[-1].text.replace('王孟源 於 ','').replace('回覆','')
        for p in rep(class_='prt'):
            p.decompose()
        for irp in rep.findAll(class_='rp'):
            reply = reply + irp.text.replace("\r\n","<br>")
        reply.replace("\n\n","\n").replace("\n","<br>")
    else:
        first_reply_date = ''
    return {"comment": comment,
            "reply": reply,
            "nickname": nickname,
            "comment_date": comment_date,
            "first_reply_date": first_reply_date,
            "latest_reply_date": first_reply_date,
            "id": art_id,
            "md5": comment2md(comment),
            "deleted": False
            }

def page2comment(doc, art_id):

    if doc.find(id="response_head"):
        reply_list = []
        for rep in doc.findAll(id=re.compile(r"rep\d+")):
            reply_list.append(rep2dict(rep, art_id))
        df_comment = pd.DataFrame(data=reply_list)
    else:
        data_dict = {"comment": "",
                    "reply": "",
                    "nickname": "",
                    "comment_date": "",
                    "first_reply_date": "",
                    "latest_reply_date": "",
                    "id": art_id,
                    "md5": "",
                    "deleted": False
        }
        df_comment = pd.DataFrame(data=data_dict, index=[0])

    l = ['comment_date', 'first_reply_date', 'latest_reply_date']
    df_comment[l] = df_comment[l].apply(pd.to_datetime,format="%Y/%m/%d %H:%M")
    
    return [df_comment]

def extract_date(note):
    idx = note.find("【後註")
    matches1 = re.search(r"(\d{4}/\d{1,2}/\d{1,2})", note[idx:idx+20]) #.group(0)
    matches2 = re.search(r"(\d{8})", note[idx:idx+20]) #.group(0)
    if matches1:
        return pd.to_datetime(matches1[0], format="%Y/%m/%d").strftime("%Y-%m-%d")
    elif matches2:
        return pd.to_datetime(matches2[0], format="%Y%m%d").strftime("%Y-%m-%d")
    else:
        return "2000-01-01"

class Wmyblog:

    def __init__(self, data_dir, html_dir, template_dir, search_dir):
        self.data_dir = data_dir
        self.ct_dir = f"{data_dir}/ct_article"
        self.html_dir = html_dir
        self.template_dir = template_dir
        self.search_dir = search_dir

        # 全部按照正序排列
        self.article_file = f"{data_dir}/article.pkl"
        self.df_article = pd.read_pickle(self.article_file)
        self.comment_file = f"{data_dir}/comment.pkl"
        self.df_comment = pd.read_pickle(self.comment_file)
        self.transcript_file = f"{data_dir}/transcript.pkl"
        self.df_transcript = pd.read_pickle(self.transcript_file)
        self.tag_file = f"{data_dir}/tag.pkl"
        self.df_tag = pd.read_pickle(self.tag_file)

        # 后注日期
        self.note_date_file = f"{data_dir}/annotation_date.json"
        with open(self.note_date_file, "r") as f:
            self.note_date_dict = json.loads(f.read())
        
        # 原版标题
        title_file = f"{data_dir}/title_dict.json"
        with open(title_file, "r") as f:
            self.title_dict = json.loads(f.read())
        
        # 数据格式化
        self.post_list = []
        self.note_list = []
        self.comment_list = []

        # merger
        self.merger = ArticleMerger(self.data_dir, self.ct_dir)
        self.merge_comment_tag()

        # logging
        formatter = logging.Formatter(
                    fmt='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y/%m/%d %I:%M:%S')
        log_file = f"{data_dir}/wmyblog.log"
        file_handle = logging.FileHandler(log_file)
        file_handle.setLevel(logging.INFO)
        file_handle.setFormatter(formatter)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handle)
    
    def merge_comment_tag(self):
        df_comment = self.df_comment
        df_tag = self.df_tag.copy()
        df_tag = df_tag.drop_duplicates("md5", keep="first")
        time_range = [datetime.datetime(2023,11,24,11,0,0),
                    datetime.datetime(2023,11,25,2,0,0)] 
        df_comment = df_comment.loc[~((df_comment['first_reply_date'] >= time_range[0])
                                    & (df_comment['first_reply_date'] <= time_range[1]))]
        df_comment['md5'] = df_comment['comment'].apply(lambda x: comment2md(x))
        df_comment_tag = pd.merge(df_comment, df_tag, on='md5', how='left')
        self.df_comment_tag =df_comment_tag.sort_values(by=["comment_date", "nickname", "comment"]).reset_index(drop=True)
        self.df_comment_tag.loc[self.df_comment_tag["tag"].isna(),'tag'] = 'empty/'
    
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
        time.sleep(1)

        # 最近有新评论的五篇文章
        url = f'https://classic-blog.udn.com/blog/inc_2011/psn_article_ajax.jsp?uid=MengyuanWang&f_FUN_CODE=new_rep'
        response = requests.get(url, headers=headers, proxies=proxies)
        status_code = response.status_code
        if status_code == 200:
            doc = BeautifulSoup(response.content, features="lxml")
            id_list += [d('a')[0]['href'].split('/')[-1] for d in doc.findAll('dt')]
        else:
            self.logger.error(f"status {status_code} from {url}")
        time.sleep(1)

        # 评论时间更老但未回复的文章 
        df_comment_noreply = self.df_comment.loc[self.df_comment["reply"].empty
                                                 & (self.df_comment["deleted"] == False)]
        id_list += list(df_comment_noreply["id"].iloc[-10:])

        # 去重 
        id_list = list(set(id_list))

        return id_list

    def fetch_page(self, art_id):

        url = f"https://blog.udn.com/MengyuanWang/{art_id}"
        self.logger.info(f"fetching {url}")
        response = requests.get(url, headers=headers, proxies=proxies)
        status_code = response.status_code

        if status_code != 200:
            self.logger.error(f"status {status_code} from {url}")
            article = []
            comment = []
        else:
            content = response.content
            doc = BeautifulSoup(content, features="lxml")
            article = page2article(doc, art_id)
            comment = page2comment(doc, art_id)

            # 下载图片，修改图片src为本地地址
            for img in doc.find(id="article_show_content").findAll('img'):
                if img.has_attr('src'):
                    src = img.attrs['src'].replace('\r','').replace('\n','')
                    imgID = src.split('/')[-1]
                    img_file = f"{self.html_dir}/img/{imgID}"
                    img_src = f"./img/{imgID}"
                    if not os.path.exists(img_file):
                        img_content = requests.get(src, proxies=proxies).content
                        with open(img_file, "wb") as f:
                            f.write(img_content)
                    img.attrs['src'] = img_src 
        
        return (article, comment) 
    
    def download_page(self, id_list):
        # 获取id_list中的文章和评论
        article_list = [self.df_article]
        comment_list = []
        for art_id in id_list:
            article, comment = self.fetch_page(art_id)
            article_list += article
            comment_list += comment
            time.sleep(1)
        
        # 更新文章
        df_article = pd.concat(article_list, ignore_index=True)
        df_article = df_article.drop_duplicates(subset="id", keep="last")
        df_article = df_article.sort_values("id").reset_index(drop=True)

        # 更新评论
        df_comment_new = pd.concat(comment_list, ignore_index=True)
        for art_id in id_list:
            d1 = df_comment_new.loc[df_comment_new["id"] == art_id]
            d2 = self.df_comment.loc[self.df_comment["id"] == art_id]
            if d1.empty:
                if not d2.empty:
                    self.df_comment.loc[self.df_comment["id"] == art_id, "deleted"] = True
                else:
                    pass
            else:
                min_comment_date = d1["comment_date"].min()
                for idx in d2.index[::-1]:
                    comment_date = d2.loc[idx, "comment_date"]
                    md5 = d2.loc[idx, "md5"]
                    if comment_date < min_comment_date:
                        break
                    else:
                        if md5 not in d1["md5"].values:
                            self.df_comment.loc[idx, "deleted"] = True
        
        df_comment = pd.concat([self.df_comment, df_comment_new], ignore_index=True)
        df_comment = df_comment.groupby(["md5", "comment_date", "id"]).aggregate({"comment": "last",
                                                                                  "reply": "last",
                                                                                  "nickname": "first",
                                                                                  "first_reply_date": "min",
                                                                                  "latest_reply_date": "max", 
                                                                                  "deleted": "first"}).reset_index()
        df_comment = df_comment.sort_values(by=["comment_date", "nickname", "comment"]).reset_index(drop=True)

        self.df_article = df_article
        self.df_comment = df_comment
        df_article.to_pickle(self.article_file)
        df_comment.to_pickle(self.comment_file)
        self.logger.info('comment updated')
        self.logger.info('article updated')
    
    def download_tag(self):
        url = 'https://cjloskjcogrkvhpkfooz.supabase.co/rest/v1/tag?select=*&order=created_at.desc&limit=500'
        headers = {
            'Apikey':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNqbG9za2pjb2dya3ZocGtmb296Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODYwMjIyNjIsImV4cCI6MjAwMTU5ODI2Mn0.peYwcTSZcDd3SvG5Rh99jlM7uyHkUjq1klvqRt2vF5c',
            'Authorization':'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNqbG9za2pjb2dya3ZocGtmb296Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODYwMjIyNjIsImV4cCI6MjAwMTU5ODI2Mn0.peYwcTSZcDd3SvG5Rh99jlM7uyHkUjq1klvqRt2vF5c'
        }
        response = requests.get(url, headers=headers)
        status_code = response.status_code
        if status_code == 200:
            tag_dict = json.loads(response.content)
            df_tag_new = pd.DataFrame(tag_dict).rename(columns={'id': 'md5'})[['md5', 'tag']]
            df_tag = pd.concat([df_tag_new, self.df_tag], ignore_index=True)
            df_tag = df_tag.drop_duplicates(keep='first').reset_index(drop=True)
        else:
            self.logger.error(f"status {status_code} from {url}")
        
        self.df_tag = df_tag
        df_tag.to_pickle(self.tag_file)
        self.logger.info('tag table updated')
    
    def format_post_note(self, art_id):
        post_data_list = []
        if art_id in self.title_dict.keys():
            post_title = self.title_dict[art_id]
        else:
            post_title = self.df_article.loc[self.df_article["id"] == art_id, "title"].iloc[0]
        post_date = self.df_article.loc[self.df_article["id"] == art_id, "art_date"].iloc[0]
        post_date = post_date.strftime("%Y-%m-%d %H:%M:%S")
        post_content = self.merger.split_post(art_id)
        post_md5 = f"{art_id}_article"
        df_post_tag = self.df_tag.loc[self.df_tag["md5"] == post_md5, "tag"]
        if df_post_tag.empty:
            post_tag = "empty/"
        else:
            post_tag = df_post_tag.iloc[0]
        post_data_list.append((art_id, post_title, post_content, post_date, post_md5, post_tag))
        
        note_data_list = []
        note_list = self.merger.split_annotation(art_id)
        idx = 1
        for note_content in note_list:
            note_title = f"{post_title} | 后注{idx}"
            note_md5 = f"{art_id}_note{idx}"
            if note_md5 in self.note_date_dict.keys():
                note_date = self.note_date_dict[note_md5]
            else:
                note_date = extract_date(note_content)
            df_note_tag = self.df_tag.loc[self.df_tag["md5"] == note_md5, "tag"]
            if df_note_tag.empty:
                note_tag = "/empty"
            else:
                note_tag = df_note_tag.iloc[0]
            note_data_list.append((art_id, note_title, note_content, note_date, note_md5, note_tag))
            idx += 1
        return (post_data_list, note_data_list)
    
    def format_comment(self, df_comment_id):
        comment_data_list = []
        for idx in df_comment_id.index:
            art_id = df_comment_id.loc[idx, "id"]
            if art_id in self.title_dict.keys():
                post_title = self.title_dict[art_id]
            else:
                post_title = self.df_article.loc[self.df_article["id"] == art_id, "title"].iloc[0]
            comment = df_comment_id.loc[idx, "comment"]
            deleted = df_comment_id.loc[idx, "deleted"]
            if comment == "":
                continue
            if deleted:
                comment = f"<strike>{comment}</strike>"
            comment = comment.replace('\n','<br><br>')
            comment = comment.replace('<br><br><br>','<br>')
            comment = comment.replace('<br><br><br>','<br>')
            nickname = df_comment_id.loc[idx, "nickname"]
            nickname = nickname.replace('\u3000',' ')
            nickname = f"{post_title} | {nickname}"
            comment_date = df_comment_id.loc[idx, "comment_date"].strftime("%Y-%m-%d %H:%M")
            md5 = df_comment_id.loc[idx, "md5"]
            comment_tag = df_comment_id.loc[idx, "tag"].replace('。','/').replace('、','/')
            reply = df_comment_id.loc[idx, "reply"]
            reply_date = "NaT"
            if reply != "":
                reply = reply.replace('\n', '<br>') 
                reply = re.sub('^<br>', '', reply)
                reply = re.sub('<br>$', '', reply)
                reply = reply.replace('<br>', '<br><br>')
                reply = reply.replace('<br><br><br>','<br>')
                first_reply_date = df_comment_id.loc[idx, "first_reply_date"]
                latest_reply_date = df_comment_id.loc[idx, "latest_reply_date"]
                if str(latest_reply_date) != "NaT":
                    reply_date = latest_reply_date.strftime("%Y-%m-%d %H:%M")
                    if first_reply_date == latest_reply_date:
                        reply += f'<br><div class="TIME">{reply_date} 回复</div>'
                    else:
                        reply += f'<br><div class="TIME"><a href="https://github.com/taizihuang/wmyblog/commits/main/html/{art_id}.html" sytle="color:black;">{reply_date} 修改</a></div>'
                else:
                    pass 
            else:
                pass
            comment_data_list.append((art_id, comment, reply, nickname, comment_date, reply_date, md5, comment_tag, deleted))
        return comment_data_list
    
    def gen_index_page(self):
        df_article = self.df_article 
        df_article["title"] = df_article["id"].map(self.title_dict)
        art_li = []
        for idx in df_article.index[::-1]:
            art_id = df_article.loc[idx, "id"]
            title = df_article.loc[idx, "title"]
            art_date = str(df_article.loc[idx, "art_date"]).split(" ")[0]
            art_li.append((art_id, title, art_date))
    
        index_template_file = f"{self.template_dir}/wmyblog_index.html"
        INDEX = Template(filename=index_template_file)
        html = INDEX.render(art_li=art_li)
        with open(f"{self.html_dir}/../index.html", "w") as f:
            f.write(html)
        self.logger.info(f"{self.html_dir}/index.html saved!")
    
    def gen_article_page(self, art_id):
        post_data, note_data = self.format_post_note(art_id)
        df_comment_id = self.df_comment_tag.loc[self.df_comment_tag["id"] == art_id]
        comment_data = self.format_comment(df_comment_id)
        self.post_list += post_data
        self.note_list += note_data
        self.comment_list += comment_data

        article_template_file = f"{self.template_dir}/wmyblog_page.html"
        html = Template(filename=article_template_file).render(post_data=post_data,
                                                               note_data=note_data,
                                                               comment_data=comment_data)
        with open(f"{self.html_dir}/{art_id}.html", "w", encoding="utf8") as f:
            f.write(html)
    
    def gen_article_pages(self):
        self.post_list = []
        self.note_list = []
        self.comment_list = []
        self.merge_comment_tag()
        for art_id in self.df_article.id:
            self.gen_article_page(art_id)
        
        post_columns = ["id", "title", "content", "date", "md5", "tag"]
        df_post = pd.DataFrame(data=self.post_list, columns=post_columns)
        df_post = df_post.sort_values("date").reset_index(drop=True)

        note_columns = post_columns
        df_note = pd.DataFrame(data=self.note_list, columns=note_columns)
        df_note = df_note.sort_values("date").reset_index(drop=True)

        comment_columns = ["id", "comment", "reply", "nickname", "date", "reply_date", "md5", "tag", "deleted"]
        df_comment = pd.DataFrame(data=self.comment_list, columns=comment_columns)
        df_comment = df_comment.sort_values("date").reset_index(drop=True)

        article_dict = {"article": df_post.to_dict("records")}
        annotation_dict = {"annotation": df_note.to_dict("records")}
        comment_dict = {"comment": df_comment.to_dict("records")}

        with open(f"{self.search_dir}/article.json", "w") as f:
            f.write(json.dumps(article_dict, indent=4, ensure_ascii=False))
        with open(f"{self.search_dir}/annotation.json", "w") as f:
            f.write(json.dumps(annotation_dict, indent=4, ensure_ascii=False))
        with open(f"{self.search_dir}/comment.json", "w") as f:
            f.write(json.dumps(comment_dict, ensure_ascii=False))
        
        df_note1 = df_note.iloc[-30:].copy()
        df_note1 = df_note1.rename(columns={"content": "reply"})
        df_note1["nickname"] = df_note1["title"].map(lambda x: x.split("| ")[-1])
        df_note1["comment"] = df_note1["title"].map(lambda x: x.split("| ")[-1])
        df_note1["comment_date"] = pd.to_datetime(df_note1["date"], format="%Y-%m-%d")
        df_note1["comment_date"] = df_note1["comment_date"].map(lambda x: x + datetime.timedelta(days=1))
        df_note1["reply_date"] = df_note1["comment_date"]
        df_note1["deleted"] = False

        df_comment_note = df_comment.loc[df_comment["reply"] != ""].iloc[-60:].copy()
        df_comment_note["comment_date"] = pd.to_datetime(df_comment_note["date"], format="%Y-%m-%d %H:%M")
        df_comment_note["reply_date"] = pd.to_datetime(df_comment_note["reply_date"], format="%Y-%m-%d %H:%M")
        df_comment_note["nickname"] = df_comment_note["nickname"].map(lambda x: x.split("| ")[-1])
        df_comment_note = pd.concat([df_comment_note, df_note1], ignore_index=True)
        df_comment_note = df_comment_note.sort_values("reply_date", ascending=False).reset_index(drop=True)
        df_comment_note["first_reply_date"] = "NaT"
        df_comment_note["latest_reply_date"] = "NaT"

        comment_data = self.format_comment(df_comment_note)
        comment_data = comment_data[:60]
        refresh_date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        latest_template_file = f"{self.template_dir}/wmyblog_latest.html" 
        LATEST = Template(filename=latest_template_file)
        html = LATEST.render(date=refresh_date, comment_data=comment_data)
        with open(f"{self.html_dir}/new_comment.html", "w", encoding="utf8") as f:
            f.write(html)

        rss_template_file = f"{self.template_dir}/wmyblog_rss.html" 
        RSS = Template(filename=rss_template_file)
        html = RSS.render(date=refresh_date, comment_data=comment_data)
        html = html.replace('&lt;br&gt;','<br>').replace('&lt;','<').replace('&gt;','>')
        with open(f"{self.html_dir}/../rss.xml", "w", encoding="utf8") as f:
            f.write(html)

    def update_data(self):
        id_list = self.get_id_list()
        self.download_tag()
        self.download_page(id_list)

if __name__ == "__main__":
    data_dir = "../data"
    html_dir = "../html"
    template_dir = "./templates"
    wmyblog = Wmyblog(data_dir, html_dir, template_dir) 
    wmyblog.update_data()
    wmyblog.gen_index_page()