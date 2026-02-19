import os
import time
import logging
from typing import Dict, Any, Optional
import openai
from config import (
    LLM_PROVIDER, LLM_MODEL, OLLAMA_BASE_URL, 
    OPENAI_API_KEY, TEMPERATURE, MAX_RETRIES,
    FALLBACK_TO_CLOUD, CLOUD_FALLBACK_MODEL
)
from core.schema import validate_json_response, get_empty_schema

class LLMClient:
    def __init__(self, provider: str = LLM_PROVIDER, model: str = LLM_MODEL):
        self.provider = provider.lower()
        self.model = model
        
        if self.provider == "openai":
            self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        elif self.provider == "ollama":
            # Ollama provides an OpenAI-compatible endpoint
            self.client = openai.OpenAI(
                base_url=OLLAMA_BASE_URL,
                api_key="ollama"  # placeholder
            )
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def parse_instruction(self, instruction: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Calls the LLM to parse a natural language instruction into JSON.
        Includes schema enforcement and retry logic.
        """
        if system_prompt is None:
            system_prompt = "You are a robotics planning assistant. Output ONLY valid JSON matching the schema."

        retries = 0
        while retries <= MAX_RETRIES:
            start_time = time.time()
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": instruction}
                    ],
                    temperature=TEMPERATURE,
                    response_format={"type": "json_object"} if self.provider == "openai" else None
                )
                
                content = response.choices[0].message.content
                latency = time.time() - start_time
                
                parsed_json = validate_json_response(content)
                if parsed_json:
                    return {
                        "data": parsed_json,
                        "latency": latency,
                        "retries": retries,
                        "success": True,
                        "provider": self.provider,
                        "model": self.model
                    }
                
                logging.warning(f"Malformed JSON on attempt {retries + 1} from {self.model}")
            except Exception as e:
                logging.error(f"LLM call failed: {e}")
                latency = time.time() - start_time

            retries += 1

        # Check for Hybrid Fallback
        if FALLBACK_TO_CLOUD and self.provider == "ollama":
            logging.info(f"Falling back to cloud model: {CLOUD_FALLBACK_MODEL}")
            fallback_client = LLMClient(provider="openai", model=CLOUD_FALLBACK_MODEL)
            result = fallback_client.parse_instruction(instruction, system_prompt)
            result["fallback_occurred"] = True
            return result

        return {
            "data": get_empty_schema(),
            "latency": 0,
            "retries": retries,
            "success": False,
            "provider": self.provider,
            "model": self.model
        }
