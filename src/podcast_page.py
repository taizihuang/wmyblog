from mako.template import Template
import pandas as pd
import json, datetime

def gen_podcast_page(info_file, audio_file, template_file, out_dir):
    current_date = datetime.date.today().strftime("%a, %d %b %Y")
    with open(info_file) as f:
        info_dict = json.loads(f.read())
    with open(audio_file) as f:
        audio_dict = json.loads(f.read())

    item_li = []
    for key in info_dict.keys():
        title = info_dict[key]["name"][12:]
        date = pd.to_datetime(f"20{key[:6]}", format="%Y%m%d")
        pub_date = date.strftime("%a, %d %b %Y")
        audio_url = audio_dict[key]
        item_li.append((title, pub_date, key, audio_url))
    
    RSS = Template(filename=template_file)
    html = RSS.render(current_date=current_date, item_li=item_li)
    with open(f"{out_dir}/podcast.xml", "w") as f:
        f.write(html)
    print(f"{out_dir}/podcast.xml saved!")

if __name__ == "__main__":
    info_file = "../data/transcript_info.json"
    audio_file = "../data/podcast_url.json"
    template_file = "./templates/podcast_index.html"
    out_dir = "../podcast"
    gen_podcast_page(info_file, audio_file, template_file, out_dir)