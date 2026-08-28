import streamlit as st
from src.rag_engine import handle_placement_chat


def render_chat_interface(user_role: str, user_context: dict = None, height: int = 400):
    """
    Renders a unified, multi-turn conversational AI Copilot inside any Streamlit view.
    Maintains isolated role-specific conversation history in st.session_state.
    
    Parameters:
    ----------
    user_role : str
        The operational role (e.g., 'Student', 'Placement Head', 'Placement Team', 
        'Hiring Partner', 'Executive Board', 'PragyanAI Engine').
    user_context : dict, optional
        Contextual dictionary containing runtime metadata (e.g., {'student_id': 'STU0001'}).
    height : int, optional
        Display height constraint (defaults to 400px).
    """
    st.subheader(f"💬 {user_role} Placement Copilot")
    st.caption("Ask natural language queries regarding interview schedules, candidate pipeline stages, salary distributions, or selection criteria.")

    # Distinct conversation history session key per role
    chat_key = f"chat_history_{user_role.lower().replace(' ', '_')}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = [
            {
                "role": "assistant",
                "content": f"👋 Hello! I am your **{user_role} AI Copilot**. How can I assist you with placement telemetry, drive schedules, or candidate tracking today?"
            }
        ]

    # Quick Prompt Chips / Starters for User Convenience
    quick_queries = {
        "Student": [
            "What is my next round?",
            "When is Qualcomm drive and what is the package?",
            "Upcoming bootcamps",
            "What is the highest package secured?"
        ],
        "Placement Head": [
            "What is the current placement rate?",
            "Who cleared rounds in AIML?",
            "CSE placement stats",
            "Recruiter feedback on skill gaps"
        ],
        "Placement Team": [
            "Who cleared rounds in CSE?",
            "Upcoming bootcamps",
            "Why did candidates get selected at NVIDIA?",
            "What is the highest package secured?"
        ],
        "Hiring Partner": [
            "What is the current placement rate?",
            "AIML placement stats",
            "Recruiter feedback on skill gaps",
            "What is the highest package secured?"
        ],
        "Executive Board": [
            "What is the current placement rate?",
            "CSE placement stats",
            "ECE placement stats",
            "Why did candidates get selected at Google?"
        ],
        "PragyanAI Engine": [
            "What is the current placement rate?",
            "Recruiter feedback on skill gaps",
            "Why did candidates get selected at NVIDIA?",
            "Upcoming bootcamps"
        ]
    }

    # Render Suggestion Chips
    available_prompts = quick_queries.get(user_role, [
        "What is the current placement rate?",
        "Upcoming bootcamps",
        "What is the highest package secured?"
    ])

    st.markdown("**Suggested Quick Inquiries:**")
    chip_cols = st.columns(len(available_prompts))
    selected_quick_prompt = None

    for idx, prompt_text in enumerate(available_prompts):
        if chip_cols[idx].button(prompt_text, key=f"chip_{user_role}_{idx}", use_container_width=True):
            selected_quick_prompt = prompt_text

    st.markdown("---")

    # Render previous conversation history inside a container
    chat_container = st.container(height=height)
    with chat_container:
        for msg in st.session_state[chat_key]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Handle User Input (via standard chat_input or quick chip click)
    user_prompt = st.chat_input(
        f"Ask a query as {user_role} (e.g. 'Status of STU0001', 'Highest package', 'AIML stats')..."
    )

    prompt_to_process = selected_quick_prompt if selected_quick_prompt else user_prompt

    if prompt_to_process:
        # 1. Append & render user message
        st.session_state[chat_key].append({"role": "user", "content": prompt_to_process})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt_to_process)

        # 2. Compute response via RAG & Chat Router Engine
        with st.spinner("Analyzing placement telemetry & knowledge graph..."):
            response = handle_placement_chat(
                query=prompt_to_process,
                user_role=user_role,
                user_context=user_context
            )

        # 3. Append & render assistant message
        st.session_state[chat_key].append({"role": "assistant", "content": response})
        with chat_container:
            with st.chat_message("assistant"):
                st.markdown(response)

        # Trigger rerun to reflect updated conversation in state cleanly
        st.rerun()
