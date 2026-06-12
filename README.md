# 🎓 Model Context Protocol (MCP) Interactive Academy

An interactive, zero-setup learning platform designed to teach the **Model Context Protocol (MCP)**. This application runs completely **keyless and local** in a Streamlit container—allowing anyone to simulate real-time client-server protocol JSON exchanges and test their knowledge without needing LLM API keys or local database servers.

👉 **Live Demo**: [mcpserver-demo.streamlit.app](https://mcpserver-demo.streamlit.app/)

---

## 🔌 What is MCP?

The **Model Context Protocol (MCP)** is an open standard developed by Anthropic that connects AI models (like Claude) to external tools and data sources. Think of it as a **USB-C port for LLMs**: instead of writing custom API integration code for every tool, a server advertises its capabilities using a unified protocol schema, and the client plugs the tools directly into the LLM.

![MCP Architecture Diagram](mcp_architecture.png)

### Core Components of the Architecture:
1. **Host**: The user-facing application (e.g., Claude Desktop, Cursor editor, or this Streamlit UI).
2. **Client**: The session runner that coordinates LLM reasoning and server tool-calling.
3. **Server**: The tool and data provider (e.g., exposing a SQLite database, a weather API, or filesystem operations).
4. **Transport Layer**: The format of the wire communication (typically `Stdio` for local terminal subprocesses, or `SSE` (Server-Sent Events) over HTTP for remote services).

---

## 🎮 Features of the Interactive Simulator

The academy contains three main tabs designed for interactive training:

### 1. 📖 Learn Dashboard
* High-level diagrams explaining Host-Client-Server workflows.
* Explanations of core protocol primitives (`initialize`, `list_tools`, `call_tool`).

### 2. 🎮 Live Protocol Simulator
* **Expose Mock Tools**: Select between a **Weather API** or a **Jobs Database Search**.
* **Step-by-Step Execution**:
  * **🔌 1. Initialize Handshake**: Watch the client and server negotiate versions and capabilities over JSON-RPC 2.0.
  * **🔍 2. Discover Tools**: See how the client calls `list_tools` and retrieves the tool's JSON Schema.
  * **🤖 3. LLM Action**: Watch the LLM inspect parameters and request execution via a `call_tool` request.
  * **📝 4. Final Compilation**: Watch the client feed raw data back to the LLM and render the final formatted response.
* **Console Logger**: The right-hand panel displays the exact JSON payloads sent over the wire at each protocol step.

### 3. 📝 Hands-On Practice Center
* **Sequence Orderer**: Arrange the steps of the MCP connection handshake in the correct order.
* **Interactive JSON Schema Builder**: Match parameter names, descriptions, and data types to create a valid MCP tool schema with real-time syntax generation.
* **MCP Certification Quiz**: A 4-question interactive assessment covering transports, roles, and discovery. Earns a "Certified MCP Scholar" badge for a perfect score!

---

## 🚀 Running the App Locally

To run this learning portal on your local machine, follow these steps:

```bash
# 1. Clone the repository
git clone https://github.com/Anilmidna/MCPServer-demo.git

# 2. Navigate to the client directory
cd MCPServer-demo/mcp-client

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the Streamlit application
streamlit run app.py
```

Open your browser to **`http://localhost:8501`** and start practicing!
