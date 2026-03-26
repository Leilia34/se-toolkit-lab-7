"""Handler for /health command."""
import asyncio
from services.lms_client import LMSClient


async def handle_health() -> str:
    """Check backend health and return status."""
    client = LMSClient()
    is_healthy, message = await client.check_health()
    return message
