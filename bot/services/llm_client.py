# services/llm_client.py
import httpx
from config import Config

class LLMClient:
    def __init__(self):
        self.base_url = Config.LLM_API_BASE_URL.rstrip('/')
        self.api_key = Config.LLM_API_KEY
        self.model = Config.LLM_API_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def chat(self, messages, tools=None):
        """Send a chat completion request. Returns the assistant's message."""
        payload = {
            "model": self.model,
            "messages": messages,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]
            except Exception as e:
                return {"role": "assistant", "content": f"Ошибка при вызове LLM: {e}"}
