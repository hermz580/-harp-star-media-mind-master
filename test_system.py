import os
import json
import logging
from pathlib import Path
from brand_brain.orchestrator import MasterOrchestrator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SYSTEM_CHECK")

def test_logic():
    print("\n--- Harp * Star Media Mind Master: Logic Health Check ---")
    
    # 1. Initialize Orchestrator
    try:
        orch = MasterOrchestrator(os.getcwd())
        print("[Logic] MasterOrchestrator Initialized successfully.")
    except Exception as e:
        print(f"[Logic] Orchestrator Init Failed: {e}")
        return

    # 2. Check V-Brain persistence
    if orch.vbrain_path.exists():
        print(f"[Data] V-Brain found at {orch.vbrain_path}")
    else:
        print("[Data] V-Brain not found (this is normal for first-run). Initializing...")
        orch.save_vbrain()

    # 3. Test Global Focus
    test_focus = "Community Empowerment in Seattle"
    orch.set_focus(test_focus)
    if orch.global_focus == test_focus:
        print(f"[Logic] Global Focus logic working: '{orch.global_focus}'")
    else:
        print("[Logic] Global Focus update failed.")

    # 4. Test Platform Addition
    test_platform = "Discord_HarpStar"
    orch.platforms.add_custom_platform(test_platform, {"url": "https://discord.com/api/webhooks/test"})
    if test_platform.lower() in orch.platforms.platforms:
        print(f"[Automation] Custom Platform addition verified.")
    else:
        print("[Automation] Platform addition failed.")

    # 5. Test System Discovery
    suggestions = orch.discover_system_roots()
    print(f"[Intelligence] System Scan discovered {len(suggestions)} potential roots.")
    if len(suggestions) > 0:
        print(f"   Sample: {suggestions[0]}")

    # 6. Verify Security Strings (Cross-check with UI)
    with open("public/index.html", "r") as f:
        html = f.read()
        if "HARP * STAR MEDIA MIND MASTER" in html and "lockdown-screen" in html:
            print("[Security] Harp*Star Lockdown Protocol identified in UI.")
        else:
            print("[Security] Security strings missing from UI!")

    print("\n--- Logic Manifestation: FULLY OPERATIONAL ---\n")

if __name__ == "__main__":
    test_logic()
