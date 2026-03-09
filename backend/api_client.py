import uuid
import requests

def send_message(user_message, request_url, headers, client_crt, client_key):
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "messageId": str(uuid.uuid4()),
                "parts": [
                    {
                        "kind": "text",
                        "text": user_message
                    }
                ]
            }
        }
    }

    response = requests.post(
        request_url,
        headers=headers,
        json=payload,
        cert=(client_crt, client_key)
    )
    data = response.json()

    agent_text = data["result"]["status"]["message"]["parts"][0]["text"]

    return agent_text