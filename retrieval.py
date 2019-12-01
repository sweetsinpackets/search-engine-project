import pandas as pd
import sys, os, pickle, pdb
import numpy as np
from BM25 import Retrieval_base
from srank import calculate_static_rank

static_weight = 20

def main():
    try:
        with open('Retrieval_base.pickle', 'rb') as handle:
            Rb = pickle.load(handle)
    except:
        Rb = Retrieval_base()
        with open('Retrieval_base.pickle', 'wb') as handle:
            pickle.dump(Rb, handle, protocol=pickle.HIGHEST_PROTOCOL)

    BM25_list = Rb.BM25_retrieval_score("ancient egypt", 20)
    ranked_game_df = calculate_static_rank()
    BM25_list = [(game[0], game[1] + static_weight * \
        ranked_game_df[(ranked_game_df.name == game[0])]['static_score'].values[0]) for game in BM25_list]
    BM25_list.sort(key=lambda tup: -tup[1])
    for i, tup_item in enumerate(BM25_list):
        print(i, tup_item)
    pdb.set_trace()

if __name__ == "__main__":
    main()