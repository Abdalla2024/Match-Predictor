"""Initialize database and collect data."""

import logging
from src.data.collector import APIFootballCollector

def main():
    """Main function to initialize data collection."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting data collection for 2023 season")
        
        # Initialize collector
        collector = APIFootballCollector()
        logger.info("Collector initialized successfully")
        
        # Collect 2023 season data without statistics
        collector.collect_season_data(season=2023, include_stats=False)
        
    except Exception as e:
        logger.error(f"Error during data collection: {str(e)}")
    finally:
        logger.info("Data collection process completed")

if __name__ == "__main__":
    main() 