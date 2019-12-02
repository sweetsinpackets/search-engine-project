from interactive import Retrival_Interface
import pandas as pd
import sys, os, pickle, pdb
import numpy as np
from BM25 import Retrieval_base
from srank import calculate_static_rank
from bs4 import BeautifulSoup

class User(Retrival_Interface):
    def __init__(self):
        self.query_set = []
    def user_search(self, query):
        self.query_set.append(query)
    def recommend_a_game(self, Rb):
        new_query = ""
        for query in self.query_set:
            new_query = new_query + ' ' + query
        Ri = Retrival_Interface(Rb, new_query, 1)
        output = Ri.Base_Retrieve_List()[0]
        return output

try:
    with open('Retrieval_base.pickle', 'rb') as handle:
        Rb = pickle.load(handle)
except:
    Rb = Retrieval_base()
    with open('Retrieval_base.pickle', 'wb') as handle:
        pickle.dump(Rb, handle, protocol=pickle.HIGHEST_PROTOCOL)

user1 = User()
user1.user_search('love')
user1.user_search('police and thief')
user1.user_search('civilization')
user1.user_search('wo ai mama')
user1.user_search('list a tiger')
print(user1.recommend_a_game(Rb))
        