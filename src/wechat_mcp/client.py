import httpx
from typing import Any, Dict, List, Optional
from .config import Config

class WeChatClient:
    BASE_URL = "https://down.mptext.top/api/public/v1"

    def __init__(self, config: Config):
        self.config = config
        self.headers = {
            "X-Auth-Key": self.config.api_key,
            "User-Agent": "mcp-wechat-client/0.1.0"
        }
    
    async def _get(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}{endpoint}",
                params=params,
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def search_account(self, keyword: str, begin: int = 0, size: int = 5) -> Dict[str, Any]:
        """
        Search for official accounts.
        Returns JSON response containing list of accounts.
        """
        return await self._get("/account", {
            "keyword": keyword,
            "begin": begin,
            "size": size
        })

    async def get_article_list(self, fakeid: str, begin: int = 0, size: int = 5) -> Dict[str, Any]:
        """
        Get article list for a specific account (fakeid).
        """
        return await self._get("/article", {
            "fakeid": fakeid,
            "begin": begin,
            "size": size
        })

    async def download_article(self, url: str, format: str = "markdown") -> str:
        """
        Download article content.
        Note: The API documentation says this endpoint does not require API key,
        but we pass headers anyway unless it causes issues.
        Returns the content as string.
        """
        # The document says this API returns html/markdown/text directly? or JSON?
        # "Return Example" is toggled in the screenshot but not visible. 
        # Usually download libraries return raw content.
        # But if it's an API that converts, it might return a wrapper.
        # Let's assume it returns the content directly for now based on "Download" name.
        # The screenshot for #4 says "Return content... supports html/markdown/text format"
        
        params = {
            "url": url,
            "format": format
        }
        
        async with httpx.AsyncClient() as client:
            # This endpoint might behave differently, let's treat it carefully.
            response = await client.get(
                f"{self.BASE_URL}/download",
                params=params,
                headers=self.headers, # Docs say "KEY NOT REQUIRED", so maybe we can skip it, but safe to keep.
                timeout=60.0 # Content download might take longer
            )
            response.raise_for_status()
            return response.text

    async def get_articles_since(self, fakeid: str, minutes_ago: int = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Helper to fetch articles, optionally filtering by time.
        Note: If API doesn't provide time filtering natively, we might need to fetch and filter.
        The screenshot shows `begin` and `size`, no time filter.
        We'll just fetch the most recent ones for now.
        """
        # TODO: If we need time filtering, we need to inspect the response structure of get_article_list
        # to see if 'update_time' or similar exists in the items.
        
        # For now, just return the list from the first page or up to limit
        res = await self.get_article_list(fakeid, 0, limit)
        # Check response structure. Usually it's like {"code": 0, "data": [...]} or just [...]
        # We will assume standard wrapper for now and let the MCP server handle it.
        return res
