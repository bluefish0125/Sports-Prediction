from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.linear_model import RidgeClassifier
from sklearn.neighbors import KNeighborsClassifier
import pandas as pd
import numpy as np
import os
import json
from joblib import dump
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SequentialFeatureSelector
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit
from scipy.stats import uniform, randint

from sklearn.decomposition import PCA
from sklearn.svm import SVC


# Whatsup Benny
# path_template = '/Users/benjamincheng/Documents/GitHub/Sports-Betting/data/tuning_data/complete_{}.csv'
path_template = '/Users/liqingyang/Documents/GitHub/sports_trading/sports_betting/data/tuning_data/complete_{}.csv'

df1 = pd.read_csv(path_template.format(1))
df2 = pd.read_csv(path_template.format(2))
df3 = pd.read_csv(path_template.format(3))
df4 = pd.read_csv(path_template.format(4))

# Concatenate the DataFrames into one DataFrame
complete_cleaning = pd.concat([df1, df2, df3, df4], ignore_index=True)

features = [col for col in complete_cleaning.columns if col != 'target_x']
X = complete_cleaning[features]
y = complete_cleaning['target_x']

# Apply PCA
pca = PCA(n_components=0.95)
X_pca = pca.fit_transform(X_scaled)

# Define a pipeline with an SVM classifier (note: PCA is already applied)
pipeline = Pipeline([
    ('classifier', SVC())
])

# Define the parameter distribution to sample from for SVM
param_distributions = {
    'classifier__C': uniform(0.01, 100),  # Wider range for the regularization parameter
    'classifier__gamma': uniform(0.0001, 1),  # Use a uniform distribution for gamma in a wider range
    'classifier__kernel': ['linear', 'rbf', 'poly', 'sigmoid'],  # Include 'linear' kernel
    'classifier__degree': randint(1, 5),  # Degree of the polynomial kernel function ('poly'). Ignored by other kernels.
    'classifier__coef0': uniform(-1, 1),  # Independent term in kernel function. It is only significant in 'poly' and 'sigmoid'.
}

# Initialize TimeSeriesSplit for cross-validation
tscv = TimeSeriesSplit(n_splits=3)

# Initialize RandomizedSearchCV
random_search = RandomizedSearchCV(
    estimator=pipeline,
    param_distributions=param_distributions,
    n_iter=100,  # Number of parameter settings sampled
    cv=tscv,  # Cross-validation strategy
    verbose=1,
    n_jobs=-1
)

random_search.fit(X_pca, y)

best_hyperparams = random_search.best_params_
best_model = random_search.best_estimator_

# Display the best hyperparameters
print("Best hyperparameters:")
print(best_hyperparams)


saved_dir = "/path/to/your/saving/directory"
os.makedirs(saved_dir, exist_ok=True)

# Save Best Hyperparameters
best_hyperparams_path = os.path.join(saved_dir, 'best_hyperparameters_svm.json')
with open(best_hyperparams_path, 'w') as f:
    json.dump(best_hyperparams, f)

# Save Fitted Model
best_model_path = os.path.join(saved_dir, 'best_model_svm.joblib')
dump(best_model, best_model_path)

# Save CV Results
cv_results_path = os.path.join(saved_dir, 'cv_results_svm.csv')
cv_results = pd.DataFrame(random_search.cv_results_)
cv_results.to_csv(cv_results_path, index=False)

print("Saved best hyperparameters, best model, and CV results.")