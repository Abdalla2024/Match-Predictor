from src.predictions.model import MatchPredictor

def main():
    predictor = MatchPredictor()
    
    # Example matches to predict
    test_matches = [
        # Manchester City vs Liverpool
        (22, 38),
        # Arsenal vs Chelsea
        (23, 37),
        # Manchester United vs Newcastle
        (39, 33),
        # Tottenham vs Brighton
        (36, 29)
    ]
    
    print("\nMatch Predictions:\n")
    print("-" * 80)
    
    for home_id, away_id in test_matches:
        home_team = predictor.get_team_name(home_id)
        away_team = predictor.get_team_name(away_id)
        
        prediction = predictor.predict_match(home_id, away_id)
        
        print(f"\n{home_team} vs {away_team}")
        print(f"Prediction: {prediction['prediction']}")
        print(f"Confidence: {prediction['confidence']}%")
        print(f"Probabilities:")
        print(f"  Home Win: {prediction['home_win_probability']}%")
        print(f"  Draw: {prediction['draw_probability']}%")
        print(f"  Away Win: {prediction['away_win_probability']}%")
        print(f"Data Quality:")
        print(f"  Home Team Games: {prediction['data_quality']['home_games']}")
        print(f"  Away Team Games: {prediction['data_quality']['away_games']}")
        print("-" * 80)

if __name__ == "__main__":
    main() 