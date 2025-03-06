from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    """Render the main prediction page"""
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
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Premier League Match Predictor</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container mt-4">
            <h1>Premier League Match Predictor</h1>
            <div class="card">
                <div class="card-body">
                    <form id="prediction-form">
                        <div class="mb-3">
                            <label for="home-team" class="form-label">Home Team</label>
                            <select class="form-select" id="home-team" required>
                                <option value="">Select Home Team</option>
                                """ + "\n".join([f'<option value="{id}">{name}</option>' for id, name in teams]) + """
                            </select>
                        </div>
                        <div class="mb-3">
                            <label for="away-team" class="form-label">Away Team</label>
                            <select class="form-select" id="away-team" required>
                                <option value="">Select Away Team</option>
                                """ + "\n".join([f'<option value="{id}">{name}</option>' for id, name in teams]) + """
                            </select>
                        </div>
                        <button type="submit" class="btn btn-primary">Predict</button>
                    </form>
                </div>
            </div>
            <div id="result" class="mt-4"></div>
        </div>
        <script>
            document.getElementById('prediction-form').addEventListener('submit', function(e) {
                e.preventDefault();
                const homeTeam = document.getElementById('home-team').value;
                const awayTeam = document.getElementById('away-team').value;
                
                fetch('/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        home_team_id: homeTeam,
                        away_team_id: awayTeam
                    })
                })
                .then(response => response.json())
                .then(data => {
                    const result = document.getElementById('result');
                    result.innerHTML = `
                        <div class="card">
                            <div class="card-body">
                                <h3>Prediction Result</h3>
                                <p>Predicted Score: ${data.predicted_score.home} - ${data.predicted_score.away}</p>
                                <p>Win Probabilities:</p>
                                <ul>
                                    <li>Home Win: ${(data.outcome_probabilities.home_win * 100).toFixed(1)}%</li>
                                    <li>Draw: ${(data.outcome_probabilities.draw * 100).toFixed(1)}%</li>
                                    <li>Away Win: ${(data.outcome_probabilities.away_win * 100).toFixed(1)}%</li>
                                </ul>
                            </div>
                        </div>
                    `;
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('result').innerHTML = '<div class="alert alert-danger">Error making prediction</div>';
                });
            });
        </script>
    </body>
    </html>
    """

@app.route('/predict', methods=['POST'])
def predict():
    """Make a prediction for a match"""
    try:
        data = request.get_json()
        home_team_id = int(data['home_team_id'])
        away_team_id = int(data['away_team_id'])
        
        if home_team_id == away_team_id:
            return jsonify({'error': 'Home and away teams must be different'}), 400
            
        # Mock prediction
        return jsonify({
            'predicted_score': {'home': 2, 'away': 1},
            'outcome_probabilities': {
                'home_win': 0.6,
                'draw': 0.2,
                'away_win': 0.2
            }
        })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask application...")
    print("Try accessing http://localhost:3000")
    app.run(debug=True, host='localhost', port=3000) 