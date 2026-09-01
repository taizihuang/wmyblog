from downloader import Downloader

headers = {
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "sec-ch-ua": "\"Chromium\";v=\"142\", \"Microsoft Edge\";v=\"142\", \"Not_A Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "dnt": "1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "referer": "https://blog.udn.com/MengyuanWang/article",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6,en-CA;q=0.5",
            "cookie": "_td=9505f9ed-d13b-4495-b48e-0b09e6caa60a",
            "priority": "u=0, i"
}

url_list = [f"https://blog.udn.com/v1/blog/guestbook/gblist_ajax.jsp?uid=MengyuanWang&pno={idx}" for idx in range(86, 126)]

Downloader(url_list, headers=headers, tSleep=1, nCache=5, outFilename="../data/guestbook.pkl").run(njob=1)
