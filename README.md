# Sports-Betting (Updated Mar 5th, 2024)

## Architectural Plan for NBA Games Prediction

### 1. Model Purpose

The purpose of the project is to create several ML models for NBA games prediction. Moreover, instead of outputing a series of predictions with the results, we want to output the probabilities of winning for each team in each game (softmax). For the first project, the plan is to design and tune several ML models for plain game prediction. After the development of the first project, we will proceed to develop models for players' performance prediction, prediction for different leagues, and parlay learner (reinforcement learning).

### 2. Data Collection

Using NBA's API (https://github.com/swar/nba_api), Rapid API (https://rapidapi.com/api-sports/api/api-nba), Pro-basketball reference (https://www.basketball-reference.com/teams/), we will collect data for games, teams' performance, players' statistics on each team, and advanced data. There are a lot more features that we can add and these are the current features we can think of. Below are the several aspects of data being collected (or intend to collect, constantly updating):


<details>
<summary> Record </summary>
  
- Current record []
  
- last 10 (or arbitrary numbers) games record []
  
- Rank []

- Home and away records []

- Records against good teams []

- Records on back to back nights []

- Records Vs. The team they are playing []

- Rival history []

</details>

<details>
<summary> Performance Statistics </summary>
  
- Avg. points scored []
  
- Avg. points against []

- Points scored per 100 possessions []

- Percentages for field goal, three points, two points, paint, and etc. []
</details>

- Number of passes made per game

<details>
<summary> Players Statistics on Team </summary>
  
- Number of all stats []
  
- Average points per player with more than 10 min playing time []

- Number of unhealthy players []

- Star players performance []

- Average field goal percentage for players []

</details>

### 3. Data Wrangling and Exploration

In this step, we clean the data on its null values, and etc; explore the correlation and impact of different features on the outcome of the game; and test different hypotheses on whether we should include certain features or not.

Tests for Hypothesis Testing: p-test, t-test, **permutation test**, and etc.

### 4. Preprocessing and Modeling

Preprocess features for training like one hot encoding, transform the data for deep learning and etc.

Models we will be using (at the moment):
- Random forest classifier
- Logistic regression
- CNN
- PCA and LDA (for dimensionality reduction, which will be using on datasets during hyperparameters tuing)
- Boosting Trees
- Random cut forest (for anomaly games detection)

### 5. Hyperparameters Tuning and Further Development

In this step, we will just tune the parameters and write temporary conclusions for further model development.
