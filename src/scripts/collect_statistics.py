"""Script to collect match statistics for the 2023 season."""

import logging
from src.data.collector import APIFootballCollector

def main():
    """Main function to collect match statistics."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Continuing statistics collection for 2023 season")
        
        # Initialize collector
        collector = APIFootballCollector()
        logger.info(f"Collector initialized successfully. {collector.requests_remaining} requests remaining")
        
        # Continue with Premier League first since we already started it
        leagues = ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"]
        
        for league in leagues:
            if collector.requests_remaining <= 1:  # Leave 1 request buffer for safety
                logger.warning(f"Daily request limit approaching. Stopping before {league}")
                break
                
            logger.info(f"Collecting statistics for {league}")
            collector.collect_season_statistics(league, "2023")
            logger.info(f"After {league}: {collector.requests_remaining} requests remaining")
            
    except Exception as e:
        logger.error(f"Error during statistics collection: {str(e)}")
    finally:
        logger.info("Statistics collection process completed")

if __name__ == "__main__":
    main() 