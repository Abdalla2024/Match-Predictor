from ..data.database import Database
from ..data.scraper import SoccerDataScraper
import logging
import sys

def setup_logging():
    """Configure logging for the initialization script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('initialization.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def main():
    """Main function to initialize database and collect initial data"""
    logger = setup_logging()
    logger.info("Starting database initialization and data collection")
    
    try:
        # Initialize database
        db = Database()
        logger.info("Database initialized successfully")
        
        # Initialize scraper
        scraper = SoccerDataScraper()
        logger.info("Scraper initialized successfully")
        
        # Define leagues to scrape
        # Format: (league_id, league_name, country)
        leagues = [
            (47, "Premier League", "England"),
            (87, "La Liga", "Spain"),
            (54, "Bundesliga", "Germany"),
            (55, "Serie A", "Italy"),
            (53, "Ligue 1", "France")
        ]
        
        # Define seasons to scrape (last 3 seasons)
        seasons = ["2023/24", "2022/23", "2021/22"]
        
        # Scrape data for each league
        for league_id, league_name, country in leagues:
            logger.info(f"Starting data collection for {league_name}")
            
            try:
                # Scrape league data
                scraper.scrape_league_data(league_id, seasons)
                logger.info(f"Completed data collection for {league_name}")
                
            except Exception as e:
                logger.error(f"Error collecting data for {league_name}: {str(e)}")
                continue
        
        logger.info("Data collection completed successfully")
        
    except Exception as e:
        logger.error(f"Error during initialization: {str(e)}")
        sys.exit(1)
    finally:
        scraper.close()
        logger.info("Resources cleaned up")

if __name__ == "__main__":
    main() 