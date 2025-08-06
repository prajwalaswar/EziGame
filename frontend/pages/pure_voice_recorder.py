import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Pure Voice Recorder",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS for the recorder
enhanced_css = """
<style>
    /* Base Styles */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: 'Poppins', 'Segoe UI', sans-serif;
    }
    do
    /* Main Container */
    .recorder-container {
        background: linear-gradient(135deg, #0a0818 0%, #1a1630 100%);
        min-height: 100vh;
        padding: 2rem;
        color: #ffffff;
        position: relative;
        overflow: hidden;
    }
    
    /* Background Effects */
    .audio-wave {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 150px;
        background: url('data:image/svg+xml;utf8,<svg viewBox="0 0 1440 320" xmlns="http://www.w3.org/2000/svg"><path fill="rgba(124, 77, 255, 0.1)" d="M0,192L48,197.3C96,203,192,213,288,229.3C384,245,480,267,576,250.7C672,235,768,181,864,181.3C960,181,1056,235,1152,234.7C1248,235,1344,181,1392,154.7L1440,128L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>');
        background-size: cover;
        background-repeat: no-repeat;
        z-index: 0;
    }
    
    .pulse-circle {
        position: absolute;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(0, 229, 255, 0.08) 0%, transparent 70%);
        border-radius: 50%;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 0;
        animation: pulse 4s infinite ease-in-out;
    }
    
    @keyframes pulse {
        0% { transform: translate(-50%, -50%) scale(0.8); opacity: 0.5; }
        50% { transform: translate(-50%, -50%) scale(1.1); opacity: 0.2; }
        100% { transform: translate(-50%, -50%) scale(0.8); opacity: 0.5; }
    }
    
    /* Header Styles */
    .recorder-header {
        text-align: center;
        margin-bottom: 2rem;
        position: relative;
        z-index: 2;
    }
    
    .recorder-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #00e5ff, #7c4dff);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        position: relative;
        display: inline-block;
    }
    
    .recorder-title::after {
        content: '';
        position: absolute;
        bottom: -8px;
        left: 50%;
        transform: translateX(-50%);
        width: 100px;
        height: 4px;
        background: linear-gradient(90deg, #00e5ff, #7c4dff);
        border-radius: 2px;
    }
    
    .recorder-subtitle {
        font-size: 1.2rem;
        color: rgba(255, 255, 255, 0.7);
        max-width: 600px;
        margin: 0 auto;
    }
    
    /* Main Panel */
    .recorder-panel {
        max-width: 600px;
        margin: 2rem auto;
        background: rgba(30, 30, 60, 0.5);
        backdrop-filter: blur(12px);
        border-radius: 24px;
        padding: 3rem 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(124, 77, 255, 0.2);
        position: relative;
        z-index: 2;
        transition: all 0.3s ease;
    }
    
    .recorder-panel:hover {
        border: 1px solid rgba(124, 77, 255, 0.4);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
    }
    
    /* Button Styles */
    .btn-container {
        display: flex;
        justify-content: center;
        gap: 1.5rem;
        margin: 2rem 0;
        flex-wrap: wrap;
    }
    
    .recorder-btn {
        padding: 1.2rem 2.5rem;
        font-size: 1.2rem;
        font-weight: 600;
        border: none;
        border-radius: 50px;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        z-index: 1;
        min-width: 220px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .recorder-btn::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, #7c4dff 0%, #00e5ff 100%);
        z-index: -1;
        transition: all 0.3s ease;
    }
    
    .recorder-btn:hover::before {
        filter: brightness(1.1);
        transform: scale(1.05);
    }
    
    .recorder-btn:active {
        transform: scale(0.98);
    }
    
    .recorder-btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }
    
    .recorder-btn:disabled::before {
        background: linear-gradient(135deg, #555 0%, #777 100%);
    }
    
    .btn-start::before {
        background: linear-gradient(135deg, #00e676 0%, #00e5ff 100%);
    }
    
    .btn-stop::before {
        background: linear-gradient(135deg, #ff1744 0%, #7c4dff 100%);
    }
    
    .btn-download::before {
        background: linear-gradient(135deg, #2979ff 0%, #00e5ff 100%);
    }
    
    /* Status Indicator */
    .status-indicator {
        padding: 1.2rem;
        margin: 1.5rem 0;
        border-radius: 12px;
        font-weight: 600;
        text-align: center;
        background: rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(124, 77, 255, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .status-indicator::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        height: 100%;
        width: 5px;
        background: #7c4dff;
    }
    
    .status-recording {
        border-color: rgba(255, 23, 68, 0.3);
        animation: statusPulse 2s infinite;
    }
    
    .status-recording::before {
        background: #ff1744;
    }
    
    .status-processing {
        border-color: rgba(0, 229, 255, 0.3);
    }
    
    .status-processing::before {
        background: #00e5ff;
    }
    
    .status-ready {
        border-color: rgba(0, 230, 118, 0.3);
    }
    
    .status-ready::before {
        background: #00e676;
    }
    
    @keyframes statusPulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 23, 68, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(255, 23, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 23, 68, 0); }
    }
    
    /* Back Link */
    .back-link {
        display: inline-flex;
        align-items: center;
        color: #00e5ff;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        text-decoration: none;
        transition: all 0.3s ease;
        position: relative;
        z-index: 2;
    }
    
    .back-link:hover {
        color: #7c4dff;
        transform: translateX(-5px);
    }
    
    /* Download Section */
    .download-section {
        margin-top: 2rem;
        text-align: center;
        animation: fadeIn 0.5s ease;
    }
    
    .download-message {
        color: rgba(255, 255, 255, 0.8);
        margin-top: 1rem;
        font-size: 1rem;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Responsive Adjustments */
    @media (max-width: 768px) {
        .recorder-title {
            font-size: 2.2rem;
        }
        
        .recorder-subtitle {
            font-size: 1rem;
        }
        
        .btn-container {
            flex-direction: column;
            align-items: center;
        }
        
        .recorder-btn {
            width: 100%;
        }
    }
</style>
"""

