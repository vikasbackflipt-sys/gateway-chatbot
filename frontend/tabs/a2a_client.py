import streamlit as st
import logging
import uuid
import json

from backend.api_client import send_message
from backend.multi_agent_orchestrator import run_multi_agent

logger = logging.getLogger("gateway-ui")

def render_a2a_client():

    st.subheader("Chat")

    # -------------------------------
    # DISPLAY CHAT HISTORY
    # -------------------------------
    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            if message["role"] == "assistant":

                try:
                    parsed = json.loads(message["content"])

                    agent_lookup = {
                        a["name"].lower(): a["name"]
                        for a in st.session_state.agent_configs
                    }

                    for item in parsed:

                        agent_name = item.get("agent", "").lower()
                        agent_response = item.get("response", "")

                        display_name = agent_lookup.get(
                            agent_name, agent_name.title()
                        )

                        st.markdown("---")

                        with st.expander(
                            f"{display_name} Response", expanded=True
                        ):
                            st.markdown(agent_response)

                except Exception:
                    st.markdown(message["content"])

            else:
                st.markdown(message["content"])

    # -------------------------------
    # CHAT INPUT
    # -------------------------------
    col1, col2 = st.columns([9, 1])

    with col2:
        if st.button("🗑", help="Clear chat history"):
            logger.info("Chat cleared by user")
            st.session_state.messages = []
            st.rerun()
    user_prompt = st.chat_input("Ask something...")

    if user_prompt:

        request_id = str(uuid.uuid4())[:8]

        logger.info("[%s] User query received: %s", request_id, user_prompt)

        if not st.session_state.config_saved:
            st.error("Please configure and save configuration first.")
            return

        logger.info(
            "[%s] UI configuration loaded | agent_mode=%s | agents=%s",
            request_id,
            st.session_state.agent_mode,
            [a["name"] for a in st.session_state.agent_configs]
        )

        # Store user message
        st.session_state.messages.append(
            {"role": "user", "content": user_prompt}
        )

        # -------------------------------
        # CALL BACKEND
        # -------------------------------
        with st.spinner("Thinking..."):

            if st.session_state.agent_mode == "Single Agent Client":

                agent = st.session_state.agent_configs[0]

                logger.info(
                    "[%s] Sending request to single agent | agent=%s",
                    request_id,
                    agent["name"]
                )

                response = send_message(
                    user_prompt,
                    agent["url"],
                    agent["headers"],
                    st.session_state.client_crt,
                    st.session_state.client_key
                )

            else:

                logger.info(
                    "[%s] Sending request to multi-agent orchestrator",
                    request_id
                )

                response = run_multi_agent(
                    user_prompt,
                    st.session_state.agent_configs,
                    st.session_state.groq_api_key,
                    st.session_state.client_crt,
                    st.session_state.client_key,
                    request_id=request_id
                )

        logger.info("[%s] Response received from backend", request_id)

        # Store assistant message
        st.session_state.messages.append(
            {"role": "assistant", "content": response}
        )

        logger.info("[%s] Stored response in chat history", request_id)

        st.rerun()