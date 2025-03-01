import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.metrics import accuracy_score, mean_squared_error, classification_report
import logging
from ..data.database import Database

class MatchPredictor:
    def __init__(self):
        """Initialize the predictor with necessary models and configurations"""
        self.db = Database()
        self.outcome_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.score_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.setup_logging()
        
    def setup_logging(self):
        """Set up logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('predictor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_team_features(self, team_id, last_n_matches=5):
        """Get team features from recent matches"""
        query = '''
            SELECT 
                ts.possession,
                ts.shots,
                ts.shots_on_target,
                ts.corners,
                ts.fouls,
                CASE 
                    WHEN m.home_team_id = ? AND m.home_score > m.away_score THEN 1
                    WHEN m.away_team_id = ? AND m.away_score > m.home_score THEN 1
                    ELSE 0
                END as won
            FROM team_stats ts
            JOIN matches m ON ts.match_id = m.id
            WHERE ts.team_id = ?
            ORDER BY m.date DESC
            LIMIT ?
        '''
        self.db.cursor.execute(query, (team_id, team_id, team_id, last_n_matches))
        results = self.db.cursor.fetchall()
        
        if not results:
            return None
        
        # Calculate average stats
        stats = np.array(results)
        return {
            'avg_possession': np.mean(stats[:, 0]),
            'avg_shots': np.mean(stats[:, 1]),
            'avg_shots_on_target': np.mean(stats[:, 2]),
            'avg_corners': np.mean(stats[:, 3]),
            'avg_fouls': np.mean(stats[:, 4]),
            'win_rate': np.mean(stats[:, 5])
        }
    
    def prepare_match_features(self, home_team_id, away_team_id):
        """Prepare features for a match prediction"""
        home_features = self.get_team_features(home_team_id)
        away_features = self.get_team_features(away_team_id)
        
        if not home_features or not away_features:
            return None
        
        # Combine features
        features = [
            home_features['avg_possession'],
            home_features['avg_shots'],
            home_features['avg_shots_on_target'],
            home_features['avg_corners'],
            home_features['avg_fouls'],
            home_features['win_rate'],
            away_features['avg_possession'],
            away_features['avg_shots'],
            away_features['avg_shots_on_target'],
            away_features['avg_corners'],
            away_features['avg_fouls'],
            away_features['win_rate']
        ]
        
        return np.array(features).reshape(1, -1)
    
    def prepare_training_data(self):
        """Prepare training data from historical matches"""
        query = '''
            SELECT 
                m.id,
                m.home_team_id,
                m.away_team_id,
                m.home_score,
                m.away_score,
                CASE 
                    WHEN m.home_score > m.away_score THEN 'H'
                    WHEN m.home_score < m.away_score THEN 'A'
                    ELSE 'D'
                END as outcome
            FROM matches m
            ORDER BY m.date DESC
        '''
        self.db.cursor.execute(query)
        matches = self.db.cursor.fetchall()
        
        X = []  # Features
        y_outcome = []  # Match outcomes
        y_score = []  # Match scores
        
        for match in matches:
            match_id, home_id, away_id, home_score, away_score, outcome = match
            features = self.prepare_match_features(home_id, away_id)
            
            if features is not None:
                X.append(features[0])
                y_outcome.append(outcome)
                y_score.append([home_score, away_score])
        
        return np.array(X), np.array(y_outcome), np.array(y_score)
    
    def train(self):
        """Train the prediction models"""
        try:
            # Prepare training data
            X, y_outcome, y_score = self.prepare_training_data()
            
            if len(X) == 0:
                self.logger.error("No training data available")
                return False
            
            # Split data
            X_train, X_test, y_outcome_train, y_outcome_test, y_score_train, y_score_test = train_test_split(
                X, y_outcome, y_score, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train outcome model
            self.outcome_model.fit(X_train_scaled, y_outcome_train)
            outcome_pred = self.outcome_model.predict(X_test_scaled)
            outcome_accuracy = accuracy_score(y_outcome_test, outcome_pred)
            
            # Train score model
            self.score_model.fit(X_train_scaled, y_score_train)
            score_pred = self.score_model.predict(X_test_scaled)
            score_mse = mean_squared_error(y_score_test, score_pred)
            
            self.logger.info(f"Model training completed:")
            self.logger.info(f"Outcome prediction accuracy: {outcome_accuracy:.2f}")
            self.logger.info(f"Score prediction MSE: {score_mse:.2f}")
            self.logger.info("\nOutcome Classification Report:")
            self.logger.info(classification_report(y_outcome_test, outcome_pred))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error training models: {str(e)}")
            return False
    
    def predict_match(self, home_team_id, away_team_id):
        """Predict the outcome and score of a match"""
        try:
            # Prepare features
            features = self.prepare_match_features(home_team_id, away_team_id)
            
            if features is None:
                return None
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Make predictions
            outcome_pred = self.outcome_model.predict(features_scaled)[0]
            outcome_probs = self.outcome_model.predict_proba(features_scaled)[0]
            score_pred = self.score_model.predict(features_scaled)[0]
            
            # Get team names
            home_team = self.get_team_name(home_team_id)
            away_team = self.get_team_name(away_team_id)
            
            return {
                'home_team': home_team,
                'away_team': away_team,
                'predicted_outcome': outcome_pred,
                'outcome_probabilities': {
                    'home_win': outcome_probs[0],
                    'draw': outcome_probs[1],
                    'away_win': outcome_probs[2]
                },
                'predicted_score': {
                    'home': round(score_pred[0]),
                    'away': round(score_pred[1])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error making prediction: {str(e)}")
            return None
    
    def get_team_name(self, team_id):
        """Get team name from ID"""
        self.db.cursor.execute('SELECT name FROM teams WHERE id = ?', (team_id,))
        result = self.db.cursor.fetchone()
        return result[0] if result else None
    
    def close(self):
        """Clean up resources"""
        self.db.close() 