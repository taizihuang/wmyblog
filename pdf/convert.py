import pdfkit
import pandas as pd
df = pd.read_pickle('./data/article_full.pkl')
for idx in df.index:
    id = df.loc[idx,'id']
    title = df.loc[idx,'title']
    d = df.loc[idx,'art_date']
    try:
        pdfkit.from_file('./html/'+id+'.html','./pdf/'+d.strftime('%Y-%m-%d %H')+' '+title+'.pdf')
    except:
        pass