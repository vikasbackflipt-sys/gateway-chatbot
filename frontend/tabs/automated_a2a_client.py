import streamlit as st
import logging
import os

logger = logging.getLogger("gateway-ui")


def render_automated_a2a_client():

    st.subheader("Run agentic automation:")

    col1, col2 = st.columns([4,1])

    with col2:
        run_button = st.button("Run")

    if run_button:

        logger.info("Agentic automation triggered")

        if not st.session_state.get("automation_config_saved"):
            st.error("Please configure automation settings first.")
            return

        st.success("Automation started (placeholder).")

    render_automation_sidebar()


def render_automation_sidebar():

    with st.sidebar:

        st.markdown("---")
        st.header("Automated A2A Configuration")

        agent_url = st.text_input(
            "A2A Agent URL",
            key="automation_agent_url"
        )

        poet_email = st.text_input(
            "Lumen Poet Email",
            key="automation_poet_email"
        )

        poet_password = st.text_input(
            "Lumen Poet Password",
            type="password",
            key="automation_poet_password"
        )

        x_client_id = st.text_input(
            "X-Client-ID",
            value="teste.client.com",
            key="automation_x_client_id"
        )

        groq_key = st.text_input(
            "LLM Groq Key",
            type="password",
            key="automation_groq_key"
        )

        header_name = st.text_input(
            "Header Name",
            value="Authorization",
            key="automation_header_name"
        )

        header_value = st.text_input(
            "Header Value",
            type="password",
            key="automation_header_value"
        )

        st.markdown("### Certificates")

        uploaded_crt = st.file_uploader(
            "Upload Client Certificate (.crt)",
            type=["crt", "pem"],
            key="automation_crt"
        )

        uploaded_key = st.file_uploader(
            "Upload Client Key (.key)",
            type=["key", "pem"],
            key="automation_key"
        )

        save_button = st.button("Save Automation Configuration")

        if save_button:

            logger.info("Saving automated client configuration")

            if not agent_url:
                st.error("Agent URL is required.")
                return

            if not poet_email or not poet_password:
                st.error("Poet credentials required.")
                return

            if not uploaded_crt or not uploaded_key:
                st.error("Certificates required.")
                return

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

            st.session_state.automation_config = {
                "agent_url": agent_url,
                "email": poet_email,
                "password": poet_password,
                "groq_key": groq_key,
                "headers": headers,
                "client_crt": client_crt,
                "client_key": client_key
            }

            st.session_state.automation_config_saved = True

            st.success("Automation configuration saved.")

            logger.info("Automation configuration saved successfully")