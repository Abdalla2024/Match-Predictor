# Match-Predictor
A machine learning project to predict football match outcomes using historical data from API-Football.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Add your API key to `src/data/config.py`

## Data Collection
- Run `python -m src.scripts.initialize_data` to collect basic match data
- Run `python -m src.scripts.collect_statistics` to collect match statistics
