import sqlite3
import numpy as np
from typing import Tuple, Dict, List, Optional

class MatchPredictor:
    def __init__(self, db_path: str = 'data.db'):
        """Initialize the predictor with database connection."""
        self.db_path = db_path
        
    def _get_team_stats(self, team_id: int, last_n_matches: int = 5) -> Dict:
        """Get team statistics from recent matches."""
        with sqlite3.connect(self.db_path) as conn:
            # Get overall team performance
            query = """
                WITH team_matches AS (
                    SELECT 
                        m.id,
                        CASE 
                            WHEN m.home_team_id = ? THEN m.home_score
                            ELSE m.away_score
                        END as team_score,
                        CASE 
                            WHEN m.home_team_id = ? THEN m.away_score
                            ELSE m.home_score
                        END as opponent_score,
                        CASE 
                            WHEN m.home_team_id = ? THEN 1
                            ELSE 0
                        END as is_home
                    FROM matches m
                    WHERE m.home_team_id = ? OR m.away_team_id = ?
                    ORDER BY m.id DESC
                    LIMIT ?
                )
                SELECT 
                    COUNT(*) as games_played,
                    SUM(CASE WHEN team_score > opponent_score THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN team_score = opponent_score THEN 1 ELSE 0 END) as draws,
                    SUM(CASE WHEN team_score < opponent_score THEN 1 ELSE 0 END) as losses,
                    AVG(CAST(team_score AS FLOAT)) as avg_goals_scored,
                    AVG(CAST(opponent_score AS FLOAT)) as avg_goals_conceded
                FROM team_matches
            """
            cursor = conn.cursor()
            cursor.execute(query, (team_id, team_id, team_id, team_id, team_id, last_n_matches))
            result = cursor.fetchone()
            
            # Get average performance metrics
            metrics_query = """
                SELECT 
                    AVG(CAST(possession AS FLOAT)) as avg_possession,
                    AVG(CAST(shots AS FLOAT)) as avg_shots,
                    AVG(CAST(shots_on_target AS FLOAT)) as avg_shots_on_target,
                    AVG(CAST(corners AS FLOAT)) as avg_corners
                FROM team_stats ts
                JOIN matches m ON m.id = ts.match_id
                WHERE ts.team_id = ?
                ORDER BY m.id DESC
                LIMIT ?
            """
            cursor.execute(metrics_query, (team_id, last_n_matches))
            metrics_result = cursor.fetchone()
            
            # Handle case where we don't have enough data
            games_played = result[0] if result[0] is not None else 0
            wins = result[1] if result[1] is not None else 0
            draws = result[2] if result[2] is not None else 0
            losses = result[3] if result[3] is not None else 0
            
            return {
                'games_played': games_played,
                'wins': wins,
                'draws': draws,
                'losses': losses,
                'avg_goals_scored': result[4] if result[4] is not None else 0,
                'avg_goals_conceded': result[5] if result[5] is not None else 0,
                'win_rate': wins / games_played if games_played > 0 else 0.33,  # Use league average if no data
                'avg_possession': metrics_result[0] if metrics_result[0] is not None else 50,
                'avg_shots': metrics_result[1] if metrics_result[1] is not None else 12,
                'avg_shots_on_target': metrics_result[2] if metrics_result[2] is not None else 4,
                'avg_corners': metrics_result[3] if metrics_result[3] is not None else 5
            }

    def predict_match(self, home_team_id: int, away_team_id: int) -> Dict:
        """Predict the outcome of a match between two teams."""
        # Get team statistics
        home_stats = self._get_team_stats(home_team_id)
        away_stats = self._get_team_stats(away_team_id)
        
        # Calculate basic win probabilities based on historical performance
        home_base_strength = home_stats['win_rate'] * 100
        away_base_strength = away_stats['win_rate'] * 100
        
        # Apply home advantage factor (historically about 5-10% advantage)
        HOME_ADVANTAGE = 7.5
        home_strength = home_base_strength + HOME_ADVANTAGE
        away_strength = away_base_strength
        
        # Adjust based on recent scoring form
        FORM_WEIGHT = 0.2
        home_form = (home_stats['avg_goals_scored'] - home_stats['avg_goals_conceded']) * FORM_WEIGHT
        away_form = (away_stats['avg_goals_scored'] - away_stats['avg_goals_conceded']) * FORM_WEIGHT
        
        # Adjust based on shooting accuracy
        SHOOTING_WEIGHT = 0.15
        home_shooting = (home_stats['avg_shots_on_target'] / home_stats['avg_shots'] if home_stats['avg_shots'] > 0 else 0) * SHOOTING_WEIGHT
        away_shooting = (away_stats['avg_shots_on_target'] / away_stats['avg_shots'] if away_stats['avg_shots'] > 0 else 0) * SHOOTING_WEIGHT
        
        # Calculate final probabilities
        total_strength = home_strength + away_strength
        draw_factor = 0.25  # Probability reserved for draws
        
        home_win_prob = (home_strength / total_strength) * (1 - draw_factor) + home_form + home_shooting
        away_win_prob = (away_strength / total_strength) * (1 - draw_factor) + away_form + away_shooting
        draw_prob = draw_factor
        
        # Normalize probabilities
        total = home_win_prob + away_win_prob + draw_prob
        home_win_prob /= total
        away_win_prob /= total
        draw_prob /= total
        
        # Add confidence penalty if we don't have enough data
        confidence_penalty = min(home_stats['games_played'], away_stats['games_played']) / 5  # 5 games is full confidence
        confidence_penalty = min(1.0, confidence_penalty)
        
        return {
            'home_win_probability': round(home_win_prob * 100, 2),
            'away_win_probability': round(away_win_prob * 100, 2),
            'draw_probability': round(draw_prob * 100, 2),
            'prediction': 'Home Win' if home_win_prob > max(away_win_prob, draw_prob) else 'Away Win' if away_win_prob > max(home_win_prob, draw_prob) else 'Draw',
            'confidence': round(max(home_win_prob, away_win_prob, draw_prob) * 100 * confidence_penalty, 2),
            'data_quality': {
                'home_games': home_stats['games_played'],
                'away_games': away_stats['games_played']
            }
        }

    def get_team_name(self, team_id: int) -> str:
        """Get team name from ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM teams WHERE id = ?", (team_id,))
            result = cursor.fetchone()
            return result[0] if result else "Unknown Team" 