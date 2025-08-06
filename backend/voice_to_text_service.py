import os
import logging
import json
from groq_whisper import transcribe_audio

# Setup logging
logger = logging.getLogger(__name__)

async def analyze_speakers_with_llm(transcript):
    """
    Analyze conversation transcript to identify speakers using LLM
    """
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        prompt = f"""
You are an expert medical conversation analyst. Analyze this conversation transcript and identify complete sentences or thoughts for each speaker. DO NOT break sentences in the middle.

TRANSCRIPT:
{transcript}

ANALYSIS RULES:
1. Identify COMPLETE sentences or thoughts for each speaker
2. DOCTOR typically: Uses medical terminology, asks diagnostic questions, gives advice/treatment, introduces themselves
3. PATIENT typically: Describes symptoms, asks questions, expresses concerns, responds to doctor's questions
4. Keep complete sentences together - do NOT split a sentence between speakers
5. A speaker can have multiple consecutive sentences if they are continuing their thought
6. Look for natural conversation flow and context clues
7. If unsure about speaker, use context: medical questions = doctor, symptom descriptions = patient

Return output in this exact JSON format:
{{
    "doctor_parts": "...",
    "patient_parts": "...",
    "timeline": [
        {{"speaker": "doctor", "text": "Complete sentence or thought here", "timestamp": "estimated"}},
        {{"speaker": "patient", "text": "Complete sentence or thought here", "timestamp": "estimated"}}
    ],
    "confidence": 0.9
}}
"""

        logger.info(" [LLM] Sending conversation to Groq for analysis...")
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a medical conversation analysis expert. "
                        "Always respond with valid JSON only. NEVER assign two consecutive lines to the same speaker unless it's clearly a follow-up."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=2000
        )

        llm_response = response.choices[0].message.content.strip()
        logger.info(f" [LLM] Received analysis: {llm_response[:200]}...")

        try:
            analysis = json.loads(llm_response)
            logger.info(" [LLM] Successfully parsed JSON response")

            # Clean timeline - remove empty entries and ensure proper formatting
            cleaned_timeline = []
            for item in analysis.get("timeline", []):
                speaker = item.get("speaker")
                text = item.get("text", "").strip()

                # Only add non-empty text entries
                if text:
                    cleaned_timeline.append({
                        "speaker": speaker,
                        "text": text,
                        "timestamp": item.get("timestamp", "estimated")
                    })

            analysis["timeline"] = cleaned_timeline
            return analysis

        except json.JSONDecodeError:
            logger.error(" [LLM] JSON parsing failed")
            return {
                "doctor_parts": "Analysis failed",
                "patient_parts": "Analysis failed",
                "timeline": [],
                "confidence": 0.3
            }

    except Exception as e:
        logger.error(f" [LLM] Analysis error: {e}")
        return {
            "doctor_parts": f"LLM Analysis Error: {str(e)}",
            "patient_parts": f"LLM Analysis Error: {str(e)}",
            "timeline": [],
            "confidence": 0.1
        }

async def process_conversation_audio(temp_path):
    """
    Process audio file for conversation analysis
    """
    try:
        logger.info(" [ANALYZE] Starting Groq Whisper transcription...")
        full_transcript = transcribe_audio(temp_path)
        logger.info(f" [ANALYZE] Full transcript obtained: {full_transcript[:100]}...")
        
        logger.info(" [ANALYZE] Sending to LLM for speaker analysis...")
        analyzed_conversation = await analyze_speakers_with_llm(full_transcript)

        result = {
            "transcript": full_transcript,
            "doctor_transcript": analyzed_conversation.get("doctor_parts", ""),
            "patient_transcript": analyzed_conversation.get("patient_parts", ""),
            "full_conversation": analyzed_conversation.get("timeline", []),
            "analysis_confidence": analyzed_conversation.get("confidence", 0.8)
        }

        return result

    except Exception as e:
        logger.error(f" [ANALYZE] Error: {str(e)}")
        return {
            "error": str(e),
            "transcript": "",
            "doctor_transcript": "",
            "patient_transcript": "",
            "full_conversation": []
        }

async def generate_conversation_summary(data):
    """
    Generate AI summary of conversation
    """
    try:
        transcript = data.get("transcript", "")
        timeline = data.get("timeline", [])
        
        if timeline and isinstance(timeline, list):
            conversation_text = " ".join([seg.get("text", "") for seg in timeline])
        else:
            conversation_text = transcript

        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        prompt = f"""
You are a medical conversation summarizer. Read the following conversation and provide a concise, clear summary of the main points, symptoms, diagnosis, and advice given. Use simple language.

CONVERSATION:
{conversation_text}

SUMMARY:
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a medical conversation summarizer. Always respond with a clear summary only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=400
        )

        summary = response.choices[0].message.content.strip()
        return {"summary": summary}
        
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return {"error": str(e), "summary": ""}

async def transcribe_simple_audio(temp_path):
    """
    Simple transcription without speaker analysis
    """
    try:
        logger.info("🎤 [TRANSCRIBE] Starting Groq Whisper transcription...")
        transcript = transcribe_audio(temp_path)
        logger.info(f" [TRANSCRIBE] Success! Transcript: {transcript[:100]}...")
        
        return {"transcript": transcript}
        
    except Exception as e:
        logger.error(f" [TRANSCRIBE] Error: {str(e)}")
        return {
            "error": str(e),
            "transcript": "",
        }
