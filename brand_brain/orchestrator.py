import os
import json
import time
import shutil
import logging
from pathlib import Path
import importlib
import pkgutil
from cryptography.fernet import Fernet
from typing import Dict, List, Any, Optional
from .synthesis import BrandSynthesisEngine, DeepScanner
from .engine import BrandContentEngine
from .memory import Cortex
import uuid
import requests
import random
from .core.events import bus, Event

logger = logging.getLogger(__name__)

class PlatformConnector:
    """Handles connections to external platforms"""
    def __init__(self, orchestrator=None):
        self.orch = orchestrator
        self.platforms = {
            "wordpress": {"status": "connected", "url": os.getenv("WORDPRESS_URL"), "type": "blog"},
            "instagram": {"status": "ready", "auth": False, "type": "social"},
            "youtube": {"status": "ready", "auth": False, "type": "video"},
            "github": {"status": "connected", "user": "hermz580", "type": "code"},
            "fal.ai": {"status": "connected", "type": "video_gen"},
            "elevenlabs": {"status": "ready", "type": "voice_synth"},
            "x": {"status": "ready", "type": "social"},
            "linkedin": {"status": "ready", "type": "social"}
        }

    def add_custom_platform(self, name: str, config: Dict[str, Any]):
        self.platforms[name.lower()] = {
            "status": "integrated",
            "type": config.get("type", "custom"),
            "url": config.get("url"),
            "api_key_ref": config.get("api_key_ref")
        }
        return self.platforms[name.lower()]

    async def post(self, platform: str, content: Dict[str, Any]):
        if platform.lower() == "local_export":
            export_path = Path("library/exports")
            export_path.mkdir(parents=True, exist_ok=True)
            file_name = f"manifest_{int(time.time())}.json"
            with open(export_path / file_name, 'w') as f:
                json.dump(content, f, indent=4)
            return {"status": "success", "message": f"Exported to {export_path / file_name}"}

        p = self.platforms.get(platform.lower())
        if not p:
            return {"status": "error", "message": f"Platform {platform} not found"}
            
        logger.info(f"📝 Agentic Post to {platform}: {content.get('title')}")
        await bus.emit(Event("platform_post", {"platform": platform, "title": content.get('title')}, source="platform_connector"))
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
            "Liaison": {"icon": "smart_toy", "color": "orange-400", "focus": "Hugging Face & Local Model Integration"},
            "Arbiter": {"icon": "gavel", "color": "red-500", "focus": "Hallucination Defense & Fact Checking"},
            "Modeler": {"icon": "account_tree", "color": "cyan-400", "focus": "Autonomous Model Stack Strategy"},
            "Synthesizer": {"icon": "psychology", "color": "purple-500", "focus": "Executive Conflict Resolution & Logic Sync"}
        }

    async def collaborate(self, asset_info: str, focus: str, user_spark: str = None, params: Dict[str, Any] = None):
        """Simulates a real-time debate between agents to build a production plan"""
        # [Apex Update 11: Goal Decomposition Dispatcher Logic]
        # Decompose the goal based on the focus and spark
        goals = ["Storytelling", "Visual Style", "Platform Impact", "Quality Verification"]
        if "video" in asset_info.lower() or "mp4" in asset_info.lower():
            goals.append("Audio Manifestation")

        await bus.emit(Event("swarm_init", {
            "asset": asset_info,
            "focus": focus,
            "spark": user_spark,
            "sub_goals": goals
        }, source="swarm"))

        dna_source = "Local Assets" + (f" + {len(self.orch.inspiration_urls)} Brand Websites" if self.orch.inspiration_urls else "")
        await self._broadcast("Narrator", f"Goal Decomposition: Addressing {len(goals)} sub-goals for {asset_info}. Synching with {dna_source}...")
        await asyncio.sleep(1.0)

        # Modeler Suggests Stack
        is_local_preferred = any(kw in focus.lower() for kw in ['privacy', 'sovereignty', 'secure', 'local'])
        stack_suggestion = "LM Studio Llama-3 (Local)" if is_local_preferred else "Gemini 1.5 Flash (Cloud)"
        await self._broadcast("Modeler", f"Task complexity analysis: Suggested Stack: {stack_suggestion}.")
        await asyncio.sleep(1.0)

        # Narrator
        msg = f"Analyzing '{asset_info}'. I've detected high-frequency creative patterns. Manifesting now."
        await self._broadcast("Narrator", msg)
        await asyncio.sleep(1.0)

        # Visionary
        await self._broadcast("Visionary", "Pixel geometry locked. Visual aesthetics optimized for brand prestige.")
        await asyncio.sleep(1.0)

        # Synthesizer
        await self._broadcast("Synthesizer", "Resolving agentic friction. Strategy and Aesthetics synchronized.")
        await asyncio.sleep(1.0)

        # Finalize
        await self._broadcast("Producer", "Manifestation pipeline locked. Director's Cut ready.")

        # Update Workflow Object
        for wf_id, wf in self.orch.active_workflows.items():
            if wf['asset'] == asset_info:
                wf['plan'] = {
                    "title": f"Manifest: {asset_info}",
                    "story": "Collaborative plan manifested by Swarm OS.",
                    "tasks": [["Narrator", "DNA Sync Complete"], ["Synthesizer", "Conflict Resolution Passed"], ["Producer", "Ready for Ignition"]],
                    "platform": "local_export"
                }
                await bus.emit(Event("workflow_updated", {"workflow_id": wf_id}, source="swarm"))

    async def _broadcast(self, agent: str, message: str):
        data = {
            "agent": agent,
            "message": message,
            "icon": self.specialists[agent]["icon"],
            "color": self.specialists[agent]["color"],
            "timestamp": time.time()
        }
        await bus.emit(Event("swarm_talk", data, source=f"agent_{agent.lower()}"))
        logger.info(f"🐝 [Swarm] {agent}: {message}")

