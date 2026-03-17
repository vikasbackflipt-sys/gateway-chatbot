import json
import logging
from typing import Any, Dict, Optional

import requests
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.api_client import send_message

logger = logging.getLogger("gateway-ui")


def _fetch_agent_card(agent_url: str, request_id: str) -> Optional[Dict[str, Any]]:

    well_known_url = agent_url.rstrip("/") + "/.well-known/agent.json"

    logger.info(
        "[%s] Fetching agent card | base_url=%s | card_url=%s",
        request_id,
        agent_url,
        well_known_url
    )

    try:
        response = requests.get(well_known_url, timeout=10)
        response.raise_for_status()

        card = response.json()

        logger.info(
            "[%s] Agent card fetched successfully | base_url=%s",
            request_id,
            agent_url
        )

        return card

    except Exception as e:
        logger.info(
            "[%s] Failed to fetch agent card | base_url=%s | error=%s",
            request_id,
            agent_url,
            str(e)
        )
        return None


def run_multi_agent(user_query, agent_configs, groq_key, crt, key, request_id):

    logger.info("[%s] Starting multi-agent orchestration", request_id)

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=groq_key,
        temperature=0
    )

    logger.info("[%s] LLM router initialized", request_id)

    agents_summary = []

    for agent in agent_configs:

        card = _fetch_agent_card(agent["url"], request_id)

        agent_entry: Dict[str, Any] = {
            "name": agent["name"],
            "url": agent["url"]
        }

        if card is not None:
            agent_entry["card"] = card

        agents_summary.append(agent_entry)

    logger.info(
        "[%s] Agents available for routing (including cards): %s",
        request_id,
        json.dumps(agents_summary, indent=2)
    )

    prompt = ChatPromptTemplate.from_template("""
You are an AI routing assistant responsible for selecting the correct agents to answer a user's request.

You will receive:
1. A user question.
2. A list of available agents with their names, URLs, and full agent cards (JSON objects describing their capabilities).

Your task:
1. Determine which of the provided agents should handle the request.
2. For each selected agent, generate a concise question that should be sent to that agent.

Important rules:
- Only use agents from the provided "Agents" list.
- Do NOT invent new agent names.
- The "agent_name" must exactly match one of the provided agent names.
- Each agent should receive only the portion of the question relevant to its capability.
- If multiple agents are required, return multiple objects in the JSON array.
- If only one agent is needed, return a single object in the array.
- Do NOT include explanations, comments, or text outside the JSON output.

Return format (strict JSON array):

[
  {{
    "agent_name": "<exact agent name from Agents list>",
    "agent_url": "<agent URL from Agents list>",
    "question_to_send": "<relevant question for that agent>"
  }}
]

Agents:
{agents}

User Question:
{question}

Return only the JSON array.
""")

    chain = prompt | llm | StrOutputParser()

    # ----------------------------------------------------
    # PAYLOAD SENT TO LLM
    # ----------------------------------------------------
    llm_payload = {
        "agents": agents_summary,
        "question": user_query
    }

    logger.info(
        "[%s] Payload sent to LLM router: %s",
        request_id,
        json.dumps(llm_payload, indent=2)
    )

    response = chain.invoke(llm_payload)

    # ----------------------------------------------------
    # RAW LLM RESPONSE
    # ----------------------------------------------------
    logger.info(
        "[%s] Raw LLM routing response: %s",
        request_id,
        response
    )

    try:
        plan = json.loads(response)

        # ----------------------------------------------------
        # EXECUTION PLAN
        # ----------------------------------------------------
        logger.info(
            "[%s] Execution plan generated: %s",
            request_id,
            json.dumps(plan, indent=2)
        )

    except Exception:
        logger.info("[%s] Failed to parse LLM routing response", request_id)
        return "Error: Failed to parse routing plan from LLM."

    results = []

    for step in plan:

        agent_name = step["agent_name"]
        question = step["question_to_send"]

        logger.info(
            "[%s] Preparing to call agent | agent=%s | question=%s",
            request_id,
            agent_name,
            question
        )

        agent = next(
            a for a in agent_configs
            if a["name"] == agent_name
        )

        # ----------------------------------------------------
        # PAYLOAD FOR AGENT CALL
        # ----------------------------------------------------
        logger.info(
            "[%s] Agent request payload | agent=%s | url=%s | question=%s",
            request_id,
            agent_name,
            agent["url"],
            question
        )

        answer = send_message(
            question,
            agent["url"],
            agent["headers"],
            crt,
            key,
            request_id = request_id
        )

        # ----------------------------------------------------
        # AGENT RESPONSE
        # ----------------------------------------------------
        logger.info(
            "[%s] Response received from agent | agent=%s | response=%s",
            request_id,
            agent_name,
            answer
        )

        results.append({
            "agent": agent_name,
            "response": answer
        })

    logger.info(
        "[%s] Multi-agent orchestration completed | total_agents=%s",
        request_id,
        len(results)
    )

    return json.dumps(results, indent=2)