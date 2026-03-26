import asyncio
from services.llm_client import LLMClient

async def main():
    client = LLMClient()
    response = await client.chat([{"role": "user", "content": "Say 'Hello, world!'"}])
    print(response)

asyncio.run(main())
