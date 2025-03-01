"""Configuration settings for data collection."""

# API Configuration
API_KEY = "your_api_key_here"  # Replace with your API-Football API key
API_BASE_URL = "https://v3.football.api-sports.io"
API_HEADERS = {
    "x-rapidapi-host": "v3.football.api-sports.io",
    "x-rapidapi-key": API_KEY
}

# League IDs for API-Football
COMPETITIONS = {
    "Premier League": 39,  # English Premier League
    "La Liga": 140,       # Spanish La Liga
    "Serie A": 135,       # Italian Serie A
    "Bundesliga": 78,     # German Bundesliga
    "Ligue 1": 61,       # French Ligue 1
}

# Default seasons for data collection
DEFAULT_SEASONS = ["2023"]  # Can be expanded to include more seasons 