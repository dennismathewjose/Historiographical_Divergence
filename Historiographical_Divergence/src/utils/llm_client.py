"""
Unified LLM Client wrapper.
Supports OpenAI and Google (Gemini) with fallback model selection.
"""
import os
import json
import time
from typing import Dict, Any, Optional
from src.utils.logger import get_logger
from config.settings import OPENAI_API_KEY, GOOGLE_API_KEY
logger = get_logger("llm_client")

class LLMClient:
    def __init__(self, provider: str = "google"):
        self.provider = provider
        
        if provider == "openai":
            from openai import OpenAI
            api_key = OPENAI_API_KEY
            if not api_key: raise ValueError("OPENAI_API_KEY missing")
            self.client = OpenAI(api_key=api_key)
            
        elif provider == "google":
            import google.generativeai as genai
            api_key = GOOGLE_API_KEY
            
            if not api_key: 
                raise ValueError("GOOGLE_API_KEY missing. Please set it in your .env file.")
                
            genai.configure(api_key=api_key)
            self.client = genai

    def extract_json(self, 
                     system_prompt: str, 
                     user_prompt: str, 
                     model: str = "gemini-1.5-flash",
                     temperature: float = 0.0) -> Dict[str, Any]:
        """
        Routes the request to the configured provider.
        """
        if self.provider == "openai":
            return self._call_openai(system_prompt, user_prompt, model, temperature)
        elif self.provider == "google":
            # Try primary model, fallback to 'gemini-pro' if flash fails
            result = self._call_gemini(system_prompt, user_prompt, model, temperature)
            if not result and model == "gemini-1.5-flash":
                logger.warning("Gemini Flash failed. Retrying with 'gemini-pro'...")
                return self._call_gemini(system_prompt, user_prompt, "gemini-pro", temperature)
            return result
        return {}

    def _call_openai(self, sys_p, user_p, model, temp):
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": sys_p},
                    {"role": "user", "content": user_p}
                ],
                response_format={"type": "json_object"},
                temperature=temp
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"OpenAI Error: {e}")
            return {}

    def _call_gemini(self, sys_p, user_p, model, temp):
        try:
            # Gemini system instruction setup
            model_instance = self.client.GenerativeModel(
                model_name=model,
                system_instruction=sys_p, # Move system prompt here for better adherence
                generation_config={
                    "temperature": temp,
                    "response_mime_type": "application/json"
                }
            )
            
            response = model_instance.generate_content(user_p)
            
            text = response.text.strip()
            # Clean markdown code blocks if present
            if text.startswith("```"):
                lines = text.split('\n')
                if lines[0].startswith("```"): lines = lines[1:]
                if lines[-1].startswith("```"): lines = lines[:-1]
                text = "\n".join(lines)
            
            return json.loads(text)
            
        except Exception as e:
            logger.error(f"Gemini ({model}) Error: {e}")
            if "429" in str(e):
                time.sleep(5)
            return {}