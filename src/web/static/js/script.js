document.addEventListener('DOMContentLoaded', function() {
    const predictionForm = document.getElementById('prediction-form');
    const homeTeamSelect = document.getElementById('home-team');
    const awayTeamSelect = document.getElementById('away-team');
    
    // Update team statistics when team is selected
    homeTeamSelect.addEventListener('change', function() {
        if (this.value) {
            fetchTeamStats(this.value, 'home');
        } else {
            document.getElementById('home-team-stats').classList.add('d-none');
        }
    });
    
    awayTeamSelect.addEventListener('change', function() {
        if (this.value) {
            fetchTeamStats(this.value, 'away');
        } else {
            document.getElementById('away-team-stats').classList.add('d-none');
        }
    });
    
    // Handle form submission
    predictionForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const homeTeamId = homeTeamSelect.value;
        const awayTeamId = awayTeamSelect.value;
        
        if (homeTeamId === awayTeamId) {
            alert('Please select different teams for home and away');
            return;
        }
        
        // Make prediction request
        fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                home_team_id: homeTeamId,
                away_team_id: awayTeamId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }
            updatePredictionResults(data);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while making the prediction');
        });
    });
});

function fetchTeamStats(teamId, type) {
    fetch(`/team-stats/${teamId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error:', data.error);
                return;
            }
            updateTeamStats(data, type);
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function updatePredictionResults(data) {
    // Show prediction results
    document.getElementById('prediction-results').classList.remove('d-none');
    
    // Update team names
    document.getElementById('home-team-name').textContent = data.home_team;
    document.getElementById('away-team-name').textContent = data.away_team;
    
    // Update predicted score
    document.getElementById('home-score').textContent = data.predicted_score.home;
    document.getElementById('away-score').textContent = data.predicted_score.away;
    
    // Update win probabilities
    const homeWinProb = data.outcome_probabilities.home_win * 100;
    const drawProb = data.outcome_probabilities.draw * 100;
    const awayWinProb = data.outcome_probabilities.away_win * 100;
    
    // Update progress bars
    document.getElementById('home-win-prob').style.width = `${homeWinProb}%`;
    document.getElementById('draw-prob').style.width = `${drawProb}%`;
    document.getElementById('away-win-prob').style.width = `${awayWinProb}%`;
    
    // Update percentage texts
    document.getElementById('home-win-percentage').textContent = `${homeWinProb.toFixed(1)}%`;
    document.getElementById('draw-percentage').textContent = `${drawProb.toFixed(1)}%`;
    document.getElementById('away-win-percentage').textContent = `${awayWinProb.toFixed(1)}%`;
}

function updateTeamStats(data, type) {
    const statsContainer = document.getElementById(`${type}-team-stats`);
    const statsContent = document.getElementById(`${type}-team-stats-content`);
    
    // Show stats container
    statsContainer.classList.remove('d-none');
    
    // Create stats HTML
    let html = `
        <h6 class="mb-3">${data.team_name}</h6>
        <div class="stat-item">
            <div class="stat-label">Average Possession</div>
            <div class="stat-value">${data.average_stats.possession}%</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Average Shots</div>
            <div class="stat-value">${data.average_stats.shots}</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Shots on Target</div>
            <div class="stat-value">${data.average_stats.shots_on_target}</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Average Corners</div>
            <div class="stat-value">${data.average_stats.corners}</div>
        </div>
        <h6 class="mt-4 mb-3">Recent Matches</h6>
    `;
    
    // Add recent matches
    data.recent_matches.forEach(match => {
        const result = match.team_score > match.opponent_score ? 'W' :
                      match.team_score < match.opponent_score ? 'L' : 'D';
        const resultClass = result === 'W' ? 'text-success' :
                          result === 'L' ? 'text-danger' : 'text-warning';
        
        html += `
            <div class="recent-match">
                <div class="match-date">${new Date(match.date).toLocaleDateString()}</div>
                <div class="match-result">
                    <span class="${resultClass}">${result}</span> vs ${match.opponent}
                    (${match.team_score}-${match.opponent_score})
                    <small class="text-muted">${match.venue}</small>
                </div>
            </div>
        `;
    });
    
    statsContent.innerHTML = html;
} 