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

    async def _request(self, method: str, path: str, json_data: dict = None) -> Tuple[bool, Any]:
        """Make an HTTP request and return (success, result)."""
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient() as client:
            try:
                if method == "POST":
                    resp = await client.post(url, headers=self.headers, json=json_data or {}, timeout=30.0)
                else:
                    resp = await client.get(url, headers=self.headers, timeout=10.0)
                resp.raise_for_status()
                return True, resp.json()
            except httpx.TimeoutException:
                return False, f"timeout: Backend is not responding"
            except httpx.HTTPStatusError as e:
                return False, f"HTTP {e.response.status_code} {e.response.reason_phrase}"
            except httpx.ConnectError as e:
                return False, f"connection refused ({self.base_url})"
            except Exception as e:
                return False, f"error: {e}"

    async def get_items(self) -> List[Dict[str, Any]]:
        """Fetch all items (labs and tasks)."""
        success, result = await self._request("GET", "/items/")
        return result if success and isinstance(result, list) else []

    async def get_learners(self) -> List[Dict[str, Any]]:
        """Fetch all enrolled learners."""
        success, result = await self._request("GET", "/learners/")
        return result if success and isinstance(result, list) else []

    async def get_scores(self, lab: str) -> List[Dict[str, Any]]:
        """Get score distribution for a lab."""
        success, result = await self._request("GET", f"/analytics/scores?lab={lab}")
        return result if success and isinstance(result, list) else []

    async def get_pass_rates(self, lab: str) -> List[Dict[str, Any]]:
        """Get per-task pass rates for a lab."""
        success, result = await self._request("GET", f"/analytics/pass-rates?lab={lab}")
        return result if success and isinstance(result, list) else []

    async def get_timeline(self, lab: str) -> List[Dict[str, Any]]:
        """Get timeline for a lab."""
        success, result = await self._request("GET", f"/analytics/timeline?lab={lab}")
        return result if success and isinstance(result, list) else []

    async def get_groups(self, lab: str) -> List[Dict[str, Any]]:
        """Get per-group performance for a lab."""
        success, result = await self._request("GET", f"/analytics/groups?lab={lab}")
        return result if success and isinstance(result, list) else []

    async def get_top_learners(self, lab: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top learners for a lab."""
        success, result = await self._request("GET", f"/analytics/top-learners?lab={lab}&limit={limit}")
        return result if success and isinstance(result, list) else []

    async def get_completion_rate(self, lab: str) -> Dict[str, Any]:
        """Get completion rate for a lab."""
        success, result = await self._request("GET", f"/analytics/completion-rate?lab={lab}")
        return result if success and isinstance(result, dict) else {}

    async def trigger_sync(self) -> Dict[str, Any]:
        """Trigger ETL sync."""
        success, result = await self._request("POST", "/pipeline/sync", json_data={})
        return result if success else {}

    async def check_health(self) -> Tuple[bool, str]:
        """Check backend health."""
        success, result = await self._request("GET", "/items/")
        if success and isinstance(result, list):
            return True, f"Backend is healthy. {len(result)} items available."
        return False, "Backend is not responding"

    async def find_lab_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find lab by name or ID."""
        items = await self.get_items()
        name_lower = name.lower()
        
        # Try lab-XX format
        if name_lower.startswith("lab-"):
            lab_num = name_lower.replace("lab-", "").lstrip("0") or "0"
            lab_num_padded = name_lower.replace("lab-", "").zfill(2)
            for item in items:
                if item.get("type") == "lab":
                    title = item.get("title", "")
                    if f"Lab {lab_num_padded}" in title or f"Lab {lab_num}" in title:
                        return item
        
        # Try by title
        for item in items:
            if item.get("type") == "lab" and name_lower in item.get("title", "").lower():
                return item
        
        return None

    def get_all_labs(self) -> List[Dict[str, Any]]:
        """Get all labs (sync wrapper)."""
        import asyncio
        return asyncio.run(self.get_items_async())
    
    async def get_items_async(self) -> List[Dict[str, Any]]:
        """Async version of get_items."""
        return await self.get_items()
