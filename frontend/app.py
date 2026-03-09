import streamlit as st
import sys
import os
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.api_client import send_message


# =========================
# LOGGER SETUP
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger("gateway-ui")


# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Gateway Client",
    layout="wide"
)

logger.info("Gateway UI started")

st.title("Gateway Client Interface")


# =========================
# TABS
# =========================

tab1, tab2 = st.tabs(["A2A Client", "MCP Client"])


# =========================
# SESSION STATE INIT
# =========================

if "config_saved" not in st.session_state:
    st.session_state.config_saved = False

if "messages" not in st.session_state:
    st.session_state.messages = []


# =========================
# SIDEBAR CONFIGURATION
# =========================

with st.sidebar:

    st.header("Configuration")

    url = st.text_input("A2A Agent URL")

    x_client_id = st.text_input(
        "X-Client-ID",
        value="teste.client.com"
    )

    header_name = st.text_input(
        "Header Name",
        value="Authorization"
    )

    header_value = st.text_input(
        "Header Value",
        type="password"
    )

    st.markdown("### Certificates")

    uploaded_crt = st.file_uploader(
        "Upload Client Certificate (.crt)",
        type=["crt", "pem"]
    )

    uploaded_key = st.file_uploader(
        "Upload Client Key (.key)",
        type=["key", "pem"]
    )

    save_config = st.button("Save Configuration")

    if save_config:

        logger.info("User clicked Save Configuration")

        if not url:
            logger.warning("Agent URL missing")
            st.error("A2A Agent URL is required.")

        elif not header_name or not header_value:
            logger.warning("Header configuration missing")
            st.error("Header name and header value are required.")

        elif not uploaded_crt or not uploaded_key:
            logger.warning("Certificates not uploaded")
            st.error("Both client certificate and client key must be uploaded.")

        else:

            os.makedirs("temp_certs", exist_ok=True)

            client_crt = os.path.join("temp_certs", uploaded_crt.name)
            client_key = os.path.join("temp_certs", uploaded_key.name)

            with open(client_crt, "wb") as f:
                f.write(uploaded_crt.getbuffer())

            with open(client_key, "wb") as f:
                f.write(uploaded_key.getbuffer())

            headers = {
                "Content-Type": "application/json",
                "X-Client-ID": x_client_id,
                header_name: header_value
            }

            st.session_state.client_crt = client_crt
            st.session_state.client_key = client_key
            st.session_state.url = url
            st.session_state.headers = headers

            st.session_state.config_saved = True

            logger.info("Configuration saved successfully")

            st.success("Configuration saved successfully.")


# =========================
# A2A CLIENT TAB
# =========================

with tab1:

    st.subheader("Chat")

    if st.button("Clear Chat"):
        logger.info("Chat cleared by user")
        st.session_state.messages = []
        st.rerun()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = st.chat_input("Ask something...")

    if user_prompt:

        logger.info("User sent message to agent")

        if not st.session_state.config_saved:
            logger.warning("User attempted message without configuration")
            st.error("Please configure and save the configuration first.")

        else:

            with st.chat_message("user"):
                st.markdown(user_prompt)

            st.session_state.messages.append(
                {"role": "user", "content": user_prompt}
            )

            with st.spinner("Thinking..."):

                logger.info("Sending message to backend API")

                response = send_message(
                    user_prompt,
                    st.session_state.url,
                    st.session_state.headers,
                    st.session_state.client_crt,
                    st.session_state.client_key
                )

            with st.chat_message("assistant"):
                st.markdown(response)

            st.session_state.messages.append(
                {"role": "assistant", "content": response}
            )

            logger.info("Agent response displayed")


# =========================
# MCP CLIENT TAB
# =========================

with tab2:
    st.subheader("MCP Client")
    logger.info("MCP tab accessed")
    st.info("MCP Client UI will be implemented here.")