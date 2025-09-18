import os
import logging
import json
from .gemini_stt import transcribe_audio
from services.logger import logger

async def analyze_speakers_with_llm(transcript, genai_client=None, model=None):
    logger.info("Starting speaker analysis using LLM.")
    """
    Analyze conversation transcript to identify speakers using LLM
    """
    try:
        if not transcript:
            logger.warning("No transcript provided to LLM analysis")
            return {
                "error": "No transcript",
                "doctor_parts": "",
                "patient_parts": "",
                "timeline": [],
                "confidence": 0.0,
            }

        # Use injected client if provided, otherwise create one
        client = genai_client
        if client is None:
            api_key = os.getenv("GEMINI_API_KEY")
            logger.info(f" [LLM] GEMINI_API_KEY check: {'Found' if api_key else 'Missing'}")
            if api_key:
                logger.info(f" [LLM] GEMINI_API_KEY starts with: {api_key[:10]}...")
            import google.genai as genai
            client = genai.Client(api_key=api_key)

        # Primary prompt: request strict JSON and set response_mime_type to application/json
        prompt_system = (
            "You are a medical conversation separator. Your ONLY job is to separate doctor and patient speech. "
            "Return STRICT JSON only matching the schema: {\n  \"doctor_parts\": string,\n  \"patient_parts\": string,\n  \"timeline\": [{\"speaker\": \"doctor|patient\", \"text\": string, \"timestamp\": string}],\n  \"confidence\": number\n}\nDo not add any explanatory text.\n"
        )

        prompt_user = f"TRANSCRIPT:\n{transcript}\n\nReturn JSON only."

        if model is None:
            model = os.getenv("GEMINI_LLM_MODEL")
            if not model:
                logger.error("GEMINI_LLM_MODEL not set in environment; please set it in backend/.env")
                return {
                    "error": "GEMINI_LLM_MODEL not configured",
                }

        try:
            response = client.models.generate_content(
                model=model,
                contents=[prompt_system, prompt_user],
                config={
                    "response_mime_type": "application/json",
                    # keep other generation defaults
                },
            )
        except Exception as e:
            logger.warning(f"[LLM] First attempt failed: {e}. Retrying without response_mime_type.")
            response = client.models.generate_content(
                model=model,
                contents=[prompt_system, prompt_user],
            )

        llm_response = getattr(response, "text", None) or str(response)
        logger.info(f" [LLM] Received analysis (truncated): {llm_response[:300]}")

        # If the SDK returned JSON directly (response.text possibly already JSON string), attempt parse
        try:
            analysis = json.loads(llm_response)
            logger.info(" [LLM] Successfully parsed JSON response")
        except json.JSONDecodeError:
            # Last resort: try to extract JSON substring
            start = llm_response.find('{')
            end = llm_response.rfind('}')
            if start != -1 and end != -1 and end > start:
                candidate = llm_response[start:end+1]
                try:
                    analysis = json.loads(candidate)
                    logger.info(" [LLM] Parsed JSON after extracting substring")
                except Exception as e:
                    logger.error(f" [LLM] Failed to parse JSON after extraction: {e}")
                    return {
                        "error": "Invalid JSON response",
                        "doctor_parts": "",
                        "patient_parts": "",
                        "timeline": [],
                        "confidence": 0.0,
                    }
            else:
                logger.error(" [LLM] No JSON object found in LLM response")
                return {
                    "error": "Invalid JSON response",
                    "doctor_parts": "",
                    "patient_parts": "",
                    "timeline": [],
                    "confidence": 0.0,
                }

        # Normalize analysis fields
        doctor = analysis.get("doctor_parts", "")
        patient = analysis.get("patient_parts", "")
        timeline = analysis.get("timeline", []) or []
        confidence = float(analysis.get("confidence", 0.0) or 0.0)

        # Clean timeline entries
        cleaned_timeline = []
        for item in timeline:
            if not isinstance(item, dict):
                continue
            text = (item.get("text") or "").strip()
            speaker = (item.get("speaker") or "").lower()
            if text:
                cleaned_timeline.append({
                    "speaker": "doctor" if speaker.startswith("doc") else "patient",
                    "text": text,
                    "timestamp": item.get("timestamp", "")
                })

        return {
            "doctor_parts": doctor,
            "patient_parts": patient,
            "timeline": cleaned_timeline,
            "confidence": confidence,
        }

    except Exception as e:
        logger.error(f" [LLM] Analysis error: {e}", exc_info=True)
        return {
            "doctor_parts": "",
            "patient_parts": "",
            "timeline": [],
            "confidence": 0.0,
            "error": str(e),
        }

async def process_conversation_audio(temp_path, genai_client=None, model=None):
    logger.info(f"Processing audio file: {temp_path}")
    """
    Process audio file for conversation analysis. Accept optional injected
    `genai_client` and `model` for DI/testing.
    """
    try:
        logger.info(" [ANALYZE] Starting Gemini transcription...")
        full_transcript = transcribe_audio(temp_path)
        logger.info(f" [ANALYZE] Full transcript obtained: {str(full_transcript)[:200]}...")

        # If transcription failed (None), return structured error response and skip LLM call
        if full_transcript is None:
            logger.warning(" [ANALYZE] Transcription failed or empty - skipping LLM analysis")
            return {
                "error": "Transcription failed",
                "transcript": "",
                "doctor_transcript": "",
                "patient_transcript": "",
                "full_conversation": [],
                "analysis_confidence": 0.0,
            }

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
        analyzed_conversation = await analyze_speakers_with_llm(full_transcript, genai_client=genai_client, model=model)

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
        logger.info("Audio processing and analysis completed successfully.")
        return result

    except Exception as e:
        logger.error(f"Error during audio processing: {str(e)}", exc_info=True)
        return {
            "error": str(e),
            "transcript": "",
            "doctor_transcript": "",
            "patient_transcript": "",
            "full_conversation": []
        }

