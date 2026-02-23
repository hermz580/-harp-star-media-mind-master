from fastapi import FastAPI, HTTPException, Body, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
import uvicorn
import shutil
from typing import List
from brand_brain.orchestrator import MasterOrchestrator

app = FastAPI(title="Phoenix Master Operations")

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

@app.get("/api/status")
async def get_status():
    return {
        "roots": orch.discovery_paths,
        "agents": orch.vbrain.get("agent_integrations", {}),
        "platforms": orch.platforms.platforms,
        "bucket_path": str(orch.bucket_path),
        "global_focus": orch.global_focus
    }

@app.post("/api/focus/update")
async def update_focus(focus_data: dict = Body(...)):
    focus = focus_data.get("focus")
    if not focus:
        raise HTTPException(status_code=400, detail="Focus text required")
    new_focus = orch.set_focus(focus)
    return {"status": "success", "focus": new_focus}

@app.get("/api/system/discover")
async def discover_system():
    potential = orch.discover_system_roots()
    return {"potential": potential}

@app.post("/api/platforms/add")
async def add_platform(platform_data: dict = Body(...)):
    name = platform_data.get("name")
    config = platform_data.get("config", {})
    if not name:
        raise HTTPException(status_code=400, detail="Platform name required")
    p = orch.platforms.add_custom_platform(name, config)
    return {"status": "success", "platform": p}

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
async def propose_workflows():
    proposals = orch.process_bucket()
    return {"status": "success", "workflows": proposals}

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
    manifest = orch.synth.manifest_brand()
    return {"status": "success", "manifest": manifest}

# Serve bucket assets for preview
app.mount("/bucket", StaticFiles(directory=str(orch.bucket_path)), name="bucket")
# Also serve processed for history
app.mount("/processed", StaticFiles(directory=str(orch.processed_path)), name="processed")

# Serve static files (Dashboard UI)
app.mount("/", StaticFiles(directory="public", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
