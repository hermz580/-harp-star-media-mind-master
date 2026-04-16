from fastapi import FastAPI, UploadFile, File, HTTPException, Body, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
import json
import time
import uvicorn
import shutil
import psutil
import asyncio
from typing import List, Dict, Any
from brand_brain.orchestrator import MasterOrchestrator
from brand_brain.core.events import bus, Event

app = FastAPI(title="Harp * Star Media Mind Master OS v3")

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                continue

ws_manager = ConnectionManager()

# Global Event Listener for WebSocket Broadcasting
async def broadcast_events(event: Event):
    await ws_manager.broadcast({
        "type": "event_pulse",
        "event": event.type,
        "data": event.data,
        "source": event.source,
        "timestamp": event.timestamp
    })

# Enable wildcard subscription
bus.subscribe("*", broadcast_events)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Orchestrator
ROOT_DIR = Path(__file__).parent
orch = MasterOrchestrator(str(ROOT_DIR))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        # Send initial state
        await websocket.send_json({
            "type": "init_state",
            "state": bus.get_state()
        })
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

@app.get("/api/status")
async def get_status():
    cpu_usage = psutil.cpu_percent()
    ram = psutil.virtual_memory()

    return {
        "roots": orch.discovery_paths,
        "agents": orch.vbrain.get("agent_integrations", {}),
        "platforms": orch.platforms.platforms,
        "bucket_path": str(orch.bucket_path),
        "global_focus": orch.global_focus,
        "vbrain": orch.vbrain,
        "resources": {
            "cpu": f"{cpu_usage}%",
            "ram": f"{ram.percent}%",
            "status": "Optimal" if cpu_usage < 80 else "High Load"
        },
        "live_state": bus.get_state()
    }

@app.post("/api/focus/update")
async def update_focus(focus_data: dict = Body(...)):
    focus = focus_data.get("focus")
    if not focus:
        raise HTTPException(status_code=400, detail="Focus text required")
    new_focus = await orch.set_focus(focus)
    return {"status": "success", "focus": new_focus}

@app.post("/api/workflow/propose")
async def propose_workflows(background_tasks: BackgroundTasks, body: dict = Body(...)):
    user_spark = body.get("user_spark")
    personality = body.get("personality", {"creativity": 0.7, "logic": 0.5})
    model_override = body.get("model_override", "auto")

    orch.vbrain["current_personality"] = personality
    orch.vbrain["model_override"] = model_override

    workflows = await orch.process_bucket(user_spark=user_spark)
    if workflows:
        asset_name = workflows[0]['asset']
        focus = orch.global_focus
        background_tasks.add_task(orch.swarm.collaborate, asset_name, focus, user_spark)
    return {"status": "success", "workflows": workflows}

@app.get("/api/workflow/pending")
async def get_pending_workflows():
    return {"workflows": list(orch.active_workflows.values())}

@app.post("/api/workflow/execute/{workflow_id}")
async def execute_workflow(workflow_id: str):
    result = await orch.execute_workflow(workflow_id)
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result

@app.post("/api/sync")
async def execute_sync():
    await orch.sync_dna()
    return {"status": "success"}

@app.get("/api/brand/bible")
async def get_brand_bible():
    vbrain = orch.vbrain
    profile_path = orch.project_root / "brand_brain" / "brand_profile.json"
    profile = {}
    if profile_path.exists():
        with open(profile_path, 'r') as f:
            profile = json.load(f)

    bible = {
        "identity": profile.get("brand_identity", vbrain.get("identity_summary", "Awaiting manifestation...")),
        "active_focus": orch.global_focus,
        "keywords": ["Empowerment", "Innovation", "Sovereignty"],
        "color_palette": ["#00F2FF", "#FF00E5", "#0A0A0F"],
        "tone": "Vibrant / Authoritative",
        "last_updated": vbrain.get("last_learning_session", time.time())
    }
    return bible

@app.post("/api/workspace/switch")
async def switch_workspace(name: str = Body(..., embed=True)):
    res = await orch.switch_workspace(name)
    return res

app.mount("/bucket", StaticFiles(directory=str(orch.bucket_path)), name="bucket")
app.mount("/processed", StaticFiles(directory=str(orch.processed_path)), name="processed")
app.mount("/", StaticFiles(directory="public", html=True), name="public")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
