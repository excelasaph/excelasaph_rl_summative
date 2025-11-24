// Daladala RL Agent Visualizer - Frontend JavaScript
// Connects to Flask API and renders agent behavior

const API_URL = 'http://localhost:5000/api';

// State Management
const state = {
    currentAlgorithm: null,
    isModelLoaded: false,
    isPlaying: false,
    isPaused: false,
    currentEpisode: 0,
    currentStep: 0,
    totalReward: 0,
    currentState: null,
    environmentInfo: null,
    playbackSpeed: 1,
    lastAction: null,
    lastReward: 0,
    episodeHistory: []
};

// DOM Elements
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const algorithmSelect = document.getElementById('algorithmSelect');
const loadBtn = document.getElementById('loadBtn');
const resetBtn = document.getElementById('resetBtn');
const playBtn = document.getElementById('playBtn');
const pauseBtn = document.getElementById('pauseBtn');
const stepBtn = document.getElementById('stepBtn');
const speedSlider = document.getElementById('speedSlider');
const messageContainer = document.getElementById('messageContainer');

// Visualization Constants
const GRID_SIZE = 15;
const CELL_SIZE = 40;
const COLORS = {
    background: '#fff',
    grid: '#e0e0e0',
    agent: '#4CAF50',
    highDemandStop: '#FFC107',
    police: '#F44336',
    trafficLight: '#FF9800',
    regularStop: '#2196F3',
    passenger: '#FF6B6B',
    money: '#4CAF50'
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    renderCanvas();
});

function setupEventListeners() {
    loadBtn.addEventListener('click', loadModel);
    resetBtn.addEventListener('click', resetEpisode);
    playBtn.addEventListener('click', playEpisode);
    pauseBtn.addEventListener('click', pauseEpisode);
    stepBtn.addEventListener('click', stepEpisode);
    speedSlider.addEventListener('input', updateSpeed);
    algorithmSelect.addEventListener('change', () => {
        if (state.isModelLoaded) {
            showMessage('Select a different algorithm and click Load Model to switch.', 'info');
        }
    });
}

// Message Display
function showMessage(message, type = 'info') {
    const div = document.createElement('div');
    div.className = `info-message ${type === 'error' ? 'error' : ''}`;
    div.textContent = message;
    messageContainer.innerHTML = '';
    messageContainer.appendChild(div);
    
    if (type === 'info') {
        setTimeout(() => messageContainer.innerHTML = '', 5000);
    }
}

function showError(error) {
    showMessage(`Error: ${error}`, 'error');
    console.error(error);
}

// API Functions
async function loadModel() {
    const algorithm = algorithmSelect.value;
    if (!algorithm) {
        showMessage('Please select an algorithm', 'error');
        return;
    }

    loadBtn.disabled = true;
    showMessage(`Loading ${algorithm} model...`, 'info');

    try {
        const response = await fetch(`${API_URL}/load-model`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ algorithm })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to load model');
        }

        const data = await response.json();
        state.currentAlgorithm = algorithm;
        state.isModelLoaded = true;

        // Get environment info (with longer timeout)
        try {
            const envResponse = await fetch(`${API_URL}/environment-info`);
            if (envResponse.ok) {
                state.environmentInfo = await envResponse.json();
            }
        } catch (e) {
            console.warn('Environment info load took too long, will retry on reset');
        }

        showMessage(`✅ ${algorithm} model loaded successfully!`, 'info');
        updateUIState();

        // Auto-reset to get initial state
        await resetEpisode();

    } catch (error) {
        showError(error.message);
        state.isModelLoaded = false;
        updateUIState();
    } finally {
        loadBtn.disabled = false;
    }
}

async function resetEpisode() {
    try {
        state.isPlaying = false;
        state.isPaused = false;
        
        const response = await fetch(`${API_URL}/reset`, { method: 'POST' });
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        state.currentState = data.state;
        state.environmentInfo = data.environmentInfo || state.environmentInfo;
        state.currentStep = 0;
        state.totalReward = 0;
        state.lastAction = null;
        state.lastReward = 0;
        state.currentEpisode++;
        state.episodeHistory = [];

        updateMetricsPanel();
        renderCanvas();
        updateUIState();
        updateStatusText(`Episode ${state.currentEpisode} reset. Ready to play.`);

    } catch (error) {
        showError(error.message);
    }
}

