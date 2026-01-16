import asyncio
import json
import os
from wechat_mcp.client import WeChatClient
from wechat_mcp.config import get_config
from wechat_mcp.server import get_account_articles

async def main():
    print("Initializing client...")
    try:
        config = get_config()
        client = WeChatClient(config) # Used for search/download checks if needed
        
        # Test 1: Search Account
        # client.headers["X-Auth-Key"] = config.api_key # header is set in __init__ now
        res = await client.search_account("机器之心")
        
        if res.get('list') and len(res['list']) > 0:
            fakeid = res['list'][0].get('fakeid')
            name = res['list'][0].get('nickname')
            print(f"Found account: {name} ({fakeid})")
            
            # Test 2: Get Articles with Date Filter (Today)
            today_str = "2026-01-16" 
            print(f"Fetching articles since {today_str} (Today)...")
            
            # Call the server tool function directly
            # Note: get_account_articles is async and returns a JSON string
            arts_json = await get_account_articles(fakeid, start_date=today_str, limit=20)
            arts = json.loads(arts_json)
            
            # Check 'list', 'articles', and 'data'
            items = arts.get('list') or arts.get('articles') or arts.get('data')
            
            if items:
                print(f"Found {len(items)} articles from today.")
                first_art = items[0]
                url = first_art.get('link')
                title = first_art.get('title')
                date_ts = first_art.get('create_time')
                print(f"First Article: {title} (Time: {date_ts})")
                
                if url:
                    print(f"Downloading {url} ...")
                    content = await client.download_article(url)
                    print(f"Downloaded {len(content)} chars.")
            else:
                print(f"No articles found for today. Full Response: {json.dumps(arts, ensure_ascii=False)}")
        else:
            print("Account not found (or 'list' key missing).")

    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
