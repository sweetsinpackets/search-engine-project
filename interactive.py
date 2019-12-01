import pandas as pd
import sys, os, pickle, pdb; pdb.set_trace()
import numpy as np
from BM25 import Retrieval_base
from srank import calculate_static_rank
from bs4 import BeautifulSoup

STATIC_WEIGHT = 20

class Retrival_Interface():
    def __init__(self, Rb, query):
        self.Rb = Rb
        self.query = query
        self.panalty_weight = 3
        self.base_retrieve_number = 1000
        self.base_retrieve_list = None
        self.retrieved_game_list = None

    def Base_Retrieve_List(self):
        BM25_list = self.Rb.BM25_retrieval_score(self.query, 1000)
        ranked_game_df = calculate_static_rank()
        self.base_retrieve_list = [(game[0], game[1] + STATIC_WEIGHT * \
            ranked_game_df[(ranked_game_df.name == game[0])]['static_score'].values[0]) for game in BM25_list]
        self.base_retrieve_list.sort(key=lambda tup: -tup[1])
        self.retrieved_game_list = [item[0] for item in self.base_retrieve_list]
        return self.base_retrieve_list
    
    def Panalize_Retrieve_List(self, index):
        description_text = self.Rb.games[(self.Rb.games.name == self.base_retrieve_list[index][0])]['description_text'].values[0]
        panalty_list = self.Rb.BM25_retrieval_score(description_text, 1000)
        
        for i, item in enumerate(panalty_list):
            if item[0] == self.base_retrieve_list[index][0]:
                self.base_retrieve_list[index] = (self.base_retrieve_list[index][0], 0)
            if item[0] in self.retrieved_game_list:
                idx = self.retrieved_game_list.index(item[0])
                self.base_retrieve_list[idx] = (self.base_retrieve_list[idx][0], \
                    self.base_retrieve_list[idx][1] - self.panalty_weight * 2/np.log2(i + 2))
        self.base_retrieve_list.sort(key=lambda tup: -tup[1])
        self.retrieved_game_list = [item[0] for item in self.base_retrieve_list]
        return self.base_retrieve_list  

    def retrieve_detail_info(self, amount):
        return self.Rb.games[(self.Rb.games.name.isin(self.retrieved_game_list[:amount]))]
        
                
         
query = "ancient egypt"
try:
    with open('Retrieval_base.pickle', 'rb') as handle:
        Rb = pickle.load(handle)
except:
    Rb = Retrieval_base()
    with open('Retrieval_base.pickle', 'wb') as handle:
        pickle.dump(Rb, handle, protocol=pickle.HIGHEST_PROTOCOL)
Ri = Retrival_Interface(Rb, query)
base_retrieve_list = Ri.Base_Retrieve_List()
for i, tup_item in enumerate(base_retrieve_list):
    print(i, tup_item)
    if i == 20:
        break

base_retrieve_list = Ri.Panalize_Retrieve_List(3)
for i, tup_item in enumerate(base_retrieve_list):
    print(i, tup_item)
    if i == 20:
        break

print(Ri.retrieve_detail_info(50))