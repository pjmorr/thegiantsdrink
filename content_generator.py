# content_generator.py
import os

import requests

SYSTEM_PROMPT = """You are a narrator for a text adventure game called The Giant's Drink.
Generate atmospheric room descriptions in the style of classic Zork text adventures.
Keep descriptions to 2-3 sentences. Be vivid and evocative but concise.
Use second person ("You see...", "The air smells of...").
Incorporate the player's profile to subtly tailor the atmosphere."""


class ContentGenerator:
    """LLM-powered room description generator with caching and static fallback.

    Uses Azure AI Foundry to produce atmospheric, Zork-style room descriptions
    tailored to the player's behavior profile. Caches generated descriptions
    per room and profile. Falls back to static descriptions when API
    credentials are missing or the request fails.

    Attributes:
        _cache: Dict mapping (room_name, profile_summary) to generated text.
    """

    def __init__(self):
        """Initialize ContentGenerator with an empty description cache."""
        self._cache = {}

    def generate_description(self, room_name, profile, description="", items=None, profile_summary=""):
        """Generate an atmospheric room description via Azure AI Foundry LLM.

        Caches results per room and profile to avoid redundant API calls.
        Falls back to static description on network or parsing failure.

            room_name (str): Name of the room to describe.
            profile (dict): Player profile (for context, not currently used in prompt).
            description (str, optional): Base/fallback description. Defaults to ''.
            items (list, optional): List of item names present in room. Defaults to None.
            profile_summary (str, optional): Text summary of player style. Defaults to ''.

            str: Generated atmospheric description or fallback description.
        """
        cache_key = (room_name, profile_summary)
        if cache_key in self._cache:
            return self._cache[cache_key]

        api_key = os.environ.get("AZURE_API_KEY", "")
        api_base = os.environ.get("AZURE_API_BASE", "")
        api_model = os.environ.get("AZURE_API_MODEL", "")

        if not api_key or not api_base or not api_model:
            return description or f"You are in the {room_name}."

        items_text = ", ".join(items) if items else "nothing of note"
        user_prompt = (
            f"Room: {room_name}\n"
            f"Base description: {description}\n"
            f"Items present: {items_text}\n"
            f"Player profile: {profile_summary or 'unknown'}\n\n"
            f"Generate a 2-3 sentence atmospheric description of this room "
            f"in Zork style."
        )

        try:
            url = api_base.rstrip("/") + "/v1/messages"
            headers = {
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            }
            payload = {
                "model": api_model,
                "max_tokens": 200,
                "system": SYSTEM_PROMPT,
                "messages": [
                    {"role": "user", "content": user_prompt},
                ],
            }

            response = requests.post(url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()

            result = response.json()
            if "error" in result:
                print(f"API error: {result['error']}")
                return description or f"You are in the {room_name}."
            generated = result["content"][0]["text"].strip()

            self._cache[cache_key] = generated
            return generated

        except (requests.RequestException, KeyError, IndexError):
            return description or f"You are in the {room_name}."
