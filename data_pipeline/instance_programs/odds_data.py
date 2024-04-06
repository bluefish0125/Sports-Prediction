import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz
import base64
from io import StringIO
pd.reset_option('display.max_rows')
#pd.set_option('display.max_rows', None)

mapping = {'Brooklyn Nets': 'BRK', 'Golden State Warriors': 'GSW', 'Los Angeles Lakers': 'LAL',
       'Milwaukee Bucks': 'MIL', 'Boston Celtics': 'BOS', 'Charlotte Hornets': 'CHO',
       'Chicago Bulls': 'CHI', 'Cleveland Cavaliers': 'CLE', 'Denver Nuggets': 'DEN',
       'Detroit Pistons': 'DET', 'Houston Rockets': 'HOU', 'Indiana Pacers': 'IND',
       'Memphis Grizzlies': 'MEM', 'Minnesota Timberwolves': 'MIN',
       'New Orleans Pelicans': 'NOP', 'New York Knicks': 'NYK', 'Oklahoma City Thunder': 'OKC',
       'Orlando Magic': 'ORL', 'Philadelphia 76ers': 'PHI', 'Phoenix Suns': 'PHO',
       'Portland Trail Blazers': 'POR', 'Sacramento Kings': 'SAC', 'San Antonio Spurs': 'SAS',
       'Toronto Raptors': 'TOR', 'Utah Jazz': 'UTA', 'Washington Wizards': 'WAS',
       'Atlanta Hawks': 'ATL', 'Dallas Mavericks': 'DAL', 'Los Angeles Clippers': 'LAC', 'Miami Heat': 'MIA'}


def shift_col(team, col_name):
    next_col = team[col_name].shift(-1)
    return next_col

def add_col(df, col_name):
    return df.groupby("Teams", group_keys=False).apply(lambda x: shift_col(x, col_name))


print("Start")

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
    df = pd.read_csv(StringIO(response.text), index_col=0)

else:
    print(f"Failed to retrieve the CSV file. Status Code: {response.status_code}")

df = df.reset_index(drop=True)

print("Dates retrieved from rankings_data")

date_series = pd.to_datetime(df['Date'])
cur_max = date_series.max().strftime("%Y-%m-%d")
df = df[df['Date'] >= cur_max]
df['date_next'] = add_col(df, 'Date')
date_prediction = (date_series.max() + timedelta(days=1)).strftime("%Y-%m-%d")
df['date_next'].fillna(date_prediction, inplace=True)
dates = df['date_next'].unique()

# Define time zones
dates_utc = []
est_timezone = pytz.timezone('America/New_York')  # Eastern Standard Time (EST)
utc_timezone = pytz.timezone('UTC')
print("Timezone changes")

threshold_value = pd.to_datetime('2020-06-27T03:55:00Z')

full = []
for date in dates:
    date = date[:10]
    # Create a datetime object for the given time in EST
    est_time = datetime.strptime(f'{date} 7:00 PM', '%Y-%m-%d %I:%M %p')
    est_time = est_timezone.localize(est_time)

    # Convert EST time to UTC
    utc_time = est_time.astimezone(utc_timezone)
    if utc_time >= threshold_value:
        final_time = utc_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        dates_utc.append(final_time)

KEY = 'dc34ee156925bf51d4a4c33c87d440fc'
SPORT = 'basketball_nba'
REGION = 'us'
MARKET = 'h2h'
FORMAT = 'decimal'
full = []

# adjust number of dates 
DATES = dates_utc
for DATE in DATES:
    response = requests.get(f'https://api.the-odds-api.com/v4/historical/sports/{SPORT}/odds',
        params={
            'api_key': KEY,
            'regions': REGION,
            'markets': MARKET,
            'oddsFormat': FORMAT,
            'date': DATE,
        }
    ).json()
    for i in range(len(response['data'])):
        # [Timestamp, good team, evil team, fanduel odds good team wins, draftkings odds, caesars odds]
        #best_odds = [[None,None,None,None,float('-inf')] for _ in range(2)]
        bookmakers = response['data'][i]['bookmakers']
        for index, data in enumerate(bookmakers):
            best_odds = [[None,None,None,None,float('-inf')] for _ in range(2)]
            if response['data'][i]['bookmakers'][index]['title'] in ["FanDuel", "BetMGM", "DraftKings"]:
                for outcome in range(2):
                    odds = response['data'][i]['bookmakers'][index]['markets'][0]['outcomes'][outcome]['price']
                    current_odds = best_odds[outcome][4]
                    best_odds[outcome][0] = response['timestamp']
                    best_odds[outcome][1] = response['data'][i]['id']
                    best_odds[outcome][2] = response['data'][i]['bookmakers'][index]['title']
                    best_odds[outcome][3] = response['data'][i]['bookmakers'][index]['markets'][0]['outcomes'][outcome]['name']
                    best_odds[outcome][4] = odds
                full.extend(best_odds)

print("Odds data retrieved")

timestamp = []
Id = []
sportsbook = []
team = []
odds = []
for i in range(len(full)):
    timestamp.append(full[i][0])
    Id.append(full[i][1])
    sportsbook.append(full[i][2])
    team.append(full[i][3])
    odds.append(full[i][4])
df = pd.DataFrame({"Timestamp": timestamp,"Id": Id, "Sportsbook": sportsbook, "Team": team, "Odds": odds})

grouped = df.groupby('Id')
group_sizes = grouped.size()

