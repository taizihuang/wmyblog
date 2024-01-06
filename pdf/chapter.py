
import re
import pandas as pd
import numpy as np
import hashlib
def comment2md(comment):
    return hashlib.md5((comment.replace('<strike>','').replace('</strike>','')).encode()).hexdigest()

    

rep_list = [
    ('&lt;','<'), ('&gt;','>'), ('&amp;','&'),
    ('<p>','\n'), ('</p>','\n'), ('<br>','\n'),('<br/>','\n'),
    ('%','\%'), ('$','\$'), ('&','\&'),('#','\#'), ('^','\^'), ('_','\_'), ('===','='),
    ('<strike>','\\cancel{'), ('</strike>','}'),
    #math
    ('σ','$\sigma$'), ('r\^2','$r^2$'), ('λ','$\lambda$'), ('π','$\pi$'), ('r\^4','$r^4$'),
    ('∝','$\propto$'), ('ρ','$\\rho$'), ('≈','$\\approx$'), ('\^','\^{}'),
    #special
    ('5d9478403b1a5b12c09b10aaadcdcdcb','empty')
]
rem_list = [
    '\r\n','p="">','<em>','</em>',
    '</span>','<div>','</div>','div>','<h2','h2>',
    '<strong>','</strong>','<code>','</code>','</font>','font color="#656565" face="Microsoft YaHei, Arial">',
    '<div class="articlebox">', '<div id="article\_show\_content">',
    '<div class="POST" style="font-size:16px">', '<p class="DATE">',
    '<p class="MsoNormal">', '<p class="MsoNormal" style="line-height:normal">',
    '<p class="MsoNormal" style="margin-bottom:0.0001pt;line-height:normal"',
    '<p align="center" class="MsoNormal" style="text-align:center;line-height:normal">',
    ' style="font-size:11.5pt;letter-spacing:0.75pt" target="\_blank','\n\n>',
    '<a href="https://www.huffingtonpost.com/entry/trump-trade-war\\_us\\_5ac53929e4b09ef3b2432f64" title="這裏"></a>',
]
    
img_list = [
    ('f_26462958_1'), ('f_25350703_1'), ('2f50f0bffaf439ca5adac6dffafb4618'),
    ('ba77ae1763533d27063da5a3a6da38e0'), ('1255f7d9f3d7178b872880a1ffb96277'),
    ('1e42c210bafb4887d03c25669817fcd7'), ('14f1704e177d6c3985238567b5a613c0'),
    ('29e192984e9ce0086e88a98be3705562'), ('ab6f21134e7dcba1cfbf2e494200f9ef'),
    ('d39156c719714a726b82aae6048a3c41'), ('b314bf52394928e7e7fb213264129366'),
    ('d400eb09ec690963cfd6d651805ad4f0'), ('c624e9ae06a66f951f3d346c7698e9a3'),
]

