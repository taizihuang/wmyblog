import pandas as pd
from mako.template import Template

def genHTML(df_comment,filename):
    HTML = Template("""<!DOCTYPE html><html><head><meta content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no" name=viewport><meta charset=utf-8>
<link rel="stylesheet" href="../html/init.css">
</head>
<body><div class="BODY">
<h1>${filename}</h1>
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
</body></html>""")
    # save html
    reply_li = []
    for j in df_comment.index:
        comment = df_comment.comment[j]
        if comment:
            reply = df_comment.reply[j].replace("\n\n","\n")
            nickname = df_comment.nickname[j]
            comment_date = df_comment.date[j]
            reply_li.append((comment,reply,nickname,comment_date))
    with open('./search/'+filename+'.html','w') as f:
        f.write(HTML.render(filename=filename,reply_li=reply_li))
    return


search_list = {
    'Quasicat': ['弃车']
    }
flag = 0 # 0: 正常搜索；1: 互斥搜索。比如，'科幻'的搜索结果内不包含['教育','思考','读书']，'美国'的搜索结果不包含关键词 ['教育','思考','读书','科幻','Asimov']。

df = pd.read_pickle('./data/comment_full.pkl')
df['flag'] = 0

for filename in search_list.keys():
    name = search_list[filename]
    idx = df.comment.str.contains(name[0]) | df.reply.str.contains(name[0]) | df.nickname.str.contains(name[0])
    if len(name) > 1:
        for i in range(1,len(name)):
            idx = idx | df.comment.str.contains(name[i]) | df.reply.str.contains(name[i]) | df.nickname.str.contains(name[i])

    df_comment = df.loc[idx & (df.flag == 0)]
    df_comment = df_comment.sort_values(by='date')
    genHTML(df_comment,filename)
    df.loc[idx,'flag'] = flag
