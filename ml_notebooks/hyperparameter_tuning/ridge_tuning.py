from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.linear_model import RidgeClassifier
import pandas as pd
import numpy as np
import os
import json
from joblib import dump
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SequentialFeatureSelector
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit
from scipy.stats import uniform, randint



# path_template = '/home/ql1063_nyu_edu/GitHub/Sports-Betting/data/tuning_data/complete_{}.csv'
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

print("Got Data")
# Define the model
rr = RidgeClassifier()

# Create a pipeline with Sequential Feature Selector
pipeline = Pipeline([
    ('feature_selector', SequentialFeatureSelector(rr, direction='forward')),
    ('classifier', rr)
])

# Define the parameter distribution to sample from
param_distributions = {
    'feature_selector__n_features_to_select': randint(20, 1000),  # Random integer between 1 and number of features
    'classifier__alpha': uniform(0.1, 100), 
    'classifier__solver': ['auto', 'svd', 'cholesky', 'lsqr', 'sparse_cg', 'sag', 'saga']  # Different solvers
}

# Initialize TimeSeriesSplit for cross-validation
tscv = TimeSeriesSplit(n_splits=2)

# Initialize RandomizedSearchCV
random_search = RandomizedSearchCV(
    estimator=pipeline,
    param_distributions=param_distributions,
    n_iter=2,  # Number of parameter settings sampled
    cv=tscv,  # Cross-validation strategy
    verbose=1,
    n_jobs=-1
)


# Perform the randomized search on the data
random_search.fit(X, y)

# Get the best combination of hyperparameters and the corresponding best model
best_hyperparams = random_search.best_params_
best_model = random_search.best_estimator_

# Display the best hyperparameters
print("Best hyperparameters:")
print(best_hyperparams)

saved_dir = '/Users/liqingyang/Documents/GitHub/sports_trading/sports_betting/data/tuning_results/'
# saved_dir = "/home/ql1063_nyu_edu/GitHub/Sports-Betting/data/tuning_results/"
os.makedirs(saved_dir, exist_ok=True) 

best_hyperparams_path = os.path.join(saved_dir, 'best_hyperparameters.json')
with open(best_hyperparams_path, 'w') as f:
    json.dump(best_hyperparams, f)

# 2. Save Fitted Model
best_model_path = os.path.join(saved_dir, 'best_model.joblib')
dump(best_model, best_model_path)

# 3. Save CV Results
cv_results_path = os.path.join(saved_dir, 'cv_results.csv')
cv_results = pd.DataFrame(random_search.cv_results_)
cv_results.to_csv(cv_results_path, index=False)

# Extract the best estimator's feature selector and then the selected features
feature_selector = best_model.named_steps['feature_selector']
selected_features = np.array(features)[feature_selector.get_support()]

print("Saved best hyperparameters, best model, and CV results.")
selected_features_path = os.path.join(saved_dir, 'selected_features.txt')

# Save the selected feature names to the file
with open(selected_features_path, 'w') as f:
    for feature in selected_features:
        f.write(f"{feature}\n")

print("Saved selected features.")