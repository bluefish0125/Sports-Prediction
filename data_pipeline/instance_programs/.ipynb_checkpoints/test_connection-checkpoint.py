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

retrieving_from = datetime.date.today() - datetime.timedelta(days=1)
base,_ = extracting_today_data(from_date=retrieving_from, data_type='Base', delay=5)
print(base.head())