async def generate_conversation_summary(data, genai_client=None, model=None):
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

        # Use injected client if provided, else create one
        client = genai_client
        if client is None:
            import google.genai as genai
            client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        prompt = f"""
You are a medical conversation summarizer. Read the following conversation and provide a concise, clear summary of the main points, symptoms, diagnosis, and advice given. Use simple language.

CONVERSATION:
{conversation_text}

SUMMARY:
"""
        if model is None:
            model = os.getenv("GEMINI_LLM_MODEL")
            if not model:
                logger.error("GEMINI_LLM_MODEL not set in environment; please set it in backend/.env")
                return {"summary": "", "error": "GEMINI_LLM_MODEL not configured"}
        response = client.models.generate_content(
            model=model,
            contents=[
                "You are a medical conversation summarizer. Always respond with a clear summary only.",
                prompt,
            ],
        )
        summary = getattr(response, "text", "").strip()
        return {"summary": summary}

    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return {"error": str(e), "summary": ""}

async def generate_soap_note(data, genai_client=None, model=None):
    """Generate SOAP note JSON via LLM and render HTML.

    Accepts an optional injected `genai_client` and `model` to make the service
    testable and configurable via dependency injection.
    """
    try:
        return await _generate_soap_note_impl(data, genai_client=genai_client, model=model)
    except Exception as e:
        logger.error(f"Error generating SOAP: {e}")
        return {"soap_html": "", "soap_json": {}, "error": str(e)}

async def _generate_soap_note_impl(data, genai_client=None, model=None):
    """
    Generate SOAP note JSON via LLM and render HTML.
    """
    try:
        transcript = data.get("transcript", "")
        timeline = data.get("timeline", [])
        if timeline and isinstance(timeline, list):
            conversation_text = " ".join([seg.get("text", "") for seg in timeline])
        else:
            conversation_text = transcript

        if not conversation_text or not conversation_text.strip():
            return {"soap_html": "", "soap_json": {}, "error": "No conversation text provided"}

        from services.prompts.soap import build_messages

        # Use injected client if provided, else create one
        client = genai_client
        if client is None:
            from google import genai
            client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        if model is None:
            model = os.getenv("GEMINI_LLM_MODEL")
            if not model:
                logger.error("GEMINI_LLM_MODEL not set in environment; please set it in backend/.env")
                return {"soap_html": "", "soap_json": {}, "error": "GEMINI_LLM_MODEL not configured"}

        messages = build_messages(conversation_text)

        # build_messages returns a list of dicts with 'role' and 'content'; extract contents
        contents_list = [m.get("content") if isinstance(m, dict) else str(m) for m in messages]
        response = client.models.generate_content(
            model=model,
            contents=contents_list,
        )
        content = getattr(response, "text", "").strip()

        import json as _json
        try:
            data_json = _json.loads(content)
        except Exception:
            # Second attempt: ask for JSON only
            if isinstance(messages[-1], dict):
                messages[-1]["content"] = messages[-1].get("content", "") + \
                                          "\n\nIMPORTANT: Return STRICT JSON only."
            retry_contents = [m.get("content") if isinstance(m, dict) else str(m) for m in messages]
            retry_resp = client.models.generate_content(
                model=model,
                contents=retry_contents,
            )
            content = getattr(retry_resp, "text", "").strip()
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

        # Render HTML
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
        <div class="result-section" style="margin-top:10px;">
            <div class="result-title">S - Subjective</div>{bullets(subj)}
        </div>
        <div class="result-section">
            <div class="result-title">O - Objective</div>{vitals_html}{bullets(exam)}{bullets(labs)}
        </div>
        <div class="result-section">
            <div class="result-title">A - Assessment</div>{bullets(assess)}
        </div>
        <div class="result-section">
            <div class="result-title">P - Plan</div>{bullets(plan)}
        </div>
        """

        return {"soap_html": soap_html, "soap_json": data_json}

    except Exception as e:
        logger.error(f"Error generating SOAP: {e}")
        return {"soap_html": "", "soap_json": {}, "error": str(e)}


async def generate_ai_edit(transcript: str, genai_client=None, model=None):
    """Call LLM to edit/clean the transcript for clarity while preserving clinical meaning."""
    try:
        if not transcript or not str(transcript).strip():
            return ""

        # Use injected client if provided, else create one
        client = genai_client
        if client is None:
            import google.genai as genai
            client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        prompt_system = (
            "You are a helpful clinical editor. Improve clarity, grammar, and formatting of the transcript while preserving all clinical facts. "
            "Return the edited transcript as plain text only (no commentary)."
        )

        prompt_user = f"TRANSCRIPT:\n{transcript}\n\nProvide the edited transcript only."

        if model is None:
            model = os.getenv("GEMINI_LLM_MODEL")
            if not model:
                logger.error("GEMINI_LLM_MODEL not set in environment; please set it in backend/.env")
                return ""
        response = client.models.generate_content(
            model=model,
            contents=[prompt_system, prompt_user],
        )

        edited = getattr(response, "text", "").strip()
        return edited
    except Exception as e:
        logger.error(f"generate_ai_edit error: {e}")
        return f"Error: {str(e)}"
