import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from utils.data_processor import DataProcessor

class MatchPredictor:
    def __init__(self):
        """Initialize the predictor with different models for different prediction tasks"""
        self.data_processor = DataProcessor()
        
        # Models
        self.outcome_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.score_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scorer_model = RandomForestClassifier(n_estimators=100, random_state=42)
        
        # Initialize models (will be trained when data is available)
        self.is_trained = False

    def train_models(self, training_data):
        """Train all prediction models"""
        # Train outcome prediction model
        X_outcome, y_outcome = self.data_processor.prepare_outcome_data(training_data)
        self.outcome_model.fit(X_outcome, y_outcome)
        
        # Train score prediction model
        X_score, y_score = self.data_processor.prepare_score_data(training_data)
        self.score_model.fit(X_score, y_score)
        
        # Train scorer prediction model
        X_scorer, y_scorer = self.data_processor.prepare_scorer_data(training_data)
        self.scorer_model.fit(X_scorer, y_scorer)
        
        self.is_trained = True

    def predict_match(self, home_team, away_team):
        """Predict match outcome (win/draw/loss)"""
        if not self.is_trained:
            raise Exception("Models need to be trained first")
        
        # Get feature vector for the match
        features = self.data_processor.get_match_features(home_team, away_team)
        
        # Make prediction
        prediction = self.outcome_model.predict_proba([features])[0]
        
        return {
            'home_win': float(prediction[0]),
            'draw': float(prediction[1]),
            'away_win': float(prediction[2])
        }

    def predict_score(self, home_team, away_team):
        """Predict match score"""
        if not self.is_trained:
            raise Exception("Models need to be trained first")
        
        # Get feature vector for the match
        features = self.data_processor.get_match_features(home_team, away_team)
        
        # Make prediction
        prediction = self.score_model.predict([features])[0]
        
        return {
            'home_goals': round(float(prediction[0])),
            'away_goals': round(float(prediction[1]))
        }

    def predict_scorers(self, home_team, away_team):
        """Predict potential goal scorers"""
        if not self.is_trained:
            raise Exception("Models need to be trained first")
        
        # Get player features
        home_players = self.data_processor.get_team_players(home_team)
        away_players = self.data_processor.get_team_players(away_team)
        
        # Get scoring probabilities for each player
        home_predictions = []
        away_predictions = []
        
        for player in home_players:
            features = self.data_processor.get_player_features(player, home_team, is_home=True)
            prob = self.scorer_model.predict_proba([features])[0][1]  # Probability of scoring
            if prob > 0.2:  # Only include players with significant scoring probability
                home_predictions.append({
                    'player': player,
                    'probability': float(prob)
                })
        
        for player in away_players:
            features = self.data_processor.get_player_features(player, away_team, is_home=False)
            prob = self.scorer_model.predict_proba([features])[0][1]
            if prob > 0.2:
                away_predictions.append({
                    'player': player,
                    'probability': float(prob)
                })
        
        # Sort by probability
        home_predictions.sort(key=lambda x: x['probability'], reverse=True)
        away_predictions.sort(key=lambda x: x['probability'], reverse=True)
        
        return {
            'home_team_scorers': home_predictions[:3],  # Top 3 most likely scorers
            'away_team_scorers': away_predictions[:3]
        } 