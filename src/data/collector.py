"""Data collector using football-data.org API."""

import requests
import logging
from datetime import datetime
from time import sleep
from .config import FOOTBALL_DATA_BASE_URL, API_HEADERS, COMPETITIONS
from .database import Database

class FootballDataCollector:
    def __init__(self):
        """Initialize the collector with necessary configurations"""
        self.db = Database()
        self.setup_logging()
    
    def setup_logging(self):
        """Set up logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('collector.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def fetch_data(self, endpoint, params=None):
        """Make API request with rate limiting and error handling"""
        try:
            url = f"{FOOTBALL_DATA_BASE_URL}/{endpoint}"
            response = requests.get(url, headers=API_HEADERS, params=params)
            
            if response.status_code == 429:  # Too Many Requests
                retry_after = int(response.headers.get('Retry-After', 60))
                self.logger.warning(f"Rate limit hit. Waiting {retry_after} seconds...")
                sleep(retry_after)
                return self.fetch_data(endpoint, params)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching data from {endpoint}: {str(e)}")
            return None
    
    def collect_team_data(self, competition_id):
        """Collect team data for a competition"""
        teams_data = self.fetch_data(f'competitions/{competition_id}/teams')
        if not teams_data:
            return
        
        for team in teams_data.get('teams', []):
            try:
                team_id = self.db.insert_team(
                    name=team['name'],
                    league=teams_data['competition']['name'],
                    country=team['area']['name']
                )
                
                # Store players
                for squad_member in team.get('squad', []):
                    self.db.insert_player(
                        name=squad_member['name'],
                        team_id=team_id,
                        position=squad_member.get('position'),
                        nationality=squad_member.get('nationality')
                    )
                
            except Exception as e:
                self.logger.error(f"Error storing team {team['name']}: {str(e)}")
    
    def collect_match_data(self, competition_id, season):
        """Collect match data for a competition and season"""
        matches_data = self.fetch_data('matches', {
            'competitionId': competition_id,
            'season': season,
            'status': 'FINISHED'
        })
        
        if not matches_data:
            return
        
        for match in matches_data.get('matches', []):
            try:
                # Get team IDs (create if not exists)
                home_team_id = self.db.insert_team(
                    name=match['homeTeam']['name'],
                    league=match['competition']['name'],
                    country=match['competition']['area']['name']
                )
                away_team_id = self.db.insert_team(
                    name=match['awayTeam']['name'],
                    league=match['competition']['name'],
                    country=match['competition']['area']['name']
                )
                
                # Store match
                match_date = datetime.strptime(match['utcDate'], '%Y-%m-%dT%H:%M:%SZ')
                match_id = self.db.insert_match(
                    home_team_id=home_team_id,
                    away_team_id=away_team_id,
                    home_score=match['score']['fullTime']['home'],
                    away_score=match['score']['fullTime']['away'],
                    date=match_date,
                    competition=match['competition']['name'],
                    season=str(season)
                )
                
                # Collect detailed match statistics
                self.collect_match_statistics(match_id, match['id'])
                
            except Exception as e:
                self.logger.error(f"Error storing match {match['id']}: {str(e)}")
    
    def collect_match_statistics(self, db_match_id, api_match_id):
        """Collect detailed statistics for a match"""
        match_stats = self.fetch_data(f'matches/{api_match_id}')
        if not match_stats:
            return
        
        try:
            # Store home team stats
            home_stats = match_stats.get('homeTeam', {}).get('statistics', {})
            if home_stats:
                self.db.insert_team_stats(
                    team_id=self.db.get_team_id(match_stats['homeTeam']['name']),
                    match_id=db_match_id,
                    possession=float(home_stats.get('possession', 0)) / 100,
                    shots=home_stats.get('shots', 0),
                    shots_on_target=home_stats.get('shotsOnGoal', 0),
                    corners=home_stats.get('corners', 0),
                    fouls=home_stats.get('fouls', 0)
                )
            
            # Store away team stats
            away_stats = match_stats.get('awayTeam', {}).get('statistics', {})
            if away_stats:
                self.db.insert_team_stats(
                    team_id=self.db.get_team_id(match_stats['awayTeam']['name']),
                    match_id=db_match_id,
                    possession=float(away_stats.get('possession', 0)) / 100,
                    shots=away_stats.get('shots', 0),
                    shots_on_target=away_stats.get('shotsOnGoal', 0),
                    corners=away_stats.get('corners', 0),
                    fouls=away_stats.get('fouls', 0)
                )
            
            # Store player statistics and events
            for goal in match_stats.get('goals', []):
                player_id = self.db.get_player_id(goal['scorer']['name'], 
                    self.db.get_team_id(goal['team']['name']))
                if player_id:
                    self.db.insert_match_event(
                        match_id=db_match_id,
                        player_id=player_id,
                        event_type='GOAL',
                        minute=goal['minute']
                    )
            
        except Exception as e:
            self.logger.error(f"Error storing match statistics for match {db_match_id}: {str(e)}")
    
    def collect_data(self, seasons):
        """Collect data for all competitions and specified seasons"""
        try:
            for competition_code, competition_id in COMPETITIONS.items():
                self.logger.info(f"Collecting data for {competition_code}")
                
                # Collect team and player data
                self.collect_team_data(competition_id)
                
                # Collect match data for each season
                for season in seasons:
                    self.logger.info(f"Collecting {competition_code} matches for season {season}")
                    self.collect_match_data(competition_id, season)
                    sleep(6)  # Rate limiting - max 10 calls per minute
                
                self.logger.info(f"Completed data collection for {competition_code}")
                sleep(10)  # Additional delay between competitions
            
            self.logger.info("Data collection completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error during data collection: {str(e)}")
        finally:
            self.db.close()
    
    def close(self):
        """Clean up resources"""
        self.db.close() 