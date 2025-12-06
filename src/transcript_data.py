import json
from downloader import Downloader

def download_transcript(info_file, out_file, latest_num=5):
    """
    download and update latest transcripts
    if latest_num <= 0, then update the whole data
    """
    with open(info_file) as f:
        fileId_dict = json.loads(f.read())

    if latest_num <= 0:
        key_list = list(fileId_dict.keys()) 
    else:
        key_list = list(fileId_dict.keys())[-latest_num:] 

    url_list = []
    for key in key_list:
        id = fileId_dict[key]["id"]
        url_list.append(f'https://docs.google.com/document/d/{id}/edit')
    Downloader(url_list, nCache=2, override=True, outFilename=out_file).run()

if __name__ == "__main__":
    info_file = "../data/transcript_info.json"
    out_file = "../data/transcript_data.pkl"
    latest_num = -1 
    download_transcript(info_file, out_file, latest_num)
