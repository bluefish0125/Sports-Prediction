import requests
import base64
from io import StringIO
import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.endpoints import playergamelog, leaguedashteamstats, teamyearbyyearstats
from nba_api.stats.library.parameters import SeasonAll
from nba_api.stats.static import players, teams
import datetime
import time
import sys

# Mapping to maintain uniform naming schemes across datasets
mapping = {'Brooklyn Nets': 'BRK', 'Golden State Warriors': 'GSW', 'Los Angeles Lakers': 'LAL',
       'Milwaukee Bucks': 'MIL', 'Boston Celtics': 'BOS', 'Charlotte Hornets': 'CHO',
       'Chicago Bulls': 'CHI', 'Cleveland Cavaliers': 'CLE', 'Denver Nuggets': 'DEN',
       'Detroit Pistons': 'DET', 'Houston Rockets': 'HOU', 'Indiana Pacers': 'IND',
       'Memphis Grizzlies': 'MEM', 'Minnesota Timberwolves': 'MIN',
       'New Orleans Pelicans': 'NOP', 'New York Knicks': 'NYK', 'Oklahoma City Thunder': 'OKC',
       'Orlando Magic': 'ORL', 'Philadelphia 76ers': 'PHI', 'Phoenix Suns': 'PHO',
       'Portland Trail Blazers': 'POR', 'Sacramento Kings': 'SAC', 'San Antonio Spurs': 'SAS',
       'Toronto Raptors': 'TOR', 'Utah Jazz': 'UTA', 'Washington Wizards': 'WAS',
       'Atlanta Hawks': 'ATL', 'Dallas Mavericks': 'DAL', 'LA Clippers': 'LAC', 'Miami Heat': 'MIA'}

def merge_with_suffixes(dataframes, names, keys):
    """Merging different sets of data of the same season together"""
    suffixed_dfs = []
    for df, name in zip(dataframes, names):
        # Suffix non-key columns only
        suffixed_cols = {col: f"{col}_{name}" if col not in keys else col for col in df.columns}
        suffixed_dfs.append(df.rename(columns=suffixed_cols))

    merged_df = suffixed_dfs[0]
    for df in suffixed_dfs[1:]:
        merged_df = pd.merge(merged_df, df, on=keys, how='inner')
    return merged_df
    

def extracting_today_data(from_date=None, season='2023-24', season_type='Regular Season', data_type='Base', delay=5):
    year_start = season[:4]
    year_end = str(int(year_start)+1)
    season_ = year_start + "-" + year_end[2:]
    season = year_start + "_" + year_end
    if from_date == None:
        path_today = f"/Users/liqingyang/Documents/GitHub/sports_trading/sports_betting/nba_api/data/teams_stats/{season}/base_{season}.csv"
        from_date = pd.read_csv(path_today, parse_dates=['Date'])['Date'].max().date()

    season_end = datetime.date.today() - datetime.timedelta(days=1)
    
    current_date = from_date
    all_data = []

    unsuccessful_dates = []
    
    while current_date <= season_end:
        date_str = current_date.strftime('%m/%d/%Y')
        
        try:
            daily_stats = leaguedashteamstats.LeagueDashTeamStats(
                measure_type_detailed_defense=data_type,
                season=season_,
                season_type_all_star=season_type,
                date_to_nullable=date_str
            ).get_data_frames()[0]
            daily_stats['Date'] = date_str
            all_data += [daily_stats]
            print(f"Data fetched for {date_str}")
        except Exception as e:
            unsuccessful_dates += [date_str]
            print(f"Error fetching data for {date_str}: {e}")
        time.sleep(delay)
        current_date += datetime.timedelta(days=1)
        
    full_season_data = pd.concat(all_data, ignore_index=True)
    return full_season_data, unsuccessful_dates

