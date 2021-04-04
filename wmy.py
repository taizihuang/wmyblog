from wmyblog import *

os.environ['http_proxy'] = "http://127.0.0.1:7890" 
os.environ['https_proxy'] = "http://127.0.0.1:7890"

# old comments
li = list(open("data.json"))
df_link = getPageLinkAll()
df_comment = pd.DataFrame(columns=['comment','reply','nickname','date','id'])
for n in range(len(li)):
    article = json.loads(li[n])
    if article[4]:
        df0 = pd.DataFrame(article[4],columns=['comment','reply','nickname','date'])
    else:
        df0 = pd.DataFrame([['','','','']],columns=['comment','reply','nickname','date'])
    if n != 0:
        df0['id'] = df_link.loc[df_link.title == article[1]].id.values[0]
    else:
        df0['id'] = "108908829"
    df_comment = pd.concat([df_comment,df0],ignore_index=True)
df_comment=df_comment.loc[df_comment.nickname != "tessie"]
df_comment=df_comment.loc[df_comment.nickname != "好康优选"]
df_comment=df_comment.loc[df_comment.nickname != "?E m ail="]
df_comment.date = pd.to_datetime(df_comment.date,format="%Y-%m-%d")

# old article
def mergeArticle():
    # Merge Old New Article
    # Load old file
    #df_link = getPageLinkAll()
    df_article_old = pd.DataFrame(columns=['id','title','art_date','post'])
    data = list(open("data.json"))
    for i in range(len(data)):
        art = json.loads(data[i])
        df0 = pd.DataFrame([[art[1],art[2],art[3]]],columns=['title','art_date','post'])
        if i != 0:
            df0['id'] = df_link.loc[df_link.title == art[1]].id.values[0]
        else:
            df0['id'] = "108908829"
        df_article_old = pd.concat([df_article_old,df0],ignore_index=True)
    df_article_old.art_date = pd.to_datetime(df_article_old.art_date,format="%Y-%m-%d")

    # Load new file
    df_article_new = pd.DataFrame(columns=['id','title','art_date','post'])
    for i in list(open('article.json')):
        # Article
        art = json.loads(i)
        id = art[0]
        title = art[1]
        art_date = art[2]
        post = art[3]
        df0 = pd.DataFrame([[id,title,art_date,post]],columns=['id','title','art_date','post'])
        df_article_new = pd.concat([df_article_new,df0],ignore_index=True)
    df_article_new.art_date = pd.to_datetime(df_article_new.art_date,format="%Y/%m/%d %H:%M")
    df_article = df_article_new.append(df_article_old,ignore_index=True)

    # Save merged file
    article_li = []
    for i in df_article.index:
        id = df_article.iloc[i].id
        title = df_article.iloc[i].title
        art_date = df_article.iloc[i].art_date
        post = df_article.iloc[i].post
        article_li.append([id,title,art_date,post])
    with open('article_full.json','wb') as data:
        for i in range(len(article_li)):
            article_li[i][2] = str(article_li[i][2])
            s = json.dumps(article_li[i]) + "\n"
            data.write(s.encode('utf-8'))
    return 