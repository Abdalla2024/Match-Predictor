from flask import Flask, render_template, request, jsonify
import os
import sqlite3
from datetime import datetime, timedelta
from src.models.predictor import MatchPredictor

template_dir = os.path.abspath(os.path.dirname(__file__)) + '/templates'
static_dir = os.path.abspath(os.path.dirname(__file__)) + '/static'
app = Flask(__name__, 
           template_folder=template_dir,
           static_folder=static_dir)

# Initialize the predictor
predictor = MatchPredictor()
predictor.train()  # Train the model when app starts

def get_db_connection():
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Render the main prediction page"""
    # Get teams from database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT t.id as team_id, t.name as team_name 
        FROM teams t
        JOIN team_stats ts ON t.id = ts.team_id
        JOIN matches m ON ts.match_id = m.id 
        WHERE m.competition = 'Premier League' 
        AND m.season = '2023'
        ORDER BY t.name
    """)
    teams = cursor.fetchall()
    conn.close()
    return render_template('index.html', teams=[(team['team_id'], team['team_name']) for team in teams])

@app.route('/predict', methods=['POST'])
def predict():
    """Make a prediction for a match"""
    try:
        data = request.get_json()
        home_team_id = int(data['home_team_id'])
        away_team_id = int(data['away_team_id'])
        
        if home_team_id == away_team_id:
            return jsonify({'error': 'Home and away teams must be different'}), 400
        
        # Use the ML predictor
        prediction = predictor.predict_match(home_team_id, away_team_id)
        
        if prediction is None:
            return jsonify({'error': 'Not enough data to make prediction'}), 400
            
        return jsonify(prediction)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/team-stats/<int:team_id>')
def team_stats(team_id):
    """Get recent statistics for a team"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get team name
        cursor.execute("SELECT name FROM teams WHERE id = ?", (team_id,))
        team_name = cursor.fetchone()['name']
        
        # Get average stats
        cursor.execute("""
            SELECT 
                AVG(possession) as possession,
                AVG(shots) as shots,
                AVG(shots_on_target) as shots_on_target,
                AVG(corners) as corners,
                AVG(fouls) as fouls
            FROM team_stats
            WHERE team_id = ?
        """, (team_id,))
        avg_stats = cursor.fetchone()
        
        # Get recent matches
        cursor.execute("""
            SELECT 
                m.date,
                t1.name as team,
                t2.name as opponent,
                CASE WHEN m.home_team_id = t1.id THEN 'H' ELSE 'A' END as venue,
                CASE 
                    WHEN m.home_team_id = t1.id THEN m.home_score
                    ELSE m.away_score
                END as team_score,
                CASE 
                    WHEN m.home_team_id = t1.id THEN m.away_score
                    ELSE m.home_score
                END as opponent_score
            FROM matches m
            JOIN teams t1 ON (m.home_team_id = t1.id OR m.away_team_id = t1.id)
            JOIN teams t2 ON (m.home_team_id = t2.id OR m.away_team_id = t2.id)
            WHERE t1.id = ? AND t2.id != ?
            ORDER BY m.date DESC
            LIMIT 5
        """, (team_id, team_id))
        recent_matches = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'team_name': team_name,
            'recent_matches': [{
                'date': match['date'],
                'opponent': match['opponent'],
                'team_score': match['team_score'],
                'opponent_score': match['opponent_score'],
                'venue': match['venue']
            } for match in recent_matches],
            'average_stats': {
                'possession': round(avg_stats['possession'], 1) if avg_stats['possession'] is not None else 0,
                'shots': round(avg_stats['shots'], 1) if avg_stats['shots'] is not None else 0,
                'shots_on_target': round(avg_stats['shots_on_target'], 1) if avg_stats['shots_on_target'] is not None else 0,
                'corners': round(avg_stats['corners'], 1) if avg_stats['corners'] is not None else 0,
                'fouls': round(avg_stats['fouls'], 1) if avg_stats['fouls'] is not None else 0
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 