def formatArticle(df_article, idx):
    title = df_article.loc[idx,'title']
    date = df_article.loc[idx,'art_date'].strftime('%Y-%m-%d %H:%M')
    header = f"\\twocolumn[\\begin{{@twocolumnfalse}}\n\\section{{{title}}}\n\\subsection{{王孟源\\break {date}}}\n\\end{{@twocolumnfalse}}]"
    post = df_article.loc[idx,'post']
    if len(post) < 100:
        return ''

    for rep in rep_list:
        post = post.replace(*rep)

    post = re.sub(r'<span .*?font-size.*?>','',post)
    post = re.sub(r'<span .*?font-family.*?>','',post)
    post = re.sub(r'<span style=.*?>','',post)
    post = re.sub(r'<div style=.*?>','',post)
    post = re.sub(r'<p style=.*?>','',post)
    post = re.sub(r'<font face=.*?>','',post)

    post = re.sub(f'[<span .*>]*<a\ +href="(.+?)".*?>http(.+?)<.*?\/a>[<\/span>]*',r'\\href{\1}{链接\\footnote{\\url{http\2}}}',post)
    post = re.sub(f'[<span .*>]*<a\ +href="(.+?)".*?>(.+?)<.*?\/a>[<\/span>]*',r'\\href{\1}{\2}',post)
    post = re.sub(f'<a href="(.*?)">',r'\\url{\1}',post)
    post = re.sub(f'<span .*標楷體.*?>(.*)<\/span>',r'{\\Kai{\1}}',post)
    post = re.sub(r'<strong>(.*)<\/strong>',r'{\\centering\\Hei{\1}}',post)
    post = re.sub(r'<span .*?underline.*?>(.*)<\/span>',r'\\uline{\1}',post)

    for rem in rem_list:
        post = post.replace(rem,'')

    #image
    matches = re.findall('<img .*src="(.*)".*\/>',post)
    for match in matches:
        post = post.replace(match, match.replace('\_','_').replace('.gif','.jpg'))
        for img in img_list:
            post = post.replace(f'{img}.jpg',f'{img}.png')
    post = re.sub(f'<img .*src="(.*?)".*\/>',r'\\begin{figure}[h]\\centering\\includegraphics[width = 0.9\\linewidth]{../html/\1}\\end{figure}',post)
    post = post.replace('\\begin{figure}[h]\\centering\\includegraphics[width = 0.9\\linewidth]{../html/./img/empty.png}\\end{figure}','')
    post = post.replace('\\begin{figure}[h]\\centering\\includegraphics[width = 0.9\\linewidth]{../html/./img/empty.jpg}\\end{figure}','')

    #table
    if '<table' in post:
        loc1 = post.find('<table')
        loc2 = post.find('/table>')
        post = post.replace(post[loc1:loc2+7],'\\begin{figure}[h]\\centering\\includegraphics[width = 1\\linewidth]{../html/img/table.png}\\end{figure}')

    #list
    if '<ol>' in post:
        post = post.replace('<ol>','\\begin{enumerate}\n').replace('</ol>','\\end{enumerate}\n').replace('<li>','\\item ').replace('</li>','\n').replace('<p style="margin-left:30px">','\n')

    #special
    post = post.replace('P<sub>R</sub>(V)','$P^R(V)$')
    post = post.replace('</','').replace('a>','')
    
    # return header + post
    return header
#

def formatComment(df_id_comment, idx):
    nickname = df_id_comment.loc[idx,'nickname']
    comment_date = df_id_comment.loc[idx,'comment_date'].strftime('%Y/%m/%d %H:%M')
    reply_date = df_id_comment.loc[idx,'latest_reply_date']
    if pd.isnull(reply_date):
        reply_date = '' 
    else:
        reply_date = reply_date.strftime('%Y/%m/%d %H:%M')
    comment = df_id_comment.loc[idx,'comment']
    reply = df_id_comment.loc[idx,'reply'].replace('<br>','<br><br>')


    comment = re.sub(r'(https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*)',r'\\href{\1}{链接\\footnote{\\url{\1}}}',comment)

    reply = re.sub(r'<span .*?font-size.*?>','',reply)
    reply = re.sub(r'<span .*?font-family.*?>','',reply)
    reply = re.sub(r'<span style=.*?>','',reply)
    reply = re.sub(r'<div style=.*?>','',reply)
    reply = re.sub(r'<p style=.*?>','',reply)
    reply = re.sub(r'<font face=.*?>','',reply)

    reply = re.sub(f'[<span .*>]*<a\ +href="(.+?)".*?>http(.+?)<.*?\/a>[<\/span>]*',r'\\href{\1}{链接\\footnote{\\url{http\2}}}',reply)
    reply = re.sub(f'[<span .*>]*<a\ +href="(.+?)".*?>(.+?)<.*?\/a>[<\/span>]*',r'\\href{\1}{\2}',reply)
    reply = re.sub(f'<a href="(.*?)">',r'\\url{\1}',reply)
    reply = re.sub(f'<span .*標楷體.*?>(.*)<\/span>',r'{\\Kai{\1}}',reply)
    reply = re.sub(r'<strong>(.*)<\/strong>',r'{\\centering\\Hei{\1}}',reply)
    reply = re.sub(r'<span .*?underline.*?>(.*)<\/span>',r'\\uline{\1}',reply)
    reply = re.sub(r'(https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*)',r'\\href{\1}{链接\\footnote{\\url{\1}}}',reply)


    for rep in rep_list:
        nickname = nickname.replace(*rep)
        comment = comment.replace(*rep)
        reply = reply.replace(*rep)

    for rem in rem_list:
        reply = reply.replace(rem,'')

    content = f"\\textit{{\\hfill\\noindent\\small {comment_date} 提问；{reply_date} 回答}}\n\n"
    # content += f"{{\\noindent[{idx+1}.]\\ \\ \\ \\ \\Kai {nickname} 问：{comment}}}\n\n"
    content += f"\\noindent[{idx+1}.]"
    content += f"{{\\Hei 答}}：{reply}\\\\\n\n"
    
    return content


