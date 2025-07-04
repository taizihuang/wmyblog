# 使用方法

【Actions每六小时更新】

直接访问：https://wmyblog.site

《王孟源文集》和《王孟源访谈》：https://book.wmyblog.site

模板来自：https://wmyblog.github.io


## 在线搜索

请访问 https://wmyblog.site/search/

## 离线搜索

**方法一：**

安装 Python, 在当前目录下运行 `python3 -m http.server 8000`，然后浏览器访问 `localhost:8000/search/index.html`

**方法二：**

Chrome 用户：彻底关闭Chrome。单击 **search** 目录下 `open_in_Chrome_windows.bat` 批处理文件

Edge 用户：彻底关闭Edge。单击 **search** 目录下 `open_in_Edge_windows.bat` 批处理文件

出于安全考虑，搜索结束请关闭Chrome/Edge，并按正常方式打开。

原理：由于Chrome默认禁止ajax访问本地文件，如需使用离线搜索功能，需要开启本地文件系统：
```bat
start C:\"Program Files"\Google\Chrome\Application\chrome.exe --allow-file-access-from-files %cd%/index.html
start C:\"Program Files (x86)"\Microsoft\Edge\Application\msedge.exe --allow-file-access-from-files %cd%/index.html
```
如果Chrome不是安装在默认目录，需要手动修改路径。


## 更新：

```bash
python main.py
```
