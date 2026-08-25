"""
Chatbot Interactive UI Component.
"""
import streamlit as st
from typing import Dict, Any
from chatbot.chatbot_engine import process_chat_message

def render_embedded_chatbot(live_context: Dict[str, Any], key_suffix: str = "main"):
    """Renders interactive conversational assistant."""
    st.markdown("### 🤖 Environmental Intelligence AI Assistant")
    st.caption("Ask questions about current AQI, weather, pollutants, forecasts, health safety, or reduction tips.")
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": f"Hello! 👋 I am your Environmental Intelligence Assistant. I am currently monitoring **{live_context.get('city', 'Delhi')}** (AQI: {live_context.get('aqi', 'N/A')}, {live_context.get('aqi_category', '')}). How can I help you today?"}
        ]
        
    # Quick query chips
    st.markdown("##### 💡 Suggested Questions:")
    quick_cols = st.columns(4)
    preset_query = None
    if quick_cols[0].button("🌫️ Current AQI & Drivers", key=f"q1_{key_suffix}", use_container_width=True):
        preset_query = "What is my current AQI and which pollutant is driving it?"
    if quick_cols[1].button("🏃 Is it safe outside?", key=f"q2_{key_suffix}", use_container_width=True):
        preset_query = "Is it safe to go for a run outside right now?"
    if quick_cols[2].button("🔮 What's the forecast?", key=f"q3_{key_suffix}", use_container_width=True):
        preset_query = "What will the AQI be over the next 24 hours?"
    if quick_cols[3].button("🌱 How to reduce pollution?", key=f"q4_{key_suffix}", use_container_width=True):
        preset_query = "How can we reduce air pollution in this city?"
        
    # Render chat message list
    chat_container = st.container(height=350)
    with chat_container:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
    user_input = st.chat_input("Type your environmental question here...", key=f"chat_input_{key_suffix}")
    active_prompt = preset_query or user_input
    
    if active_prompt:
        st.session_state.chat_history.append({"role": "user", "content": active_prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(active_prompt)
            with st.chat_message("assistant"):
                resp = process_chat_message(active_prompt, st.session_state.chat_history, live_context)
                st.markdown(resp)
        st.session_state.chat_history.append({"role": "assistant", "content": resp})
        st.rerun()