def getting_stats(delay=5, retrieving_from=None):
    """Getting cumulative season stats for each game"""
    track_start='2023'
    season_end='2024'
    if retrieving_from is None:
        retrieving_from = datetime.now() - timedelta(seconds=delay)
    
    base, unsuccessful_dates_base = extracting_today_data(from_date=retrieving_from, data_type='Base', delay=delay)
    advanced, unsuccessful_dates_advanced = extracting_today_data(from_date=retrieving_from, data_type='Advanced', delay=delay)
    misc, unsuccessful_dates_misc = extracting_today_data(from_date=retrieving_from, data_type='Misc', delay=delay)
    four_factors, unsuccessful_dates_four_factors = extracting_today_data(from_date=retrieving_from, data_type='Four Factors', delay=delay)
    scoring, unsuccessful_dates_scoring = extracting_today_data(from_date=retrieving_from, data_type='Scoring', delay=delay)
    opponent, unsuccessful_dates_opponent = extracting_today_data(from_date=retrieving_from, data_type='Opponent', delay=delay)
    defense, unsuccessful_dates_defense = extracting_today_data(from_date=retrieving_from, data_type='Defense', delay=delay)

    year_start = track_start[:4]
    year_end = season_end[:4]
    season_ = year_start + "_" + year_end[2:]
    season = year_start + "_" + year_end

    datas = [base, advanced, misc, four_factors, scoring, opponent, defense]
    
    unsuccessful_dates_lst = [unsuccessful_dates_base, unsuccessful_dates_advanced, unsuccessful_dates_misc, unsuccessful_dates_four_factors, unsuccessful_dates_scoring, unsuccessful_dates_opponent, unsuccessful_dates_defense]
    datas_names = ["base", "advanced", "misc", "four_factors",
               "scoring", "opponent", "defense"]
    columns_to_exclude = ['TEAM_NAME', 'GP', 'W', 'L', 'W_PCT', 'MIN']
    others = [advanced, misc, four_factors, scoring, opponent, defense]
    others = [i[i.columns[~i.columns.isin(columns_to_exclude)]] for i in others]
    datas = [base] + others
    
    merge_keys = ['Date', 'TEAM_ID']
    merged_df = merge_with_suffixes(datas, datas_names, merge_keys) 
    merged_df['Date'] = pd.to_datetime(merged_df['Date'])

    return merged_df

def process(df):
    df.reset_index(drop=True, inplace=True)
    df['Teams'] = df['TEAM_NAME_base'].map(mapping)
    del df['TEAM_NAME_base']
    return df

# Your personal access token and repo details
token = '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'
username = 'bluefish0125'
repo = 'Sports-Betting'
path_to_file = 'nba_api/data/teams_stats/processed_cum_2018_2024.csv'

# GitHub API URL for your file
url = f'https://api.github.com/repos/{username}/{repo}/contents/{path_to_file}'

# Hvae to use raw file
raw_url = 'https://raw.githubusercontent.com/bluefish0125/Sports-Betting/main/nba_api/data/teams_stats/processed_cum_2018_2024.csv'
# Headers for authentication
headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.VERSION.raw'
}

# Send a GET request with headers including your personal access token for authentication
response = requests.get(raw_url, headers=headers)
if response.status_code == 200: # 200 means successful
    processed_data = pd.read_csv(StringIO(response.text), index_col=0)
    processed_data['Date'] = pd.to_datetime(processed_data['Date'], format='mixed')
    max_day = processed_data['Date'].max().date()
    next_day = max_day + datetime.timedelta(days=1)
    print("CSV retrieved from Github")
    
else:
    print(f"Failed to retrieve the CSV file. Status Code: {response.status_code}")

today = pd.DataFrame()
if (next_day == datetime.date.today()):
    print("Updated already")
    sys.exit(1)
else:
    print("Getting Stats")
    print(next_day)
    today = getting_stats(retrieving_from=next_day).iloc[:, 1:]
    today = process(today)
nba = pd.concat([processed_data, today], axis=0, ignore_index=True)

# Convert the DataFrame to CSV
csv_content = nba.to_csv()
content_encoded = base64.b64encode(csv_content.encode('utf-8')).decode('utf-8')
new_path_to_file = 'nba_api/data/teams_stats/processed_cum_2018_2024.csv'
new_url = f'https://api.github.com/repos/{username}/{repo}/contents/{new_path_to_file}'
# Prepare headers
headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json',
}

# Fetch the file from GitHub to get its SHA
response = requests.get(new_url, headers=headers)
data = response.json()
sha = data['sha']

# Create the payload with the new content and the SHA
payload = {
    'message': 'Daily Rankings Update',
    'content': content_encoded,
    'sha': sha,
    'branch': 'main',  # specify the branch if not 'main'
}

# Make a PUT request to update the file
response = requests.put(new_url, headers=headers, json=payload)

if response.status_code == 200:
    print('File updated successfully.')
else:
    print('Failed to update the file.')