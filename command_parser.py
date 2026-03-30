# command_parser.py
import json
import os

import requests

SYSTEM_PROMPT = """You are a command parser for a text adventure game called The Giant's Drink.
The player explores a castle, collects items, and faces a giant.

Valid actions: move, take, use, attack, check, look, help, quit
Valid move targets: north, south, east, west
Valid check targets: inventory

Parse the player's natural language input into a JSON object with exactly two fields:
  "action": one of [move, take, use, attack, check, look, help, quit]
  "target": the target of the action (use "around" for look, "commands" for help, "game" for quit)

Examples:
- "go north" -> {"action": "move", "target": "north"}
- "take rusty sword" -> {"action": "take", "target": "rusty sword"}
- "drink potion" -> {"action": "use", "target": "potion"}
- "attack giant" -> {"action": "attack", "target": "giant"}
- "inventory" -> {"action": "check", "target": "inventory"}
- "look" -> {"action": "look", "target": "around"}
- "look around" -> {"action": "look", "target": "around"}
- "help" -> {"action": "help", "target": "commands"}
- "quit" -> {"action": "quit", "target": "game"}
- "exit" -> {"action": "quit", "target": "game"}

Respond with ONLY the JSON object, no other text."""

# Cache to store parsed results for performance
command_cache = {}


def parse_command(command):
    """Parse a player's natural language command using Azure AI Foundry LLM.

    Caches results per input string to avoid redundant API calls for repeated
    inputs.  Falls back to ``(None, None)`` on network error or parse failure.

    Args:
        command (str): The player's raw input (e.g. "take the rusty sword").

    Returns:
        tuple[str, str] | tuple[None, None]: ``(action, target)`` on success,
            or ``(None, None)`` if parsing fails.
    """
    if command in command_cache:
        return command_cache[command]

    try:
        api_key = os.environ.get("AZURE_API_KEY", "")
        api_base = os.environ.get("AZURE_API_BASE", "")
        api_model = os.environ.get("AZURE_API_MODEL", "")

        if not api_key or not api_base or not api_model:
            return None, None

        url = api_base.rstrip("/") + "/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        }
        payload = {
            "model": api_model,
            "max_tokens": 100,
            "system": SYSTEM_PROMPT,
            "messages": [
                {"role": "user", "content": command},
            ],
        }

        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()

        result = response.json()
        if "error" in result:
            print(f"API error: {result['error']}")
            return None, None
        generated_text = result["content"][0]["text"].strip()

        action, target = extract_action_target(generated_text)

        if action and target:
            command_cache[command] = (action, target)
            return action, target
        else:
            return None, None

    except (requests.RequestException, KeyError, IndexError):
        return None, None


def extract_action_target(text):
    """Extract action and target from the LLM's JSON response text.

    Args:
        text (str): Raw LLM output expected to contain a JSON object
            with ``action`` and ``target`` keys.

    Returns:
        tuple[str, str] | tuple[None, None]: ``(action, target)`` if valid,
            otherwise ``(None, None)``.
    """
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            data = json.loads(text[start:end])
            action = data.get("action")
            target = data.get("target")
            valid_actions = {"move", "take", "use", "attack", "check", "look", "help", "quit"}
            if action in valid_actions and target:
                return action, target
        return None, None
    except json.JSONDecodeError:
        return None, None
