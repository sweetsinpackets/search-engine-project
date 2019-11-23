import html2text
import pandas as pd
from bs4 import BeautifulSoup
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer



def convert_html_to_text(html_list):
    return [BeautifulSoup(item).get_text() for item in html_list]

def description_preprocess(det_description_text):
    # tokenize (remove punctuation)
    tokenizer = RegexpTokenizer(r'\w+')
    tokens_list = [tokenizer.tokenize(item) for item in det_description_text]

    # lower case
    tokens_list_lower = []
    for tokens in tokens_list:
        tokens_list_lower.append([w.lower() for w in tokens])

    # remove stop words
    stop_words = set(stopwords.words('english')) 
    filtered_sentence = []
    for tokens in tokens_list_lower:
        filtered_sentence.append([w for w in tokens if w not in stop_words])

    return filtered_sentence




# Read data
games = pd.read_excel("steam_clean.xlsx",index_col=0)

# Series to list
det_description_html = games['detailed_description'].tolist()

# convert html to text
det_description_text = convert_html_to_text(det_description_html)

det_description_final = description_preprocess(det_description_text)


#games['detailed_description'] = h.handle(games['detailed_description'])

#print(h.handle("<p><strong>Zed's</strong> dead baby, <em>Zed's</em> dead.</p>"))

print('1')