import streamlit as st
import os
import sys
import json
from pathlib import Path

# Add brand-engine directory to path
BRAND_ENGINE_DIR = Path(__file__).parent.parent
sys.path.append(str(BRAND_ENGINE_DIR))

# Also add the actual root for scraping context
ROOT_DIR = BRAND_ENGINE_DIR.parent

from brand_brain.synthesis import BrandSynthesisEngine
from brand_brain.engine import BrandContentEngine
from brand_brain.orchestrator import MasterOrchestrator

st.set_page_config(page_title="Phoenix Master Terminal", page_icon="🧬", layout="wide")

# Initialize Orchestrator
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = MasterOrchestrator(str(ROOT_DIR))
    # Auto-integrate requested agents
    st.session_state.orchestrator.integrate_agent("creative-ai-assistant", "https://github.com/hermz580/creative-ai-assistant.git")
    st.session_state.orchestrator.integrate_agent("agenticSeek", "https://github.com/Fosowl/agenticSeek.git")
    st.session_state.orchestrator.integrate_agent("Open-AutoGLM", "https://github.com/zai-org/Open-AutoGLM.git")

orch = st.session_state.orchestrator

# Premium Theme - Obsidian & Zinc with Pulse
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'JetBrains Mono', monospace;
    }
    
    .stApp {
        background-color: #0a0a0b;
        color: #d4d4d8;
    }
    
    .stSidebar {
        background-color: #111113 !important;
        border-right: 1px solid #222 !important;
    }
    
    .bucket-card {
        background: #18181b;
        padding: 24px;
        border-left: 4px solid #d4d4d8;
        border-radius: 8px;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    
    .agent-tag {
        background: #27272a;
        color: #a1a1aa;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        margin: 4px;
        display: inline-block;
        border: 1px solid #3f3f46;
    }
    
    h1, h2, h3 {
        color: #f4f4f5 !important;
        letter-spacing: -0.02em;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        color: #71717a;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        color: #f4f4f5 !important;
        border-bottom-color: #f4f4f5 !important;
    }

    div.stButton > button:first-child {
        background: white;
        color: black;
        border-radius: 4px;
        font-weight: bold;
        border: none;
        width: 100%;
        transition: 0.2s ease;
    }

    div.stButton > button:first-child:hover {
        background: #d4d4d8;
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🧬 Phoenix Master Terminal")
st.text("Autonomous Multi-Root Intelligence Engine v2.0")

# Sidebar: Discovery & Intelligence
with st.sidebar:
    st.header("📍 Knowledge Roots")
    new_path = st.text_input("Ingest Path", placeholder="e.g. C:/Users/HermanHarp/creative-ai-assistant")
    if st.button("Add to Brain"):
        if new_path:
            orch.add_discovery_path(new_path)
            st.success("Path added to discovery queue.")
    
    st.write("---")
    st.write("Active Paths:")
    for p in orch.discovery_paths:
        st.caption(f"📁 `{Path(p).name}`")

    st.header("🤖 Active Agents")
    for name, data in orch.vbrain.get("agent_integrations", {}).items():
        st.markdown(f"<div class='agent-tag'>{name}</div>", unsafe_allow_html=True)

# Main Terminal Tabs
tab1, tab2, tab3 = st.tabs(["🔮 Manifest", "📦 The Bucket", "📊 Intelligence Log"])

with tab1:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### Strategy Synthesis")
        st.write("Synchronize all knowledge roots and manifest the brand's next move.")
        if st.button("🚀 EXECUTE FULL SYNC"):
            with st.spinner("Machine Learning in progress... finger-printing filesystems..."):
                orch.learn()
                manifest = orch.synth.manifest_brand()
                st.session_state['manifestation'] = manifest
    
    if 'manifestation' in st.session_state:
        m = st.session_state['manifestation']
        st.divider()
        st.subheader("Current Manifest")
        st.json(m)

with tab2:
    st.header("📥 The Drop Bucket")
    st.markdown(f"**Drop new assets here:** `{orch.bucket_path}`")
    st.caption("Anything dropped here will be processed autonomously using your brand context.")
    
    if st.button("⚙️ PROCESS PENDING ASSETS"):
        with st.spinner("Analyzing bucket contents..."):
            actions = orch.process_bucket()
            st.session_state['bucket_actions'] = actions

    if 'bucket_actions' in st.session_state:
        actions = st.session_state['bucket_actions']
        if isinstance(actions, str):
            st.info(actions)
        else:
            for act in actions:
                st.markdown(f"""
                    <div class='bucket-card'>
                        <h4 style='margin-top:0'>📦 Action for: {act['asset']}</h4>
                        <div style='font-size:0.9rem; line-height:1.6;'>
                            {act['strategy']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

with tab3:
    st.header("📊 V-Brain Context Map")
    if orch.vbrain.get("context_map"):
        for path, data in orch.vbrain["context_map"].items():
            with st.expander(f"Context Fingerprint: {Path(path).name}"):
                st.write(data)
    else:
        st.warning("No context learned yet. Hit 'Execute Full Sync' in the Manifest tab.")

st.sidebar.divider()
st.sidebar.caption("Phoenix Unbound: Sovereignty Through Intelligence")