content = """
\\documentclass[twocolumn]{ctexart}
\\usepackage{ctex}
\\usepackage{graphicx}
\\usepackage{titlesec}
\\usepackage[hyphens]{url}
\\usepackage[colorlinks=true, urlcolor=blue, linkcolor=black]{hyperref}
\\usepackage{geometry}
\\usepackage{cancel}
\\setmainfont{Times New Roman}
\\setCJKmainfont{SimSun}
\\newCJKfontfamily\Kai{STKaiti}
\\newCJKfontfamily\Hei{SimHei} 
\\setcounter{secnumdepth}{0}
\\setcounter{tocdepth}{1}
\\titleformat*{\\section}{\\centering\\Large\\bfseries }
\\titleformat*{\\subsection}{\\centering}
\\titlespacing*{\\subsection} {0pt}{0pt}{10ex}
\\geometry{a4paper, scale=0.85}
\\begin{document}
\\pagestyle{plain}
"""

articleFile = '../data/article_full.pkl'       
commentFile="../data/comment_full.pkl"
tagFile="../data/tag.pkl"

df_article = pd.read_pickle(articleFile)
df_comment = pd.read_pickle(commentFile)
df_tag = pd.read_pickle(tagFile)

df_tag = df_tag.drop_duplicates('md5').reset_index(drop=True)
df_comment['md5'] = df_comment['comment'].apply(lambda x: comment2md(x))
df_comment_tag = pd.merge(df_comment, df_tag, on='md5',how='left')
df_comment_tag.loc[df_comment_tag.tag.isna(),'tag'] = 'empty/'

idx = (df_comment_tag["tag"].str.contains('经济')) | (df_comment_tag["tag"].str.contains('金融'))
df_chapter = df_comment_tag.loc[idx]
df_chapter =df_chapter.sort_values('id')
id_list = list(df_chapter.id.drop_duplicates().values)


for id in id_list:
    print(id)
    df_article_id = df_article.loc[df_article.id == id].reset_index(drop=True)
    df_comment_id = df_chapter.loc[df_comment.id == id]
    # df_comment_id = df_comment_id.loc[~df_comment.comment.str.contains('<strike')]
    df_comment_id = df_comment_id.loc[df_comment.reply != '']
    df_comment_id = df_comment_id.sort_values('comment_date',ascending=True).reset_index(drop=True)

    # content += formatArticle(df_article_id, 0) + '\n\n'
    content += f'\\section{{{len(df_comment_id)}条问答}}\n\n'

    for idx in df_comment_id.index:
        content += formatComment(df_comment_id, idx)

    content = content.replace('{\Hei 答}：\n\n',r'{\Hei 答}：')
    content = content.replace(r'\&ldquo;','“')
    content = content.replace(r'\&rdquo;','”')

content += '\n \\end{document}'

with open(f'chapter.tex','w',encoding='utf8') as f:
    f.write(content)