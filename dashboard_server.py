# dashboard_server.py - MISSION CONTROL INTERFACE

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import json
from datetime import datetime
from typing import List
from jarvis_brain import jarvis
from logger_system import affilify_logger

app = FastAPI(title="AFFILIFY Command Center")

# WebSocket connections
active_connections: List[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket for real-time updates
    """
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Send live updates every 2 seconds
            status = jarvis.get_current_status()
            await websocket.send_json(status)
            await asyncio.sleep(2)
    
    except WebSocketDisconnect:
        active_connections.remove(websocket)

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """
    Main dashboard HTML
    """
    return """
<!DOCTYPE html>
<html>
<head>
    <title>AFFILIFY Command Center</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
            color: #00ff41;
            overflow: hidden;
        }
        
        .container {
            display: grid;
            grid-template-columns: 300px 1fr;
            grid-template-rows: 80px 1fr;
            height: 100vh;
            gap: 10px;
            padding: 10px;
        }
        
        .header {
            grid-column: 1 / -1;
            background: rgba(0, 255, 65, 0.1);
            border: 2px solid #00ff41;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 30px;
            box-shadow: 0 0 30px rgba(0, 255, 65, 0.3);
        }
        
        .logo {
            font-size: 32px;
            font-weight: bold;
            text-shadow: 0 0 10px #00ff41;
        }
        
        .status {
            display: flex;
            gap: 20px;
        }
        
        .status-item {
            text-align: center;
        }
        
        .status-value {
            font-size: 24px;
            font-weight: bold;
        }
        
        .status-label {
            font-size: 12px;
            opacity: 0.7;
        }
        
        .sidebar {
            background: rgba(0, 255, 65, 0.05);
            border: 2px solid #00ff41;
            border-radius: 10px;
            padding: 20px;
            overflow-y: auto;
        }
        
        .main-content {
            display: grid;
            grid-template-rows: 1fr 1fr;
            gap: 10px;
        }
        
        .panel {
            background: rgba(0, 255, 65, 0.05);
            border: 2px solid #00ff41;
            border-radius: 10px;
            padding: 20px;
            overflow-y: auto;
        }
        
        .panel-title {
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #00ff41;
            text-shadow: 0 0 5px #00ff41;
        }
        
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .metric-card {
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid #00ff41;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }
        
        .metric-value {
            font-size: 28px;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .metric-label {
            font-size: 12px;
            opacity: 0.8;
        }
        
        .activity-feed {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .activity-item {
            background: rgba(0, 0, 0, 0.3);
            border-left: 3px solid #00ff41;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 5px;
            animation: slideIn 0.3s ease-out;
        }
        
        @keyframes slideIn {
            from {
                transform: translateX(-20px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        .timestamp {
            font-size: 11px;
            opacity: 0.6;
        }
        
        .jarvis-brain {
            text-align: center;
            margin: 20px 0;
        }
        
        .brain-icon {
            font-size: 60px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% {
                opacity: 1;
                text-shadow: 0 0 20px #00ff41;
            }
            50% {
                opacity: 0.7;
                text-shadow: 0 0 40px #00ff41;
            }
        }
        
        .success { color: #00ff41; }
        .warning { color: #ffaa00; }
        .error { color: #ff0040; }
        .info { color: #00aaff; }
        
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.3);
        }
        
        ::-webkit-scrollbar-thumb {
            background: #00ff41;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div class="logo">🚀 AFFILIFY COMMAND CENTER</div>
            <div class="status">
                <div class="status-item">
                    <div class="status-value" id="comments-today">0</div>
                    <div class="status-label">COMMENTS TODAY</div>
                </div>
                <div class="status-item">
                    <div class="status-value" id="success-rate">100%</div>
                    <div class="status-label">SUCCESS RATE</div>
                </div>
                <div class="status-item">
                    <div class="status-value" id="active-accounts">0</div>
                    <div class="status-label">ACTIVE ACCOUNTS</div>
                </div>
            </div>
        </div>
        
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="jarvis-brain">
                <div class="brain-icon">🧠</div>
                <h3>JARVIS</h3>
                <p style="font-size: 12px; opacity: 0.7;">Dolphin-X1-Llama-3.1</p>
                <p id="jarvis-status" class="success">OPERATIONAL</p>
            </div>
            
            <div class="panel-title">AI DECISIONS</div>
            <div id="ai-decisions" class="activity-feed"></div>
            
            <div class="panel-title" style="margin-top: 20px;">CODE MODIFICATIONS</div>
            <div id="code-mods" class="activity-feed"></div>
        </div>
        
        <!-- Main Content -->
        <div class="main-content">
            <!-- Top Panel: Metrics -->
            <div class="panel">
                <div class="panel-title">📊 LIVE METRICS</div>
                <div class="metric-grid">
                    <div class="metric-card">
                        <div class="metric-label">TOTAL COMMENTS</div>
                        <div class="metric-value" id="total-comments">0</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">ERRORS</div>
                        <div class="metric-value error" id="total-errors">0</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">AI FIXES</div>
                        <div class="metric-value info" id="ai-fixes">0</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">OPTIMIZATIONS</div>
                        <div class="metric-value warning" id="optimizations">0</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">AVG COMMENT TIME</div>
                        <div class="metric-value" id="avg-time">0s</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">TARGETS QUEUED</div>
                        <div class="metric-value" id="targets">0</div>
                    </div>
                </div>
            </div>
            
            <!-- Bottom Panel: Activity Feed -->
            <div class="panel">
                <div class="panel-title">📡 LIVE ACTIVITY FEED</div>
                <div id="activity-feed" class="activity-feed"></div>
            </div>
        </div>
    </div>
    
    <script>
        // WebSocket connection
        const ws = new WebSocket('ws://localhost:8000/ws');
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            updateDashboard(data);
        };
        
        function updateDashboard(data) {
            const metrics = data.metrics;
            
            // Update header
            document.getElementById('comments-today').textContent = metrics.total_comments_posted || 0;
            document.getElementById('success-rate').textContent = (metrics.success_rate || 100).toFixed(1) + '%';
            document.getElementById('active-accounts').textContent = metrics.accounts_active || 0;
            
            // Update metrics
            document.getElementById('total-comments').textContent = metrics.total_comments_posted || 0;
            document.getElementById('total-errors').textContent = metrics.total_errors || 0;
            document.getElementById('ai-fixes').textContent = metrics.code_fixes_deployed || 0;
            document.getElementById('optimizations').textContent = metrics.ai_optimizations_made || 0;
            document.getElementById('avg-time').textContent = (metrics.avg_comment_time || 0).toFixed(1) + 's';
            document.getElementById('targets').textContent = metrics.current_targets || 0;
            
            // Update JARVIS status
            const jarvisStatus = document.getElementById('jarvis-status');
            if (data.monitoring_active && data.optimization_active) {
                jarvisStatus.textContent = 'OPERATIONAL';
                jarvisStatus.className = 'success';
            } else {
                jarvisStatus.textContent = 'DEGRADED';
                jarvisStatus.className = 'warning';
            }
            
            // Update AI decisions
            if (data.recent_decisions) {
                updateAIDecisions(data.recent_decisions);
            }
            
            // Update code modifications
            if (data.recent_modifications) {
                updateCodeModifications(data.recent_modifications);
            }
        }
        
        function updateAIDecisions(decisions) {
            const container = document.getElementById('ai-decisions');
            container.innerHTML = '';
            
            decisions.slice(-10).reverse().forEach(decision => {
                const item = document.createElement('div');
                item.className = 'activity-item';
                item.innerHTML = `
                    <div class="timestamp">${new Date(decision.timestamp).toLocaleTimeString()}</div>
                    <div>${decision.type}: ${decision.analysis?.health_status || 'Processing...'}</div>
                `;
                container.appendChild(item);
            });
        }
        
        function updateCodeModifications(mods) {
            const container = document.getElementById('code-mods');
            container.innerHTML = '';
            
            mods.slice(-5).reverse().forEach(mod => {
                const item = document.createElement('div');
                item.className = 'activity-item';
                item.innerHTML = `
                    <div class="timestamp">${new Date(mod.timestamp).toLocaleTimeString()}</div>
                    <div class="success">✓ ${mod.error_type} - ${mod.status}</div>
                `;
                container.appendChild(item);
            });
        }
        
        // Simulate activity feed (in production, this would come from WebSocket)
        function addActivity(message, type = 'info') {
            const feed = document.getElementById('activity-feed');
            const item = document.createElement('div');
            item.className = 'activity-item';
            item.innerHTML = `
                <div class="timestamp">${new Date().toLocaleTimeString()}</div>
                <div class="${type}">${message}</div>
            `;
            feed.insertBefore(item, feed.firstChild);
            
            // Keep only last 50 items
            while (feed.children.length > 50) {
                feed.removeChild(feed.lastChild);
            }
        }
        
        // Connection status
        ws.onopen = function() {
            addActivity('🟢 Connected to JARVIS', 'success');
        };
        
        ws.onerror = function() {
            addActivity('🔴 Connection error', 'error');
        };
        
        ws.onclose = function() {
            addActivity('🟡 Disconnected from JARVIS', 'warning');
        };
    </script>
</body>
</html>
    """

@app.get("/api/status")
async def get_status():
    """
    API endpoint for current status
    """
    return jarvis.get_current_status()

@app.post("/api/command/{command}")
async def send_command(command: str):
    """
    Send command to JARVIS
    """
    # Commands: optimize, analyze, fix_errors, etc.
    return {"status": "command_received", "command": command}


# Run dashboard
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
