import streamlit as st
import streamlit.components.v1 as components

# Remove duplicate page config since it's already set in main app
# st.set_page_config(page_title="Medical Voice Analyzer", layout="wide")

# Enhanced header with consistent styling
st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h1 style="
            font-size: 2.8rem; font-weight: 800; margin-bottom: 0.5rem;
            background: linear-gradient(90deg, #00e5ff, #7c4dff, #00e676);
            background-size: 200% auto; -webkit-background-clip: text;
            background-clip: text; color: transparent;
            animation: gradient 5s linear infinite;
        ">🎙️ Voice-to-Text Analysis</h1>
        <p style="font-size: 1.1rem; color: rgba(255, 255, 255, 0.8); margin: 0;">
            Record medical conversations with real-time transcription and AI-powered analysis
        </p>
    </div>
    <style>
        @keyframes gradient {
            0% { background-position: 0% center; }
            100% { background-position: 200% center; }
        }
    </style>
""", unsafe_allow_html=True)

components.html("""
<html>
<head>
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }

    body {
        font-family: 'Segoe UI', sans-serif;
        background: #0f0f0f;
        background-image: radial-gradient(#212121 1px, transparent 1px),
                          radial-gradient(#212121 1px, transparent 1px);
        background-size: 40px 40px;
        background-position: 0 0, 20px 20px;
        animation: moveBackground 60s linear infinite;
        padding: 30px;
        color: #e0e0e0;
    }

    @keyframes moveBackground {
        from { background-position: 0 0, 20px 20px; }
        to { background-position: 1000px 1000px, 1020px 1020px; }
    }

    .container {
        max-width: 100%;
        margin: auto;
        display: flex;
        flex-direction: row;
        gap: 30px;
        align-items: flex-start;
    }

    .left-panel, .right-panel {
        border-radius: 20px;
        backdrop-filter: blur(12px);
        background: rgba(38, 50, 56, 0.6);
        box-shadow: 0 8px 25px rgba(0,0,0,0.5);
        padding: 30px;
    }

    .left-panel {
        flex: 0.3;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .right-panel {
        flex: 0.7;
        max-height: 90vh;
        overflow-y: auto;
    }

    .neon-title {
        text-align: center;
        font-size: 36px;
        font-weight: 800;
        margin-bottom: 10px;
        background: linear-gradient(90deg, #00e5ff, #7c4dff, #00e5ff);
        background-size: 300%;
        color: transparent;
        -webkit-background-clip: text;
        background-clip: text;
        animation: glowMove 5s infinite linear;
        text-shadow: 0 0 10px #00e5ff99, 0 0 20px #7c4dff55;
    }

    @keyframes glowMove {
        0% { background-position: 0%; }
        100% { background-position: 300%; }
    }

    .subtext {
        text-align: center;
        font-size: 18px;
        color: #b0bec5;
        margin-bottom: 30px;
    }

    /* Same previous panel styles (reuse from dark version) */
    .button-row {
        display: flex;
        gap: 15px;
        margin-top: 20px;
    }

    .btn {
        padding: 12px 25px;
        font-size: 15px;
        border: none;
        border-radius: 30px;
        cursor: pointer;
        font-weight: bold;
        width: 180px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }

    .btn-start { background: linear-gradient(135deg, #7c4dff 0%, #00e5ff 100%); color: white; }
    .btn-stop { background: linear-gradient(135deg, #ff1744 0%, #d32f2f 100%); color: white; }
    .btn-summary { margin-top: 20px; background: linear-gradient(135deg, #00e676 0%, #00c853 100%); color: white; }

    .btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.5);
        opacity: 0.95;
    }

    .status-indicator {
        margin-top: 20px;
        padding: 12px 20px;
        background: rgba(25, 118, 210, 0.15);
        border: 1px solid #90caf9;
        border-radius: 30px;
        font-weight: 500;
        font-size: 14px;
        color: #90caf9;
    }

    .live-section {
        margin-bottom: 30px;
        background: rgba(0, 230, 118, 0.1);
        border-left: 5px solid #00e676;
        border-radius: 10px;
        padding: 15px 20px;
        color: #c8e6c9;
        animation: pulse 2s infinite ease-in-out;
    }

    @keyframes pulse {
        0% { box-shadow: 0 0 0px #00e67633; }
        50% { box-shadow: 0 0 12px #00e67699; }
        100% { box-shadow: 0 0 0px #00e67633; }
    }

    .timeline-item {
        margin-top: 15px;
        padding: 15px;
        border-left: 5px solid #90caf9;
        background: rgba(55,71,79,0.6);
        border-radius: 10px;
        color: #ffffff;
        transition: all 0.3s;
    }

    .timeline-item:hover {
        transform: scale(1.01);
        background: rgba(69, 90, 100, 0.8);
    }

    .speaker-doctor { border-left-color: #00e676; }
    .speaker-patient { border-left-color: #2979ff; }

    .section-title {
        font-weight: bold;
        font-size: 20px;
        margin-top: 30px;
        color: #ffffff;
    }

    .transcript-content, .summary-result {
        background: rgba(55,71,79,0.7);
        border-radius: 10px;
        padding: 15px 20px;
        margin-top: 10px;
        color: #fff;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.4);
    }

    @media (max-width: 1024px) {
        .container {
            flex-direction: column;
        }
        .left-panel, .right-panel {
            flex: 1;
            width: 100%;
        }
        .button-row {
            justify-content: center;
            flex-wrap: wrap;
        }
    }
</style>
</head>
<body>
    <div class="neon-title">Doctor-Patient Voice Conversation Analyzer</div>
    <div class="subtext">Record medical conversations, separate speakers, and get AI-based summaries</div>

    <div class="container">
        <div class="left-panel">
            <h2>🎙️ Start Recording</h2>
            <div class="button-row">
                <button class="btn btn-start" id="startBtn">Start</button>
                <button class="btn btn-stop" id="stopBtn" disabled>Stop</button>
            </div>
            <div class="status-indicator" id="status">Waiting to start...</div>
        </div>
        <div class="right-panel">
            <div class="live-section">
                <div><strong>Live Words:</strong> <span id="liveWords">Listening...</span></div>
            </div>
            <div id="result"></div>
        </div>
    </div>
<script>
let mediaRecorder;
let audioChunks = [];
let recognition;
let isRecording = false;

// Initialize speech recognition
if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onresult = function(event) {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }

        document.getElementById('liveWords').textContent =
            finalTranscript + (interimTranscript ? ' ' + interimTranscript : '');
    };

    recognition.onerror = function(event) {
        console.error('Speech recognition error:', event.error);
    };
}

// Add click event listeners
document.getElementById('startBtn').addEventListener('click', startRecording);
document.getElementById('stopBtn').addEventListener('click', stopRecording);

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            await processAudio(audioBlob);
        };

        mediaRecorder.start();
        isRecording = true;

        // Start speech recognition
        if (recognition) {
            recognition.start();
        }

        // Update UI
        document.getElementById('startBtn').disabled = true;
        document.getElementById('stopBtn').disabled = false;
        document.getElementById('status').textContent = '🔴 Recording...';

    } catch (error) {
        console.error('Error starting recording:', error);
        alert('Error accessing microphone. Please check permissions.');
    }
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
        isRecording = false;

        // Stop speech recognition
        if (recognition) {
            recognition.stop();
        }

        // Update UI
        document.getElementById('startBtn').disabled = false;
        document.getElementById('stopBtn').disabled = true;
        document.getElementById('status').textContent = '⏳ Processing...';
    }
}

async function processAudio(audioBlob) {
    try {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');

        const response = await fetch('http://localhost:8000/analyze-conversation/', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        displayResults(data);

        document.getElementById('status').textContent = '✅ Done';

    } catch (error) {
        console.error('Error processing audio:', error);
        document.getElementById('status').textContent = '❌ Error - Ready to try again';
        alert('Error processing audio. Please check if the backend server is running.');
    }
}

function displayResults(data) {
    let html = ``;

    if (data.full_conversation) {
        html += `<div class="section-title">👥 Conversation Timeline</div>`;

        data.full_conversation.forEach(entry => {
            const speakerClass = entry.speaker === 'doctor' ? 'speaker-doctor' : 'speaker-patient';
            html += `
                <div class="timeline-item ${speakerClass}">
                    <strong>${entry.speaker.toUpperCase()}:</strong> ${entry.text}
                </div>
            `;
        });

        html += `<button class="btn btn-summary" onclick="generateSummary()">
                    🧠 Generate Summary
                 </button>`;
    }

    document.getElementById('result').innerHTML = html;
}

async function generateSummary() {
    try {
        const button = document.querySelector('.btn-summary');
        button.disabled = true;
        button.textContent = '⏳ Generating Summary...';

        const response = await fetch('http://localhost:8000/generate-summary/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                conversation: document.getElementById('result').textContent
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        const summaryHtml = `
            <div class="section-title">📋 AI Summary</div>
            <div class="summary-result">${data.summary}</div>
        `;

        document.getElementById('result').innerHTML += summaryHtml;

        button.disabled = false;
        button.textContent = '🧠 Generate Summary';

    } catch (error) {
        console.error('Error generating summary:', error);
        alert('Error generating summary. Please try again.');

        const button = document.querySelector('.btn-summary');
        button.disabled = false;
        button.textContent = '🧠 Generate Summary';
    }
}
</script>
</body>
</html>

""", height=900, scrolling=True)