# Filter groups with less than 6 rows
ids_with_less_than_six_rows = group_sizes[group_sizes < 6].index.tolist()

print("Ids with less than 6 rows retrieved")
print(ids_with_less_than_six_rows)

miss = []
for Id in ids_with_less_than_six_rows:
    group = df[df['Id'] == Id]
    sportsbooks = ["FanDuel", "BetMGM", "DraftKings"]
    
    # check which sportsbook is missing
    present_sportsbooks = group['Sportsbook'].unique()
    missing_sportsbooks = [sb for sb in sportsbooks if sb not in present_sportsbooks][0]

    teams = group['Team'].unique()
    for team in teams:
        missing = [None, None, None, None, float('-inf')]
        # calculate average odds 
        missing[0] = group['Timestamp'].iloc[0]
        missing[1] = Id
        missing[2] = missing_sportsbooks
        missing[3] = team
        missing[4] = round(group[group['Team'] == team]['Odds'].mean(), 2)
        miss.append(missing)
missing_df = pd.DataFrame(miss, columns=['Timestamp', 'Id', 'Sportsbook', 'Team', 'Odds'])

print("Missing data filled")

concat = pd.concat([df, missing_df], ignore_index=True)
concat = concat.sort_values(by=['Timestamp', 'Id'])
concat = concat.reset_index(drop=True)
full = concat.merge(concat,
               left_on=['Timestamp','Id', 'Sportsbook'],
               right_on = ['Timestamp','Id', 'Sportsbook'])
full = full.drop(full[full['Team_x'] == full['Team_y']].index)
full = full.reset_index(drop=True)

print("concated with missing_df")

full['Timestamp'] = pd.to_datetime(full['Timestamp'])

utc_timezone = pytz.utc
est_timezone = pytz.timezone('US/Eastern')

full['Timestamp'] = full['Timestamp'].dt.tz_convert(est_timezone)
full['Timestamp'] = full['Timestamp'].dt.strftime('%Y-%m-%d')

full['Team_x'] = full['Team_x'].map(mapping)
full['Team_y'] = full['Team_y'].map(mapping)

fanduel = full[full['Sportsbook'] == 'FanDuel']
columns = fanduel.columns
columns = ['Timestamp', 'Id', 'Sportsbook', 'Team_x', 'Fanduel_odds_x','Team_y', 'Fanduel_odds_y']
fanduel.columns = columns
fanduel = fanduel.drop('Sportsbook', axis=1)

draftkings = full[full['Sportsbook'] == 'DraftKings']
columns = draftkings.columns
columns = ['Timestamp', 'Id', 'Sportsbook', 'Team_x', 'Draftkings_odds_x','Team_y', 'Draftkings_odds_y']
draftkings.columns = columns
draftkings = draftkings.drop('Sportsbook', axis=1)

betMGM = full[full['Sportsbook'] == 'BetMGM']
columns = betMGM.columns
columns = ['Timestamp', 'Id', 'Sportsbook', 'Team_x', 'BetMGM_odds_x','Team_y', 'BetMGM_odds_y']
betMGM.columns = columns
betMGM = betMGM.drop('Sportsbook', axis=1)

print("Fanduel, betMGM, and DraftKings odds ready")

merged_fd_dk = pd.merge(fanduel, draftkings, on=['Timestamp', 'Id', 'Team_x', 'Team_y'], how='left')

# Merge the result with betMGM DataFrame
final = pd.merge(merged_fd_dk, betMGM, on=['Timestamp', 'Id', 'Team_x', 'Team_y'], how='left')
columns = final.columns
columns = ['Timestamp', 'Id', 'Teams_x', 'Fanduel_odds_x','Teams_y', 'Fanduel_odds_y', 'Draftkings_odds_x', 'Draftkings_odds_y', 'BetMGM_odds_x', 'BetMGM_odds_y']
final.columns = columns
final = final.drop('Id', axis=1)

order = ['Timestamp', 'Teams_x', 'Fanduel_odds_x','Draftkings_odds_x', 'BetMGM_odds_x', 'Teams_y', 'Fanduel_odds_y','Draftkings_odds_y', 'BetMGM_odds_y']
final = final[order]
print("Final got it")

print("Saving to path")



# Hvae to use raw file
raw_url = 'https://raw.githubusercontent.com/bluefish0125/Sports-Betting/main/data/odds_data/odds_daily_updated.csv'
# Headers for authentication
headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.VERSION.raw'
}

# Send a GET request with headers including your personal access token for authentication
response = requests.get(raw_url, headers=headers)
if response.status_code == 200: # 200 means successful
    whole = pd.read_csv(StringIO(response.text), index_col=0)

else:
    print(f"Failed to retrieve the CSV file for Odds. Status Code: {response.status_code}")

complete = pd.concat([whole, final], axis=0)
# Convert the DataFrame to CSV
csv_content = complete.to_csv()
content_encoded = base64.b64encode(csv_content.encode('utf-8')).decode('utf-8')
new_path_to_file = 'data/odds_data/odds_daily_updated.csv'
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
    'message': 'Daily Odds Update',
    'content': content_encoded,
    'sha': sha,
    'branch': 'main',  # specify the branch if not 'main'
}

# Make a PUT request to update the file
response = requests.put(new_url, headers=headers, json=payload)

if response.status_code == 200:
    print('Odds updated successfully.')
else:
    print('Failed to update the file.')