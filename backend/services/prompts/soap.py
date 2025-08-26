from typing import List

SOAP_JSON_SCHEMA = r"""
Return a STRICT JSON object with the following keys (no extra keys):
{
  "patient_name": string | null,
  "date": string | null,
  "age_gender": string | null,
  "reason_for_visit": string | null,
  "subjective": [string],
  "objective": {
    "vitals": {"Temp": string | null, "BP": string | null, "HR": string | null, "RR": string | null, "SpO2": string | null},
    "exam_findings": [string],
    "labs_imaging": [string]
  },
  "assessment": [string],
  "plan": [string]
}
Rules:
- Use only information present in the conversation. If something is not mentioned, set it to null or use an empty list.
- Keep items concise and clinical; use complete, readable phrases.
- Preserve values/units exactly as spoken.
- Do not invent vitals, labs, or diagnoses.
- Return ONLY JSON. No markdown, no prose, no explanation.
"""

SOAP_TEMPLATE_GUIDE = r"""
SOAP Note Template Guidance

S – Subjective: What the patient says (chief complaint, HPI, symptoms).
O – Objective: What the clinician observes/measures (vitals, exam findings, labs/imaging).
A – Assessment: Clinician’s diagnosis/differential based on S + O.
P – Plan: Treatment/tests/follow‑up/education/referrals/medication changes.
"""

SOAP_STYLE_EXAMPLE = r"""
Example SOAP Note (style example only, do NOT copy specifics into output)
Patient Name: Ramesh Patil
Date: 06-Jun-2025
Age/Gender: 68/Male
Reason for Visit: Follow-up for abdominal discomfort post colonic biopsy
S – Subjective:
- Patient reports improvement in abdominal discomfort.
- Still experiencing occasional bloating.
- Stools now regular, no bleeding.
- Appetite has improved.
- Reports slight weight loss (~2 kg over 1 month).
- No fever or vomiting.
O – Objective:
- Temp: 98.6°F; BP: 128/76 mmHg; HR: 72 bpm.
- Weight: 65 kg (down from 67 kg).
- Abdomen: Soft, non-tender, no masses.
- Surgical wound healing well; no signs of infection.
- Histopathology report received.
A – Assessment:
- Healing post colonic procedure is on track.
- No signs of complications.
- Mild weight loss may be due to recovery phase.
- Non-malignant inflammatory changes.
P – Plan:
- Continue regular diet, increase protein intake.
- Monitor weight weekly.
- Review again in 2 weeks; return earlier if pain, bleeding, or fever.
- Continue wound care as instructed.
- Educate family on signs of complications.
"""

def build_messages(conversation_text: str) -> List[dict]:
    system = (
        "You are a clinical scribe. Return STRICT JSON only that conforms to the given schema. "
        "No markdown, no prose, no extra commentary."
    )
    user = (
        f"{SOAP_JSON_SCHEMA}\n\n{SOAP_TEMPLATE_GUIDE}\n\n"
        f"EXAMPLE STYLE (do NOT copy the exact patient details; style guidance only):\n{SOAP_STYLE_EXAMPLE}\n\n"
        f"CONVERSATION TO SUMMARIZE (use only facts present):\n{conversation_text}\n\n"
        "Return ONLY JSON."
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

