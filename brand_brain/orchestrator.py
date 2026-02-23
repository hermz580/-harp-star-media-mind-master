import os
import json
import time
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from .synthesis import BrandSynthesisEngine, DeepScanner
from .engine import BrandContentEngine
import uuid

logger = logging.getLogger(__name__)

class PlatformConnector:
    """Handles connections to external platforms"""
    def __init__(self):
        self.platforms = {
            "wordpress": {"status": "connected", "url": os.getenv("WORDPRESS_URL"), "type": "blog"},
            "instagram": {"status": "ready", "auth": False, "type": "social"},
            "youtube": {"status": "ready", "auth": False, "type": "video"},
            "github": {"status": "connected", "user": "hermz580", "type": "code"}
        }

    def add_custom_platform(self, name: str, config: Dict[str, Any]):
        self.platforms[name.lower()] = {
            "status": "integrated",
            "type": config.get("type", "custom"),
            "url": config.get("url"),
            "api_key_ref": config.get("api_key_ref")
        }
        return self.platforms[name.lower()]

    def post(self, platform: str, content: Dict[str, Any]):
        p = self.platforms.get(platform.lower())
        if not p:
            return {"status": "error", "message": f"Platform {platform} not found"}
            
        logger.info(f"📝 Agentic Post to {platform}: {content.get('title')}")
        # Real integration logic would switch based on platform type/config
        return {"status": "success", "url": p.get("url", "local_manifest_only")}

from fastapi import WebSocket
import asyncio

class AgentSwarm:
    """Manages a collection of free specialist agents that collaborate in real-time"""
    def __init__(self, orchestrator):
        self.orch = orchestrator
        self.specialists = {
            "Narrator": {"icon": "auto_stories", "color": "primary", "focus": "Brand Story & Copy"},
            "Visionary": {"icon": "visibility", "color": "secondary", "focus": "Aesthetics & Visual Style"},
            "Strategist": {"icon": "leaderboard", "color": "accent", "focus": "Platform Impact & ROI"},
            "Producer": {"icon": "movie_filter", "color": "emerald", "focus": "Execution & Agent Coordination"},
            "Liaison": {"icon": "smart_toy", "color": "orange-400", "focus": "Hugging Face & Local Model Integration"}
        }
        self.active_broadcasts = []

    async def collaborate(self, asset_info: str, focus: str, ws_manager=None, user_spark: str = None):
        """Simulates a real-time debate between agents to build a production plan"""
        logs = []
        
        # 0. System Note: Agents check learned DNA
        dna_source = "Local Assets" + (f" + {len(self.orch.inspiration_urls)} Brand Websites" if self.orch.inspiration_urls else "")
        await self._broadcast("Narrator", f"Initializing sequence. Synching with {dna_source}...", ws_manager)
        await asyncio.sleep(1.0)

        if user_spark:
            await self._broadcast("Narrator", f"Recieving User Steering: '{user_spark}'", ws_manager)
            await asyncio.sleep(0.5)

        # 1. Narrator starts with Cohesion
        if user_spark:
            msg = f"Analyzing '{asset_info}'. I will weave your spark '{user_spark}' into the brand core."
        else:
            msg = f"Analyzing '{asset_info}'. Autonomous decision: I'm manifesting a high-energy anthem based on the vibrant tones detected in the pixels."
        await self._broadcast("Narrator", msg, ws_manager)
        
        # 2. Visionary weighs in on Consistency
        await asyncio.sleep(1.5)
        if user_spark:
            msg = f"Style lock engaged. Morphing visual geometry to {user_spark} spec."
        else:
            msg = "Pixel scanning complete. I've identified a unique grain pattern here. I'm going to generate a series of matching hyper-textures to surround this asset in the final render."
        await self._broadcast("Visionary", msg, ws_manager)

        # 3. Liaison suggests Free/Community paths
        await asyncio.sleep(1.0)
        msg = "I've scouted the HF Hub. For this specific texture, I'm pulling 'Stable-Diffusion-XL-Base' with a custom Lora for that afro-tech shimmer."
        await self._broadcast("Liaison", msg, ws_manager)
        
        # 4. Strategist analyzes inspiration websites
        await asyncio.sleep(1.2)
        msg = "Market alignment: This asset screams 'Premium Engagement'. I'm shifting the production cadence to 4K Wide-Screen to dominate the desktop feed."
        await self._broadcast("Strategist", msg, ws_manager)
        
        # 5. Producer finalizes
        await asyncio.sleep(1.8)
        msg = "Manifestation pipeline locked. I'm creating a 'Director's Cut' sequence using ALL available media fragments to ensure the story is complete. Ready for ignition."
        await self._broadcast("Producer", msg, ws_manager)

    async def _broadcast(self, agent: str, message: str, ws_manager):
        data = {
            "type": "swarm_talk",
            "agent": agent,
            "message": message,
            "icon": self.specialists[agent]["icon"],
            "color": self.specialists[agent]["color"],
            "timestamp": time.time()
        }
        if ws_manager:
            await ws_manager.broadcast(data)
        logger.info(f"🐝 [Swarm] {agent}: {message}")