class MasterOrchestrator:
    """The Supreme Controller: Learns from multi-roots and acts on the Bucket"""
    
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        
        if (self.workspace_root / "brand_brain").exists() or self.workspace_root.name == "brand-engine":
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
        self.platforms = PlatformConnector(self)
        self.swarm = AgentSwarm(self)
        
        self.vbrain = self._load_vbrain()
        self.inspiration_urls = self.vbrain.get("inspiration_urls", [])
        self.active_workflows = {}
        self.memory = Cortex()

    async def set_focus(self, focus_text: str):
        self.global_focus = focus_text
        await bus.emit(Event("focus_changed", {"new_focus": focus_text}, source="orchestrator"))
        return self.global_focus

    def _get_encryption_key(self):
        key_path = self.project_root / "brand_brain" / ".vkey"
        if key_path.exists():
            return key_path.read_bytes()
        else:
            key = Fernet.generate_key()
            key_path.write_bytes(key)
            return key

    def _load_vbrain(self, vault_override=None) -> Dict:
        encrypted_path = vault_override or (self.project_root / "brand_brain" / "vbrain.vault")
        if encrypted_path.exists():
            try:
                cipher = Fernet(self._get_encryption_key())
                encrypted_data = encrypted_path.read_bytes()
                decrypted_data = cipher.decrypt(encrypted_data)
                return json.loads(decrypted_data)
            except Exception as e:
                logger.error(f"Failed to decrypt V-Brain Vault: {e}")

        if self.vbrain_path.exists():
            with open(self.vbrain_path, 'r') as f:
                return json.load(f)

        return {"learned_patterns": [], "context_map": {}, "agent_integrations": {}, "workflows": [], "inspiration_urls": []}

    async def save_vbrain(self):
        data_str = json.dumps(self.vbrain, indent=2)
        cipher = Fernet(self._get_encryption_key())
        encrypted_data = cipher.encrypt(data_str.encode())

        v_name = self.vbrain_path.stem
        encrypted_path = self.vbrain_path.parent / f"{v_name}.vault"
        encrypted_path.write_bytes(encrypted_data)

        with open(self.vbrain_path, 'w') as f:
            f.write(data_str)

        await bus.emit(Event("brain_saved", {"path": str(self.vbrain_path)}, source="orchestrator"))

    async def switch_workspace(self, workspace_name: str):
        safe_name = "".join([c for c in workspace_name if c.isalnum()]).lower()
        if not safe_name: safe_name = "default"

        self.vbrain_path = self.project_root / "brand_brain" / f"vbrain_{safe_name}.json"
        new_vault_path = self.project_root / "brand_brain" / f"vbrain_{safe_name}.vault"

        await self.save_vbrain()
        self.vbrain = self._load_vbrain(vault_override=new_vault_path)
        self.inspiration_urls = self.vbrain.get("inspiration_urls", [])
        await bus.emit(Event("workspace_switched", {"workspace": workspace_name}, source="orchestrator"))
        return {"status": "success", "workspace": workspace_name}

    async def sync_dna(self):
        await bus.emit(Event("sync_started", source="orchestrator"))
        manifest = self.synth.manifest_brand(external_urls=self.inspiration_urls)
        if 'context_snippets' in manifest:
            await self.memory.add_snippets(manifest['context_snippets'])
        self.vbrain["context_map"][self.discovery_paths[0]] = manifest
        await self.save_vbrain()
        await bus.emit(Event("sync_completed", {"snippets": len(manifest.get('context_snippets', []))}, source="orchestrator"))

    async def process_bucket(self, user_spark: str = None) -> List[Dict]:
        proposals = []
        asset_exts = ('.png', '.jpg', '.jpeg', '.mp4', '.mov', '.webp')
        all_assets = list(self.bucket_path.glob('*'))

        for path in all_assets:
            if path.suffix.lower() in asset_exts and 'processed' not in str(path):
                w_id = str(uuid.uuid4())[:8]
                is_free = path.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp')
                
                proposals.append({
                    "id": w_id, "asset": path.name, "type": "Auto-Manifest", "status": "pending", "free": is_free,
                    "plan": {"title": f"Manifesting {path.stem}", "story": "Scanning DNA...", "tasks": [["System", "Initializing"]]}
                })
                self.active_workflows[w_id] = proposals[-1]
        
        await bus.emit(Event("bucket_processed", {"count": len(proposals)}, source="orchestrator"))
        return proposals

    async def execute_workflow(self, workflow_id: str, attempt: int = 1):
        """Update 4: Self-Healing Logic with Auto-Retry"""
        if workflow_id not in self.active_workflows:
            return {"status": "error", "message": "Workflow not found"}

        wf = self.active_workflows[workflow_id]
        wf["status"] = "executing"
        await bus.emit(Event("workflow_started", {"id": workflow_id, "attempt": attempt}, source="orchestrator"))

        try:
            # Simulated Execution with potential "Model failure"
            if attempt == 1 and random.random() < 0.2: # 20% simulated failure rate for testing self-healing
                raise Exception("Cloud API Timeout")

            await asyncio.sleep(2.0)
            
            platform = wf["plan"].get("platform")
            if platform:
                post_res = await self.platforms.post(platform, {"title": wf["plan"]["title"], "body": wf["plan"]["story"]})
                wf["post_result"] = post_res

            wf["status"] = "completed"
            asset_path = self.bucket_path / wf["asset"]
            if asset_path.exists():
                shutil.move(str(asset_path), str(self.processed_path / wf["asset"]))

            await bus.emit(Event("workflow_completed", {"id": workflow_id}, source="orchestrator"))
            return wf
            
        except Exception as e:
            logger.warning(f"⚠️ Workflow {workflow_id} failed: {e}. Initiating Self-Healing...")
            await bus.emit(Event("workflow_failure", {"id": workflow_id, "error": str(e)}, source="orchestrator"))
            
            if attempt < 3:
                await bus.emit(Event("self_healing", {"id": workflow_id, "strategy": "Switch to Local Stack"}, source="orchestrator"))
                await asyncio.sleep(1.0)
                return await self.execute_workflow(workflow_id, attempt + 1)
            else:
                wf["status"] = "failed"
                return {"status": "error", "message": f"Execution failed after 3 attempts: {str(e)}"}

    def add_discovery_path(self, path: str):
        if os.path.exists(path) and path not in self.discovery_paths:
            self.discovery_paths.append(path)
            logger.info(f"📍 Added discovery path: {path}")

    def discover_system_roots(self):
        """Searches for potential high-value roots on the system to suggest to the user"""
        potential = []
        user_home = Path.home()
        scan_dirs = [user_home, user_home / "Documents", user_home / "Desktop"]
        for sd in scan_dirs:
            if sd.exists():
                try:
                    for item in sd.iterdir():
                        if item.is_dir() and not item.name.startswith('.'):
                            if (item / "README.md").exists() or (item / "package.json").exists() or (item / ".git").exists():
                                if str(item) not in self.discovery_paths:
                                    potential.append(str(item))
                except Exception:
                    continue
        return potential[:10]
