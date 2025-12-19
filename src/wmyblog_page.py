import re, datetime, hashlib, sys, os, time, json
import pandas as pd
from mako.template import Template
from transcript_page import extract_script

def gen_annotation(df):
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
                df_anno = pd.concat([df_anno,pd.DataFrame(data={'comment':comment,  
                                                                'reply':reply,
                                                                'nickname':comment,
                                                                'comment_date':date,
                                                                "first_reply_date": date,
                                                                "latest_reply_date": date,
                                                                'id':id}, index=[0]
                                                        )],ignore_index=True)
    df_anno = df_anno.sort_values(by='comment_date',ascending=False).reset_index(drop=True)
    return df_anno

def gen_index_page(data_dir, template_dir, out_dir):
    article_file = f"{data_dir}/article_full.pkl"
    df_article = pd.read_pickle(article_file)
    art_li = []
    for idx in df_article.index:
        art_id = df_article.loc[idx, "id"]
        title = df_article.loc[idx, "title"]
        art_date = str(df_article.loc[idx, "art_date"]).split(" ")[0]
        art_li.append((art_id, title, art_date))
    
    index_template_file = f"{template_dir}/wmyblog_index.html"
    INDEX = Template(filename=index_template_file)
    html = INDEX.render(art_li=art_li)
    with open(f"{out_dir}/index.html", "w") as f:
        f.write(html)
    print(f"{out_dir}/index.html saved!")

def gen_single_page(art_id, df_article, df_comment_tag, article_template_file, out_dir):
    idx = df_article.loc[df_article["id"] == art_id].index[0]
    title = df_article.loc[idx, "title"]
    art_date = df_article.loc[idx, "art_date"]
    post = df_article.loc[idx, "post"]

    reply_li = []
    df_comment_id = df_comment_tag.loc[df_comment_tag["id"] == art_id]
    df_comment_id = df_comment_id.sort_values(by=["comment_date",
                                                  "nickname",
                                                  "comment"])
    df_comment_id = df_comment_id.drop_duplicates(subset=["comment"], keep="first")
    for idx in df_comment_id.index:
        comment = df_comment_id.loc[idx, "comment"]
        if len(comment) == 0:
            continue
        else:
            comment = comment.replace('\n','<br><br>')
            comment = comment.replace('<br><br><br>','<br>')
            comment = comment.replace('<br><br><br>','<br>')

            reply = df_comment_id.loc[idx, "reply"]
            if len(reply) == 0:
                pass
            else:
                reply = reply.replace('\n', '<br>') 
                reply = re.sub('^<br>', '', reply)
                reply = re.sub('<br>$', '', reply)
                reply = reply.replace('<br>', '<br><br>')
                reply = reply.replace('<br><br><br>','<br>')

                first_reply_date = df_comment_id.loc[idx, "first_reply_date"]
                latest_reply_date = df_comment_id.loc[idx, "latest_reply_date"]
                if str(first_reply_date) != "NaT":
                    reply_date = latest_reply_date.strftime("%Y-%m-%d %H:%M")
                    if first_reply_date == latest_reply_date:
                        reply += f'<br><div class="TIME">{reply_date} 回复</div>'
                    else:
                        reply += f'<br><div class="TIME"><a href="https://github.com/taizihuang/wmyblog/commits/main/html/{art_id}.html" sytle="color:black;">{reply_date} 修改</a></div>'
        nickname = df_comment_id.loc[idx, "nickname"]
        comment_date = df_comment_id.loc[idx, "comment_date"].strftime("%Y-%m-%d %H:%M")
        uuid = df_comment_id.loc[idx, "md5"]
        tag_list = df_comment_id.loc[idx, "tag"].replace('。','/').replace('、','/')
        striked = "<strike>" in comment
        reply_li.append((uuid, comment, reply, nickname, comment_date, tag_list, striked))
    
    html = Template(filename=article_template_file).render(title=title,
                                                   date=art_date,
                                                   art_id=art_id,
                                                   post=post,
                                                   reply_li=reply_li)
    with open(f"{out_dir}/{art_id}.html", "w", encoding="utf8") as f:
        f.write(html)
    # print(f"{out_dir}/{art_id}.html saved!")

