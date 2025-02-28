// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Form submission handler
    const predictionForm = document.getElementById('prediction-form');
    if (predictionForm) {
        predictionForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const homeTeam = document.getElementById('home-team').value;
            const awayTeam = document.getElementById('away-team').value;
            
            try {
                // Get match outcome prediction
                const outcomeResponse = await fetch('/api/predict/match', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        home_team: homeTeam,
                        away_team: awayTeam
                    })
                });
                
                const outcomeData = await outcomeResponse.json();
                
                // Get score prediction
                const scoreResponse = await fetch('/api/predict/score', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        home_team: homeTeam,
                        away_team: awayTeam
                    })
                });
                
                const scoreData = await scoreResponse.json();
                
                // Get scorer prediction
                const scorerResponse = await fetch('/api/predict/scorers', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        home_team: homeTeam,
                        away_team: awayTeam
                    })
                });
                
                const scorerData = await scorerResponse.json();
                
                // Display predictions
                displayPredictions(outcomeData, scoreData, scorerData);
                
            } catch (error) {
                console.error('Error:', error);
                displayError('An error occurred while getting predictions');
            }
        });
    }
});

function displayPredictions(outcome, score, scorers) {
    const resultsDiv = document.getElementById('prediction-results');
    if (!resultsDiv) return;
    
    // Calculate most likely outcome
    const outcomes = [
        { type: 'Home Win', probability: outcome.prediction.home_win },
        { type: 'Draw', probability: outcome.prediction.draw },
        { type: 'Away Win', probability: outcome.prediction.away_win }
    ];
    const mostLikely = outcomes.reduce((prev, current) => 
        (prev.probability > current.probability) ? prev : current
    );
    
    // Format probabilities as percentages
    const homeWinProb = (outcome.prediction.home_win * 100).toFixed(1);
    const drawProb = (outcome.prediction.draw * 100).toFixed(1);
    const awayWinProb = (outcome.prediction.away_win * 100).toFixed(1);
    
    resultsDiv.innerHTML = `
        <div class="prediction-result">
            <h3>Match Prediction</h3>
            <p>Most likely outcome: <strong>${mostLikely.type}</strong></p>
            <p>Probabilities:</p>
            <ul>
                <li>Home Win: ${homeWinProb}%</li>
                <li>Draw: ${drawProb}%</li>
                <li>Away Win: ${awayWinProb}%</li>
            </ul>
            
            <h3>Score Prediction</h3>
            <p><strong>${score.prediction.home_goals} - ${score.prediction.away_goals}</strong></p>
            
            <h3>Likely Scorers</h3>
            <div class="row">
                <div class="col-md-6">
                    <h4>Home Team</h4>
                    <ul>
                        ${scorers.prediction.home_team_scorers.map(player => 
                            `<li>${player.player} (${(player.probability * 100).toFixed(1)}%)</li>`
                        ).join('')}
                    </ul>
                </div>
                <div class="col-md-6">
                    <h4>Away Team</h4>
                    <ul>
                        ${scorers.prediction.away_team_scorers.map(player => 
                            `<li>${player.player} (${(player.probability * 100).toFixed(1)}%)</li>`
                        ).join('')}
                    </ul>
                </div>
            </div>
        </div>
    `;
}

function displayError(message) {
    const resultsDiv = document.getElementById('prediction-results');
    if (!resultsDiv) return;
    
    resultsDiv.innerHTML = `
        <div class="alert alert-danger" role="alert">
            ${message}
        </div>
    `;
}

// Team statistics chart
function createTeamStatsChart(teamName, stats) {
    const ctx = document.getElementById('team-stats-chart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Goals Scored', 'Goals Conceded', 'Possession', 'Shots', 'Shots on Target', 'Passes'],
            datasets: [{
                label: teamName,
                data: [
                    stats.goals_scored,
                    stats.goals_conceded,
                    stats.possession,
                    stats.shots,
                    stats.shots_on_target,
                    stats.passes
                ],
                fill: true,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgb(54, 162, 235)',
                pointBackgroundColor: 'rgb(54, 162, 235)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgb(54, 162, 235)'
            }]
        },
        options: {
            elements: {
                line: {
                    borderWidth: 3
                }
            },
            scales: {
                r: {
                    angleLines: {
                        display: true
                    },
                    suggestedMin: 0,
                    suggestedMax: 100
                }
            }
        }
    });
} 