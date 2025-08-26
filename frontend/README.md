# 🩺 Medical Voice Assistant - Frontend

Modern web-based frontend for the Medical Voice Assistant with two main features:

## 🎯 Features

### 1. 🎙️ Voice-to-Text Analysis
- **Live transcription** during recording
- **AI-powered speaker identification** (Doctor vs Patient)
- **Conversation analysis** with timeline
- **Summary generation** using LLM
- **Real-time audio visualization**

### 2. 🔊 Pure Voice Recording
- **High-quality audio recording** (48kHz)
- **Pause/Resume functionality**
- **Real-time timer**
- **Instant download** as WAV files
- **Recording management**

## 🚀 Quick Start

### 1. Start Backend Server
```bash
cd ../backend
python main.py
```
Backend will run on: `http://localhost:8000`

### 2. Start Frontend Server
```bash
cd frontend
python server.py
```
Frontend will run on: `http://localhost:3000`

### 3. Open Browser
The browser will automatically open to: `http://localhost:3000`

## 📁 File Structure

```
frontend/
├── index.html              # Main landing page
├── voice-analyzer.html     # Voice-to-text analysis
├── voice-recorder.html     # Pure voice recording
├── server.py              # Frontend HTTP server
└── README.md              # This file
```

## 🔧 Technical Details

### Voice-to-Text Analysis
- Uses **Web Speech API** for live transcription
- Sends audio to backend for **Groq Whisper** processing
- **LLM analysis** for speaker identification
- **Summary generation** via Groq API

### Pure Voice Recording
- **MediaRecorder API** for high-quality recording
- **WebM/Opus** format with fallback to WAV
- **Client-side audio processing**
- **Automatic file naming** with timestamps

### Browser Compatibility
- ✅ **Chrome/Edge** (Recommended)
- ✅ **Firefox** (Limited speech recognition)
- ✅ **Safari** (Limited features)

## 🎨 UI Features

- **Responsive design** for mobile/desktop
- **Gradient backgrounds** with glassmorphism
- **Real-time animations** and feedback
- **Intuitive controls** with visual states
- **Professional medical theme**

## 🔗 API Integration

Frontend communicates with backend via:
- `POST /api/v1/conversation/analyze-conversation/` - Audio analysis
- `POST /generate_summary` - Summary generation
- `POST /api/v1/voice-recording/record/` - Save recordings
- `GET /api/v1/voice-recording/download/{filename}` - Download files

## 🛠️ Development

### Local Development
```bash
# Start with auto-reload
python server.py
```

### Production Deployment
- Serve static files via **Nginx/Apache**
- Use **HTTPS** for microphone access
- Configure **CORS** for API calls

## 📱 Mobile Support

- **Touch-friendly** controls
- **Responsive layouts**
- **Mobile-optimized** recording
- **Gesture support**

## 🔒 Security

- **HTTPS required** for microphone access
- **CORS enabled** for API communication
- **No data stored** in frontend
- **Privacy-focused** design

---

**Made with ❤️ for medical professionals**
