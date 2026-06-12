import streamlit as st
import json
import time

st.set_page_config(
    page_title="MCP Learning Portal & Simulator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Custom CSS
st.markdown("""
<style>
    .reportview-container { margin-top: -2em; }
    .stDeployButton { display:none; }
    .mcp-card {
        background-color: rgba(49, 51, 63, 0.05);
        border: 1px solid rgba(49, 51, 63, 0.1);
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .mcp-badge {
        background-color: #00CC66;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
        display: inline-block;
    }
    .console-header {
        background-color: #1e1e1e;
        color: #00FF00;
        padding: 8px 12px;
        border-radius: 6px 6px 0 0;
        font-family: monospace;
        font-size: 0.85rem;
        border-bottom: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# Define mock databases for simulator
MOCK_WEATHER_DB = {
    "bangalore": {"temp": "28°C", "condition": "Sunny", "humidity": "60%"},
    "chennai": {"temp": "34°C", "condition": "Humid & Cloudy", "humidity": "85%"},
    "mumbai": {"temp": "31°C", "condition": "Heavy Rain", "humidity": "90%"},
    "delhi": {"temp": "40°C", "condition": "Hot & Dry", "humidity": "25%"}
}

MOCK_JOBS_DB = [
    {"id": 101, "title": "Data Engineer", "company": "TechCorp", "location": "Bangalore", "salary": "18 LPA"},
    {"id": 102, "title": "GenAI Architect", "company": "FutureAI", "location": "Mumbai", "salary": "32 LPA"},
    {"id": 103, "title": "Python Developer", "company": "SaaSify", "location": "Chennai", "salary": "12 LPA"}
]

# Title & Overview
st.title("🎓 Model Context Protocol (MCP) Academy")
st.caption("An interactive playground to learn, simulate, and practice LLM-to-tool connections.")

# Sidebar Information
with st.sidebar:
    st.image("https://raw.githubusercontent.com/modelcontextprotocol/mcp/main/logo.png", width=80)
    st.header("MCP Quick Ref 📝")
    st.markdown("""
    * **Host**: The orchestrator (e.g., Claude Desktop, Streamlit client).
    * **Client**: Opens a session and coordinates between LLM and Server.
    * **Server**: Exposes tools/resources (e.g., DBs, APIs, local directories).
    * **Transport**: The wire format (`Stdio` for local processes, `SSE` for web servers).
    """)
    st.divider()
    st.info("💡 Tip: Go to **🎮 2. Interactive Simulator** to see how client-server JSON messages fly over the wire!")

# Navigation Tabs
tab1, tab2, tab3 = st.tabs(["📖 1. What is MCP?", "🎮 2. Interactive Simulator", "📝 3. Student Practice"])

# ==========================================================
# TAB 1: LEARN
# ==========================================================
with tab1:
    st.header("Understanding Model Context Protocol")
    
    col1, col2 = st.columns([3, 2], gap="large")
    
    with col1:
        st.subheader("🔌 The 'USB Port' Analogy")
        st.markdown("""
        Before MCP, if you wanted an LLM to read a database, you had to write a custom backend, hardcode the API schemas, write custom parsing code for the LLM, and update it every time you changed the database.
        
        **MCP solves this by acting like a USB port for LLM models.** 
        * **One Standard**: Instead of writing separate connectors, developers build an **MCP Server** that exposes tools.
        * **Decoupled Client**: The **MCP Client** reads the tools and tells the LLM what it can do. The LLM can access anything plugged into the client!
        """)
        
        st.subheader("🔄 How the Protocol Flows")
        st.markdown("""
        1. **Handshake**: The client connects to the server and negotiates protocol version (`initialize`).
        2. **Discovery**: The client requests available tools (`list_tools`). The server responds with their **JSON Schema** parameters.
        3. **LLM Decision**: The user asks a question. The LLM inspects the schemas and decides which tool to call.
        4. **Execution**: The client executes the tool on the server (`call_tool`) and sends the results back to the LLM.
        5. **Final Output**: The LLM compiles the data into a human-readable response.
        """)
        
    with col2:
        st.markdown('<div class="mcp-card">', unsafe_allow_html=True)
        st.markdown("### 🏛️ The Three-Agent Architecture")
        st.image("https://modelcontextprotocol.io/img/architecture.png", caption="MCP Architecture (Host, Client, Server)", use_container_width=True)
        st.markdown("""
        * **Host**: Application where the user interacts (like Claude Desktop or this Streamlit UI).
        * **Client**: The library maintaining connection to servers and handling the LLM conversation loop.
        * **Server**: The lightweight process providing tools, resources, and prompts.
        """)
        st.markdown('</div>', unsafe_allow_html=True)


# ==========================================================
# TAB 2: INTERACTIVE PLAYGROUND / SIMULATOR
# ==========================================================
with tab2:
    st.header("🎮 MCP Live Protocol Simulator")
    st.markdown("Step through the protocol execution and watch the exact JSON requests/responses generated at each layer.")

    # Simulator State Setup
    if "sim_step" not in st.session_state:
        st.session_state["sim_step"] = 0
    if "sim_tool" not in st.session_state:
        st.session_state["sim_tool"] = "Weather API"
    if "sim_query" not in st.session_state:
        st.session_state["sim_query"] = "What's the weather like in Chennai?"
    if "sim_logs" not in st.session_state:
        st.session_state["sim_logs"] = []

    # Reset button
    def reset_sim():
        st.session_state["sim_step"] = 0
        st.session_state["sim_logs"] = []
        
    col_ctrl, col_wire = st.columns([1, 1], gap="medium")
    
    with col_ctrl:
        st.subheader("Simulator Controls")
        
        # Configure Mock Tool
        tool_choice = st.selectbox(
            "Select Server-Side Tool to Expose:",
            options=["Weather API", "Jobs Database Search"],
            index=0 if st.session_state["sim_tool"] == "Weather API" else 1,
            on_change=reset_sim
        )
        st.session_state["sim_tool"] = tool_choice
        
        # Configure Query
        default_query = "What's the weather like in Chennai?" if tool_choice == "Weather API" else "Find me Data Engineer jobs in Bangalore"
        query_val = st.text_input("User Prompt:", value=default_query)
        if query_val != st.session_state["sim_query"]:
            st.session_state["sim_query"] = query_val
            reset_sim()
            
        st.divider()
        
        # Stepper Buttons
        step = st.session_state["sim_step"]
        
        if step == 0:
            st.info("ℹ️ Step 1: Initialize the connection handshake.")
            if st.button("🔌 1. Initialize Handshake (Connect)"):
                st.session_state["sim_step"] = 1
                st.session_state["sim_logs"].append({
                    "direction": "Client ➡️ Server",
                    "method": "initialize",
                    "payload": {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "initialize",
                        "params": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {},
                            "clientInfo": {"name": "streamlit-mcp-edu-client", "version": "1.0.0"}
                        }
                    }
                })
                st.session_state["sim_logs"].append({
                    "direction": "Server ⬅️ Client",
                    "method": "initialize_response",
                    "payload": {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {
                                "tools": {"listChanged": False}
                            },
                            "serverInfo": {"name": "mock-mcp-edu-server", "version": "1.0.0"}
                        }
                    }
                })
                st.rerun()

        elif step == 1:
            st.info("ℹ️ Step 2: The client discovers what tools are exposed by the server.")
            if st.button("🔍 2. Discover Tools (list_tools)"):
                st.session_state["sim_step"] = 2
                
                # Setup tools response based on choice
                if tool_choice == "Weather API":
                    tools_list = [{
                        "name": "get_weather",
                        "description": "Fetch live weather data for a city",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "city": {"type": "string", "description": "Name of the city"}
                            },
                            "required": ["city"]
                        }
                    }]
                else:
                    tools_list = [{
                        "name": "search_jobs",
                        "description": "Search jobs database by keyword and location",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "Job title keyword"},
                                "location": {"type": "string", "description": "City filter"}
                            },
                            "required": ["query"]
                        }
                    }]
                
                st.session_state["sim_logs"].append({
                    "direction": "Client ➡️ Server",
                    "method": "tools/list",
                    "payload": {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "tools/list"
                    }
                })
                st.session_state["sim_logs"].append({
                    "direction": "Server ⬅️ Client",
                    "method": "tools/list_response",
                    "payload": {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "result": {"tools": tools_list}
                    }
                })
                st.rerun()

        elif step == 2:
            st.info("ℹ️ Step 3: LLM reads tools, decides to call the tool, and issues call_tool.")
            if st.button("🤖 3. LLM Decides & Calls Tool (call_tool)"):
                st.session_state["sim_step"] = 3
                
                # Setup call based on choice
                if tool_choice == "Weather API":
                    tool_args = {"city": "chennai"}
                    tool_output = MOCK_WEATHER_DB["chennai"]
                else:
                    tool_args = {"query": "Data Engineer", "location": "Bangalore"}
                    tool_output = [MOCK_JOBS_DB[0]] # Data Engineer in Bangalore
                    
                st.session_state["sim_logs"].append({
                    "direction": "Client ➡️ Server",
                    "method": "tools/call",
                    "payload": {
                        "jsonrpc": "2.0",
                        "id": 3,
                        "method": "tools/call",
                        "params": {
                            "name": "get_weather" if tool_choice == "Weather API" else "search_jobs",
                            "arguments": tool_args
                        }
                    }
                })
                st.session_state["sim_logs"].append({
                    "direction": "Server ⬅️ Client",
                    "method": "tools/call_response",
                    "payload": {
                        "jsonrpc": "2.0",
                        "id": 3,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(tool_output)
                                }
                            ]
                        }
                    }
                })
                st.rerun()

        elif step == 3:
            st.info("ℹ️ Step 4: The LLM receives the database output and generates the final answer.")
            if st.button("📝 4. Compile Final Answer"):
                st.session_state["sim_step"] = 4
                st.rerun()
                
        else:
            st.success("🎉 Simulation complete! The LLM successfully answered the query using the MCP server data.")
            if st.button("🔄 Restart Simulator"):
                reset_sim()
                st.rerun()

        # Display UI response matching current step
        st.subheader("💡 Host/UI View")
        if step >= 1:
            st.success("🟢 MCP Connected: localhost:8000")
        else:
            st.error("🔴 MCP Session Not Initialized")
            
        st.text_area("User Query", value=st.session_state["sim_query"], disabled=True)
        
        if step == 4:
            if tool_choice == "Weather API":
                st.write("**Agent Response:**")
                st.info("☀️ The weather in Chennai is currently **34°C** with **Humid & Cloudy** conditions and a relative humidity of 85%.")
            else:
                st.write("**Agent Response:**")
                st.info("💼 I found a **Data Engineer** job posting at **TechCorp** located in **Bangalore** with a salary of **18 LPA**.")
                
    with col_wire:
        st.subheader("📡 MCP Wire Protocol logs")
        st.markdown("Watch the JSON-RPC 2.0 messages passing over the transport layer:")
        
        if not st.session_state["sim_logs"]:
            st.caption("No logs yet. Click '1. Initialize Handshake' on the left to start.")
            
        for log in st.session_state["sim_logs"]:
            direction = log["direction"]
            method = log["method"]
            payload = log["payload"]
            
            st.markdown(f"<div class='console-header'>{direction} · Method: {method}</div>", unsafe_allow_html=True)
            st.code(json.dumps(payload, indent=2), language="json")


# ==========================================================
# TAB 3: STUDENT PRACTICE & EXERCISES
# ==========================================================
with tab3:
    st.header("📝 MCP Hands-On Practice")
    st.markdown("Test your understanding of the Model Context Protocol and JSON schema definitions.")
    
    exercise_type = st.radio(
        "Choose an Exercise:",
        ["1. Protocol Flow Ordering", "2. Interactive Tool Schema Builder", "3. MCP Concept Quiz"],
        horizontal=True
    )
    
    # ------------------------------------------------------
    # Exercise 1: Sequence Orderer
    # ------------------------------------------------------
    if exercise_type == "1. Protocol Flow Ordering":
        st.subheader("Exercise 1: Order the MCP Handshake Steps")
        st.markdown("Arrange the steps in the correct chronological sequence to connect a client to an MCP server:")
        
        steps = [
            "Client calls list_tools() to discover what functions the server supports.",
            "Client connects via SSE/Stdio and issues an initialize request.",
            "Client runs call_tool() sending parameters to the server.",
            "LLM reads the tools and user prompt, then decides which tool to use.",
            "Server executes the database/API query and returns content back to client."
        ]
        
        # Select box sequence
        pos_1 = st.selectbox("Position 1 (First Step):", ["-- Choose --"] + steps)
        pos_2 = st.selectbox("Position 2:", ["-- Choose --"] + steps)
        pos_3 = st.selectbox("Position 3:", ["-- Choose --"] + steps)
        pos_4 = st.selectbox("Position 4:", ["-- Choose --"] + steps)
        pos_5 = st.selectbox("Position 5 (Last Step):", ["-- Choose --"] + steps)
        
        if st.button("Check Sequence ✅"):
            if (pos_1 == steps[1] and 
                pos_2 == steps[0] and 
                pos_3 == steps[3] and 
                pos_4 == steps[2] and 
                pos_5 == steps[4]):
                st.success("🎉 Correct! You've mastered the exact protocol sequence flow!")
            else:
                st.error("❌ Incorrect sequence. Remember: Handshake first, then Discovery, then LLM reasoning, then Client execution, then Server database returns.")

    # ------------------------------------------------------
    # Exercise 2: Schema Builder
    # ------------------------------------------------------
    elif exercise_type == "2. Interactive Tool Schema Builder":
        st.subheader("Exercise 2: Construct a valid MCP Tool Schema")
        st.markdown("MCP servers expose tools to the LLM using **JSON Schema**. Complete the configuration below to define a `calculate_tax` tool:")
        
        tool_name = st.text_input("Tool Name:", value="calculate_tax", disabled=True)
        tool_desc = st.text_area("Description (what the LLM will see):", value="Calculates the income tax for a given salary amount.")
        
        col_param1, col_param2 = st.columns(2)
        with col_param1:
            param_name = st.text_input("Parameter 1 Name:", value="salary")
            param_type = st.selectbox("Parameter 1 Type:", ["string", "integer", "boolean", "array"])
        with col_param2:
            param_desc = st.text_input("Parameter Description:", value="The annual gross salary in USD")
            is_req = st.checkbox("Is this parameter required?", value=True)
            
        # Compile Schema
        schema = {
            "name": tool_name,
            "description": tool_desc,
            "inputSchema": {
                "type": "object",
                "properties": {
                    param_name: {
                        "type": param_type,
                        "description": param_desc
                    }
                },
                "required": [param_name] if is_req else []
            }
        }
        
        st.write("🔧 Generated MCP Tool Schema:")
        st.code(json.dumps(schema, indent=2), language="json")
        
        if st.button("Validate Schema 🔬"):
            if not param_name:
                st.error("Parameter name cannot be empty.")
            elif param_type != "integer":
                st.warning("⚠️ Warning: Salaries are numeric. While valid JSON, a model will behave better if you set Type to 'integer'.")
            else:
                st.success("✅ Perfect! This schema is standard-compliant and Claude can read it dynamically.")

    # ------------------------------------------------------
    # Exercise 3: Mini-Quiz
    # ------------------------------------------------------
    elif exercise_type == "3. MCP Concept Quiz":
        st.subheader("Exercise 3: Test Your MCP Knowledge")
        
        q1 = st.radio(
            "1. Which component is responsible for exposing tools and databases?",
            ["Host", "Client", "Server", "Transport"]
        )
        
        q2 = st.radio(
            "2. How does an MCP Client know what tools are available on the Server?",
            [
                "The developer must manually copy-paste the code schemas.",
                "It dynamically calls list_tools() at runtime to fetch the schemas.",
                "It reads a local config file on the client's hard drive."
            ]
        )
        
        q3 = st.radio(
            "3. Which wire format protocol is used for MCP messages?",
            ["gRPC", "GraphQL", "JSON-RPC 2.0", "WebSockets SOAP"]
        )
        
        q4 = st.radio(
            "4. What transport type is typically used for local desktop integrations (like Claude Desktop)?",
            ["Server-Sent Events (SSE)", "Stdio (Standard Input/Output)", "HTTP POST request polling"]
        )
        
        if st.button("Submit Quiz Answers 📋"):
            score = 0
            if q1 == "Server": score += 1
            if q2 == "It dynamically calls list_tools() at runtime to fetch the schemas.": score += 1
            if q3 == "JSON-RPC 2.0": score += 1
            if q4 == "Stdio (Standard Input/Output)": score += 1
            
            if score == 4:
                st.balloons()
                st.markdown('<div class="mcp-badge">🏆 MCP Certified Scholar (Score: 4/4)</div>', unsafe_allow_html=True)
                st.success("Perfect score! You have completely mastered the core concepts of the Model Context Protocol.")
            else:
                st.error(f"You scored {score}/4. Review the '1. What is MCP?' tab and try again!")
