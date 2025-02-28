from flask import Blueprint, request, jsonify
from models.predictor import MatchPredictor
from utils.data_processor import DataProcessor

api_bp = Blueprint('api', __name__)
predictor = MatchPredictor()
data_processor = DataProcessor()

@api_bp.route('/predict/match', methods=['POST'])
def predict_match():
    """Predict match outcome"""
    try:
        data = request.get_json()
        home_team = data.get('home_team')
        away_team = data.get('away_team')
        
        # Get prediction
        prediction = predictor.predict_match(home_team, away_team)
        
        return jsonify({
            'success': True,
            'prediction': prediction
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@api_bp.route('/predict/score', methods=['POST'])
def predict_score():
    """Predict match score"""
    try:
        data = request.get_json()
        home_team = data.get('home_team')
        away_team = data.get('away_team')
        
        # Get score prediction
        prediction = predictor.predict_score(home_team, away_team)
        
        return jsonify({
            'success': True,
            'prediction': prediction
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@api_bp.route('/predict/scorers', methods=['POST'])
def predict_scorers():
    """Predict potential goal scorers"""
    try:
        data = request.get_json()
        home_team = data.get('home_team')
        away_team = data.get('away_team')
        
        # Get scorer predictions
        prediction = predictor.predict_scorers(home_team, away_team)
        
        return jsonify({
            'success': True,
            'prediction': prediction
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@api_bp.route('/statistics/team/<team_name>', methods=['GET'])
def team_statistics(team_name):
    """Get team statistics"""
    try:
        stats = data_processor.get_team_statistics(team_name)
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400 