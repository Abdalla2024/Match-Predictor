from flask import Flask, render_template, request, jsonify
import os

template_dir = os.path.abspath(os.path.dirname(__file__)) + '/templates'
static_dir = os.path.abspath(os.path.dirname(__file__)) + '/static'
app = Flask(__name__, 
           template_folder=template_dir,
           static_folder=static_dir)

@app.route('/')
def index():
    """Render the main prediction page"""
    # Temporary hardcoded teams for testing
    teams = [
        (1, "Arsenal"),
        (2, "Aston Villa"),
        (3, "Bournemouth"),
        (4, "Brentford"),
        (5, "Brighton"),
        (6, "Burnley"),
        (7, "Chelsea"),
        (8, "Crystal Palace"),
        (9, "Everton"),
        (10, "Fulham"),
        (11, "Liverpool"),
        (12, "Luton"),
        (13, "Manchester City"),
        (14, "Manchester United"),
        (15, "Newcastle"),
        (16, "Nottingham Forest"),
        (17, "Sheffield United"),
        (18, "Tottenham"),
        (19, "West Ham"),
        (20, "Wolves")
    ]
    return render_template('index.html', teams=teams)

@app.route('/predict', methods=['POST'])
def predict():
    """Make a prediction for a match"""
    try:
        data = request.get_json()
        home_team_id = int(data['home_team_id'])
        away_team_id = int(data['away_team_id'])
        
        if home_team_id == away_team_id:
            return jsonify({'error': 'Home and away teams must be different'}), 400
            
        # Temporary mock prediction
        return jsonify({
            'home_team': 'Team A',
            'away_team': 'Team B',
            'predicted_outcome': 'H',
            'outcome_probabilities': {
                'home_win': 0.6,
                'draw': 0.2,
                'away_win': 0.2
            },
            'predicted_score': {
                'home': 2,
                'away': 1
            }
        })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/team-stats/<int:team_id>')
def team_stats(team_id):
    """Get recent statistics for a team"""
    try:
        # Temporary mock stats
        return jsonify({
            'team_name': f'Team {team_id}',
            'recent_matches': [
                {
                    'date': '2024-03-01',
                    'opponent': 'Team B',
                    'team_score': 2,
                    'opponent_score': 1,
                    'venue': 'H'
                }
            ],
            'average_stats': {
                'possession': 55.5,
                'shots': 12.3,
                'shots_on_target': 5.2,
                'corners': 6.1,
                'fouls': 10.2
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 