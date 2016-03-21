#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import

__author__ = "Clare Corthell"
__copyright__ = "Copyright 2016, summer.ai & Wordnik"
__date__ = "2016-01-02"
__email__ = "clare+github@thegeometrist.com"

import datetime
import numpy as np
import pandas as pd

from sklearn.cross_validation import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_selection import SelectKBest
from serapis.learning_utils import ItemSelector
from sklearn.naive_bayes import MultinomialNB
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import precision_recall_fscore_support, roc_curve, auc
from serapis.persist_model import PackagedPipeline

import logging
log = logging.getLogger('serapis.sklearn_model')

def get_training_data():
    data = pd.DataFrame.from_csv('training_data_here.csv')
    x = data['data']
    y = data['label']
    return train_test_split(x, y)

def build_pipeline():
    x_train, x_test, y_train, y_test = get_training_data()
    sentence_tfidf = TfidfVectorizer()

    feature_union = FeatureUnion(
                transformer_list=[
                    ('s_clean', Pipeline([
                        ('selector', ItemSelector(key='x')),
                        ('tfidf', sentence_tfidf),
                        ('best', SelectKBest(k=1000))
                    ]))
                ])

    X_features = feature_union.fit(x_train, y_train).transform(x_train)
    param_grid = dict(univ_select__k=[1,100,1000,10000], mnb__alpha=[0.01, 0.1, 1.0])
    grid = GridSearchCV(MultinomialNB(), param_grid=param_grid)
    grid.fit(X_features, y_train)
    c = grid.best_estimator_

    X_test = feature_union.transform(x_test)
    pred = np.array(c.predict(X_test))
    pred_proba = np.array([a[1] for a in c.predict_proba(X_test)])
    precision, recall, fscore, support = precision_recall_fscore_support(actual, pred)
    fpr, tpr, thresholds = roc_curve(actual, pred)
    auc_score = auc(fpr, tpr)

    now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    metadata = {
        'pipeline':      str(grid.best_estimator_),
        'created_at':    now,
        'git_hash':      0,
        'precision':     [float(p) for p in precision],
        'recall':        [float(r) for r in recall],
        'fscore':        [float(f) for f in fscore],
        'support':       [int(s) for s in support],
        'auc': auc_score
    }

    p = PackagedPipeline(pipeline=grid.best_estimator_, feature_union=feature_union, metadata=metadata,
        x_train=x_train, y_train=y_train, x_test=x_test, y_test=y_test)
    p.save()
