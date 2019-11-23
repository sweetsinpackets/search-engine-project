import pandas as pd
import pdb
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

def inverted_index(Gamedataframe):
    # accept pd.dataframe
    # return an inverted index
    pass

def static_rank(Gamedataframe):
    # accept pd.dataframe
    # return pd.dataframe with static_ranking
    
    pass

def main():
    game_df = pd.read_excel("steam_modified.xlsx",index_col=0)
    plt.plot(game_df['negative_ratings'].values)
    plt.show()

if __name__ == "__main__":
    main()