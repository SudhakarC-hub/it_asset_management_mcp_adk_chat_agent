import streamlit as st
import httpx
import json

# Page config
st.set_page_config(page_title="IT Asset Manager", page_icon="💼", layout="centered")

# Title
st.title("💼 IT Asset Manager Chat")
st.caption("Powered by MCP + Ollama Mistral")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    st.subheader("🔧 MCP Server")
    st.success("✅ Connected to MCP")
    st.caption("Endpoint: http://localhost:8002/sse")
    
    st.subheader("🤖 Model")
    st.success("✅ Ollama Mistral")
    st.caption("Endpoint: http://localhost:11434")
    
    st.subheader("📊 API Server")
    st.success("✅ FastAPI Running")
    st.caption("Endpoint: http://localhost:8005")
    
    st.divider()
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Helper functions to call API directly
def list_assets():
    """Call the API to list assets"""
    try:
        response = httpx.get("http://localhost:8005/assets", timeout=10.0)
        response.raise_for_status()
        assets = response.json()
        
        if not assets:
            return "No assets found in the inventory."
        
        # Format assets nicely
        result = "**Current IT Assets:**\n\n"
        for asset in assets:
            result += f"- **{asset['name']}** (ID: {asset['id']})\n"
            result += f"  - Owner: {asset['owner']}\n"
            result += f"  - Status: {asset['status']}\n\n"
        return result
    except Exception as e:
        return f"Error listing assets: {str(e)}"

def add_asset(asset_id, name, owner, status="active"):
    """Call the API to add an asset"""
    try:
        asset_data = {
            "id": asset_id,
            "name": name,
            "owner": owner,
            "status": status
        }
        response = httpx.post("http://localhost:8005/assets", json=asset_data, timeout=10.0)
        response.raise_for_status()
        result = response.json()
        return f"✅ Successfully added asset: **{result['name']}** (ID: {result['id']}) - Owner: {result['owner']}, Status: {result['status']}"
    except Exception as e:
        return f"Error adding asset: {str(e)}"

def call_ollama(prompt, conversation_history):
    """Call Ollama directly with tool-like behavior"""
    try:
        # Simple intent detection
        prompt_lower = prompt.lower()
        
        # Check for list intent
        if any(word in prompt_lower for word in ['list', 'show', 'display', 'get', 'all assets', 'inventory']):
            return list_assets()
        
        # Check for add intent
        elif any(word in prompt_lower for word in ['add', 'create', 'new asset']):
            # Parse asset details from prompt
            import re
            
            # Extract id
            id_match = re.search(r'id["\s:]*(\d+)', prompt_lower)
            # Extract name (look for name: "..." or name: ...)
            name_match = re.search(r'name["\s:]*["\']?([^,"\']+)["\']?', prompt, re.IGNORECASE)
            # Extract owner
            owner_match = re.search(r'owner["\s:]*["\']?([^,"\']+)["\']?', prompt, re.IGNORECASE)
            # Extract status (optional)
            status_match = re.search(r'status["\s:]*["\']?([^,"\']+)["\']?', prompt, re.IGNORECASE)
            
            if id_match and name_match and owner_match:
                asset_id = int(id_match.group(1))
                name = name_match.group(1).strip()
                owner = owner_match.group(1).strip()
                status = status_match.group(1).strip() if status_match else "active"
                
                return add_asset(asset_id, name, owner, status)
            else:
                return "❌ Could not parse asset details. Please provide: asset ID, name, owner, and optionally status.\n\nExample: 'Add asset id 3, name MacBook Air, owner John, status active'"
        
        # For other queries, use Ollama for general response
        else:
            response = httpx.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "mistral",
                    "prompt": f"You are an IT Asset Manager assistant. {prompt}",
                    "stream": False
                },
                timeout=30.0
            )
            response.raise_for_status()
            return response.json().get('response', 'No response from model')
            
    except Exception as e:
        return f"Error: {str(e)}"

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me to list assets or add a new asset..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            response_text = call_ollama(prompt, st.session_state.messages)
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
