import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import logging
from .database import Database

class SoccerDataScraper:
    def __init__(self):
        """Initialize the scraper with necessary configurations"""
        self.db = Database()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.setup_logging()
    
    def setup_logging(self):
        """Set up logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_selenium(self):
        """Set up Selenium WebDriver"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        return webdriver.Chrome(options=options)
    
    def scrape_fotmob_matches(self, league_id, season):
        """Scrape match data from Fotmob"""
        base_url = f"https://www.fotmob.com/leagues/{league_id}/matches"
        
        try:
            driver = self.setup_selenium()
            driver.get(base_url)
            
            # Wait for matches to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "matches"))
            )
            
            # Get all match elements
            match_elements = driver.find_elements(By.CLASS_NAME, "match-row")
            
            for match in match_elements:
                try:
                    # Extract match data
                    home_team = match.find_element(By.CLASS_NAME, "home-team").text
                    away_team = match.find_element(By.CLASS_NAME, "away-team").text
                    score = match.find_element(By.CLASS_NAME, "score").text
                    date_str = match.find_element(By.CLASS_NAME, "date").text
                    
                    # Process the data
                    home_score, away_score = map(int, score.split(' - '))
                    match_date = datetime.strptime(date_str, "%Y-%m-%d")
                    
                    # Store in database
                    home_team_id = self.db.insert_team(home_team, league_id, None)
                    away_team_id = self.db.insert_team(away_team, league_id, None)
                    
                    match_id = self.db.insert_match(
                        home_team_id, away_team_id, home_score, away_score,
                        match_date, league_id, season
                    )
                    
                    # Get detailed match statistics
                    self.scrape_match_details(match_id, match.get_attribute("href"))
                    
                except Exception as e:
                    self.logger.error(f"Error processing match: {str(e)}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error scraping Fotmob: {str(e)}")
        finally:
            driver.quit()
    
    def scrape_match_details(self, match_id, match_url):
        """Scrape detailed match statistics"""
        try:
            driver = self.setup_selenium()
            driver.get(match_url)
            
            # Wait for statistics to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "match-stats"))
            )
            
            # Get team statistics
            stats = driver.find_elements(By.CLASS_NAME, "stat-row")
            
            home_stats = {}
            away_stats = {}
            
            for stat in stats:
                name = stat.find_element(By.CLASS_NAME, "stat-name").text
                home_value = stat.find_element(By.CLASS_NAME, "home-value").text
                away_value = stat.find_element(By.CLASS_NAME, "away-value").text
                
                home_stats[name] = home_value
                away_stats[name] = away_value
            
            # Store team statistics
            self.store_team_stats(match_id, home_stats, away_stats)
            
            # Get player statistics
            self.scrape_player_stats(match_id, driver)
            
        except Exception as e:
            self.logger.error(f"Error scraping match details: {str(e)}")
        finally:
            driver.quit()
    
    def store_team_stats(self, match_id, home_stats, away_stats):
        """Store team statistics in database"""
        match_data = self.db.get_match_data(match_id)
        
        # Store home team stats
        self.db.insert_team_stats(
            match_data['home_team_id'],
            match_id,
            float(home_stats.get('Possession', '0').strip('%')) / 100,
            int(home_stats.get('Shots', 0)),
            int(home_stats.get('Shots on Target', 0)),
            int(home_stats.get('Corners', 0)),
            int(home_stats.get('Fouls', 0))
        )
        
        # Store away team stats
        self.db.insert_team_stats(
            match_data['away_team_id'],
            match_id,
            float(away_stats.get('Possession', '0').strip('%')) / 100,
            int(away_stats.get('Shots', 0)),
            int(away_stats.get('Shots on Target', 0)),
            int(away_stats.get('Corners', 0)),
            int(away_stats.get('Fouls', 0))
        )
    
    def scrape_player_stats(self, match_id, driver):
        """Scrape and store player statistics"""
        try:
            # Wait for player stats to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "player-stats"))
            )
            
            # Get all player rows
            player_rows = driver.find_elements(By.CLASS_NAME, "player-row")
            
            for row in player_rows:
                name = row.find_element(By.CLASS_NAME, "player-name").text
                team_name = row.find_element(By.CLASS_NAME, "team-name").text
                
                # Get team ID
                team_id = self.db.get_team_id(team_name)
                if not team_id:
                    continue
                
                # Get or create player
                player_id = self.db.get_player_id(name, team_id)
                if not player_id:
                    player_id = self.db.insert_player(
                        name, team_id,
                        row.find_element(By.CLASS_NAME, "position").text,
                        None  # Nationality not available in this view
                    )
                
                # Get player stats
                stats = {
                    'minutes': int(row.find_element(By.CLASS_NAME, "minutes").text),
                    'goals': int(row.find_element(By.CLASS_NAME, "goals").text),
                    'assists': int(row.find_element(By.CLASS_NAME, "assists").text),
                    'shots': int(row.find_element(By.CLASS_NAME, "shots").text),
                    'shots_on_target': int(row.find_element(By.CLASS_NAME, "shots-on-target").text),
                    'passes': int(row.find_element(By.CLASS_NAME, "passes").text),
                    'pass_accuracy': float(row.find_element(By.CLASS_NAME, "pass-accuracy").text.strip('%')) / 100
                }
                
                # Store player stats
                self.db.insert_player_stats(
                    player_id, match_id,
                    stats['minutes'], stats['goals'], stats['assists'],
                    stats['shots'], stats['shots_on_target'],
                    stats['passes'], stats['pass_accuracy']
                )
                
        except Exception as e:
            self.logger.error(f"Error scraping player stats: {str(e)}")
    
    def scrape_league_data(self, league_id, seasons):
        """Scrape data for multiple seasons of a league"""
        for season in seasons:
            self.logger.info(f"Scraping season {season} for league {league_id}")
            self.scrape_fotmob_matches(league_id, season)
            time.sleep(2)  # Be nice to the server
    
    def close(self):
        """Clean up resources"""
        self.db.close() 