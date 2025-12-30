let mediaRecorder = null;
let audioChunks = [];
let websocket = null;

// Tab switching
function switchTab(tabName) {
    // Hide all tabs
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Remove active class from buttons
    const buttons = document.querySelectorAll('.tab-btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
}

// Text Translation
async function translateText() {
    const text = document.getElementById('text-input').value.trim();
    if (!text) {
        showStatus('text-status', 'Please enter text to translate', 'error');
        return;
    }
    
    showStatus('text-status', 'Translating...', 'loading');
    
    try {
        const response = await fetch('/api/translate/text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, source_language: 'vi', target_language: 'en' })
        });
        
        if (!response.ok) throw new Error('Translation failed');
        
        const data = await response.json();
        document.getElementById('text-source').textContent = data.source_text;
        document.getElementById('text-translation').textContent = data.translated_text;
        document.getElementById('text-result').classList.add('show');
        showStatus('text-status', 'Translation complete!', 'success');
    } catch (error) {
        showStatus('text-status', 'Error: ' + error.message, 'error');
    }
}

// Audio Upload
async function translateAudio() {
    const fileInput = document.getElementById('audio-file');
    if (!fileInput.files.length) {
        showStatus('audio-status', 'Please select an audio file', 'error');
        return;
    }
    
    showStatus('audio-status', 'Processing audio...', 'loading');
    
    try {
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        
        const response = await fetch('/api/translate/audio', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) throw new Error('Audio translation failed');
        
        const data = await response.json();
        document.getElementById('audio-source').textContent = data.source_text;
        document.getElementById('audio-translation').textContent = data.translated_text;
        document.getElementById('audio-duration').textContent = data.duration_seconds.toFixed(2) + ' seconds';
        document.getElementById('audio-result').classList.add('show');
        showStatus('audio-status', 'Translation complete!', 'success');
    } catch (error) {
        showStatus('audio-status', 'Error: ' + error.message, 'error');
    }
}

// Live Recording
async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };
        
        mediaRecorder.start(2000); // Send chunks every 2 seconds
        
        document.getElementById('record-btn').disabled = true;
        document.getElementById('record-btn').classList.add('recording');
        document.getElementById('stop-btn').disabled = false;
        
        // Connect WebSocket
        connectWebSocket();
        showStatus('live-status', 'Recording... Speak into your microphone', 'success');
    } catch (error) {
        showStatus('live-status', 'Microphone access denied: ' + error.message, 'error');
    }
}

function stopRecording() {
    if (mediaRecorder) {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
        
        document.getElementById('record-btn').disabled = false;
        document.getElementById('record-btn').classList.remove('recording');
        document.getElementById('stop-btn').disabled = true;
        
        if (websocket) websocket.close();
        
        showStatus('live-status', 'Recording stopped', 'success');
    }
}

function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    websocket = new WebSocket(protocol + '//' + window.location.host + '/ws/live-translate');
    
    websocket.onopen = () => {
        showStatus('live-status', 'Connected to live translation server', 'success');
    };
    
    websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.error) {
            showStatus('live-status', 'Error: ' + data.error, 'error');
        } else {
            addLiveTranslation(data);
        }
    };
    
    websocket.onerror = () => {
        showStatus('live-status', 'WebSocket connection error', 'error');
    };
    
    mediaRecorder.ondataavailable = (event) => {
        if (websocket && websocket.readyState === WebSocket.OPEN) {
            websocket.send(event.data);
        }
    };
}

function addLiveTranslation(data) {
    const container = document.getElementById('live-translations');
    const item = document.createElement('div');
    item.className = 'history-item';
    item.innerHTML = `
        <div class="history-source"><strong>Vietnamese:</strong> ${escapeHtml(data.source_text)}</div>
        <div class="history-translation"><strong>English:</strong> ${escapeHtml(data.translated_text)}</div>
    `;
    container.insertBefore(item, container.firstChild);
    document.getElementById('live-result').classList.add('show');
}

// Translation History
async function loadHistory() {
    showStatus('history-status', 'Loading history...', 'loading');
    
    try {
        const response = await fetch('/api/history?limit=20');
        if (!response.ok) throw new Error('Failed to load history');
        
        const data = await response.json();
        const container = document.getElementById('history-list');
        container.innerHTML = '';
        
        if (data.translations.length === 0) {
            container.innerHTML = '<p style="color: #999; text-align: center;">No translations yet</p>';
        } else {
            data.translations.forEach(t => {
                const item = document.createElement('div');
                item.className = 'history-item';
                item.innerHTML = `
                    <div class="history-time">${new Date(t.timestamp).toLocaleString()}</div>
                    <div><strong>Vietnamese:</strong> ${escapeHtml(t.source_text)}</div>
                    <div class="history-translation"><strong>English:</strong> ${escapeHtml(t.translated_text)}</div>
                `;
                container.appendChild(item);
            });
        }
        
        showStatus('history-status', `Showing ${data.returned} of ${data.total_translations} translations`, 'success');
    } catch (error) {
        showStatus('history-status', 'Error: ' + error.message, 'error');
    }
}

// Utility Functions
function showStatus(elementId, message, type) {
    const element = document.getElementById(elementId);
    element.innerHTML = `<div class="status ${type}">${message}</div>`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Drag and drop for file input
document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('audio-file');
    const fileLabel = document.querySelector('.file-input-label');
    
    if (fileLabel) {
        fileLabel.addEventListener('dragover', (e) => {
            e.preventDefault();
            fileLabel.style.background = '#ede7f6';
        });
        
        fileLabel.addEventListener('dragleave', () => {
            fileLabel.style.background = '';
        });
        
        fileLabel.addEventListener('drop', (e) => {
            e.preventDefault();
            fileLabel.style.background = '';
            fileInput.files = e.dataTransfer.files;
        });
    }
});
