import pandas as pd
import numpy as np
# import sklearn
# import sklearn.model_selection 

from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SequentialFeatureSelector
from sklearn.linear_model import RidgeClassifier
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit
from scipy.stats import uniform

from datetime import datetime




path_template = '/home/ql1063_nyu_edu/GitHub/Sports-Betting/data/tuning_data/complete_{}.csv'
df1 = pd.read_csv(path_template.format(1))
df2 = pd.read_csv(path_template.format(2))
df3 = pd.read_csv(path_template.format(3))
df4 = pd.read_csv(path_template.format(4))

# Concatenate the DataFrames into one DataFrame
complete_cleaning = pd.concat([df1, df2, df3, df4], ignore_index=True)

rr = RidgeClassifier(alpha=1)
split = TimeSeriesSplit(n_splits=3)
sfs = SequentialFeatureSelector(rr, n_features_to_select = 85, direction='forward', cv=split)
sfs.fit(complete_cleaning[regard], complete_cleaning['target_x'])



























