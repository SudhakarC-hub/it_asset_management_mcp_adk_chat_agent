"""
Simple Streamlit Chat App for IT Asset Manager
Uses the ADK agent with MCP integration
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add parent directory to path to import the agent
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from it_asset_manager_app.agent import root_agent
import asyncio

# Page config
st.set_page_config(
    page_title="IT Asset Manager Chat",
    page_icon="💼",
    layout="centered"
)

# Title
st.title("💼 IT Asset Manager")
st.caption("Powered by Google ADK + MCP + Ollama Mistral")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar with status
with st.sidebar:
    st.header("⚙️ System Status")
    
    st.success("✅ ADK Agent Active")
    st.caption("Agent: it_asset_manager")
    
    st.success("✅ MCP Server Connected")
    st.caption("http://localhost:8002/mcp")
    
    st.success("✅ Ollama Mistral")
    st.caption("http://localhost:11434")
    
    st.divider()
    
    st.subheader("💡 Try These Commands")
    st.code("List all assets", language="text")
    st.code("Add asset id 10, name iPad Pro, owner Sarah", language="text")
    st.code("Show me the inventory", language="text")
    
    st.divider()
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me about IT assets..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Call the ADK agent
                async def get_response():
                    response = await root_agent.generate_async(prompt)
                    return response.text if hasattr(response, 'text') else str(response)
                
                response_text = asyncio.run(get_response())
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                
            except Exception as e:
                error_msg = f"⚠️ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
