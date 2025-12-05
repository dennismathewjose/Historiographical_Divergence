"""
Core Logic for extracting historical event claims.
Configured for Google Gemini 2.0 Flash with Type Safety.
"""
import json
from typing import List, Dict, Any, Optional
from src.utils.llm_client import LLMClient
from src.utils.logger import get_logger

logger = get_logger("extractor")

class EventExtractor:
    
    EVENTS = {
        "election_1860": ["election", "1860", "wigwam", "chicago", "nomination", "presidency", "lincoln"],
        "fort_sumter": ["sumter", "anderson", "charleston", "provision", "reinforce", "fox", "seward"],
        "gettysburg": ["gettysburg", "cemetery", "dedication", "score", "consecrate", "1863"],
        "second_inaugural": ["inaugural", "malice", "charity", "1865", "march 4"],
        "assassination": ["ford", "theatre", "booth", "pistol", "shot", "assassination", "april 14"]
    }

    def __init__(self):
        # Initialize with Google provider
        self.llm = LLMClient(provider="google")
        self.model = "gemini-2.0-flash"

    def process_document(self, doc: Dict) -> List[Dict]:
        extracted_events = []
        content = doc.get('content', '')
        
        # GEMINI OPTIMIZATION:
        # Gemini 2.0 Flash has a massive context window.
        # We can increase chunk size significantly (e.g., 50k chars).
        chunks = self._chunk_text(content, chunk_size=50000)
        
        for event_key, keywords in self.EVENTS.items():
            relevant_text = []
            for chunk in chunks:
                if any(kw in chunk.lower() for kw in keywords):
                    relevant_text.append(chunk)
            
            if not relevant_text:
                continue 
                
            # Limit context to avoid rate limits
            context = "\n---\n".join(relevant_text)[:100000]
            
            logger.info(f"Extracting '{event_key}' from {doc.get('title')}...")
            
            result = self._extract_claims(context, event_key, doc)
            if result:
                extracted_events.append(result)
                
        return extracted_events

    def _extract_claims(self, text: str, event: str, doc_metadata: Dict) -> Optional[Dict]:
        system_prompt = """You are an expert historian. Extract specific factual claims, temporal details, and author tone regarding the specified historical event.
        
        Return a JSON object with this EXACT schema:
        {
            "event": "event_name",
            "author": "Author Name",
            "claims": ["claim 1", "claim 2", "claim 3"],
            "temporal_details": {"date": "YYYY-MM-DD", "time": "HH:MM"},
            "tone": "objective/critical/reverent"
        }
        
        Rules:
        1. If the text does not contain specific claims about the event, return empty claims [].
        2. Extract at least 3-5 distinct claims if available.
        3. Keep claims concise (1 sentence each).
        """

        user_prompt = f"""
        EVENT: {event}
        SOURCE: {doc_metadata.get('title')}
        AUTHOR: {doc_metadata.get('from', 'Unknown')}
        
        TEXT:
        {text}
        """
        
        data = self.llm.extract_json(system_prompt, user_prompt, model=self.model)
        
        # --- SAFETY BLOCK: Handle Types (Dict vs List) ---
        if isinstance(data, list):
            # If LLM returned a list (e.g. []), return None
            if not data: 
                return None
            # If it returned a list of objects, take the first one
            if isinstance(data[0], dict):
                data = data[0]
            else:
                return None
        # -------------------------------------------------
        
        if data and isinstance(data, dict) and data.get("claims") and len(data["claims"]) > 0:
            data["source_id"] = doc_metadata.get("id")
            data["source_type"] = doc_metadata.get("document_type")
            return data
            
        return None

    def _chunk_text(self, text: str, chunk_size: int) -> List[str]:
        if not text: return []
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size - 1000)]