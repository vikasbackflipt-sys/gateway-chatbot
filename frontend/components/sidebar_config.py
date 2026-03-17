import streamlit as st
import os
import logging
import requests

logger = logging.getLogger("gateway-ui")


def _fetch_agent_name_from_card(agent_url: str) -> str:
    """
    Fetch the agent's display name from its agent card at:
        <agent_url>/.well-known/agent.json
    No headers or certificates are required.
    """

    well_known_url = agent_url.rstrip("/") + "/.well-known/agent.json"

    try:
        response = requests.get(well_known_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        name = data.get("name", "").strip()
        return name
    except Exception as e:
        logger.info(
            "Failed to fetch agent name from card | base_url=%s | error=%s",
            agent_url,
            str(e),
        )
        return ""


def render_sidebar_config():

    logger.info("Rendering sidebar configuration")

    with st.sidebar:

        # Expand sidebar width + remove top padding
        st.markdown(
            """
            <style>
            section[data-testid="stSidebar"] {
                width: 900px !important;
                padding-top: 10px !important;
            }
            section[data-testid="stSidebar"][aria-expanded="true"] {
                width: 900px !important;
                min-width: 900px !important;
            }
            div[data-testid="stSidebarNav"] {
                margin-top: -30px;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        st.header("A2A Client Configuration")

        agent_mode = st.radio(
            "Client Mode",
            ["Single Agent Client", "Multi Agent Client"],
            key="agent_mode"
        )

        logger.info("Client mode selected: %s", agent_mode)

        # ------------------------------
        # Initialize session state
        # ------------------------------

        if "agent_urls" not in st.session_state:
            st.session_state.agent_urls = [""]
            logger.info("Initialized session state: agent_urls")

        if "agent_names" not in st.session_state:
            st.session_state.agent_names = [""]
            logger.info("Initialized session state: agent_names")

        if "agent_header_names" not in st.session_state:
            st.session_state.agent_header_names = ["Authorization"]
            logger.info("Initialized session state: agent_header_names")

        if "agent_header_values" not in st.session_state:
            st.session_state.agent_header_values = [""]
            logger.info("Initialized session state: agent_header_values")

        if "agent_added" not in st.session_state:
            # Align agent_added length with existing agent_urls (for backward compatibility)
            st.session_state.agent_added = [False] * len(st.session_state.agent_urls)
            logger.info("Initialized session state: agent_added")
        else:
            # Ensure agent_added is always the same length as agent_urls
            if len(st.session_state.agent_added) < len(st.session_state.agent_urls):
                st.session_state.agent_added.extend(
                    [False] * (len(st.session_state.agent_urls) - len(st.session_state.agent_added))
                )
            elif len(st.session_state.agent_added) > len(st.session_state.agent_urls):
                st.session_state.agent_added = st.session_state.agent_added[: len(st.session_state.agent_urls)]

        st.markdown("### A2A Agents")

        # =================================================
        # SINGLE AGENT CLIENT
        # =================================================

        if agent_mode == "Single Agent Client":

            logger.info("Rendering configuration for single agent client")

            # Dynamic label based on agent name from card (if already fetched)
            display_name = (
                st.session_state.agent_names[0]
                if st.session_state.agent_names[0]
                else "A2A Agent"
            )

            st.markdown(f"**{display_name}**")

            col_url, col_header_name, col_header_value, col_actions = st.columns(
                [4, 2, 2, 1]
            )

            with col_url:
                url = st.text_input(
                    f"{display_name} URL",
                    value=st.session_state.agent_urls[0],
                    key="single_agent_url",
                )

            with col_header_name:
                header_name = st.text_input(
                    "Header Name",
                    value=st.session_state.agent_header_names[0],
                    key="single_header_name",
                )

            with col_header_value:
                header_value = st.text_input(
                    "Header Value",
                    value=st.session_state.agent_header_values[0],
                    key="single_header_value",
                    type="password",
                )

            with col_actions:
                # Small spacer to align button vertically with text inputs
                st.markdown(
                    "<div style='height:0.4rem'></div>",
                    unsafe_allow_html=True,
                )
                fetch_clicked = st.button("Add", key="single_agent_fetch")

            if fetch_clicked:

                if not url.strip() or not header_name.strip() or not header_value.strip():
                    st.error(
                        "Please fill Agent URL, Header Name, and Header Value before clicking Add."
                    )
                else:
                    agent_name = _fetch_agent_name_from_card(url.strip())

                    if agent_name:
                        st.session_state.agent_names[0] = agent_name
                        st.session_state.agent_header_names[0] = header_name
                        st.session_state.agent_header_values[0] = header_value
                        st.session_state.agent_added[0] = True
                    else:
                        st.error("Failed to fetch agent name from agent card.")

            st.session_state.agent_urls = [url]

        # =================================================
        # MULTI AGENT CLIENT
        # =================================================

        else:

            logger.info("Rendering configuration for multi-agent client")

            for i in range(len(st.session_state.agent_urls)):

                # Dynamic display name from card (if fetched)
                display_name = (
                    st.session_state.agent_names[i]
                    if st.session_state.agent_names[i]
                    else f"A2A Agent {i+1}"
                )

                st.markdown(f"**{display_name}**")

                col_url, col_header_name, col_header_value, col_add, col_delete = st.columns(
                    [4, 2, 2, 1, 1]
                )

                with col_url:
                    st.session_state.agent_urls[i] = st.text_input(
                        f"{display_name} URL",
                        value=st.session_state.agent_urls[i],
                        key=f"a2a_agent_url_{i}"
                    )

                with col_header_name:
                    st.session_state.agent_header_names[i] = st.text_input(
                        f"Header Name {i+1}",
                        value=st.session_state.agent_header_names[i],
                        key=f"agent_header_name_{i}"
                    )

                with col_header_value:
                    st.session_state.agent_header_values[i] = st.text_input(
                        f"Header Value {i+1}",
                        value=st.session_state.agent_header_values[i],
                        key=f"agent_header_value_{i}",
                        type="password"
                    )

                with col_add:
                    # Small spacer to align button vertically with text inputs
                    st.markdown(
                        "<div style='height:0.4rem'></div>",
                        unsafe_allow_html=True,
                    )
                    fetch_clicked = st.button(
                        "Add",
                        key=f"fetch_agent_name_{i}",
                        help="Fetch agent name from agent card",
                        use_container_width=True,
                    )

                if fetch_clicked:

                    url = st.session_state.agent_urls[i].strip()
                    header_name = st.session_state.agent_header_names[i].strip()
                    header_value = st.session_state.agent_header_values[i].strip()

                    if not url or not header_name or not header_value:
                        st.error(
                            f"Please fill Agent URL, Header Name, and Header Value for agent {i+1} before clicking Add."
                        )
                    else:
                        agent_name = _fetch_agent_name_from_card(url)

                        if agent_name:
                            st.session_state.agent_names[i] = agent_name
                            st.session_state.agent_added[i] = True
                        else:
                            st.error(
                                f"Failed to fetch agent name for URL {i+1}. "
                                "Please check the URL or try again."
                            )

                with col_delete:

                    if len(st.session_state.agent_urls) > 1:

                        # Small spacer to align button vertically with text inputs
                        st.markdown(
                            "<div style='height:0.4rem'></div>",
                            unsafe_allow_html=True,
                        )

                        delete_clicked = st.button(
                            "❌",
                            key=f"delete_url_{i}",
                            help="Remove this agent",
                            use_container_width=True
                        )

                        if delete_clicked:
                            logger.info("Removing agent configuration at index %s", i)

                            st.session_state.agent_urls.pop(i)
                            st.session_state.agent_names.pop(i)
                            st.session_state.agent_header_names.pop(i)
                            st.session_state.agent_header_values.pop(i)
                            st.session_state.agent_added.pop(i)

                            st.rerun()

            # Add new agent row
            if st.button("Add Another Agent URL"):

                # All existing agents must be "added" before creating a new one
                if any(not added for added in st.session_state.agent_added):
                    st.error("Please click Add for all existing agents before adding another agent URL.")
                else:
                    logger.info("Adding new agent configuration row")

                    st.session_state.agent_urls.append("")
                    st.session_state.agent_names.append("")
                    st.session_state.agent_header_names.append("Authorization")
                    st.session_state.agent_header_values.append("")
                    st.session_state.agent_added.append(False)

                    st.rerun()

        # ------------------------------
        # Other Configuration Inputs
        # ------------------------------

        x_client_id = st.text_input(
            "X-Client-ID",
            value="teste.client.com"
        )

        if agent_mode == "Multi Agent Client":
            groq_api_key = st.text_input(
                "Groq API Key",
                type="password"
            )
        else:
            groq_api_key = None

        if agent_mode == "Single Agent Client":

            # Values already captured inline with URL row
            header_name = st.session_state.get("single_header_name", "Authorization")
            header_value = st.session_state.get("single_header_value", "")

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

        # ------------------------------
        # Save Configuration
        # ------------------------------

        if save_config:

            logger.info("User initiated configuration save")

            url = next((u for u in st.session_state.agent_urls if u.strip()), None)

            if not url:
                logger.info("Configuration validation failed: missing agent URL")
                st.error("At least one A2A Agent URL is required.")
                return

            if not uploaded_crt or not uploaded_key:
                logger.info("Configuration validation failed: certificates missing")
                st.error("Both client certificate and client key must be uploaded.")
                return

            os.makedirs("temp_certs", exist_ok=True)

            client_crt = os.path.join("temp_certs", uploaded_crt.name)
            client_key = os.path.join("temp_certs", uploaded_key.name)

            with open(client_crt, "wb") as f:
                f.write(uploaded_crt.getbuffer())

            with open(client_key, "wb") as f:
                f.write(uploaded_key.getbuffer())

            st.session_state.agent_configs = []

            if agent_mode == "Single Agent Client":

                headers = {
                    "Content-Type": "application/json",
                    "X-Client-ID": x_client_id,
                    header_name: header_value
                }

                st.session_state.agent_configs.append({
                    "name": st.session_state.agent_names[0],
                    "url": st.session_state.agent_urls[0],
                    "headers": headers
                })

                logger.info(
                    "Saved configuration for single agent: %s",
                    st.session_state.agent_names[0]
                )

            else:

                for i in range(len(st.session_state.agent_urls)):

                    headers = {
                        "Content-Type": "application/json",
                        "X-Client-ID": x_client_id,
                        st.session_state.agent_header_names[i]: st.session_state.agent_header_values[i]
                    }

                    st.session_state.agent_configs.append({
                        "name": st.session_state.agent_names[i],
                        "url": st.session_state.agent_urls[i],
                        "headers": headers
                    })

                logger.info("Saved configuration for %s agents", len(st.session_state.agent_configs))

            st.session_state.client_crt = client_crt
            st.session_state.client_key = client_key
            st.session_state.groq_api_key = groq_api_key
            st.session_state.config_saved = True

            logger.info("Configuration saved successfully")

            st.success("Configuration saved successfully.")