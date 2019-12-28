import pandas as pd
import sys, os, pickle, pdb
import numpy as np
from BM25 import Retrieval_base
from srank import calculate_static_rank
from bs4 import BeautifulSoup

STATIC_WEIGHT = 10

def getKeysByValues(dictOfElements, listOfValues):
    listOfKeys = list()
    listOfItems = dictOfElements.items()
    for item  in listOfItems:
        if item[1] in listOfValues:
            listOfKeys.append(item[0])
    return  listOfKeys 

class Retrival_Interface():
    def __init__(self, Rb, query, base_retrieve_number):
        self.Rb = Rb
        self.query = query
        self.panalty_weight = 3
        self.PseudoFB_weight = 1
        self.base_retrieve_number = base_retrieve_number
        self.base_retrieve_list = None
        self.retrieved_game_list = None
        self.PseudoFB_number = 5
        self.PseudoFB_round = 2
        self.query_correction_flag = False
        self.final_query = None

    def Base_Retrieve_List(self):
        BM25_list = self.Rb.BM25_retrieval_score(self.query, self.base_retrieve_number, True)
        self.query_correction_flag = self.Rb.query_correction_flag
        if self.Rb.query_correction_flag:
            self.final_query = ' '.join(self.Rb.query)
        else:
            self.final_query = self.query
        self.Rb.query_correction_flag = False
        ranked_game_df = calculate_static_rank()
        self.base_retrieve_list = []
        for game in BM25_list:
            static_rank = ranked_game_df[(ranked_game_df.name == game[0])]['static_rank'].values[0]
            static_score = STATIC_WEIGHT / np.log2(static_rank + 1)
            self.base_retrieve_list.append((game[0], game[1] * static_score))
        self.base_retrieve_list.sort(key=lambda tup: -tup[1])
        self.retrieved_game_list = [item[0] for item in self.base_retrieve_list]
        for PFB_round in range(self.PseudoFB_round):
            print('PFB round', PFB_round)
            self.PseudoFB_Retrieve_List()
        self.Rb.query = None
        self.Rb.query_correction_flag = False
        return self.base_retrieve_list
    
    def PseudoFB_Retrieve_List(self):
        for PFB_i in range(self.PseudoFB_number):
            appid = self.Rb.games[(self.Rb.games.name == self.retrieved_game_list[PFB_i])]['appid'].values[0]
            game_name = self.retrieved_game_list[PFB_i]
            index = PFB_i
            # pdb.set_trace()
            description_text = self.Rb.games[(self.Rb.games.appid == appid)]['description_text'].values[0]
            PseudoFB_list = self.Rb.BM25_retrieval_score(description_text, self.base_retrieve_number, False)
            for i, item in enumerate(PseudoFB_list):
                if item[0] in self.retrieved_game_list and item[0] != game_name:
                    idx = self.retrieved_game_list.index(item[0])
                    self.base_retrieve_list[idx] = (self.base_retrieve_list[idx][0], \
                        self.base_retrieve_list[idx][1] + self.PseudoFB_weight * 2/np.log2(i + 2))
        for PFB_i in range(self.PseudoFB_number):
            appid = self.Rb.games[(self.Rb.games.name == self.retrieved_game_list[-PFB_i])]['appid'].values[0]
            game_name = self.retrieved_game_list[-PFB_i]
            index = -PFB_i
            # pdb.set_trace()
            description_text = self.Rb.games[(self.Rb.games.appid == appid)]['description_text'].values[0]
            PseudoFB_list = self.Rb.BM25_retrieval_score(description_text, self.base_retrieve_number, False)
            for i, item in enumerate(PseudoFB_list):
                if item[0] in self.retrieved_game_list and item[0] != game_name:
                    idx = self.retrieved_game_list.index(item[0])
                    self.base_retrieve_list[idx] = (self.base_retrieve_list[idx][0], \
                        self.base_retrieve_list[idx][1] - self.PseudoFB_weight * 2/np.log2(i + 2))
        self.base_retrieve_list.sort(key=lambda tup: -tup[1])
        self.retrieved_game_list = [item[0] for item in self.base_retrieve_list]
        return self.base_retrieve_list  

    def Panalize_Retrieve_List(self, appid):
        game_name = self.Rb.games[(self.Rb.games.appid == appid)]['name'].values[0]
        index = None
        for i, tup in enumerate(self.base_retrieve_list):
            if tup[0] == game_name:
                index = i
        if index == None:
            return self.base_retrieve_list
        description_text = self.Rb.games[(self.Rb.games.appid == appid)]['description_text'].values[0]
        panalty_list = self.Rb.BM25_retrieval_score(description_text, self.base_retrieve_number, False)
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

    def query_suggestion(self, amount) -> 'a list of str':
        keyword_list = [w.lower() for w in self.final_query.split()]
        word_suggestion_score_array = np.zeros(self.Rb.BM25_mat.shape[1])
        for item in self.base_retrieve_list:
            game_index = self.Rb.games[(self.Rb.games.name == item[0])].index.values[0]
            word_suggestion_score_array += self.Rb.BM25_mat[game_index].toarray().squeeze()
        word_index_list = word_suggestion_score_array.argsort()[-amount-len(keyword_list):]
        key_list = getKeysByValues(self.Rb.vectorizer.vocabulary_, word_index_list)
        suggestion_list = [self.final_query + ' ' + key for key in key_list if key not in keyword_list]
        return suggestion_list

    def retrieve_detail_info(self, amount):
        output = self.Rb.games[(self.Rb.games.name.isin(self.retrieved_game_list[:amount]))]
        output.drop(['detailed_description', 'about_the_game','short_description', 'steamspy_tags'], axis = 1, inplace = True)
        output['rank'] = output['name'].apply(lambda x: self.retrieved_game_list.index(x))
        output.set_index('appid', inplace = True)
        output.sort_values(by=['rank'], inplace = True)
        return output
        
def main():
    query = "Ancient Egypt123"
    try:
        with open('Retrieval_base.pickle', 'rb') as handle:
            Rb = pickle.load(handle)
    except:
        Rb = Retrieval_base()
        with open('Retrieval_base.pickle', 'wb') as handle:
            pickle.dump(Rb, handle, protocol=pickle.HIGHEST_PROTOCOL)
    Ri = Retrival_Interface(Rb, query, 1000)
    
    base_retrieve_list = Ri.Base_Retrieve_List()

    if_corrected = Ri.query_correction_flag
    print('If query is corrected: ', if_corrected)
    print('Final Query: ', Ri.final_query)

    suggestion_list = Ri.query_suggestion(5)

    # for i, tup_item in enumerate(base_retrieve_list):
    #     print(i, tup_item)
    #     if i == 20:
    #         break
    # # base_retrieve_list = Ri.Panalize_Retrieve_List(12450)
    # for i, tup_item in enumerate(base_retrieve_list):
    #     print(i, tup_item)
    #     if i == 20:
    #         break

    out_df = Ri.retrieve_detail_info(50)
    print(out_df)
    print(suggestion_list)

if __name__ == "__main__":
    main()   

# def query_suggestion(self):
#     keyword_list = [w.lower() for w in self.query.split()]

