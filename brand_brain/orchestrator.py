import os
import json
import time
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from .synthesis import BrandSynthesisEngine, DeepScanner
from .engine import BrandContentEngine

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

class MasterOrchestrator:
    """The Supreme Controller: Learns from multi-roots and acts on the Bucket"""
    
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.bucket_path = self.workspace_root / "brand-engine" / "bucket"
        self.processed_path = self.workspace_root / "brand-engine" / "bucket" / "processed"
        self.vbrain_path = self.workspace_root / "brand-engine" / "brand_brain" / "vbrain.json"
        
        self.global_focus = "General Brand Sovereignty"
        self.discovery_paths = [str(self.workspace_root)]
        
        # Ensure folders exist
        self.bucket_path.mkdir(parents=True, exist_ok=True)
        self.processed_path.mkdir(parents=True, exist_ok=True)
        
        self.synth = BrandSynthesisEngine(str(self.workspace_root))
        self.engine = BrandContentEngine()
        self.platforms = PlatformConnector()
        
        self.vbrain = self._load_vbrain()
        self.active_workflows = {}

    def set_focus(self, focus_text: str):
        self.global_focus = focus_text
        logger.info(f"🎯 Global Intelligence Focus set to: {focus_text}")
        return self.global_focus

    def _load_vbrain(self) -> Dict:
        if self.vbrain_path.exists():
            with open(self.vbrain_path, 'r') as f:
                return json.load(f)
        return {"learned_patterns": [], "context_map": {}, "agent_integrations": {}, "workflows": []}

    def save_vbrain(self):
        with open(self.vbrain_path, 'w') as f:
            json.dump(self.vbrain, f, indent=2)

    def add_discovery_path(self, path: str):
        if os.path.exists(path) and path not in self.discovery_paths:
            self.discovery_paths.append(path)
            logger.info(f"📍 Added discovery path: {path}")

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

    def process_bucket(self):
        """Creates proposed workflows for items in the bucket, using global focus"""
        new_items = [f for f in self.bucket_path.glob('*') if f.is_file()]
        if not new_items:
            return []
        
        proposals = []
        for item in new_items:
            workflow_id = f"wf_{int(time.time())}_{item.stem}"
            
            # Analyze context for creation
            manifest = self.vbrain.get("context_map", {}).get(self.discovery_paths[0], {})
            brand_info = manifest.get("brand_identity", {"brand_name": "Phoenix"})
            
            prompt = f"""
            Identify the best Workflow for this asset: '{item.name}'.
            Brand DNA: {json.dumps(brand_info)}
            USER MISSION FOCUS: {self.global_focus}
            
            Deliver a high-impact strategy that aligns with the user's specific mission focus.
            
            Output a JSON with:
            - title: Name of the workflow
            - story: The narrative hook (must incorporate the Focus)
            - tasks: List of [agent, task_description]
            - platform: Best platform for this (e.g. wordpress, instagram, youtube, or any custom platform)
            """
            
            try:
                response = self.synth.model.generate_content(prompt)
                plan = json.loads(response.text.strip('`json\n'))
                
                workflow = {
                    "id": workflow_id,
                    "asset": item.name,
                    "plan": plan,
                    "status": "awaiting_approval",
                    "timestamp": time.time()
                }
                
                self.active_workflows[workflow_id] = workflow
                proposals.append(workflow)
                
            except Exception as e:
                logger.error(f"Failed to propose workflow for {item.name}: {e}")
        
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