def comment2md(comment):
    return hashlib.md5((comment.replace('<strike>','').replace('</strike>','').replace("\r\n","").replace('\n','').replace('<br>','')).encode()).hexdigest()

def get_df(data_dir):
    article_file = f"{data_dir}/article_full.pkl" 
    comment_file = f"{data_dir}/comment_full.pkl" 
    tag_file = f"{data_dir}/tag.pkl" 
    df_article = pd.read_pickle(article_file)
    df_comment = pd.read_pickle(comment_file)
    df_tag = pd.read_pickle(tag_file)

    time_range = [datetime.datetime(2023,11,24,11,0,0),
                  datetime.datetime(2023,11,25,2,0,0)] 
    df_comment = df_comment.loc[~((df_comment['first_reply_date'] >= time_range[0])
                                  & (df_comment['first_reply_date'] <= time_range[1]))]
    df_comment['md5'] = df_comment['comment'].apply(lambda x: comment2md(x))
    df_comment_tag = pd.merge(df_comment, df_tag, on='md5', how='left')
    df_comment_tag.loc[df_comment_tag.tag.isna(),'tag'] = 'empty/'

    return df_article, df_comment_tag

def gen_all_page(data_dir, template_dir, out_dir):
    article_template_file = f"{template_dir}/wmyblog_page.html"
    df_article, df_comment_tag = get_df(data_dir)
    for art_id in df_article["id"]:
        gen_single_page(art_id, df_article, df_comment_tag, article_template_file, out_dir)

def gen_latest_page(data_dir, template_dir, out_dir):
    os.environ['TZ'] = "Asia/Shanghai"
    if sys.platform == 'linux':
        time.tzset()
    refresh_date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    article_file = f"{data_dir}/article_full.pkl" 
    comment_file = f"{data_dir}/comment_full.pkl" 
    df_article = pd.read_pickle(article_file)
    df_comment = pd.read_pickle(comment_file)
    df_anno = gen_annotation(df_article)
    df_merge = pd.concat([df_comment, df_anno], ignore_index=True)
    df_latest = df_merge.sort_values(by="latest_reply_date", ascending=False).iloc[:60]

    reply_li = []
    rss_reply_li = []
    for idx in df_latest.index:
        comment = df_latest.loc[idx, "comment"]
        if len(comment) == 0:
            pass
        else:
            comment = comment.replace('\n','<br><br>')
            comment = comment.replace('<br><br><br>','<br>')
            comment = comment.replace('<br><br><br>','<br>')
            nickname = df_latest.loc[idx, "nickname"].replace('\u3000',' ')
            comment_date = df_latest.loc[idx, "comment_date"]
            rss_comment_date = comment_date.strftime("%Y-%m-%dT%H:%M:%S+0800")
            uuid = comment2md(comment)
            art_id = df_latest.loc[idx, "id"]
            source = df_article.loc[df_article["id"] == art_id, "title"].iloc[0] 
            striked = '<strike>' in comment
            reply = df_latest.loc[idx, "reply"]
            if len(reply) == 0:
                pass
            else:
                reply = reply.replace('\n','<br>')
                reply = reply.replace('src="./img/', 'src="https://wmyblog.site/html/img/') 
                reply = re.sub('^<br>','', reply)
                reply = re.sub('<br>$','', reply)
                reply = reply.replace('<br>','<br><br>')
                reply = reply.replace('<br><br><br>','<br>')
                first_reply_date = df_latest.loc[idx, 'first_reply_date']
                latest_reply_date = df_latest.loc[idx, 'latest_reply_date']
                if str(first_reply_date) != 'NaT':
                    reply_date = latest_reply_date.strftime("%Y-%m-%d %H:%M")
                    if first_reply_date == latest_reply_date:
                        reply += f'<br><div class="TIME">{reply_date} 回复</div>'
                    else:
                        reply += f'<br><div class="TIME"><a href="https://github.com/taizihuang/wmyblog/commits/main/html/{art_id}.html">{reply_date} 修改</a></div>'
            reply_li.append((source, art_id, uuid, comment, reply, nickname, comment_date, striked))
            rss_reply_li.append((source, art_id, uuid, comment, reply, nickname, rss_comment_date, striked))
    latest_template_file = f"{template_dir}/wmyblog_latest.html" 
    LATEST = Template(filename=latest_template_file)
    html = LATEST.render(title="最新回复", date=refresh_date, reply_li=reply_li)
    with open(f"{out_dir}/new_comment.html", "w", encoding="utf8") as f:
        f.write(html)
    
    rss_template_file = f"{template_dir}/wmyblog_rss.html" 
    RSS = Template(filename=rss_template_file)
    html = RSS.render(date=refresh_date, reply_li=rss_reply_li)
    html = html.replace('&lt;br&gt;','<br>').replace('&lt;','<').replace('&gt;','>')
    with open(f"{out_dir}/../rss.xml", "w", encoding="utf8") as f:
        f.write(html)
    print(f"{out_dir}/../rss.xml saved!")

