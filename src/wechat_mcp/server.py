import json
from datetime import datetime, timedelta
from typing import List, Optional, Any
from mcp.server.fastmcp import FastMCP
from .config import get_config
from .client import WeChatClient

# Initialize configuration and client
config = get_config()
# Increase timeout for the global client if possible, or handle in tools
client = WeChatClient(config)

mcp = FastMCP("wechat-article")

@mcp.tool()
def list_followed_accounts() -> str:
    """
    List all followed public accounts configured in the JSON file.
    Returns a JSON string of accounts.
    """
    accounts = config.followed_accounts
    return json.dumps([{"name": acc.name, "fakeid": acc.fakeid} for acc in accounts], ensure_ascii=False, indent=2)

@mcp.tool()
def add_followed_account(name: str, fakeid: str) -> str:
    """
    Add a new public account to the followed accounts list.
    
    Args:
        name: The name of the account.
        fakeid: The fakeid of the account.
    """
    try:
        # Load existing
        current_accounts = []
        if config.followed_accounts_path.exists():
            with open(config.followed_accounts_path, 'r', encoding='utf-8') as f:
                current_accounts = json.load(f)
        
        # Check if exists
        for acc in current_accounts:
            if acc.get('fakeid') == fakeid:
                return f"Account {name} already exists."
        
        # Add new
        current_accounts.append({"name": name, "fakeid": fakeid})
        
        # Save
        with open(config.followed_accounts_path, 'w', encoding='utf-8') as f:
            json.dump(current_accounts, f, ensure_ascii=False, indent=2)
            
        return f"Successfully added account: {name}"
    except Exception as e:
        return f"Error adding account: {str(e)}"

@mcp.tool()
async def search_public_account(keyword: str) -> str:
    """
    Search for a WeChat public account by keyword.
    Useful to find the 'fakeid' of an account if you only have the name.
    """
    try:
        result = await client.search_account(keyword)
        # We process the result to be more readable if needed, or return raw JSON
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Error searching account: {str(e)}"

@mcp.tool()
async def get_account_articles(
    fakeid: str,
    start_date: Optional[str] = None,
    limit: int = 5
) -> str:
    """
    Get a list of articles for a specific public account (by fakeid).
    
    Args:
        fakeid: The unique ID of the public account.
        start_date: (Optional) Filter articles published on or after this date (YYYY-MM-DD).
                    If provided, the server will attempt to fetch ALL articles since this date,
                    up to a reasonable safety limit.
        limit: Max number of articles to return (default 5). 
               If start_date is set, this acts as a hard limit on total returned items.
    """
    try:
        all_articles = []
        begin = 0
        page_size = 20 # Maximize page size for efficiency
        
        cutoff_time = None
        if start_date:
            try:
                # Parse YYYY-MM-DD
                dt = datetime.strptime(start_date, "%Y-%m-%d")
                cutoff_time = dt
            except ValueError:
                return f"Error: Invalid start_date format. Use YYYY-MM-DD."

        while True:
            # If we collected enough (only if start_date is NOT set, or if we hit hard limit)
            if limit and len(all_articles) >= limit:
                break
                
            # Fetch batch
            # If start_date is set, we want to fetch as much as needed, so ignore 'limit' for batch retrieval
            # but respect it for total count if it's acting as a safety valve.
            # Actually, user said "all articles", so let's treat limit as purely a top-N if start_date is NOT provided,
            # OR as a safety max if it IS provided.
            
            fetch_size = page_size
            
            result = await client.get_article_list(fakeid, begin=begin, size=fetch_size)
            
            if not result or ('data' not in result and 'list' not in result and 'articles' not in result):
                # No more data or error
                break

            items = result.get('list') or result.get('articles') or result.get('data', [])
            if not items:
                break
                
            # Filter and add
            batch_added = 0
            stop_fetching = False
            
            for art in items:
                # If we have enough
                if limit and len(all_articles) >= limit:
                    stop_fetching = True
                    break

                if cutoff_time:
                    # Check time
                    ts = art.get('create_time') or art.get('update_time') or art.get('publish_time')
                    if ts:
                        try:
                            art_time = datetime.fromtimestamp(int(ts))
                            if art_time < cutoff_time:
                                # Found an article older than start_date. 
                                # Since API returns typically in reverse chronological order, we can stop.
                                stop_fetching = True
                                # Don't add this one
                                continue
                        except:
                            pass # Keep if broken timestamp? Or skip. Let's keep.
                    
                    all_articles.append(art)
                    batch_added += 1
                else:
                    # No time filter, just add
                    all_articles.append(art)
                    batch_added += 1
            
            if stop_fetching or batch_added == 0:
                break
                
            # Prepare for next page
            begin += len(items)
            
            # Safety break for huge accounts if specific date not found fast enough
            if begin > 100 and cutoff_time: 
                # Avoid infinite loops if something is wrong
                # But allow fetching up to 100 items deep for "today" or "recent"
                pass
            
            if len(items) < page_size:
                # End of list
                break

        # Wrap result
        # We perform a manual wrap to match structure
        final_result = {
            "base_resp": {"ret": 0, "err_msg": "ok"},
            "articles": all_articles,
            "total": len(all_articles)
        }

        return json.dumps(final_result, ensure_ascii=False, indent=2)
            
    except Exception as e:
        return f"Error getting articles: {str(e)}"

@mcp.tool()
async def download_article(url: str) -> str:
    """
    Download the content of an article in Markdown format.
    """
    try:
        content = await client.download_article(url, format="markdown")
        return content
    except Exception as e:
        return f"Error downloading article: {str(e)}"

if __name__ == "__main__":
    mcp.run()
