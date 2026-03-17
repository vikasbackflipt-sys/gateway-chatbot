import uuid
import logging
import requests
from typing import Dict

logger = logging.getLogger(__name__)

session = requests.Session()


def send_message(
    user_message: str,
    request_url: str,
    headers: Dict[str, str],
    client_crt: str,
    client_key: str,
    request_id: str = None
) -> str:

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

    # --------------------------------------------------
    # AGENT REQUEST PAYLOAD
    # --------------------------------------------------
    logger.info(
        "[%s] Agent request payload | url=%s | payload=%s",
        request_id,
        request_url,
        payload
    )

    try:

        logger.info(
            "[%s] Sending HTTP request to agent | url=%s",
            request_id,
            request_url
        )

        response = session.post(
            request_url,
            headers=headers,
            json=payload,
            cert=(client_crt, client_key),
        )

        # --------------------------------------------------
        # HTTP STATUS
        # --------------------------------------------------
        logger.info(
            "[%s] Agent HTTP response received | url=%s | status_code=%s",
            request_id,
            request_url,
            response.status_code
        )

        response.raise_for_status()

        # --------------------------------------------------
        # RAW HTTP RESPONSE
        # --------------------------------------------------
        logger.info(
            "[%s] Raw agent response | url=%s | response=%s",
            request_id,
            request_url,
            response.text
        )

    except requests.exceptions.Timeout:

        logger.info(
            "[%s] Agent request timed out | url=%s",
            request_id,
            request_url
        )

        return "Error: Request timed out."

    except requests.exceptions.ConnectionError as e:

        logger.info(
            "[%s] Connection error while calling agent | url=%s | error=%s",
            request_id,
            request_url,
            str(e)
        )

        return f"Connection error: {str(e)}"

    except requests.exceptions.HTTPError as e:

        logger.info(
            "[%s] HTTP error from agent | url=%s | error=%s",
            request_id,
            request_url,
            str(e)
        )

        return f"HTTP error: {str(e)}"

    except Exception as e:

        logger.info(
            "[%s] Unexpected error during agent call | url=%s | error=%s",
            request_id,
            request_url,
            str(e)
        )

        return f"Unexpected error: {str(e)}"

    try:

        data = response.json()

        logger.info(
            "[%s] Parsed JSON response from agent | url=%s",
            request_id,
            request_url
        )

    except ValueError:

        logger.info(
            "[%s] Invalid JSON response from agent | url=%s",
            request_id,
            request_url
        )

        return "Error: Invalid JSON response from server."

    try:

        agent_text = data["result"]["status"]["message"]["parts"][0]["text"]

        # --------------------------------------------------
        # PARSED RESPONSE
        # --------------------------------------------------
        logger.info(
            "[%s] Final parsed agent message | url=%s | text=%s",
            request_id,
            request_url,
            agent_text
        )

    except (KeyError, IndexError, TypeError):

        logger.info(
            "[%s] Unexpected response format from agent | url=%s | data=%s",
            request_id,
            request_url,
            data
        )

        return f"Unexpected response format: {data}"

    return agent_text