import pandas as pd
import hashlib

def comment2md(comment):
    return hashlib.md5((comment.replace('<strike>','').replace('</strike>','').replace("\r\n","").replace('\n','').replace('<br>','')).encode()).hexdigest()

tag_file = f"../data/tag.pkl"
df_tag = pd.read_pickle(tag_file)
df_tag = df_tag.drop_duplicates(subset=["md5"], keep="first")

comment_file = f"../data/comment_full.pkl"
df_comment = pd.read_pickle(comment_file)

df_comment['md5'] = df_comment['comment'].apply(lambda x: comment2md(x))
df_comment_tag = pd.merge(df_comment, df_tag, on='md5',how='left')

tag_list = [
    "建设",
    "问答1000",
    "基础科研",
    "应用技术",
    "学术管理",
    "工业",
    "医学",
    "其他理工",
    "政治",
    "外交",
    "历史",
    "经济",
    "宣传",
    "战略",
    "金融",
    "教育",
    "宗教",
    "其他社科",
    "艺术",
    "文化",
    "人生态度",
    "逻辑",
    "哲学",
    "军事",
    "其他"
]
df_tag = df_comment_tag
df_tag = df_tag.loc[~df_tag["tag"].isna()]
for i in range(len(tag_list)):
    df_tag = df_tag.loc[~df_tag["tag"].str.contains(tag_list[i])]
df_tag