async function stepEpisode() {
    if (!state.isModelLoaded || !state.currentState) {
        showError('Load a model and reset the episode first');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/step`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ use_model: true })
        });

        if (!response.ok) {
            const error = await response.json();
            const errorMsg = error.error || 'Unknown error';
            if (errorMsg.includes('done') || errorMsg.includes('Episode')) {
                showMessage('🏁 Episode complete!', 'info');
                state.isPlaying = false;
                updateUIState();
                return;
            }
            throw new Error(errorMsg);
        }

        const data = await response.json();
        
        // Handle case where response has no state
        if (data.state) {
            state.currentState = data.state;
        }
        
        state.currentStep++;
        state.totalReward += data.reward;
        state.lastAction = data.action;
        state.lastReward = data.reward;

        if (data.done) {
            showMessage('🏁 Episode complete!', 'info');
            state.isPlaying = false;
        }

        updateMetricsPanel();
        renderCanvas();
        updateStatusText(`Step ${state.currentStep}: ${data.action} (Reward: ${data.reward})`);

    } catch (error) {
        showError(error.message);
    }
}

async function playEpisode() {
    if (!state.isModelLoaded) {
        showError('Load a model first');
        return;
    }

    state.isPlaying = true;
    state.isPaused = false;
    updateUIState();

    while (state.isPlaying) {
        await stepEpisode();
        
        if (!state.isPlaying) break;
        
        const delay = (1000 / state.playbackSpeed) / 10;
        await new Promise(resolve => setTimeout(resolve, delay));
    }
}

function pauseEpisode() {
    state.isPlaying = false;
    state.isPaused = true;
    updateUIState();
    updateStatusText('Paused');
}

function updateSpeed(e) {
    state.playbackSpeed = parseFloat(e.target.value);
    document.getElementById('speedValue').textContent = `${state.playbackSpeed}x`;
}

function updateUIState() {
    const modelLoaded = state.isModelLoaded;
    resetBtn.disabled = !modelLoaded;
    playBtn.disabled = !modelLoaded || state.isPlaying;
    pauseBtn.disabled = !state.isPlaying;
    stepBtn.disabled = !modelLoaded || state.isPlaying;
    speedSlider.disabled = !modelLoaded;

    if (state.isPlaying) {
        playBtn.textContent = '⏸ Playing...';
        playBtn.disabled = true;
    } else {
        playBtn.textContent = '▶ Play';
    }
}

function updateMetricsPanel() {
    if (!state.currentState) return;

    const st = state.currentState;
    const envInfo = state.environmentInfo;

    // Update metrics
    document.getElementById('episodeNum').textContent = state.currentEpisode;
    document.getElementById('stepNum').textContent = state.currentStep;
    document.getElementById('totalReward').textContent = state.totalReward.toFixed(1);
    document.getElementById('instantReward').textContent = state.lastReward.toFixed(1);

    document.getElementById('passengerCount').textContent = `${st.passengers} / ${st.capacity}`;
    document.getElementById('capacity').textContent = st.capacity;
    document.getElementById('moneyEarned').textContent = st.money.toFixed(0);
    document.getElementById('speed').textContent = st.speed.toFixed(1);
    document.getElementById('position').textContent = `(${st.x}, ${st.y})`;

    // Hazard status
    let hazardText = '🟢 Safe';
    if (st.light_red) hazardText = '🔴 Red Light';
    else if (st.police_here) hazardText = '🚨 Police Here';
    else if (st.must_stop) hazardText = '⚠️ Must Stop';
    document.getElementById('hazardStatusValue').textContent = hazardText;

    // Last action
    if (state.lastAction) {
        document.getElementById('lastAction').textContent = state.lastAction;
        const rewardDisplay = document.getElementById('rewardDisplay');
        const rewardClass = state.lastReward >= 0 ? '' : 'negative';
        const rewardSign = state.lastReward >= 0 ? '+' : '';
        rewardDisplay.innerHTML = `<span class="reward-badge ${rewardClass}">${rewardSign}${state.lastReward.toFixed(1)}</span>`;
    }
}

function updateStatusText(text) {
    document.getElementById('statusText').textContent = text;
}

// Canvas Rendering
function renderCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw grid
    ctx.strokeStyle = COLORS.grid;
    ctx.lineWidth = 1;
    for (let i = 0; i <= GRID_SIZE; i++) {
        // Vertical lines
        ctx.beginPath();
        ctx.moveTo(i * CELL_SIZE, 0);
        ctx.lineTo(i * CELL_SIZE, GRID_SIZE * CELL_SIZE);
        ctx.stroke();

        // Horizontal lines
        ctx.beginPath();
        ctx.moveTo(0, i * CELL_SIZE);
        ctx.lineTo(GRID_SIZE * CELL_SIZE, i * CELL_SIZE);
        ctx.stroke();
    }

    if (!state.currentState || !state.environmentInfo) {
        ctx.fillStyle = '#999';
        ctx.font = '16px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('Load a model to start', canvas.width / 2, canvas.height / 2);
        return;
    }

    const envInfo = state.environmentInfo;
    const st = state.currentState;

    // Draw stops
    if (envInfo.stops) {
        envInfo.stops.forEach((stop, idx) => {
            const [x, y] = stop;
            const isHighDemand = envInfo.high_demand_stops && envInfo.high_demand_stops.includes(idx);
            const color = isHighDemand ? COLORS.highDemandStop : COLORS.regularStop;
            
            drawCell(x, y, color, 0.7);
            
            // Draw stop number
            ctx.fillStyle = '#000';
            ctx.font = 'bold 12px sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(idx.toString(), x * CELL_SIZE + CELL_SIZE / 2, y * CELL_SIZE + CELL_SIZE / 2);
        });
    }

    // Draw hazards
    if (st.hazards) {
        st.hazards.forEach(hazard => {
            const [x, y, type] = hazard;
            const color = type === 'police' ? COLORS.police : COLORS.trafficLight;
            drawCell(x, y, color, 0.5);
            
            // Draw icon
            ctx.fillStyle = '#fff';
            ctx.font = 'bold 16px sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            const icon = type === 'police' ? '🚨' : '🚦';
            ctx.fillText(icon, x * CELL_SIZE + CELL_SIZE / 2, y * CELL_SIZE + CELL_SIZE / 2);
        });
    }

    // Draw agent
    drawAgent(st.x, st.y, st.passengers);

    // Draw information overlay
    drawInfoOverlay();
}

function drawCell(x, y, color, opacity = 1) {
    ctx.fillStyle = color;
    ctx.globalAlpha = opacity;
    ctx.fillRect(x * CELL_SIZE + 2, y * CELL_SIZE + 2, CELL_SIZE - 4, CELL_SIZE - 4);
    ctx.globalAlpha = 1;
}

function drawAgent(x, y, passengers) {
    // Draw agent (bus)
    ctx.fillStyle = COLORS.agent;
    ctx.beginPath();
    ctx.arc(x * CELL_SIZE + CELL_SIZE / 2, y * CELL_SIZE + CELL_SIZE / 2, CELL_SIZE / 3, 0, Math.PI * 2);
    ctx.fill();

    // Draw passenger indicator
    if (passengers > 0) {
        ctx.fillStyle = COLORS.passenger;
        ctx.font = 'bold 10px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(passengers.toString(), x * CELL_SIZE + CELL_SIZE / 2, y * CELL_SIZE + CELL_SIZE / 2);
    }

    // Draw selection border
    ctx.strokeStyle = '#000';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(x * CELL_SIZE + CELL_SIZE / 2, y * CELL_SIZE + CELL_SIZE / 2, CELL_SIZE / 3 + 2, 0, Math.PI * 2);
    ctx.stroke();
}

function drawInfoOverlay() {
    if (!state.currentState) return;

    const st = state.currentState;
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(10, 10, 200, 80);

    ctx.fillStyle = '#fff';
    ctx.font = 'bold 12px monospace';
    ctx.textAlign = 'left';
    const lines = [
        `Episode: ${state.currentEpisode}`,
        `Step: ${state.currentStep}`,
        `Reward: ${state.totalReward.toFixed(1)}`,
        `Speed: ${st.speed.toFixed(1)}`
    ];

    lines.forEach((line, i) => {
        ctx.fillText(line, 20, 25 + i * 15);
    });
}

// Export function for potential future use
async function exportEpisodeData() {
    try {
        const response = await fetch(`${API_URL}/episode-data`);
        return await response.json();
    } catch (error) {
        showError('Failed to export episode data');
        return null;
    }
}

console.log('Daladala RL Visualizer loaded. Ready to connect to Flask API.');
