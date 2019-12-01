import pandas as pd
import sys, os, pickle, pdb
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from BM25 import clean_game_name

class StaticRank():
    def __init__(self):
        self.pos_per_alpha = 0.25
        self.num_rat_alpha = 0.25
        self.net_pos_alpha = 0.25
        self.freshness_alpha = 0.25
    
    def _standardize(self, df):
        df -= df.min()
        df /= df.max()
        return df

    def _score_function(self, Gamedataframe):
        freshness_term = self.freshness_alpha * self._standardize(Gamedataframe['freshness'])
        percent_postive_term = self.pos_per_alpha * self._standardize(Gamedataframe['percent_positive'])
        number_ratings_term = self.num_rat_alpha * self._standardize(np.log(Gamedataframe['number_ratings']))
        net_positive_term = self.net_pos_alpha * self._standardize(np.log(Gamedataframe['net_positive']))
        score_df = percent_postive_term + number_ratings_term + net_positive_term + freshness_term
        return score_df

    def static_rank(self, Gamedataframe):
        # accept pd.dataframe
        # return pd.dataframe with static_ranking
        Gamedataframe['freshness'] = (Gamedataframe['release_date'] - Gamedataframe['release_date'].min()).astype('int')
        Gamedataframe['net_positive'] = (Gamedataframe['positive_ratings'] - Gamedataframe['negative_ratings']).apply(lambda x: max(x, 0.5))
        Gamedataframe['number_ratings'] = Gamedataframe['positive_ratings'] + Gamedataframe['negative_ratings']
        Gamedataframe['percent_positive'] = Gamedataframe['positive_ratings'] / Gamedataframe['number_ratings']
        
        # pdb.set_trace()
        # plt.plot(-np.sort(-Gamedataframe['percent_positive'].values))
        # plt.plot(-np.sort(-Gamedataframe['freshness'].values))
        # plt.show()
        Gamedataframe['static_score'] = self._score_function(Gamedataframe)
        Gamedataframe['static_rank'] = Gamedataframe['static_score'].rank(ascending=False)
        return Gamedataframe

def calculate_static_rank():
    try:
        with open('ranked_game_df.pickle', 'rb') as handle:
            ranked_game_df = pickle.load(handle)
    except:
        game_df = pd.read_excel("steam_clean.xlsx",index_col=0)
        # game_df.dropna(inplace = True)
        game_df['release_date'] = pd.to_datetime(game_df['release_date'])
        SR = StaticRank()
        game_df = SR.static_rank(game_df)
        game_df.sort_values(by=['static_rank'], inplace = True)
        ranked_game_df = game_df[['name', 'static_rank', 'static_score']]
        game_df['name'] = game_df['name'].apply(lambda x: clean_game_name(x))
        with open('ranked_game_df.pickle', 'wb') as handle:
            pickle.dump(ranked_game_df, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return ranked_game_df