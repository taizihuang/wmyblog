# 使用方法

【Actions每小时更新】

直接访问：https://taizihuang.github.io/wmyblog

模板来自：https://wmyblog.github.io


## 问答搜索

修改文件 **search.py** 内的 **search_list** 字典和 **flag** ：
```python
search_list = {
    '教育': ['教育','思考','读书'],
    '科幻': ['科幻','Asimov'],
    '美国': ['美国']
    }
flag = 0 # 0: 正常搜索；1: 互斥搜索。'美国'的搜索结果不包含关键词 ['教育','思考','读书','科幻','Asimov']
```
执行 `python search.py`，搜索结果放在文件夹 `./search`内。


## 全盘更新，大约15分钟：

```python
from wmyblog import * # wmyblog.py是库函数，你需要用pip或者conda安装requirements.txt内的依赖

os.environ['http_proxy'] = "http://127.0.0.1:xxxx" #代理的端口
os.environ['https_proxy'] = "http://127.0.0.1:xxxx"

updateArticle() #更新文章，保存成pkl和json格式
updateComment() # 更新评论，保存成pkl和json格式
genHTMLAll() # 利用文章和评论的pkl文件生成独立的html文件 [不需要联网]
genINDEX() # 生成文章目录index.html [不需要联网]
```

## 每日更新，只需10秒：

```python
from wmyblog import *

os.environ['http_proxy'] = "http://127.0.0.1:xxxx" #代理的端口
os.environ['https_proxy'] = "http://127.0.0.1:xxxx"

latest = today() - datetime.timedelta(days=2) #获取近三日的评论与回复
updateDaily(latest) 
```

安卓手机可以在Termux上面安装python，实现随时随地更新文章，亲测好用。


### Git 备忘

```
git add .
git commit -m "1"
git branch -M main
git remote add origin git@github.com:taizihuang/wmyblog.git
git push -u origin main
```
