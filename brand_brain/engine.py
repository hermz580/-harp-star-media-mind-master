import os
import json
import requests
import anthropic
import google.generativeai as genai
from typing import Dict, Any, List
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrandContentEngine:
    def __init__(self, profile_path: str = None):
        if profile_path is None:
            # Default to brand_profile.json in the same directory as this file
            base_dir = Path(__file__).parent
            profile_path = base_dir / "brand_profile.json"
        
        with open(profile_path, 'r') as f:
            self.profile = json.load(f)
        
        self.anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        
        self.asset_library_path = os.getenv("BRAND_LIBRARY_PATH", "./library")

    def get_system_prompt(self, task_type: str) -> str:
        voice = self.profile.get("voice", {})
        phrases = ", ".join(voice.get("signature_phrases", []))
        return f"""You are the Brand Content Engine for {self.profile['brand_name']}.
Mission: {self.profile['mission']}
Tone: {voice.get('tone')}
Signature Phrases to use when appropriate: {phrases}

You generate high-impact content that prioritizes community sovereignty and protection.
"""

    def generate_content(self, task: str, task_type: str = "default", params: Dict[str, Any] = None) -> Dict[str, Any]:
        # [Update: Model Stack Approval Logic]
        # Check for user-driven override or autonomous suggestion passed in params
        model_override = params.get("model_stack") if params else None

        routing = self.profile.get("llm_routing", {})
        model_name = routing.get(task_type, routing.get("default", "gemini-1.5-flash"))
        
        if model_override:
            if model_override == "gemini": model_name = "gemini-1.5-flash"
            elif model_override == "lmstudio": model_name = "lmstudio/luna-ai-llama2"
            elif model_override == "ollama": model_name = "ollama/llama3"
            logger.info(f"🤖 User/Autonomous override active: {model_name}")

        logger.info(f"Generating content for task: {task} using model: {model_name}")
        
        system_prompt = self.get_system_prompt(task_type)
        
        # [Update 10: Agent Personality Tuning]
        # Merge precision/creativity parameters if provided
        generation_params = params or {}

        if "claude" in model_name:
            return self._generate_claude(model_name, system_prompt, task, generation_params)
        elif model_name.startswith("ollama/"):
            return self._generate_ollama(model_name.replace("ollama/", ""), system_prompt, task, generation_params)
        elif model_name.startswith("lmstudio/"):
            return self._generate_lmstudio(model_name.replace("lmstudio/", ""), system_prompt, task, generation_params)
        else:
            return self._generate_gemini(model_name, system_prompt, task, generation_params)

    def _generate_claude(self, model: str, system: str, prompt: str, params: Dict[str, Any]) -> Dict[str, Any]:
        temp = params.get("temperature", 0.7)
        message = self.anthropic_client.messages.create(
            model=model,
            max_tokens=2048,
            system=system,
            temperature=temp,
            messages=[{"role": "user", "content": prompt}]
        )
        return {
            "content": message.content[0].text,
            "model": model,
            "provider": "anthropic"
        }

    def _generate_gemini(self, model_name: str, system: str, prompt: str, params: Dict[str, Any]) -> Dict[str, Any]:
        temp = params.get("temperature", 0.7)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            f"{system}\n\nUser Task: {prompt}",
            generation_config=genai.types.GenerationConfig(temperature=temp)
        )
        return {
            "content": response.text,
            "model": model_name,
            "provider": "google"
        }

    def _generate_lmstudio(self, model: str, system: str, prompt: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Support for LM Studio local API (OpenAI compatible)"""
        url = os.getenv("LMSTUDIO_URL", "http://localhost:1234/v1/chat/completions")
        temp = params.get("temperature", 0.7)

        try:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temp,
                "stream": False
            }
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return {
                "content": data["choices"][0]["message"]["content"],
                "model": model,
                "provider": "lmstudio"
            }
        except Exception as e:
            logger.error(f"LM Studio generation failed: {e}")
            return {"error": str(e), "provider": "lmstudio"}

    def _generate_ollama(self, model: str, system: str, prompt: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update 1: Local LLM Integration (Ollama)"""
        url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        temp = params.get("temperature", 0.7)

        try:
            payload = {
                "model": model,
                "prompt": f"{system}\n\nTask: {prompt}",
                "stream": False,
                "options": {
                    "temperature": temp
                }
            }
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return {
                "content": data.get("response", ""),
                "model": model,
                "provider": "ollama"
            }
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return {"error": str(e), "provider": "ollama"}

    def list_assets(self) -> List[str]:
        """Recursively list assets in the library"""
        assets = []
        if not os.path.exists(self.asset_library_path):
            return assets
        
        for root, dirs, files in os.walk(self.asset_library_path):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.mp4', '.mov')):
                    assets.append(os.path.relpath(os.path.join(root, file), self.asset_library_path))
        return assets

if __name__ == "__main__":
    # Quick CLI test
    engine = BrandContentEngine()
    test_task = "Draft a community alert post about new data sovereignty tools being deployed in Seattle."
    result = engine.generate_content(test_task, task_type="analytical")
    print(f"\n--- GENERATED CONTENT ({result['model']}) ---")
    print(result['content'])
    print("\n--- ASSETS FOUND ---")
    print(engine.list_assets())
