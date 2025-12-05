"""
The LLM Judge.
Compares historical accounts and quantifies consistency.
"""
import json
from typing import List, Dict
from src.utils.llm_client import LLMClient
from src.utils.logger import get_logger

logger = get_logger("judge")

class LLMJudge:
    def __init__(self):
        # We use a low temperature for the judge to ensure deterministic, fair scoring.
        self.llm = LLMClient(provider="google")
        self.model = "gemini-2.0-flash"

    def judge_all(self, extractions: List[Dict]) -> List[Dict]:
        """
        Main entry point: Groups extractions and runs the judge on all pairs.
        """
        # 1. Group by Event
        events = {}
        for ext in extractions:
            e_name = ext['event']
            if e_name not in events:
                events[e_name] = {'lincoln': [], 'others': []}
            
            # Identify if this is Lincoln (Source Zero) or a Historian
            if "loc_" in ext['source_id']:
                events[e_name]['lincoln'].append(ext)
            else:
                events[e_name]['others'].append(ext)

        results = []
        
        # 2. Iterate through events
        for event_name, sources in events.items():
            lincoln_accounts = sources['lincoln']
            historian_accounts = sources['others']

            if not lincoln_accounts:
                logger.warning(f"Skipping {event_name}: No primary source (Lincoln) found.")
                continue
            
            # We usually compare against the first matching Lincoln document
            # (In a more complex system, we might merge multiple Lincoln docs)
            primary = lincoln_accounts[0]

            logger.info(f"Judging Event: {event_name} ({len(historian_accounts)} comparisons)")

            # 3. Create Pairs and Judge
            for secondary in historian_accounts:
                judgment = self.judge_pair(primary, secondary)
                if judgment:
                    results.append(judgment)
                    
        return results

    def judge_pair(self, primary: Dict, secondary: Dict) -> Dict:
        """
        Compares one Primary source against one Secondary source.
        """
        system_prompt = """You are an impartial Historian Judge. 
        Your task is to compare a Primary Source (Lincoln's own words) against a Secondary Source (a historian's account) regarding a specific event.
        
        Output strict JSON:
        {
            "consistency_score": <int 0-100>,
            "classification": "Consistent" | "Nuanced" | "Contradictory",
            "reasoning": "<concise explanation>",
            "discrepancies": [
                {
                    "claim": "<the specific claim in question>",
                    "type": "Factual Error" | "Omission" | "Interpretive Difference",
                    "severity": "High" | "Low"
                }
            ]
        }
        
        Scoring Rubric:
        - 100: Perfect alignment.
        - 80-99: Minor omissions or slight rewording.
        - 60-79: Significant omissions or differing interpretations of tone.
        - 40-59: Minor factual errors or major interpretive disagreements.
        - 0-39: Direct factual contradictions or complete fabrication.
        """

        user_prompt = f"""
        EVENT: {primary['event']}
        
        === PRIMARY SOURCE (LINCOLN) ===
        Author: Abraham Lincoln
        Source ID: {primary['source_id']}
        Claims: {json.dumps(primary.get('claims', []))}
        Tone: {primary.get('tone', 'N/A')}
        
        === SECONDARY SOURCE (HISTORIAN) ===
        Author: {secondary.get('author', 'Unknown')}
        Source ID: {secondary['source_id']}
        Claims: {json.dumps(secondary.get('claims', []))}
        Tone: {secondary.get('tone', 'N/A')}
        
        COMPARE the Secondary Source against the Primary Source.
        Does the historian accurately reflect Lincoln's account?
        """

        try:
            result = self.llm.extract_json(system_prompt, user_prompt, model=self.model)
            
            # Attach metadata for analysis later
            result['event'] = primary['event']
            result['primary_source'] = primary['source_id']
            result['secondary_source'] = secondary['source_id']
            result['historian'] = secondary.get('author', 'Unknown')
            
            return result
        except Exception as e:
            logger.error(f"Judging failed for {secondary['source_id']}: {e}")
            return None