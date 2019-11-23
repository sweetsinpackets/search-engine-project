import pandas as pd
import pdb
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

def inverted_index(Gamedataframe):
    # accept pd.dataframe
    # return an inverted index
    pass

class StaticRank():
    def __init__(self):
        pos_per_alpha = 0.3
        num_rat_alpha = 0.3
        net_pos_alpha = 0.3
    
    def _standardize(df):
        df -= df.min()
        df /= df.max()
        return df

    def _score_function(self, Gamedataframe):
        percent_postive_term = pos_per_alpha * self._standardize(Gamedataframe['percent_positive'])
        number_ratings_term = num_rat_alpha * self._standardize(np.log(Gamedataframe['number_ratings']))
        net_positive_term = net_pos_alpha * self._standardize(np.log(Gamedataframe['net_positive']))
        score = percent_postive_term + number_ratings_term + net_positive_term
        return score

    def static_rank(self, Gamedataframe):
        # accept pd.dataframe
        # return pd.dataframe with static_ranking
        
        Gamedataframe['net_positive'] = Gamedataframe['positive_ratings'] - Gamedataframe['negative_ratings']
        Gamedataframe['number_ratings'] = Gamedataframe['positive_ratings'] + Gamedataframe['negative_ratings']
        Gamedataframe['percent_positive'] = Gamedataframe['positive_ratings'] / Gamedataframe['number_ratings']
        
        # pdb.set_trace()
        # plt.plot(-np.sort(-Gamedataframe['percent_positive'].values))
        plt.plot(np.log(-np.sort(-Gamedataframe['number_ratings'].values)))
        plt.show()
        
        return []

def main():
    game_df = pd.read_excel("steam_clean.xlsx",index_col=0)
    game_df.dropna(inplace = True)
    pdb.set_trace()
    plt.plot(np.log(-np.sort(-game_df['positive_ratings'].values)))
    plt.show()
    SR = StaticRank()
    rank_list = SR.static_rank(game_df)

if __name__ == "__main__":
    main()