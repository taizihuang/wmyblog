import pandas as pd
import json, requests

def updateTag(data_dir):

    tag_file = f"{data_dir}/tag.pkl"
    df_tag = pd.read_pickle(tag_file)

    url = 'https://cjloskjcogrkvhpkfooz.supabase.co/rest/v1/tag?select=*&order=created_at.desc&limit=500'
    headers = {
        'Apikey':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNqbG9za2pjb2dya3ZocGtmb296Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODYwMjIyNjIsImV4cCI6MjAwMTU5ODI2Mn0.peYwcTSZcDd3SvG5Rh99jlM7uyHkUjq1klvqRt2vF5c',
        'Authorization':'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNqbG9za2pjb2dya3ZocGtmb296Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODYwMjIyNjIsImV4cCI6MjAwMTU5ODI2Mn0.peYwcTSZcDd3SvG5Rh99jlM7uyHkUjq1klvqRt2vF5c'
    }
    tag_dict = json.loads(requests.get(url, headers=headers).content)
    df_tag_new = pd.DataFrame(tag_dict).rename(columns={'id': 'md5'})[['md5', 'tag']]
    df_tag = pd.concat([df_tag_new,df_tag], ignore_index=True).drop_duplicates(keep='first').reset_index(drop=True)
    df_tag.to_pickle(tag_file)
    print('tag table updated')

if __name__ == "__main__":
    tag_file = "../data"
    updateTag(tag_file)