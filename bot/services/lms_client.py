# services/lms_client.py
import httpx
from typing import List, Dict, Any, Optional, Tuple
from config import Config

class LMSClient:
    def __init__(self):
        self.base_url = Config.LMS_API_BASE_URL.rstrip('/')
        self.api_key = Config.LMS_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def _request(self, method: str, path: str) -> Tuple[bool, Any]:
        """Make an HTTP request and return (success, result)."""
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.request(method, url, headers=self.headers, timeout=10.0)
                resp.raise_for_status()
                return True, resp.json()
            except httpx.TimeoutException as e:
                return False, f"timeout: Backend is not responding"
            except httpx.HTTPStatusError as e:
                return False, f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
            except httpx.ConnectError as e:
                error_msg = str(e).lower()
                if "connection refused" in error_msg or "refused" in error_msg:
                    return False, f"connection refused ({self.base_url}). Check that the services are running."
                return False, f"connection error: {e}"
            except Exception as e:
                return False, f"error: {e}"

    async def get_items(self) -> List[Dict[str, Any]]:
        """Fetch all items (labs and tasks)."""
        success, result = await self._request("GET", "/items/")
        if not success:
            return []
        if isinstance(result, list):
            return result
        return []

    async def get_items_with_count(self) -> Tuple[bool, int, str]:
        """Fetch items and return (success, count, error_message)."""
        success, result = await self._request("GET", "/items/")
        if not success:
            return False, 0, result
        if isinstance(result, list):
            return True, len(result), ""
        return True, 0, ""

    async def get_pass_rates(self, lab: str) -> Tuple[bool, List[Dict[str, Any]], str]:
        """Fetch per-task pass rates for a lab. Returns (success, data, error)."""
        success, result = await self._request("GET", f"/analytics/pass-rates?lab={lab}")
        if not success:
            return False, [], result
        if isinstance(result, list):
            return True, result, ""
        return False, [], "Invalid response format"

    async def check_health(self) -> Tuple[bool, str]:
        """Check if backend is reachable. Returns (is_healthy, message)."""
        success, count, error = await self.get_items_with_count()
        if success:
            return True, f"Backend is healthy. {count} items available."
        else:
            return False, f"Backend error: {error}"

    async def find_lab_by_id(self, lab_id: str) -> Optional[Dict[str, Any]]:
        """Find a lab by its ID (e.g., 'lab-01', 'lab-04')."""
        items = await self.get_items()
        lab_id_normalized = lab_id.lower().strip()
        
        lab_number = lab_id_normalized.replace("lab-", "").lstrip("0") or "0"
        lab_number_padded = lab_id_normalized.replace("lab-", "").zfill(2)
        
        for item in items:
            if item.get("type") == "lab":
                title = item.get("title", "")
                if f"Lab {lab_number_padded}" in title or f"Lab {lab_number}" in title:
                    return item
                if str(item.get("id", "")) == lab_id_normalized:
                    return item
        return None
