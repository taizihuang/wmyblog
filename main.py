import sys
sys.path.append("src")

from wmyblog import Wmyblog

data_dir = "./data"
html_dir = "./html"
template_dir = "./src/templates"
search_dir = "./search"
wmyblog = Wmyblog(data_dir, html_dir, template_dir, search_dir) 
# wmyblog.update_data()
wmyblog.gen_article_pages()
wmyblog.gen_index_page()