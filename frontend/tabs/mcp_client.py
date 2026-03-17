import streamlit as st
import logging

logger = logging.getLogger("gateway-ui")


def render_mcp_client():

    logger.info("MCP tab opened")

    st.subheader("MCP Client")

    st.info("MCP Client UI will be implemented here.")