import html2text
import pandas as pd
from bs4 import BeautifulSoup
from nltk import word_tokenize

def convert_html_to_text(html_list):
    return [BeautifulSoup(item).get_text() for item in html_list]


games = pd.read_excel("steam_modified.xlsx",index_col=0)

#h = html2text.HTML2Text()
#h.ignore_links = True



det_description_html = games['detailed_description'].tolist()

det_description_text = convert_html_to_text(det_description_html)

#games['detailed_description'] = h.handle(games['detailed_description'])

#print(h.handle("<p><strong>Zed's</strong> dead baby, <em>Zed's</em> dead.</p>"))

print('1')