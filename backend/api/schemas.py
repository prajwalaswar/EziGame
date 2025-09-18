from pydantic import BaseModel, ConfigDict, model_validator
from typing import List, Optional, Any

class GenerateSummaryRequest(BaseModel):
    doctor_conversation: str
    patient_conversation: str
    full_transcript: str

class TimelineItem(BaseModel):
    speaker: str
    text: str
    timestamp: Optional[str] = None

class GenerateSOAPRequest(BaseModel):
    doctor_conversation: str
    patient_conversation: str
    full_transcript: str
    timeline: Optional[List[TimelineItem]] = None

class SummaryResponse(BaseModel):
     model_config = ConfigDict(extra='forbid')
     summary: Optional[str] = None
     error: Optional[str] = None
 
     @model_validator(mode="after")
     def _one_of_summary_or_error(self):
         if (self.summary is None) == (self.error is None):
             raise ValueError("Exactly one of 'summary' or 'error' must be set")
         return self

class SOAPResponse(BaseModel):
     model_config = ConfigDict(extra='forbid')
     soap_html: Optional[str] = None
     soap_json: Optional[dict[str, Any]] = None
     error: Optional[str] = None

     @model_validator(mode="after")
     def _success_payload_or_error(self):
         if self.error is not None:
             if self.soap_html is not None or self.soap_json is not None:
                 raise ValueError("On error, omit soap_html and soap_json")
         else:
             if not (self.soap_html is not None or self.soap_json is not None):
                 raise ValueError("Provide soap_html or soap_json when no error")
         return self
     


# from pydantic import BaseModel, ConfigDict, model_validator
# from typing import List, Optional, Dict, Any

# class GenerateSummaryRequest(BaseModel):
#     doctor_conversation: str
#     patient_conversation: str
#     full_transcript: str

# class TimelineItem(BaseModel):
#     speaker: str
#     text: str
#     timestamp: Optional[str] = None

# class GenerateSOAPRequest(BaseModel):
#     doctor_conversation: str
#     patient_conversation: str
#     full_transcript: str
#     timeline: Optional[List[TimelineItem]] = None

# class SummaryResponse(BaseModel):
#     model_config = ConfigDict(extra='forbid')
#     summary: Optional[str] = None
#     error: Optional[str] = None

#     @model_validator(mode="after")
#     def _one_of_summary_or_error(self):
#         if (self.summary is None) == (self.error is None):
#             raise ValueError(
#                 "SummaryResponse must contain either 'summary' OR 'error', but not both"
#             )
#         return self

# class SOAPResponse(BaseModel):
#     model_config = ConfigDict(extra='forbid')
#     soap_html: Optional[str] = None
#     soap_json: Optional[Dict[str, Any]] = None
#     error: Optional[str] = None

#     @model_validator(mode="after")
#     def _success_payload_or_error(self):
#         if self.error is not None:
#             if self.soap_html is not None or self.soap_json is not None:
#                 raise ValueError("On error, omit soap_html and soap_json")
#         else:
#             if not (self.soap_html is not None or self.soap_json is not None):
#                 raise ValueError(
#                     "Provide soap_html or soap_json when no error is present"
#                 )
#         return self
