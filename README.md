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


## 全盘更新，大约2分钟：

```python
import wmyblog_coron as blog # wmyblog_coron.py是库函数，你需要用pip或者conda安装requirements.txt内的依赖
# 更新博客数据
blog.updateBlogData(nTask=20, proxy='', articleUpdate=True,commentFullUpdate=False)
    ## nTask: 协程（≈线程）数量
    ## proxy: 代理地址
    ## articleUpdate: 更新所有文章和文章页面的评论
    ## commentFullUpdate: 更新所有评论

blog.updateBlogPage(days=7,articleFile="./data/article_full.pkl",commentFile="./data/comment_full.pkl")
    ## days: 最新n天的回复
    ## articleFile: 文章dataframe数据地址
    ## commentFile: 评论dataframe数据地址

```

### Git 备忘

```
git add .
git commit -m "1"
git branch -M main
git remote add origin git@github.com:taizihuang/wmyblog.git
git push -u origin main
```
