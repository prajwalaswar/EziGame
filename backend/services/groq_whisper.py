import os
import requests

def transcribe_audio(audio_path):
    """
    Send audio file to Groq Whisper API and return transcript.
    """
    print(f" [GROQ] Checking API key...")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print(" [GROQ] GROQ_API_KEY not found in environment!")
        return "[Error: GROQ_API_KEY not found in environment]"

    print(f" [GROQ] API key found: {api_key[:10]}...")

    print(f" [GROQ] Sending request to Groq Whisper API...")
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        with open(audio_path, "rb") as audio_file:
            files = {"file": audio_file}
            data = {"model": "whisper-large-v3"}
            print(f" [GROQ] Uploading audio file: {audio_path}")
            response = requests.post(url, headers=headers, files=files, data=data)

        if response.status_code == 200:
            transcript = response.json().get("text", "")
            print(f" [GROQ] Success! Transcript length: {len(transcript)} characters")
            return transcript
        else:
            print(f" [GROQ] API error: {response.status_code} - {response.text}")
            return f"[Transcription failed: {response.status_code}]"
    except Exception as e:
        print(f" [GROQ] Exception in transcribe_audio: {e}")
        return f"[Transcription error: {str(e)}]"