# HTML for the enhanced recorder
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pure Voice Recorder</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    {enhanced_css}
</head>
<body>
    <div class="recorder-container">
        <div class="pulse-circle"></div>
        <div class="audio-wave"></div>
        
        <div class="recorder-header">
            <h1 class="recorder-title">🔊 Pure Voice Recorder</h1>
            <p class="recorder-subtitle">Record high-quality audio and download as MP3</p>
            <a href="#" class="back-link">← Back to Main Menu</a>
        </div>
        
        <div class="recorder-panel">
            <div class="btn-container">
                <button class="recorder-btn btn-start" id="startBtn">🎤 Start Recording</button>
                <button class="recorder-btn btn-stop" id="stopBtn" disabled>⏹️ Stop Recording</button>
            </div>
            
            <div class="status-indicator" id="status">Ready to record...</div>
            
            <div id="downloadSection" class="download-section" style="display: none;">
                <button class="recorder-btn btn-download" id="downloadBtn">⬇️ Download MP3</button>
                <p class="download-message">Your recording is ready! Click above to download.</p>
            </div>
        </div>
    </div>
    
    <script>
        let mediaRecorder;
        let audioChunks = [];
        let isRecording = false;
        let audioUrl = null;
        
        // DOM elements
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        const statusDiv = document.getElementById('status');
        const downloadSection = document.getElementById('downloadSection');
        const downloadBtn = document.getElementById('downloadBtn');
        
        // Event listeners
        startBtn.addEventListener('click', startRecording);
        stopBtn.addEventListener('click', stopRecording);
        downloadBtn.addEventListener('click', downloadRecording);
        
        // Start recording function
        async function startRecording() {{
            try {{
                const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];
                
                mediaRecorder.ondataavailable = event => {{
                    audioChunks.push(event.data);
                }};
                
                mediaRecorder.onstop = async () => {{
                    const audioBlob = new Blob(audioChunks, {{ type: 'audio/wav' }});
                    await processAudio(audioBlob);
                }};
                
                mediaRecorder.start();
                isRecording = true;
                
                // Update UI
                startBtn.disabled = true;
                stopBtn.disabled = false;
                statusDiv.textContent = '🔴 Recording in progress...';
                statusDiv.className = 'status-indicator status-recording';
                downloadSection.style.display = 'none';
                
                // Clean up previous recording
                if (audioUrl) {{
                    URL.revokeObjectURL(audioUrl);
                    audioUrl = null;
                }}
                
            }} catch (error) {{
                console.error('Error starting recording:', error);
                statusDiv.textContent = '❌ Error accessing microphone';
                statusDiv.className = 'status-indicator';
                alert('Please allow microphone access to use the recorder.');
            }}
        }}
        
        // Stop recording function
        function stopRecording() {{
            if (mediaRecorder && isRecording) {{
                mediaRecorder.stop();
                mediaRecorder.stream.getTracks().forEach(track => track.stop());
                isRecording = false;
                
                // Update UI
                startBtn.disabled = false;
                stopBtn.disabled = true;
                statusDiv.textContent = 'Processing recording...';
                statusDiv.className = 'status-indicator status-processing';
            }}
        }}
        
        // Process audio function
        async function processAudio(audioBlob) {{
            try {{
                // Simulate processing delay
                await new Promise(resolve => setTimeout(resolve, 1500));
                
                // In a real app, you would send to server here
                // For demo, we'll create a client-side download link
                audioUrl = URL.createObjectURL(audioBlob);
                
                // Update UI
                statusDiv.textContent = '✅ Recording complete!';
                statusDiv.className = 'status-indicator status-ready';
                downloadSection.style.display = 'block';
                
            }} catch (error) {{
                console.error('Error processing audio:', error);
                statusDiv.textContent = '❌ Error processing recording';
                statusDiv.className = 'status-indicator';
                alert('Error processing audio. Please try again.');
            }}
        }}
        
        // Download recording function
        function downloadRecording() {{
            if (audioUrl) {{
                const a = document.createElement('a');
                a.href = audioUrl;
                a.download = 'recording.mp3';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            }}
        }}
    </script>
</body>
</html>
"""

# Render the component
components.html(html_content, height=800, scrolling=False)