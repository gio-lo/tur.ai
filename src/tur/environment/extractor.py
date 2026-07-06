"""Heuristics for summarizing recent conversational environment context."""

from __future__ import annotations

import re


class EnvironmentExtractor:
    """Builds short ambient event summaries from completed turns."""

    _TOPIC_RULES = (
        (re.compile(r"\ballerg"), "food allergies and what to avoid"),
        (re.compile(r"\bpeanut\b|\bcashew\b|\bfood\b|\beat\b|\bsnack\b"), "food and snack safety"),
        (re.compile(r"\bbike\b|\bmotorcycle\b|\bninja\b|\bride\b"), "motorcycles and riding"),
        (re.compile(r"\bcode\b|\bproject\b|\bbuild\b|\barchitecture\b"), "software and ongoing projects"),
    )

    def summarize_interaction(
        self,
        personality_name: str,
        user_message: str,
        assistant_reply: str,
    ) -> str | None:
        """Return a short ambient event summary for a completed interaction."""
        topic = self._topic_for_text(f"{user_message} {assistant_reply}")
        if topic is None:
            snippet = self._snippet(user_message)
            if not snippet:
                return None
            return f"{personality_name} was recently talking with Gio about {snippet}."

        return f"{personality_name} was recently talking with Gio about {topic}."

    def _topic_for_text(self, text: str) -> str | None:
        lowered = text.lower()
        for pattern, topic in self._TOPIC_RULES:
            if pattern.search(lowered):
                return topic
        return None

    def _snippet(self, message: str) -> str:
        tokens = re.findall(r"[a-z0-9']+", message.lower())
        filtered = [token for token in tokens if len(token) > 2][:6]
        return " ".join(filtered)
