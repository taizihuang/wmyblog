import asyncio,aiohttp,platform,os,json
import pandas as pd

class Downloader:

    def __init__(self, url_list, 
                        request_type='get', 
                        headers='', 
                        json_data='', 
                        proxy='',
                        tSleep=1,
                        nCache=500,
                        nRetry=3,
                        str_list=[],
                        decode='utf8',
                        reverse=False,
                        override=True,
                        outFilename='out.pkl'):
        self.url_list = url_list
        self.headers = headers
        self.json_data = json_data
        self.proxy = proxy
        self.request_type = request_type
        self.tSleep = tSleep
        self.nCache = nCache
        self.nRetry = nRetry
        self.str_list = str_list 
        self.decode = decode
        self.errorString = b'NULL from response'
        self.reverse=reverse
        self.override=override
        self.outFilename = outFilename
        
        if os.path.exists(self.outFilename):
            self.df = pd.read_pickle(self.outFilename)
        else:
            self.df = pd.DataFrame()
    
    def fetchError(self):
        url_error = []
        if not self.df.empty:
        #    url_error = list(self.df.loc[self.df.response == self.errorString].url)
        #    url_error += list(self.df.loc[self.df.response == b''].url)
        #    if self.str_list:
        #        for s in self.str_list:
        #            url_error += list(self.df.loc[self.df.response.map(lambda x: x.decode(self.decode).find(s)) > 0].url)

        #    url_error = list(set(url_error))
            url_error = list(self.df.loc[self.df['status'] != 200, 'url'])
        return url_error

    def url_todo(self):
        url_done = []
        if not self.df.empty:
            url_done = list(self.df.url)
        url_error = self.fetchError()
        url_todo = list(set(self.url_list).difference(url_done)) 
        url_todo += url_error
        url_todo = list(set(url_todo))

        return url_todo
    
    async def fetchResponse(self, url):
        if self.request_type == 'get':
            df = await self.get(url)
        elif self.request_type == 'post':
            df = await self.post(url)
        return df

    async def get(self, url):
        try:
            async with self.sem:
                async with aiohttp.ClientSession(headers=self.headers) as session:
                    async with session.get(url=url, headers=self.headers, proxy=self.proxy) as response:
                        code = response.status
                        res = await response.read()
                        await asyncio.sleep(self.tSleep)
        except:
            res = self.errorString
            code = 400

        return pd.DataFrame(data={'url':url, 'response': res, 'status': code},index=[0])

    async def post(self, url):
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                if self.reverse is True:
                    true_url = self.json_data
                    true_json = json.loads(url)
                else:
                    true_url = url
                    true_json = json.loads(self.json_data)
                async with session.post(url=true_url, headers=self.headers, json=true_json) as response:
                    code = response.status
                    res = await response.read()
                    await asyncio.sleep(self.tSleep)
        except:
            res = self.errorString
            code = 400
        
        return pd.DataFrame(data={'url':url, 'response': res, 'status': code},index=[0])
    
    async def tasker(self, njob):
        self.sem = asyncio.Semaphore(njob)
        n = 0
        url_todo = self.url_todo()
        if self.override == True:
            url_todo += self.url_list
            url_todo = list(set(url_todo))
        else:
            pass
        print(f'{len(url_todo)} urls to be downloaded')
        while (url_todo != []) and (n < 3):
            for idx in list(range(len(url_todo)))[::self.nCache]:
                task_list = [self.fetchResponse(url) for url in url_todo[idx:idx+self.nCache]]
                L = await asyncio.gather(*task_list)
                self.df = pd.concat([self.df] + L, ignore_index=True).drop_duplicates(subset=['url'],keep='last')
                self.df.to_pickle(self.outFilename)
                print(f'<{n+1}>: Fetching {idx+self.nCache} entries')
            url_todo = self.url_todo()
            n += 1

    def run(self, njob=10):
        if platform.system() == 'Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(self.tasker(njob))
        print('done')
        return self.df

def fetchNullUrl(df):
    #url_null = list(df.loc[df.response == b'NULL from response'].url)
    #url_null += list(df.loc[df.response.map(lambda x: x.find(b'Just a moment')) > 0].url)
    url_null = list(df.loc[df['status'] != 200, 'url'])
    return url_null

def retry(dfFilename, proxy=''):
    df = pd.read_pickle(dfFilename)
    url_null = fetchNullUrl(df)
    if os.path.exists('retry.pkl'):
        os.remove('retry.pkl')
    if len(url_null) > 0:
        print(f'retry: {dfFilename} {len(url_null)} null responses')
        #logging.info(f'retry: {dfFilename} {len(url_null)} null responses')
        df_retry = Downloader(url_null, proxy=proxy, tSleep=5, outFilename='retry.pkl').run()
        df = pd.concat([df_retry, df],ignore_index=True).drop_duplicates(subset='url', keep='first')
        df.to_pickle(dfFilename)
    return df

        
