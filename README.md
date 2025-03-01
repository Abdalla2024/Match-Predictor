# Match-Predictor

A machine learning project to predict football match outcomes using historical data from API-Football.

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Copy `src/data/config.template.py` to `src/data/config.py`
3. Add your API key to `src/data/config.py`

## Data Collection

- Run `python -m src.scripts.initialize_data` to collect basic match data
- Run `python -m src.scripts.collect_statistics` to collect match statistics

## API Usage

This project uses the API-Football API. You'll need to:

1. Sign up at https://www.api-football.com/
2. Get your API key from your dashboard
3. Add your API key to the config file
4. Note: Free tier has a limit of 100 requests per day
