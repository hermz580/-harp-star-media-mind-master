import os
import json
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

    def generate_content(self, task: str, task_type: str = "default") -> Dict[str, Any]:
        routing = self.profile.get("llm_routing", {})
        model_name = routing.get(task_type, routing.get("default", "gemini-1.5-flash"))
        
        logger.info(f"Generating content for task: {task} using model: {model_name}")
        
        system_prompt = self.get_system_prompt(task_type)
        
        if "claude" in model_name:
            return self._generate_claude(model_name, system_prompt, task)
        else:
            return self._generate_gemini(model_name, system_prompt, task)

    def _generate_claude(self, model: str, system: str, prompt: str) -> Dict[str, Any]:
        message = self.anthropic_client.messages.create(
            model=model,
            max_tokens=2048,
            system=system,
            messages=[{"role": "user", "content": prompt}]
        )
        return {
            "content": message.content[0].text,
            "model": model,
            "provider": "anthropic"
        }

    def _generate_gemini(self, model_name: str, system: str, prompt: str) -> Dict[str, Any]:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(f"{system}\n\nUser Task: {prompt}")
        return {
            "content": response.text,
            "model": model_name,
            "provider": "google"
        }

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
