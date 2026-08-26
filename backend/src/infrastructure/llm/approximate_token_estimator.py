"""Adapter nhỏ quanh LangChain approximate token counter."""

from langchain_core.messages import HumanMessage
from langchain_core.messages.utils import count_tokens_approximately


class ApproximateTokenEstimator:
    """Giữ dependency LangChain ngoài application/domain boundaries."""

    def __init__(self, chars_per_token: float = 4.0) -> None:
        self._chars_per_token = chars_per_token

    def count(self, *sections: str) -> int:
        messages = [HumanMessage(content=section) for section in sections if section]
        return count_tokens_approximately(
            messages,
            chars_per_token=self._chars_per_token,
        )
