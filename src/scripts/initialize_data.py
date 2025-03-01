import logging
import sys
from ..data.collector import FootballDataCollector
from ..data.config import FOOTBALL_DATA_API_KEY

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
    
    if not FOOTBALL_DATA_API_KEY:
        logger.error("No API key found. Please set FOOTBALL_DATA_API_KEY in .env file")
        sys.exit(1)
    
    try:
        # Initialize collector
        collector = FootballDataCollector()
        logger.info("Collector initialized successfully")
        
        # Define seasons to collect (last 3 seasons)
        seasons = [2023, 2022, 2021]  # Season format: YYYY
        
        # Start data collection
        collector.collect_data(seasons)
        
    except Exception as e:
        logger.error(f"Error during initialization: {str(e)}")
        sys.exit(1)
    finally:
        collector.close()
        logger.info("Resources cleaned up")

if __name__ == "__main__":
    main() 