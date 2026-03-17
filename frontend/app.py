import streamlit as st
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tabs.a2a_client import render_a2a_client
from tabs.mcp_client import render_mcp_client
from components.sidebar_config import render_sidebar_config
from tabs.automated_a2a_client import render_automated_a2a_client


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


# =========================
# UI HEADER
# =========================

st.title("Gateway Client Interface")
logger.info("Main page rendered")


# =========================
# SESSION STATE INIT
# =========================

if "config_saved" not in st.session_state:
    st.session_state.config_saved = False
    logger.info("Session state initialized: config_saved=False")

if "messages" not in st.session_state:
    st.session_state.messages = []
    logger.info("Session state initialized: messages list created")


# =========================
# SIDEBAR
# =========================

logger.info("Rendering sidebar configuration")
render_sidebar_config()


# =========================
# TABS
# =========================

logger.info("Initializing application tabs")

tab1, tab2, tab3 = st.tabs([
    "A2A Client",
    "MCP Client",
    "Automated A2A Client"
])


# =========================
# TAB 1 : A2A CLIENT
# =========================

with tab1:
    logger.info("A2A Client tab opened")
    render_a2a_client()


# =========================
# TAB 2 : MCP CLIENT
# =========================

with tab2:
    logger.info("MCP Client tab opened")
    render_mcp_client()


# =========================
# TAB 3 : AUTOMATED A2A CLIENT
# =========================

with tab3:
    logger.info("Automated A2A Client tab opened")
    render_automated_a2a_client()