class MasterOrchestrator:
    """The Supreme Controller: Learns from multi-roots and acts on the Bucket"""
    
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        
        # Check if we are already in the brand-engine directory
        if self.workspace_root.name == "brand-engine":
            self.project_root = self.workspace_root
        else:
            self.project_root = self.workspace_root / "brand-engine"

        self.bucket_path = self.project_root / "bucket"
        self.processed_path = self.project_root / "bucket" / "processed"
        self.vbrain_path = self.project_root / "brand_brain" / "vbrain.json"
        
        self.global_focus = "General Brand Sovereignty"
        self.discovery_paths = [str(self.workspace_root)]
        
        # Ensure folders exist
        self.bucket_path.mkdir(parents=True, exist_ok=True)
        self.processed_path.mkdir(parents=True, exist_ok=True)
        (self.project_root / "brand_brain").mkdir(parents=True, exist_ok=True)
        
        self.synth = BrandSynthesisEngine(str(self.workspace_root))
        self.engine = BrandContentEngine()
        self.platforms = PlatformConnector()
        self.swarm = AgentSwarm(self) # Initialize Swarm
        
        self.vbrain = self._load_vbrain()
        self.inspiration_urls = self.vbrain.get("inspiration_urls", [])
        self.active_workflows = {}

    def set_focus(self, focus_text: str):
        self.global_focus = focus_text
        logger.info(f"🎯 Global Intelligence Focus set to: {focus_text}")
        return self.global_focus

    def _load_vbrain(self) -> Dict:
        if self.vbrain_path.exists():
            with open(self.vbrain_path, 'r') as f:
                return json.load(f)
        return {"learned_patterns": [], "context_map": {}, "agent_integrations": {}, "workflows": [], "inspiration_urls": []}

    def save_vbrain(self):
        with open(self.vbrain_path, 'w') as f:
            json.dump(self.vbrain, f, indent=2)

    def add_discovery_path(self, path: str):
        if os.path.exists(path) and path not in self.discovery_paths:
            self.discovery_paths.append(path)
            logger.info(f"📍 Added discovery path: {path}")

    def add_inspiration_url(self, url: str):
        if url not in self.inspiration_urls:
            self.inspiration_urls.append(url)
            self.vbrain["inspiration_urls"] = self.inspiration_urls
            self.save_vbrain()
            logger.info(f"🔗 Added Inspiration URL: {url}")
        return self.inspiration_urls

    def sync_dna(self):
        """Multi-root learning + External Website Synthesis"""
        logger.info("📡 Starting Deep DNA Sync...")
        # Manifest from both local roots and inspiration websites
        manifest = self.synth.manifest_brand(external_urls=self.inspiration_urls)
        
        self.vbrain["context_map"][self.discovery_paths[0]] = manifest
        self.vbrain["last_learning_session"] = time.time()
        self.save_vbrain()

    def learn(self):
        """Phase 2: Machine Learning - Fingerprinting all allowed filesystems"""
        logger.info("🧠 Initializing Multi-Root Learning Phase...")
        all_dna = []
        for path in self.discovery_paths:
            scanner = DeepScanner(path)
            discovery = scanner.scan()
            self.vbrain["context_map"][path] = discovery
            all_dna.append(discovery.get("dna_captured", []))
            
        logger.info(f"✅ Learned from {len(self.discovery_paths)} roots.")
        self.vbrain["last_learning_session"] = time.time()
        self.save_vbrain()

    def discover_system_roots(self):
        """Searches for potential high-value roots on the system to suggest to the user"""
        potential = []
        user_home = Path.home()
        # Look for common project directories
        scan_dirs = [user_home, user_home / "Documents", user_home / "Desktop"]
        
        for sd in scan_dirs:
            if sd.exists():
                try:
                    for item in sd.iterdir():
                        if item.is_dir() and not item.name.startswith('.'):
                            # Check if it looks like a project
                            if (item / "README.md").exists() or (item / "package.json").exists() or (item / ".git").exists():
                                if str(item) not in self.discovery_paths:
                                    potential.append(str(item))
                except Exception:
                    continue
        return potential[:10] # Return top 10 suggestions

    def process_bucket(self, user_spark: str = None) -> List[Dict]:
        """Scans bucket and proposes workflows based on discovered assets, DNA, and optional user steering"""
        proposals = []
        asset_exts = ('.png', '.jpg', '.jpeg', '.mp4', '.mov', '.webp')
        
        for path in self.bucket_path.glob('*'):
            if path.suffix.lower() in asset_exts and 'processed' not in str(path):
                w_id = str(uuid.uuid4())[:8]
                # Default to a free workflow if it's an image
                is_free = path.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp')
                
                desc = f"Targeting {path.stem}. Utilizing Hugging Face Liaison for free creative synthesis."
                if user_spark:
                    desc += f" Context: User requested '{user_spark}'."

                proposals.append({
                    "id": w_id,
                    "asset": path.name,
                    "type": "No-Key Manifestation" if is_free else "Premium Production",
                    "description": desc,
                    "status": "pending",
                    "free": is_free
                })
                self.active_workflows[w_id] = proposals[-1]
        
        return proposals

    def execute_workflow(self, workflow_id: str):
        """Actually performs the work after approval"""
        if workflow_id not in self.active_workflows:
            return {"status": "error", "message": "Workflow not found"}
        
        wf = self.active_workflows[workflow_id]
        wf["status"] = "executing"
        
        results = []
        for agent, task in wf["plan"]["tasks"]:
            logger.info(f"🤖 Agent {agent} executing: {task}")
            # Here we would call the actual agentic scripts
            results.append({"agent": agent, "status": "simulated_success"})
            
        # Post to platform
        platform = wf["plan"].get("platform")
        if platform:
            post_res = self.platforms.post(platform, {"title": wf["plan"]["title"], "body": wf["plan"]["story"]})
            wf["post_result"] = post_res
            
        wf["status"] = "completed"
        
        # Move asset only after full completion
        asset_path = self.bucket_path / wf["asset"]
        if asset_path.exists():
            shutil.move(str(asset_path), str(self.processed_path / wf["asset"]))
            
        return wf

    def integrate_agent(self, name: str, url: str):
        self.vbrain["agent_integrations"][name] = {
            "url": url,
            "status": "ready",
            "integration_time": time.time()
        }
        self.save_vbrain()
