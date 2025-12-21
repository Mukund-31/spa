"""
GAN Training Dashboard - Minimalistic professional design
"""
from flask import Flask, render_template_string, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Store training data
training_data = {
    'rounds': [],
    'generator_scores': [],
    'discriminator_scores': [],
    'generator_learnings': [],
    'discriminator_learnings': [],
    'agent_scores_history': []
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>GAN Training Monitor</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
            padding: 40px;
            min-height: 100vh;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        
        header {
            border-bottom: 1px solid #222;
            padding-bottom: 20px;
            margin-bottom: 40px;
        }
        h1 {
            font-size: 1.5rem;
            font-weight: 500;
            color: #fff;
            letter-spacing: -0.5px;
        }
        .subtitle {
            color: #666;
            font-size: 0.875rem;
            margin-top: 4px;
        }
        
        .metrics {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 40px;
        }
        .metric {
            background: #111;
            border: 1px solid #222;
            border-radius: 4px;
            padding: 20px;
        }
        .metric-label {
            font-size: 0.75rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }
        .metric-value {
            font-size: 2rem;
            font-weight: 600;
            font-family: 'SF Mono', Monaco, monospace;
        }
        .metric-value.red { color: #ff4444; }
        .metric-value.green { color: #44ff88; }
        .metric-value.white { color: #fff; }
        
        .charts {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 40px;
        }
        .chart-box {
            background: #111;
            border: 1px solid #222;
            border-radius: 4px;
            padding: 20px;
        }
        .chart-title {
            font-size: 0.875rem;
            color: #888;
            margin-bottom: 15px;
        }
        
        .agents {
            background: #111;
            border: 1px solid #222;
            border-radius: 4px;
            padding: 20px;
            margin-bottom: 40px;
        }
        .agents-title {
            font-size: 0.875rem;
            color: #888;
            margin-bottom: 15px;
        }
        .agents-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 10px;
        }
        .agent {
            background: #0a0a0a;
            border: 1px solid #1a1a1a;
            border-radius: 4px;
            padding: 12px;
            text-align: center;
        }
        .agent-name {
            font-size: 0.7rem;
            color: #555;
            margin-bottom: 4px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .agent-score {
            font-size: 1.25rem;
            font-weight: 600;
            font-family: 'SF Mono', Monaco, monospace;
            color: #888;
        }
        
        .logs {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .log-box {
            background: #111;
            border: 1px solid #222;
            border-radius: 4px;
            padding: 20px;
        }
        .log-title {
            font-size: 0.75rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
        }
        .log-title.red { color: #ff4444; }
        .log-title.green { color: #44ff88; }
        .log-items {
            font-size: 0.8rem;
            color: #888;
            max-height: 120px;
            overflow-y: auto;
        }
        .log-item {
            padding: 6px 0;
            border-bottom: 1px solid #1a1a1a;
        }
        .log-round {
            color: #444;
            font-family: monospace;
            margin-right: 8px;
        }
        
        .status {
            text-align: center;
            color: #444;
            font-size: 0.75rem;
            padding: 20px 0;
            border-top: 1px solid #222;
            margin-top: 40px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>GAN Training Monitor</h1>
            <p class="subtitle">Generator vs Discriminator • Real-time Analysis</p>
        </header>
        
        <div class="metrics">
            <div class="metric">
                <div class="metric-label">Round</div>
                <div class="metric-value white" id="round">0</div>
            </div>
            <div class="metric">
                <div class="metric-label">Generator (Evasion)</div>
                <div class="metric-value red" id="gen-score">0%</div>
            </div>
            <div class="metric">
                <div class="metric-label">Discriminator (Detection)</div>
                <div class="metric-value green" id="disc-score">0%</div>
            </div>
            <div class="metric">
                <div class="metric-label">Status</div>
                <div class="metric-value white" id="status-text" style="font-size: 1rem;">Waiting</div>
            </div>
        </div>
        
        <div class="charts">
            <div class="chart-box">
                <div class="chart-title">Training Progress</div>
                <canvas id="ganChart"></canvas>
            </div>
            <div class="chart-box">
                <div class="chart-title">Agent Scores</div>
                <canvas id="agentChart"></canvas>
            </div>
        </div>
        
        <div class="agents">
            <div class="agents-title">Latest Agent Scores</div>
            <div class="agents-grid" id="agent-scores">
                <div class="agent"><div class="agent-name">—</div><div class="agent-score">—</div></div>
            </div>
        </div>
        
        <div class="logs">
            <div class="log-box">
                <div class="log-title red">Generator Learnings</div>
                <div class="log-items" id="gen-learnings"><em style="color:#333">No data</em></div>
            </div>
            <div class="log-box">
                <div class="log-title green">Discriminator Learnings</div>
                <div class="log-items" id="disc-learnings"><em style="color:#333">No data</em></div>
            </div>
        </div>
        
        <div class="status" id="status">Waiting for training data...</div>
    </div>
    
    <script>
        Chart.defaults.color = '#666';
        Chart.defaults.borderColor = '#222';
        
        const ganChart = new Chart(document.getElementById('ganChart'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    { label: 'Generator', data: [], borderColor: '#ff4444', backgroundColor: 'transparent', tension: 0.3, borderWidth: 2, pointRadius: 3 },
                    { label: 'Discriminator', data: [], borderColor: '#44ff88', backgroundColor: 'transparent', tension: 0.3, borderWidth: 2, pointRadius: 3 }
                ]
            },
            options: {
                responsive: true,
                plugins: { legend: { labels: { boxWidth: 12, font: { size: 11 } } } },
                scales: { y: { min: 0, max: 100, grid: { color: '#1a1a1a' } }, x: { grid: { color: '#1a1a1a' } } }
            }
        });
        
        const agentChart = new Chart(document.getElementById('agentChart'), {
            type: 'line',
            data: { labels: [], datasets: [] },
            options: {
                responsive: true,
                plugins: { legend: { position: 'bottom', labels: { boxWidth: 8, font: { size: 10 } } } },
                scales: { y: { min: 0, max: 100, grid: { color: '#1a1a1a' } }, x: { grid: { color: '#1a1a1a' } } }
            }
        });
        
        const colors = ['#ff4444', '#44ff88', '#ffaa44', '#44aaff', '#ff44aa', '#aaaaaa'];
        
        function update() {
            fetch('/api/training-data').then(r => r.json()).then(data => {
                if (data.rounds.length > 0) {
                    const n = data.rounds.length;
                    document.getElementById('round').textContent = data.rounds[n-1];
                    document.getElementById('gen-score').textContent = data.generator_scores[n-1].toFixed(1) + '%';
                    document.getElementById('disc-score').textContent = data.discriminator_scores[n-1].toFixed(1) + '%';
                    document.getElementById('status-text').textContent = 'Running';
                    document.getElementById('status').textContent = 'Training in progress • ' + n + ' rounds completed';
                    
                    ganChart.data.labels = data.rounds.map(r => r);
                    ganChart.data.datasets[0].data = data.generator_scores;
                    ganChart.data.datasets[1].data = data.discriminator_scores;
                    ganChart.update('none');
                    
                    if (data.agent_scores_history.length > 0) {
                        const agents = new Set();
                        data.agent_scores_history.forEach(s => Object.keys(s).filter(k => !k.includes('collaboration')).forEach(k => agents.add(k)));
                        agentChart.data.labels = data.rounds.map(r => r);
                        agentChart.data.datasets = Array.from(agents).map((name, i) => ({
                            label: name.replace('Analyst', '').replace('Detector', ''),
                            data: data.agent_scores_history.map(s => s[name] || null),
                            borderColor: colors[i % colors.length],
                            backgroundColor: 'transparent',
                            tension: 0.3,
                            borderWidth: 1.5,
                            pointRadius: 2
                        }));
                        agentChart.update('none');
                        
                        const latest = data.agent_scores_history[n-1] || {};
                        document.getElementById('agent-scores').innerHTML = Object.entries(latest)
                            .map(([k,v]) => `<div class="agent"><div class="agent-name">${k}</div><div class="agent-score">${v.toFixed(0)}%</div></div>`)
                            .join('');
                    }
                    
                    document.getElementById('gen-learnings').innerHTML = data.generator_learnings
                        .map((l,i) => `<div class="log-item"><span class="log-round">${i+1}</span>${l}</div>`).join('') || '<em>None</em>';
                    document.getElementById('disc-learnings').innerHTML = data.discriminator_learnings
                        .map((l,i) => `<div class="log-item"><span class="log-round">${i+1}</span>${l}</div>`).join('') || '<em>None</em>';
                }
            });
        }
        setInterval(update, 2000);
        update();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/training-data')
def get_training_data():
    return jsonify(training_data)

@app.route('/api/update', methods=['POST'])
def update_training():
    from flask import request
    data = request.json
    training_data['rounds'].append(data.get('round', len(training_data['rounds']) + 1))
    training_data['generator_scores'].append(data.get('generator_score', 0))
    training_data['discriminator_scores'].append(data.get('discriminator_score', 0))
    training_data['generator_learnings'].append(data.get('generator_learning', ''))
    training_data['discriminator_learnings'].append(data.get('discriminator_learning', ''))
    training_data['agent_scores_history'].append(data.get('agent_scores', {}))
    return jsonify({'status': 'ok'})

@app.route('/api/reset', methods=['POST'])
def reset_training():
    for key in training_data:
        training_data[key] = []
    return jsonify({'status': 'reset'})

if __name__ == '__main__':
    print("GAN Training Monitor")
    print("→ http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
