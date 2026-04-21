import sys
sys.path.append("src")

from tag_data import updateTag
from wmyblog_data import update_data
from wmyblog_page import gen_index_page, gen_all_page, gen_latest_page, gen_search_data

data_dir = "./data"
ct_dir = "./data/ct_article"
img_dir = "./html/img"
template_dir = "./src/templates"

#updateTag(data_dir)
update_data(data_dir, img_dir)
gen_index_page(data_dir, template_dir, out_dir=".")
gen_all_page(data_dir, ct_dir, template_dir, out_dir="./html")
gen_latest_page(data_dir, template_dir, out_dir = "./html")
gen_search_data(data_dir, ct_dir, out_dir="./search")
