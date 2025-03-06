from src.web import app
import logging
import sys

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    try:
        logger.info("Starting Flask application on http://localhost:3000")
        logger.info("Press CTRL+C to stop the server")
        app.run(debug=True, host='localhost', port=3000)
    except Exception as e:
        logger.error(f"Failed to start Flask application: {str(e)}", exc_info=True) 