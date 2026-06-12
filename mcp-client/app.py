import os
import streamlit as st

# Inject Streamlit secrets into environment variables so SDKs can discover them
try:
    for key in st.secrets:
        os.environ[key] = str(st.secrets[key])
except Exception:
    pass

import asyncio
import json
import requests
from agent import run

st.set_page_config(page_title="Jobs AI Assistant", layout="wide")

import sys
import subprocess
import time
from pathlib import Path

MCP_HEALTH_URL = "http://localhost:8000/health"


@st.cache_data(ttl=10)
def check_server() -> bool:
    try:
        r = requests.get(MCP_HEALTH_URL, timeout=2)
        return r.status_code == 200
    except Exception:
        return False


# Auto-start FastAPI backend if offline (for Streamlit Cloud or single-process local run)
server_dir = Path(__file__).resolve().parent.parent / "mcp-server"
log_path = server_dir / "uvicorn.log"

if not check_server():
    if (server_dir / "main.py").exists():
        try:
            # We open the log file to capture standard output/error from uvicorn
            with open(log_path, "w") as log_file:
                subprocess.Popen(
                    [sys.executable, "-m", "uvicorn", "main:app", "--port", "8000"],
                    cwd=str(server_dir),
                    stdout=log_file,
                    stderr=log_file
                )
            # Give the server 4 seconds to spin up
            time.sleep(4)
            # Clear Streamlit cache to force a fresh health check check
            st.cache_data.clear()
        except Exception as e:
            st.sidebar.error(f"Failed to auto-start backend server: {e}")


st.title("Jobs AI Assistant")
st.caption("Powered by Claude + MCP · Queries the jobs database via SSE tool calls")

server_ok = check_server()
if server_ok:
    st.success("🟢  MCP Server connected · localhost:8000")
else:
    st.error("🔴  MCP Server offline")
    if log_path.exists():
        with open(log_path, "r") as log_file:
            log_content = log_file.read()
        if log_content:
            st.warning("⚠️ FastAPI Background Server Logs:")
            st.code(log_content)
        else:
            st.warning("⚠️ Uvicorn background process initiated, but the log file is empty. Check if port 8000 is occupied.")

# Sidebar configuration panel
with st.sidebar:
    st.title("Settings ⚙️")
    model_name = st.selectbox(
        "Claude Model Selection",
        options=[
            "claude-3-5-sonnet-20241022",
            "claude-3-5-sonnet-20240620",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
        ],
        index=0,
        help="Select the exact Anthropic Claude model version to use."
    )

left, right = st.columns(2, gap="large")

with left:
    st.subheader("Query")
    query = st.text_input(
        "Ask about jobs...",
        placeholder="Show me senior React jobs in Bangalore",
        disabled=not server_ok,
    )
    ask_clicked = st.button("Ask", disabled=not server_ok or not query)

    if ask_clicked and query:
        with st.spinner("Agent thinking..."):
            response_text, tool_log = asyncio.run(run(query, model_name=model_name))
        st.session_state["response_text"] = response_text
        st.session_state["tool_log"] = tool_log

    if "response_text" in st.session_state:
        st.subheader("Response")
        if st.session_state["response_text"]:
            st.markdown(st.session_state["response_text"])
        else:
            st.error("No response — see the MCP Inspector for error details.")

with right:
    st.subheader("MCP Tool Inspector")

    if not server_ok:
        st.warning("Start App A to see live tool calls here.")
    else:
        st.info("Tools are discovered dynamically from the MCP server at runtime.")

    if "tool_log" in st.session_state:
        log = st.session_state["tool_log"]
        if not log:
            st.caption("No tool calls were made for this query.")
        for entry in log:
            if "error" in entry:
                st.error(entry["error"])
            else:
                st.markdown(f"**▶ Tool Call: `{entry['tool']}`**")
                st.code(json.dumps(entry["input"], indent=2), language="json")
                st.markdown("**◀ Tool Result:**")
                output = entry["output"]
                display = output if len(output) <= 600 else output[:600] + "\n... (truncated)"
                st.code(display, language="json")
                st.divider()
