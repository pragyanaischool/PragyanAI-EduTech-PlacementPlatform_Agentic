import streamlit as st
from src.rag_engine import handle_placement_chat

def render_chat_interface(user_role: str, user_context: dict = None, height: int = 400):
    """Renders a standard, reusable chat interface for any dashboard view."""
    st.subheader(f" {user_role} Placement Copilot")
    st.caption("Ask queries about schedules, candidate rounds, package distributions, or selection criteria in plain English.")

    # Unique chat history container per role
    chat_key = f"chat_history_{user_role.lower().replace(' ', '_')}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = [
            {"role": "assistant", "content": f"👋 Hello! I am your **{user_role} AI Copilot**. How can I help you today?"}
        ]

    # Render Messages
    for msg in st.session_state[chat_key]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input
    if user_prompt := st.chat_input(f"Ask a placement query as {user_role}..."):
        st.session_state[chat_key].append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        response = handle_placement_chat(user_prompt, user_role=user_role, user_context=user_context)
        st.session_state[chat_key].append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
