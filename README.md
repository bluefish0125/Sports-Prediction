# Sports-Betting (Updated Mar 5th, 2024)

### Architectural Plan for NBA Games Prediction
1. Model Purpose

The purpose of the project is to create several ML models for NBA games prediction. Moreover, instead of outputing a series of predictions with the results, we want to output the probabilities of winning for each team in each game (softmax). For the first project, the plan is to design and tune several ML models for plain game prediction. After the development of the first project, we will proceed to develop models for players' performance prediction, prediction for different leagues, and parlay learner (reinforcement learning).

2. Data Collection

Using NBA's API (https://github.com/swar/nba_api), Rapid API (https://rapidapi.com/api-sports/api/api-nba), Pro-basketball reference (https://www.basketball-reference.com/teams/), we will collect data for games, teams' performance, players' statistics on each team, and advanced data. Below are the several aspects of data being collected (or intend to collect, constantly updating):

Record:
- Current record []
- last 10 (or arbitrary numbers) games record []
- Rank []

Performance Statistics

<details>
<summary> Record </summary>
- Current record []
  
- last 10 (or arbitrary numbers) games record []
  
- Rank []
</details>

<details>
<summary> Performance Statistics </summary>
- Avg. points scored []
  
- Avg. points against []
</details>


</details>

3. 
