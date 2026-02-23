from fastapi import FastAPI, UploadFile, File, HTTPException, Body, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
import uvicorn
import shutil
from typing import List, Dict, Any
from brand_brain.orchestrator import MasterOrchestrator

app = FastAPI(title="Harp * Star Media Mind Master")

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

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Orchestrator
ROOT_DIR = Path(__file__).parent.parent
orch = MasterOrchestrator(str(ROOT_DIR))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text() # Keep alive
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

@app.get("/api/status")
async def get_status():
    return {
        "roots": orch.discovery_paths,
        "agents": orch.vbrain.get("agent_integrations", {}),
        "platforms": orch.platforms.platforms,
        "bucket_path": str(orch.bucket_path),
        "global_focus": orch.global_focus,
        "vbrain": orch.vbrain
    }

@app.post("/api/focus/update")
async def update_focus(focus_data: dict = Body(...)):
    focus = focus_data.get("focus")
    if not focus:
        raise HTTPException(status_code=400, detail="Focus text required")
    new_focus = orch.set_focus(focus)
    return {"status": "success", "focus": new_focus}

@app.get("/api/system/discover")
async def discover_roots():
    roots = orch.discover_system_roots()
    return {"status": "success", "suggested": roots}

@app.post("/api/inspiration/add")
async def add_inspiration(url: str = Body(..., embed=True)):
    urls = orch.add_inspiration_url(url)
    return {"status": "success", "inspiration_urls": urls}

@app.post("/api/platforms/add")
async def add_platform(name: str = Body(..., embed=True), config: dict = Body(..., embed=True)):
    orch.platforms.add_custom_platform(name, config)
    return {"status": "success"}

@app.post("/api/bucket/upload")
async def upload_to_bucket(files: List[UploadFile] = File(...)):
    uploaded = []
    for file in files:
        file_path = orch.bucket_path / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        uploaded.append(file.filename)
    return {"status": "success", "uploaded": uploaded}

@app.post("/api/workflow/propose")
async def propose_workflows(background_tasks: BackgroundTasks, body: dict = Body(...)):
    user_spark = body.get("user_spark")
    workflows = orch.process_bucket(user_spark=user_spark)
    if workflows:
        # Trigger real-time swarm debate in the background
        asset_name = workflows[0]['asset']
        focus = orch.global_focus
        background_tasks.add_task(orch.swarm.collaborate, asset_name, focus, ws_manager, user_spark)
    return {"status": "success", "workflows": workflows}

@app.get("/api/workflow/pending")
async def get_pending_workflows():
    return {"workflows": list(orch.active_workflows.values())}

@app.post("/api/workflow/execute/{workflow_id}")
async def execute_workflow(workflow_id: str):
    result = orch.execute_workflow(workflow_id)
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result

@app.post("/api/roots/add")
async def add_root(path_data: dict = Body(...)):
    path = path_data.get("path")
    if not path:
        raise HTTPException(status_code=400, detail="Path is required")
    orch.add_discovery_path(path)
    return {"status": "success", "roots": orch.discovery_paths}

@app.post("/api/sync")
async def execute_sync():
    orch.learn()
    orch.sync_dna()
    return {"status": "success"}

app.mount("/bucket", StaticFiles(directory=str(orch.bucket_path)), name="bucket")
app.mount("/processed", StaticFiles(directory=str(orch.processed_path)), name="processed")
app.mount("/", StaticFiles(directory="public", html=True), name="public")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
