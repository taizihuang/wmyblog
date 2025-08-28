import json, re
import pandas as pd
from bs4 import BeautifulSoup
from mako.template import Template
from downloader import Downloader

def extract_script(doc):
    string_left = 'DOCS_modelChunk = [{'
    string_right = '},{"'
    text = ''
    while string_left in doc:
        loc1 = doc.index(string_left)
        loc2 = doc[loc1:].index(string_right)
        doc_dict = json.loads(doc[loc1+18:loc1+loc2] + '}]')
        loc_idx = 0
        if 's' not in doc_dict[0]:
            loc3 = doc[loc1+loc2+2:].index(string_right)
            doc_dict = json.loads(doc[loc1+18:loc1+loc2+2+loc3] + '}]')
            loc_idx = 1
            if 's' not in doc_dict[1]:
                loc4 = doc[loc1+loc2+2+loc3+2:].index(string_right)
                doc_dict = json.loads(doc[loc1+18:loc1+loc2+loc3+2+loc4+2] + '}]')
                loc_idx = 2
        text += doc_dict[loc_idx]['s']
        doc = doc[loc1+loc2+2:]
    return text

def add_timestamp(content):
    timestamp_list = re.findall(r"<br>(.{3,10}\d{2}:\d{2}) {0,2}<br>", content)
    for timestamp in timestamp_list:
        timestamp = timestamp.replace("<br>", "")
        author = timestamp.split(" ")[0]
        t = timestamp.split(" ")[-1]
        hms = t.split(":")
        if len(hms) == 3:
            ts = 3600*int(hms[0]) + 60*int(hms[1]) + int(hms[2])
        else:
            ts = 60*int(hms[0]) + int(hms[1])

        content = content.replace(timestamp, f'<a onclick="seek({ts})">{author} {t}</a>')
    return content

def save_script(name, url, audio_url, doc, template_dir, out_dir):
    title = name[12:]
    art_date = f"20{name[:2]}-{name[2:4]}-{name[4:6]}" 
    text = extract_script(doc)
    content = text.replace('\n','<br>')
    body = add_timestamp(content)
    html = Template(filename=f"{template_dir}/transcript_page.html").render(title=title,
                                                                            url=url,
                                                                            audio_url=audio_url,
                                                                            date=art_date,
                                                                            body=body)

    docs = BeautifulSoup(html, features="lxml")
    h2_list = []
    for h2 in docs.findAll("h2"):
        h2_list.append(h2.text)
        h2.string = f"""<h2 id="{h2.text}" onclick="scrollPage('toc')">{h2.text}</h2>"""
    
    toc_list = [f"""<div><a onclick="scrollPage('{h2}')">{h2}</a></div>""" for h2 in h2_list]
    docs.find(id="toc").string = "".join(toc_list)
    html_str = str(docs).replace("&lt;", "<").replace("&gt;", ">")
    html_str = html_str.replace("<br/><br/>", "<br/>\n<br/>")
    html_str = html_str.replace("</a><br/>", "</a>\n<br/>")

    filename = name[:12]
    out_file = f'{out_dir}/{filename}.html' 
    with open(out_file,'w',encoding='utf8') as f:
        f.write(html_str)
    print(f'{out_file} saved!')

    return h2_list

def gen_script_page(info_file, audio_file, transcript_file, template_dir, out_dir):
    with open(info_file, "r") as f:
        fileId_dict = json.loads(f.read())
    with open(audio_file, "r") as f:
        audio_dict = json.loads(f.read())
    df_transcript = pd.read_pickle(transcript_file)

    art_li = []
    for key in fileId_dict.keys():
        id = fileId_dict[key]["id"]
        name = fileId_dict[key]["name"]
        url = f'https://docs.google.com/document/d/{id}/edit'
        audio_url = audio_dict[key]
        doc = df_transcript.loc[df_transcript["url"] == url, "response"].iloc[0].decode("utf8")
        h2_list = save_script(name, url, audio_url, doc, template_dir, out_dir)
        art_date = f"20{key[:2]}-{key[2:4]}-{key[4:6]}" 
        art_li.append((key, name[6:], art_date, h2_list))
    
    art_li = art_li[::-1]
    
    INDEX = Template(filename=f"{template_dir}/transcript_index.html")
    with open(f"{out_dir}/transcript.html", "w") as f:
        f.write(INDEX.render(art_li=art_li))

if __name__ == "__main__":
    info_file = "../data/transcript_info.json"
    audio_file = "../data/podcast_url.json"
    transcript_file = "../data/transcript_data.pkl"
    template_dir = "./templates"
    out_dir = "../html"
    gen_script_page(info_file, audio_file, transcript_file, template_dir, out_dir)
