# 使用方法

【Actions每小时更新】

直接访问：https://taizihuang.github.io/wmyblog

模板来自：https://wmyblog.github.io


## 在线搜索

请访问 https://taizihuang.github.io/wmyblog/search/

## 离线搜索

Chrome 用户：彻底关闭Chrome。单击 **search** 目录下 `open_in_Chrome_windows.bat` 批处理文件

Edge 用户：彻底关闭Edge。单击 **search** 目录下 `open_in_Edge_windows.bat` 批处理文件

出于安全考虑，搜索结束请关闭Chrome/Edge，并按正常方式打开。

原理：由于Chrome默认禁止ajax访问本地文件，如需使用离线搜索功能，需要开启本地文件系统：
```bat
start C:\"Program Files"\Google\Chrome\Application\chrome.exe --allow-file-access-from-files %cd%/index.html
start C:\"Program Files (x86)"\Microsoft\Edge\Application\msedge.exe --allow-file-access-from-files %cd%/index.html
```
如果Chrome不是安装在默认目录，需要手动修改路径。




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
