from wmyblog import *

latest = today() - datetime.timedelta(days=4)
updateDaily(latest)

#updateArticle() #更新文章，保存成pkl和json格式
#updateComment() # 更新评论，保存成pkl和json格式
#genHTMLAll() # 利用文章和评论的pkl文件生成独立的html文件 [不需要联网]
#genINDEX() # 生成文章目录index.html [不需要联网]
