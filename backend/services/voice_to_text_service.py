import os
import logging
import json
from .groq_whisper import transcribe_audio

logger = logging.getLogger(__name__)

async def analyze_speakers_with_llm(transcript):
    """
    Analyze conversation transcript to identify speakers using LLM
    """
    try:
        api_key = os.getenv("GROQ_API_KEY")
        logger.info(f" [LLM] API Key check: {'Found' if api_key else 'Missing'}")
        if api_key:
            logger.info(f" [LLM] API Key starts with: {api_key[:10]}...")

        from groq import Groq
        client = Groq(api_key=api_key)

        prompt = f"""
You are an expert medical conversation analyst. Your job is to SEPARATE a conversation between a DOCTOR and a PATIENT.

TRANSCRIPT TO ANALYZE:
{transcript}

CRITICAL INSTRUCTIONS:
1. CAREFULLY READ the entire transcript
2. IDENTIFY which parts are spoken by the DOCTOR vs the PATIENT
3. SEPARATE them into two distinct groups
4. DO NOT duplicate text - each sentence should go to ONLY ONE speaker

SPEAKER IDENTIFICATION CLUES:
- DOCTOR: Uses medical terms, asks diagnostic questions, gives treatment advice, introduces as "Dr." or "Doctor"
- PATIENT: Describes symptoms, expresses pain/concerns, asks for help, responds to medical questions

EXAMPLE:
If transcript is: "Hello I am Dr Smith what brings you here today I have a headache and feel dizzy"
Then separate as:
- Doctor: "Hello I am Dr Smith what brings you here today"
- Patient: "I have a headache and feel dizzy"

NOW ANALYZE THIS TRANSCRIPT AND SEPARATE IT:

Return ONLY this JSON format (no extra text):
{{
    "doctor_parts": "All sentences spoken by the doctor combined here",
    "patient_parts": "All sentences spoken by the patient combined here",
    "timeline": [
        {{"speaker": "doctor", "text": "First doctor sentence", "timestamp": "0:00"}},
        {{"speaker": "patient", "text": "First patient sentence", "timestamp": "0:05"}}
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
                        "You are a medical conversation separator. Your ONLY job is to separate doctor and patient speech. "
                        "NEVER duplicate text between speakers. Each sentence goes to ONLY ONE speaker. "
                        "Respond with ONLY valid JSON - no explanations, no extra text."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,  # Make it more deterministic
            max_tokens=1500
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

        # Check if transcript is empty or too short
        if not full_transcript or len(full_transcript.strip()) < 10:
            logger.warning(" [ANALYZE] Transcript too short or empty, skipping LLM analysis")
            return {
                "transcript": full_transcript,
                "doctor_transcript": "No sufficient audio detected",
                "patient_transcript": "No sufficient audio detected",
                "full_conversation": [],
                "analysis_confidence": 0.1
            }

        logger.info(" [ANALYZE] Sending to LLM for speaker analysis...")
        analyzed_conversation = await analyze_speakers_with_llm(full_transcript)

        logger.info(f" [ANALYZE] LLM Analysis result keys: {list(analyzed_conversation.keys())}")
        logger.info(f" [ANALYZE] Doctor parts length: {len(analyzed_conversation.get('doctor_parts', ''))}")
        logger.info(f" [ANALYZE] Patient parts length: {len(analyzed_conversation.get('patient_parts', ''))}")
        logger.info(f" [ANALYZE] Timeline items: {len(analyzed_conversation.get('timeline', []))}")

        result = {
            "transcript": full_transcript,
            "doctor_transcript": analyzed_conversation.get("doctor_parts", ""),
            "patient_transcript": analyzed_conversation.get("patient_parts", ""),
            "full_conversation": analyzed_conversation.get("timeline", []),
            "analysis_confidence": analyzed_conversation.get("confidence", 0.8)
        }

        logger.info(f" [ANALYZE] Final result keys: {list(result.keys())}")
        return result

    except Exception as e:
        logger.error(f" [ANALYZE] Error: {str(e)}")
        logger.error(f" [ANALYZE] Error traceback: ", exc_info=True)
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



async def generate_soap_note(data):
    """Generate SOAP note JSON via LLM and render HTML."""
    try:
        transcript = data.get("transcript", "")
        timeline = data.get("timeline", [])
        if timeline and isinstance(timeline, list):
            conversation_text = " ".join([seg.get("text", "") for seg in timeline])
        else:
            conversation_text = transcript

        if not conversation_text or not conversation_text.strip():
            return {"soap_html": "", "soap_json": {}, "error": "No conversation text provided"}

        from groq import Groq
        from services.prompts.soap import build_messages

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        messages = build_messages(conversation_text)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.1,
            max_tokens=900,
        )
        content = response.choices[0].message.content.strip()

        import json as _json
        try:
            data_json = _json.loads(content)
        except Exception:
            # Second attempt: ask for JSON only
            messages[-1]["content"] += "\n\nIMPORTANT: Return STRICT JSON only."
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=0.1,
                max_tokens=900,
            )
            content = response.choices[0].message.content.strip()
            data_json = _json.loads(content)

        # Normalize fields
        def norm(x, default=None):
            return x if (x is not None and str(x).strip() != "") else default

        subj = data_json.get("subjective") or []
        obj = data_json.get("objective") or {}
        vit = obj.get("vitals") or {"Temp": None, "BP": None, "HR": None, "RR": None, "SpO2": None}
        exam = obj.get("exam_findings") or []
        labs = obj.get("labs_imaging") or []
        assess = data_json.get("assessment") or []
        plan = data_json.get("plan") or []

        patient_name = norm(data_json.get("patient_name"), "Not discussed")
        date = norm(data_json.get("date"), "Not discussed")
        age_gender = norm(data_json.get("age_gender"), "Not discussed")
        reason = norm(data_json.get("reason_for_visit"), "Not discussed")

        # Render HTML matching the provided style
        def bullets(items):
            if not items:
                return "<div>Not discussed</div>"
            return "".join([f"<div>• {str(i)}</div>" for i in items])

        vitals_line = []
        for k in ["Temp", "BP", "HR", "RR", "SpO2"]:
            if vit.get(k):
                vitals_line.append(f"{k}: {vit[k]}")
        vitals_html = f"<div>{' ; '.join(vitals_line)}</div>" if vitals_line else "<div>Not discussed</div>"

        soap_html = f"""
        <div><strong>Patient Name:</strong> {patient_name}</div>
        <div><strong>Date:</strong> {date}</div>
        <div><strong>Age/Gender:</strong> {age_gender}</div>
        <div><strong>Reason for Visit:</strong> {reason}</div>
        <div class=\"result-section\" style=\"margin-top:10px;\"><div class=\"result-title\">S – Subjective</div>{bullets(subj)}</div>
        <div class=\"result-section\"><div class=\"result-title\">O – Objective</div>{vitals_html}{bullets(exam)}{bullets(labs)}</div>
        <div class=\"result-section\"><div class=\"result-title\">A – Assessment</div>{bullets(assess)}</div>
        <div class=\"result-section\"><div class=\"result-title\">P – Plan</div>{bullets(plan)}</div>
        """

        return {"soap_html": soap_html, "soap_json": data_json}

    except Exception as e:
        logger.error(f"Error generating SOAP: {e}")
        return {"soap_html": "", "soap_json": {}, "error": str(e)}
