import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.api_client import send_message

st.set_page_config(layout="wide")

st.title("Gateway Client Interface")

tab1, tab2 = st.tabs(["A2A Client", "MCP Client"])

# Initialize session state
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

        if not url:
            st.error("A2A Agent URL is required.")

        elif not header_name or not header_value:
            st.error("Header name and header value are required.")

        elif not uploaded_crt or not uploaded_key:
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

            st.success("Configuration saved successfully.")


# =========================
# A2A CLIENT TAB
# =========================
# =========================
# A2A CLIENT TAB
# =========================
# =========================
# A2A CLIENT TAB
# =========================

with tab1:

    st.subheader("Chat")

    # Clear Chat Button
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    # Ensure message storage exists
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 1️⃣ Render chat history FIRST
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 2️⃣ Place input at the bottom AFTER messages
    user_prompt = st.chat_input("Ask something...")

    # 3️⃣ Handle new input
    if user_prompt:

        if not st.session_state.config_saved:
            st.error("Please configure and save the configuration in the sidebar first.")

        else:
            # Show user message immediately
            with st.chat_message("user"):
                st.markdown(user_prompt)

            st.session_state.messages.append(
                {"role": "user", "content": user_prompt}
            )

            with st.spinner("Thinking..."):
                response = send_message(
                    user_prompt,
                    st.session_state.url,
                    st.session_state.headers,
                    st.session_state.client_crt,
                    st.session_state.client_key
                )

            # Show assistant response
            with st.chat_message("assistant"):
                st.markdown(response)

            st.session_state.messages.append(
                {"role": "assistant", "content": response}
            )

with tab2:
    st.subheader("MCP Client")
    st.info("MCP Client UI will be implemented here.")