def gen_search_data(data_dir, out_dir):
    df_article, df_comment_tag = get_df(data_dir)
    article_list = []
    title_dict = {}
    for idx in df_article.index:
        id = df_article.loc[idx, "id"]
        title = df_article.loc[idx, "title"]
        art_date = df_article.loc[idx, "art_date"].strftime("%Y-%m-%d %H:%M:%S")
        post = df_article.loc[idx, "post"]
        article_list.append({"id": id,
                             "title": title,
                             "date": art_date,
                             "post":post})
        title_dict[id] = title
    
    df_comment_tag = df_comment_tag.drop_duplicates(subset=['comment'], keep='first')
    comment_list = []
    for idx in df_comment_tag.index:
        id = df_comment_tag.loc[idx, "id"]
        title = title_dict[id]
        nickname = df_comment_tag.loc[idx, "nickname"]
        comment = df_comment_tag.loc[idx, "comment"]
        comment_date = df_comment_tag.loc[idx, "comment_date"].strftime("%Y-%m-%d %H:%M:%S")
        reply = df_comment_tag.loc[idx, "reply"]
        tag = df_comment_tag.loc[idx, "tag"].replace('。','/').replace('、','/')
        md5 = df_comment_tag.loc[idx, "md5"]
        if len(reply) != 0:
            comment_list.append({"id": id,
                                 "title": title,
                                 "nickname": nickname,
                                 "date": comment_date,
                                 "comment": comment,
                                 "reply": reply,
                                 "tag":tag,
                                 "md5":md5
                                 })
        else:
            pass
    
    info_file = f"{data_dir}/transcript_info.json"
    transcript_file = f"{data_dir}/transcript_data.pkl"
    with open(info_file, "r") as f:
        info_dict = json.loads(f.read())
    df_transcript = pd.read_pickle(transcript_file)

    transcript_list = []
    for key in info_dict.keys():
        id = info_dict[key]["id"]
        title = info_dict[key]["name"]
        url = f"https://docs.google.com/document/d/{id}/edit"
        doc = df_transcript.loc[df_transcript["url"] == url, "response"].iloc[0].decode("utf8")
        content = extract_script(doc)
        art_date = f"20{key[:2]}-{key[2:4]}-{key[4:6]}"
        for chapter in content.split("<h2>"):
            if "</h2>" in chapter:
                title, content = chapter.split("</h2>")
            else:
                content = chapter
            if title != "片花":
                transcript_list.append({"key": key,
                                    "title": title,
                                    "date": art_date,
                                    "content": content})
    
    article_dict = {"article": article_list}
    comment_dict = {"comment": comment_list}
    transcript_dict = {"transcript": transcript_list}
    with open(f"{out_dir}/article.json", "w") as f:
        f.write(json.dumps(article_dict, indent=4, ensure_ascii=False))
    with open(f"{out_dir}/comment.json", "w") as f:
        f.write(json.dumps(comment_dict, ensure_ascii=False))
    with open(f"{out_dir}/transcript.json", "w") as f:
        f.write(json.dumps(transcript_dict, indent=4, ensure_ascii=False))
    print(f"{out_dir}/search.json saved!")

if __name__ == "__main__":
    data_dir = "../data"
    template_dir = "./templates"

    gen_index_page(data_dir, template_dir, out_dir="..")
    gen_all_page(data_dir, template_dir, out_dir="../html")
    gen_latest_page(data_dir, template_dir, out_dir = "../html")
    gen_search_data(data_dir, out_dir="../search")
