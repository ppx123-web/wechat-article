# WeChat MCP Server Walkthrough

This document describes how to set up and use the WeChat Public Article MCP server.

## Overview
The server connects to the `mptext.top` API to:
1.  Manage a list of followed public accounts.
2.  Search for accounts.
3.  Retrieve article lists (with optional time filtering).
4.  Download article content (Markdown).

## Setup

### 1. Prerequisites
- Python 3.10+
- `uv` (recommended) or `pip`

### 2. Configuration
Create a `.env` file in the project root:
```ini
WECHAT_API_KEY=your_api_key_here
WECHAT_FOLLOWED_ACCOUNTS_PATH=followed_accounts.json
```

Create a `followed_accounts.json` file:
```json
[
  {
    "name": "Machine Heart",
    "fakeid": "MzIwMTc4NDk3Nw=="
  }
]
```

### 3. Installation
```bash
uv sync
# Or
pip install -e .
```

### 4. Running the Server

#### Use with Claude Desktop
Add config to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "wechat": {
      "command": "uv",
      "args": [
        "run",
        "wechat-mcp"
      ],
      "cwd": "/absolute/path/to/wechat-article",
      "env": {
        "WECHAT_API_KEY": "..."
      }
    }
  }
}
```

## Tools

### `list_followed_accounts`
Returns the list of accounts configured in `followed_accounts.json`.

### `add_followed_account(name, fakeid)`
Add a new account to the followed list.
- `name`: Display name of the account.
- `fakeid`: The unique ID of the account (found via `search_public_account`).
**Example**: `add_followed_account(name="Machines Heart", fakeid="MzIwMTc4NDk3Nw==")`

### `search_public_account(keyword)`
Search for an account to find its `fakeid`.
**Example**: `search_public_account(keyword="机器之心")`

### `get_account_articles(fakeid, start_date=None, limit=5)`
Get articles for a specific account.
- `fakeid`: The account ID.
- `start_date`: (Optional) Filter for articles published on or after this date (Format: `YYYY-MM-DD`). The tool will attempt to fetch all matching articles.
- `limit`: Maximum number of articles to return (Overall limit).

**Example**: `get_account_articles(fakeid="...", start_date="2026-01-16")`

**Tip**: To get articles from **yesterday to today**, set `start_date` to yesterday's date.
*   Example: If today is `2026-01-16`, use `start_date="2026-01-15"` to get all articles from yesterday and today.

### `download_article(url)`
Download the content of an article.

## Verification
A verification script `verify_mcp.py` is provided to test the flow programmatically.
```bash
uv run verify_mcp.py
```
**Note**: The API may be slow. If you encounter timeouts, try again.
