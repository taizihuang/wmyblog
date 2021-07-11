import pandas as pd
from mako.template import Template

def genHTML(df_comment,filename):
    HTML = Template("""<!DOCTYPE html><html><head><meta content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no" name=viewport><meta charset=utf-8>
<link rel="stylesheet" href="./init.css">
</head>
<body><div class="BODY">
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
    with open('/mnt/d/Documents/Downloads/'+filename+'.html','w') as f:
        f.write(HTML.render(reply_li=reply_li))
    return

name = ''
df = pd.read_pickle('/mnt/d/Documents/Downloads/comment_full.pkl')
df_comment = df.loc[df.comment.str.contains(name) | df.reply.str.contains(name)]
genHTML(df_comment,name)
