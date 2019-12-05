from __future__ import absolute_import, division, print_function, unicode_literals
import os, sys, pickle, operator, pdb
import pandas as pd
from bs4 import BeautifulSoup
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import scipy.sparse as sp
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import check_is_fitted
from sklearn.feature_extraction.text import _document_frequency
import heapq
import re

'''
https://github.com/arosh/BM25Transformer/blob/master/bm25.py
'''

class BM25Transformer(BaseEstimator, TransformerMixin):
    """
    Parameters
    ----------
    use_idf : boolean, optional (default=True)
    k1 : float, optional (default=2.0)
    b : float, optional (default=0.75)
    References
    ----------
    Okapi BM25: a non-binary model - Introduction to Information Retrieval
    http://nlp.stanford.edu/IR-book/html/htmledition/okapi-bm25-a-non-binary-model-1.html
    """
    def __init__(self, use_idf=True, k1=2.0, b=0.75):
        self.use_idf = use_idf
        self.k1 = k1
        self.b = b

    def fit(self, X):
        """
        Parameters
        ----------
        X : sparse matrix, [n_samples, n_features]
            document-term matrix
        """
        if not sp.issparse(X):
            X = sp.csc_matrix(X)
        if self.use_idf:
            n_samples, n_features = X.shape
            df = _document_frequency(X)
            idf = np.log((n_samples - df + 0.5) / (df + 0.5))
            self._idf_diag = sp.spdiags(idf, diags=0, m=n_features, n=n_features)
        return self

    def transform(self, X, copy=True):
        """
        Parameters
        ----------
        X : sparse matrix, [n_samples, n_features]
            document-term matrix
        copy : boolean, optional (default=True)
        """
        if hasattr(X, 'dtype') and np.issubdtype(X.dtype, np.float):
            # preserve float family dtype
            X = sp.csr_matrix(X, copy=copy)
        else:
            # convert counts or binary occurrences to floats
            X = sp.csr_matrix(X, dtype=np.float64, copy=copy)

        n_samples, n_features = X.shape

        # Document length (number of terms) in each row
        # Shape is (n_samples, 1)
        dl = X.sum(axis=1)
        # Number of non-zero elements in each row
        # Shape is (n_samples, )
        sz = X.indptr[1:] - X.indptr[0:-1]
        # In each row, repeat `dl` for `sz` times
        # Shape is (sum(sz), )
        # Example
        # -------
        # dl = [4, 5, 6]
        # sz = [1, 2, 3]
        # rep = [4, 5, 5, 6, 6, 6]
        rep = np.repeat(np.asarray(dl), sz)
        # Average document length
        # Scalar value
        avgdl = np.average(dl)
        # Compute BM25 score only for non-zero elements
        data = X.data * (self.k1 + 1) / (X.data + self.k1 * (1 - self.b + self.b * rep / avgdl))
        X = sp.csr_matrix((data, X.indices, X.indptr), shape=X.shape)

        if self.use_idf:
            check_is_fitted(self, '_idf_diag', 'idf vector is not fitted')

            expected_n_features = self._idf_diag.shape[0]
            if n_features != expected_n_features:
                raise ValueError("Input has n_features=%d while the model"
                                 " has been trained with n_features=%d" % (
                                     n_features, expected_n_features))
            # *= doesn't work
            X = X * self._idf_diag

        return X

def convert_html_to_text(html_list):
    return [BeautifulSoup(item, features="html.parser").get_text() for item in html_list]

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

def dummy_tokenizer(text):
    return text

def get_count_mat(corpus):
    vectorizer = CountVectorizer(tokenizer=dummy_tokenizer, lowercase=False)
    X = vectorizer.fit_transform(corpus)
    term_list = vectorizer.get_feature_names()
    print(X.shape)
    return X, term_list, vectorizer

'''
    input: tfidf-vectortizer and term
    return: the column index of a word in the tfidf matrix
'''
def get_col_index(vectorizer, term):
    # get index
    return  vectorizer.vocabulary_.get(term)

def query_proprocess(q):
    return [w.lower() for w in q.split()]

def clean_game_name(x):
    try:
        # if x == 'Discovery Tour by Assassin‚Äôs Creed¬Æ: Ancient Egypt':
        #     pdb.set_trace()
        x = x.replace('¬Æ', '')
        x = x.replace('‚Äôs', '')
        x = x.replace('‚Ñ¢', '')
    except:
        print("An exception occurred")
    return x


class Retrieval_base():
    def __init__(self):
        # Read data
        self.games = pd.read_excel("steam_clean.xlsx",index_col=0)
        self.games['description_text'] = self.games['detailed_description'].apply(lambda x: BeautifulSoup(x, features="html.parser").get_text())
        self.games['name'] = self.games['name'].apply(lambda x: clean_game_name(x))
        # Series to list
        det_description_text = self.games['detailed_description'].tolist()
        det_description_final = description_preprocess(det_description_text)
        #tfidf, col_name, vectorizer = get_tfidf(det_description_final)
        #tfidf_as_array = tfidf.toarray()
        self.count_mat, self.col_name, self.vectorizer = get_count_mat(det_description_final)
        self.BM25_vec = BM25Transformer()
        self.BM25_vec = self.BM25_vec.fit(self.count_mat)
        self.BM25_mat = self.BM25_vec.transform(self.count_mat)

    def BM25_retrieval_score(self, query, amount) -> "A list of games with best BM25 score": 
        query = query_proprocess(query)
        index_list = [get_col_index(self.vectorizer, w) for w in query]
        index_list = [item for item in index_list if item is not None]
        score = np.sum(self.BM25_mat[:,index_list], axis=1)
        out_game_list = heapq.nlargest(amount, enumerate(score), key=operator.itemgetter(1))
        output = []
        for item in out_game_list:
            bonus_factor = self.name_matchness(self.games['name'][item[0]], query)
            output.append((self.games['name'][item[0]], item[1][0,0] * bonus_factor))
        return output
    
    def name_matchness(self, name, query_tokens) -> 'FLOAT bonus factor':
        match_count = 0
        total_count = len(query_tokens)
        for token in query_tokens:
            if token.lower() is str(name).lower():
                match_count += 1 
        bonus_factor = (match_count/total_count) ** 2 * 0.01 + 1
        return bonus_factor
            
