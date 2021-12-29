from wmyblog import *

#os.environ['http_proxy'] = "http://127.0.0.1:7890" #代理的端口
#os.environ['https_proxy'] = "http://127.0.0.1:7890"

latest = today() - datetime.timedelta(days=14)
updateDaily(latest)

#updateArticle() #更新文章，保存成pkl和json格式
#updateComment() # 更新评论，保存成pkl和json格式
genHTMLAll() # 利用文章和评论的pkl文件生成独立的html文件 [不需要联网]
genINDEX() # 生成文章目录index.html [不需要联网]
