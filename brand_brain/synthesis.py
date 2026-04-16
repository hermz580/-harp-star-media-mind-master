import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeepScanner:
    """Autonomously scans filesystem to understand brand context and assets"""
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.context_files = []
        self.assets = []
        self.code_fingerprints = []

    def _extract_clusters(self, content: str) -> List[str]:
        """Simplified logic clustering for Recursive Code Mapping"""
        clusters = []
        lines = content.split('\n')
        for line in lines:
            if 'class ' in line or 'def ' in line or 'function ' in line:
                clusters.append(line.strip())
        return clusters

    def scan(self) -> Dict[str, Any]:
        logger.info(f"🚀 Initializing Deep Scan of {self.root_path}")
        
        # Scan for context (READMEs, documentation, project summaries, text files)
        # [Update 51: Universal Media Ingester (Text/Doc Focus)]
        context_exts = ('.md', '.txt', '.py', '.js', '.html', '.css', '.pdf')
        for path in self.root_path.rglob('*'):
            if path.suffix.lower() in context_exts and 'node_modules' not in str(path) and '.git' not in str(path):
                try:
                    # PDF Stub logic
                    if path.suffix.lower() == '.pdf':
                        content = f"[Apex 51] PDF DNA: {path.name} (Binary content - awaiting OCR/Whisper sync)"
                    else:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read(2000) # Get first 2k chars for context

                    self.context_files.append({
                        "path": str(path.relative_to(self.root_path)),
                        "snippet": content
                    })
                except:
                    continue

        # Scan for assets (Images, Videos)
        asset_exts = ('.png', '.jpg', '.jpeg', '.mp4', '.mov', '.webp', '.gif')
        for path in self.root_path.rglob('*'):
            if path.suffix.lower() in asset_exts and 'node_modules' not in str(path):
                self.assets.append({
                    "path": str(path.relative_to(self.root_path)),
                    "type": "video" if path.suffix.lower() in ('.mp4', '.mov') else "image",
                    "size": path.stat().st_size
                })

        # [Update 3: Recursive Code Mapping]
        # Scan for Project DNA (package.json, setup files, main entries)
        dna_files = ['package.json', 'requirements.txt', 'Dockerfile', 'main.py', 'index.html', 'AGENTS.md']
        for dna in dna_files:
            dna_path = self.root_path / dna
            if dna_path.exists():
                try:
                    with open(dna_path, 'r', encoding='utf-8') as f:
                        content = f.read(2000)
                        self.code_fingerprints.append({
                            "file": dna,
                            "content": content,
                            "logic_clusters": self._extract_clusters(content)
                        })
                except:
                    continue

        return {
            "context_count": len(self.context_files),
            "asset_count": len(self.assets),
            "dna_captured": [f['file'] for f in self.code_fingerprints],
            "assets": self.assets[:20], # Sample for summary
            "context_snippets": self.context_files[:5]
        }

class AssetIntelligence:
    """Analyzes URLs and external data to build brand knowledge"""
    @staticmethod
    def scrape_url(url: str) -> Dict[str, str]:
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            return {
                "url": url,
                "title": soup.title.string if soup.title else "No Title",
                "text": ' '.join([p.text for p in soup.find_all('p')[:10]]) # First 10 paragraphs
            }
        except Exception as e:
            return {"url": url, "error": str(e)}

class BrandSynthesisEngine:
    """The master brain that manifested the brand from discoveries"""
    def __init__(self, root_path: str):
        self.root_path = root_path
        self.scanner = DeepScanner(root_path)
        self.intelligence = AssetIntelligence()
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        else:
            self.model = None

    def analyze_asset_vision(self, file_path: Path) -> str:
        """Update 2: Vision DNA Extraction"""
        if not self.api_key:
            return "Vision analysis skipped: No API Key."

        try:
            with open(file_path, "rb") as f:
                image_data = f.read()

            # Simple heuristic to avoid uploading huge files for basic DNA
            if len(image_data) > 4 * 1024 * 1024:
                return "File too large for fast vision sync."

            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content([
                "Describe the visual style, dominant colors, and mood of this brand asset for DNA extraction. Be concise.",
                {"mime_type": "image/jpeg", "data": image_data}
            ])
            return response.text
        except Exception as e:
            logger.error(f"Vision analysis failed for {file_path.name}: {e}")
            return f"Vision error: {str(e)}"

    def manifest_brand(self, external_urls: List[str] = []) -> Dict[str, Any]:
        """Deep Synthesis: Scan, Scrap, and Manifest"""
        # 1. Internal Physical Discovery
        discovery_data = self.scanner.scan()
        
        # 1b. Enhanced Vision Sync (Update 2)
        vision_insights = []
        asset_exts = ('.png', '.jpg', '.jpeg', '.webp')
        # Only analyze first 3 assets to keep sync fast
        count = 0
        for asset in discovery_data.get('assets', []):
            if any(asset['path'].lower().endswith(ext) for ext in asset_exts):
                full_path = Path(self.root_path) / asset['path']
                if full_path.exists():
                    insight = self.analyze_asset_vision(full_path)
                    vision_insights.append({"asset": asset['path'], "insight": insight})
                    count += 1
                    if count >= 3: break

        # 2. External Intelligence Discovery
        external_context = []
        for url in external_urls:
            # Handle if url is a dict or string
            actual_url = url['url'] if isinstance(url, dict) else url
            external_context.append(self.intelligence.scrape_url(actual_url))

        # 3. Autonomous Manifestation Prompt
        synthesis_prompt = f"""
        Analyze this raw data from my filesystem and external sources to MANIFEST my brand identity and current workflow.
        
        FILESYSTEM DISCOVERY:
        - Assets: {json.dumps(discovery_data['assets'])}
        - Project DNA: {json.dumps(discovery_data['dna_captured'])}
        - Context Snippets: {json.dumps(discovery_data['context_snippets'])}
        - Vision Insights: {json.dumps(vision_insights)}
        
        EXTERNAL CONTEXT:
        {json.dumps(external_context)}
        
        TASK:
        1. Define the Brand Identity (Mission, Tone, Signature Phrases).
        2. Identify the core "Product" or "Work" I am focused on right now.
        3. Suggest 3 immediate WORKFLOWS (e.g. "Create a product launch video using asset_x.mp4").
        4. Generate a 'Brand Manifest' JSON object.
        
        Return ONLY a JSON object with keys: brand_identity, active_focus, suggested_workflows, brand_manifest_json.
        """
        
        if not self.model:
            return {"error": "Generative model not configured. Missing API Key."}

        try:
            response = self.model.generate_content(synthesis_prompt)
            result = json.loads(response.text.strip('`json\n'))
            
            # Persist to profile
            profile_path = Path(self.root_path) / "brand_brain" / "brand_profile.json"
            if profile_path.parent.exists():
                with open(profile_path, 'w') as f:
                    json.dump(result['brand_manifest_json'], f, indent=2)
            
            return result
        except Exception as e:
            logger.error(f"Manifestation failed: {str(e)}")
            return {"error": str(e)}

if __name__ == "__main__":
    # Test manifestation
    engine = BrandSynthesisEngine(os.getcwd())
    print("🔮 Phoenix is manifesting your brand...")
    manifest = engine.manifest_brand()
    print(json.dumps(manifest, indent=2))
