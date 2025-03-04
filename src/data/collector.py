"""Data collector using API-Football."""

import requests
import logging
import json
from datetime import datetime
from time import sleep
from .config import API_BASE_URL, API_HEADERS, COMPETITIONS
from .database import Database
import time

class APIFootballCollector:
    def __init__(self):
        """Initialize the collector with necessary configurations"""
        self.db = Database()
        self.setup_logging()
        self.requests_remaining = 1000  # Start with higher limit
        self.requests_made = 0
        
        # Log API configuration (without the actual key)
        self.logger.info(f"API Base URL: {API_BASE_URL}")
        self.logger.info(f"API Host: {API_HEADERS.get('x-rapidapi-host')}")
        self.logger.info("Checking API key length: " + str(len(API_HEADERS.get('x-rapidapi-key', ''))))
        
        # Get actual remaining requests from API
        status = self.fetch_data('status')
        if status:
            self.logger.info(f"Full API Status Response: {json.dumps(status, indent=2)}")
            if status.get('response', {}).get('requests'):
                self.requests_remaining = status['response']['requests']['limit_day']
                self.logger.info(f"API Status: {self.requests_remaining} requests remaining today")
            else:
                self.logger.error(f"Unexpected API response structure: {status}")
        else:
            self.logger.error("Failed to get API status")
    
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
        """Fetch data from the API with rate limiting."""
        if self.requests_remaining <= 0:
            self.logger.warning("No requests remaining")
            return None
            
        url = f"{API_BASE_URL}/{endpoint}"
        headers = {
            'x-rapidapi-host': API_HEADERS.get('x-rapidapi-host'),
            'x-rapidapi-key': API_HEADERS.get('x-rapidapi-key')
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            self.requests_made += 1
            self.requests_remaining = int(response.headers.get('x-ratelimit-requests-remaining', 0))
            
            self.logger.info(f"Response Status Code: {response.status_code}")
            self.logger.info(f"Request {self.requests_made}: {self.requests_remaining} requests remaining")
            
            if response.status_code == 200:
                data = response.json()
                # Add a delay to respect rate limit (10 requests per minute)
                time.sleep(6)  # Wait 6 seconds between requests
                return data
            else:
                self.logger.error(f"API request failed with status code {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error making API request: {str(e)}")
            return None

    def collect_team_data(self, league_id, season):
        """Collect team data for a league and season"""
        teams_data = self.fetch_data('teams', {
            'league': league_id,
            'season': season
        })
        
        if not teams_data or not teams_data.get('response'):
            return
        
        for team in teams_data['response']:
            try:
                team_info = team['team']
                venue_info = team['venue']
                
                team_id = self.db.insert_team(
                    name=team_info['name'],
                    league=str(league_id),  # We'll update this with league name later
                    country=venue_info.get('country', 'Unknown')
                )
                
                self.logger.info(f"Stored team: {team_info['name']}")
                
            except Exception as e:
                self.logger.error(f"Error storing team {team_info['name']}: {str(e)}")
    
    def collect_match_data(self, league_id, season):
        """Collect match data for a league and season"""
        matches_data = self.fetch_data('fixtures', {
            'league': league_id,
            'season': season,
            'status': 'FT'  # Only finished matches
        })
        
        if not matches_data or not matches_data.get('response'):
            return
        
        total_matches = len(matches_data['response'])
        self.logger.info(f"Found {total_matches} matches for league {league_id} season {season}")
        
        for match in matches_data['response']:
            try:
                fixture = match['fixture']
                teams = match['teams']
                goals = match['goals']
                score = match['score']
                league = match['league']
                
                # Get or create team IDs
                home_team_id = self.db.insert_team(
                    name=teams['home']['name'],
                    league=league['name'],
                    country=league['country']
                )
                away_team_id = self.db.insert_team(
                    name=teams['away']['name'],
                    league=league['name'],
                    country=league['country']
                )
                
                # Parse match date
                match_date = datetime.fromtimestamp(fixture['timestamp'])
                
                # Store match
                match_id = self.db.insert_match(
                    home_team_id=home_team_id,
                    away_team_id=away_team_id,
                    home_score=goals['home'],
                    away_score=goals['away'],
                    date=match_date,
                    competition=league['name'],
                    season=str(season),
                    api_fixture_id=fixture['id']  # Store API fixture ID for later statistics collection
                )
                
                self.logger.info(f"Stored match: {teams['home']['name']} vs {teams['away']['name']}")
                
            except Exception as e:
                self.logger.error(f"Error storing match {fixture['id']}: {str(e)}")
    
    def collect_match_statistics(self, db_match_id, fixture_id):
        """Collect statistics for a specific match"""
        stats_data = self.fetch_data('fixtures/statistics', {
            'fixture': fixture_id
        })
        
        if not stats_data or not stats_data.get('response'):
            return
            
        for team_stats in stats_data['response']:
            try:
                team_id = self.db.get_team_id(team_stats['team']['name'])
                stats = {stat['type']: stat['value'] for stat in team_stats['statistics']}
                
                self.db.insert_team_stats(
                    team_id=team_id,
                    match_id=db_match_id,
                    possession=float(stats.get('Ball Possession', '0%').rstrip('%')) / 100,
                    shots=stats.get('Total Shots', 0),
                    shots_on_target=stats.get('Shots on Goal', 0),
                    corners=stats.get('Corner Kicks', 0),
                    fouls=stats.get('Fouls', 0)
                )
                
            except Exception as e:
                self.logger.error(f"Error storing match statistics for match {db_match_id}: {str(e)}")
    
    def collect_season_data(self, season=2023, include_stats=False, max_requests=None):
        """Collect all data for a specific season"""
        try:
            for league_code, league_id in COMPETITIONS.items():
                self.logger.info(f"Collecting {league_code} data for season {season}")
                
                # Collect team data
                self.collect_team_data(league_id, season)
                
                # Collect match data
                self.collect_match_data(league_id, season)
                
                # Only collect statistics if specifically requested
                if include_stats and self.requests_remaining > 0:
                    self.collect_season_statistics(league_code, season, max_requests)
                    if max_requests and self.requests_made >= max_requests:
                        break
                
                self.logger.info(f"Completed data collection for {league_code}")
                
                # Break if we've hit the rate limit
                if self.requests_remaining <= 0:
                    self.logger.warning("Stopping data collection due to rate limit")
                    break
                
        except Exception as e:
            self.logger.error(f"Error during season data collection: {str(e)}")
        finally:
            self.db.close()
            self.logger.info(f"Data collection completed. Made {self.requests_made} requests.")
    
    def collect_season_statistics(self, league_code, season, max_requests=None):
        """Collect statistics for all matches in a season that don't have statistics yet"""
        try:
            # Get matches without statistics
            matches = self.db.get_matches_without_statistics(league_code, season)
            initial_requests = self.requests_made
            
            for match_id, fixture_id in matches:
                if self.requests_remaining <= 0:
                    self.logger.warning("Stopping statistics collection due to rate limit")
                    break
                
                if max_requests and (self.requests_made - initial_requests) >= max_requests:
                    self.logger.info(f"Stopping after using {max_requests} requests as requested")
                    break
                    
                self.collect_match_statistics(match_id, fixture_id)
                
            self.logger.info(f"After {league_code}: {self.requests_remaining} requests remaining")
                
        except Exception as e:
            self.logger.error(f"Error collecting season statistics: {str(e)}")
    
    def close(self):
        """Clean up resources"""
        self.db.close() 