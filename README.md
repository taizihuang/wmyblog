# 使用方法

https://taizihuang.github.io/wmyblog

用python脚本或者jupyter notebook执行：

```python
from wmyblog import * # wmyblog.py是库函数，你需要用pip或者conda安装相应的包

os.environ['http_proxy'] = "http://127.0.0.1:xxxx" #代理的端口
os.environ['https_proxy'] = "http://127.0.0.1:xxxx"

updateArticle() #更新文章，保存成pkl和json格式
updateComment() # 更新评论，保存成pkl和json格式
genHTML() # 利用文章和评论的pkl文件生成独立的html文件 [不需要联网]
genINDEX() # 生成文章目录index.html [不需要联网]
```

安卓手机可以在Termux上面安装python，实现随时随地更新文章，亲测好用。



# Git 备忘

```
git add .
git commit -m "1"
git branch -M main
git remote add origin git@github.com:taizihuang/pythonChallenge.git
git push -u origin main
```
