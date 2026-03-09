import uuid
import logging
import requests
from typing import Dict, Tuple

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

# Reuse HTTP connection
session = requests.Session()


def send_message(
    user_message: str,
    request_url: str,
    headers: Dict[str, str],
    client_crt: str,
    client_key: str
) -> str:
    """
    Sends a message to the A2A agent endpoint and returns the agent response.
    """

    message_id = str(uuid.uuid4())

    payload = {
        "jsonrpc": "2.0",
        "id": message_id,
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "messageId": message_id,
                "parts": [
                    {
                        "kind": "text",
                        "text": user_message
                    }
                ]
            }
        }
    }

    logger.info("Sending request to agent")
    logger.debug("Request URL: %s", request_url)
    logger.debug("Payload ID: %s", message_id)

    try:
        response = session.post(
            request_url,
            headers=headers,
            json=payload,
            cert=(client_crt, client_key),
            timeout=30
        )

        logger.info("Received response with status code %s", response.status_code)

        response.raise_for_status()

    except requests.exceptions.Timeout:
        logger.error("Request timed out")
        return "Error: Request timed out."

    except requests.exceptions.ConnectionError as e:
        logger.error("Connection error: %s", str(e))
        return f"Connection error: {str(e)}"

    except requests.exceptions.HTTPError as e:
        logger.error("HTTP error: %s", str(e))
        return f"HTTP error: {str(e)}"

    except Exception as e:
        logger.exception("Unexpected error during API call")
        return f"Unexpected error: {str(e)}"

    try:
        data = response.json()
        logger.debug("Response JSON: %s", data)

    except ValueError:
        logger.error("Invalid JSON response received")
        return "Error: Invalid JSON response from server."

    try:
        agent_text = data["result"]["status"]["message"]["parts"][0]["text"]
        logger.info("Agent response extracted successfully")

    except (KeyError, IndexError, TypeError):
        logger.error("Unexpected API response structure: %s", data)
        return f"Unexpected response format: {data}"

    return agent_text