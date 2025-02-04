import ssl
import urllib.error
import urllib.parse
import urllib.request
from collections import OrderedDict

import pandas as pd
from bs4 import BeautifulSoup

from com.cricket.stats.formats import Formats


class BattingHistoryDownloader:
    def __init__(self):
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE

    def get_ipl_batting_stats(self, player_id):
        try:
            url = self.__create_profile_url(player_id)
            html = urllib.request.urlopen(url, context=self.ctx).read()
            soup = BeautifulSoup(html, "html.parser")

            # Find Batting & Fielding table
            batting_tables = soup.find_all('p', class_='ds-text-tight-s ds-font-medium ds-py-2 ds-ml-4 ds-text-typo-mid3 ds-uppercase')
            if len(batting_tables) < 3:
                raise RuntimeError("Not enough batting tables found")
            batting_table = batting_tables[2].find_next('table')
            if not batting_table:
                raise RuntimeError("Batting & Fielding table not found")

            # Find Bowling table
            bowling_tables = soup.find_all('p', text='Bowling')
            if len(bowling_tables) < 2:
                raise RuntimeError("Not enough bowling tables found")
            bowling_table = bowling_tables[1].find_next('table')
            if not bowling_table:
                raise RuntimeError("Bowling table not found")

            # Extract IPL row from Batting table
            # ipl_batting_row = batting_table.find_all('tr')[0]
            tbody = batting_table.find('tbody')
            if not tbody:
                raise RuntimeError("Table body not found")
            ipl_batting_row = tbody.find_all('tr')[0]
            ipl_batting_data = [td.text.strip() for td in ipl_batting_row.find_all('td')]

            # Extract IPL row from Bowling table
            tbody = bowling_table.find('tbody')
            if not tbody:
                raise RuntimeError("Table body not found")
            ipl_bowling_row = tbody.find_all('tr')[0]
            ipl_bowling_data = [td.text.strip() for td in ipl_bowling_row.find_all('td')]

            # Define columns for Batting and Bowling tables
            batting_columns = [
                "Tournament", "Teams", "Matches", "Innings", "Not Out", "Runs", "Highest", "Average", 
                "Balls Faced", "Strike Rate", "100s", "50s", "4s", "6s", "Catches", "Stumpings"
            ]
            bowling_columns = [
                "Tournament", "Teams", "Matches", "Innings", "Balls", "Runs", "Wickets", "Best Bowling Innings", 
                "Best Bowling Match", "Average", "Economy", "Strike Rate", "4w", "5w", "10w"
            ]

            # Create DataFrames for Batting and Bowling stats
            batting_df = pd.DataFrame([ipl_batting_data], columns=batting_columns)
            bowling_df = pd.DataFrame([ipl_bowling_data], columns=bowling_columns)

            return batting_df, bowling_df

        except Exception as e:
            print(f"Error fetching IPL stats: {e}")
            return None, None

    def __create_profile_url(self, player_id):
        """
        Constructs the new player profile URL using the modern format.
        Example: https://www.espncricinfo.com/cricketers/rohit-sharma-34102
        """
        return f"https://www.espncricinfo.com/cricketers/{player_id}"
