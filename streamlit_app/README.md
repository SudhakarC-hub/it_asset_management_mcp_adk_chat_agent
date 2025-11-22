# Streamlit Chat App

A simple web UI for the IT Asset Manager using Streamlit.

## Running the App

Make sure all services are running first:

1. **Terminal 1**: FastAPI Server
   ```bash
   python swagger_api/api_server.py
   ```

2. **Terminal 2**: MCP Server
   ```bash
   python mcp_servers/mcp_server.py
   ```

3. **Terminal 3**: Streamlit App
   ```bash
   streamlit run streamlit_app/app.py
   ```

The app will open in your browser at http://localhost:8501

## Features

- 💬 Chat interface for natural language interaction
- 🤖 Uses the same ADK agent as `adk run`
- 📊 Real-time system status in sidebar
- 🗑️ Clear chat history button
- 💡 Example commands

## How It Works

The Streamlit app imports and uses the same `root_agent` from `it_asset_manager_app/agent.py`, ensuring consistent behavior across CLI and web interfaces.
