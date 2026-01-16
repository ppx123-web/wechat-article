import os
import json
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Account:
    name: str
    fakeid: Optional[str] = None

@dataclass
class Config:
    api_key: str
    followed_accounts_path: Path

    @property
    def followed_accounts(self) -> List[Account]:
        if not self.followed_accounts_path.exists():
            return []
        
        try:
            with open(self.followed_accounts_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Account(name=item.get('name'), fakeid=item.get('fakeid')) for item in data]
        except Exception as e:
            print(f"Error loading followed accounts: {e}")
            return []

def get_config() -> Config:
    api_key = os.environ.get("WECHAT_API_KEY")
    if not api_key:
        raise ValueError("WECHAT_API_KEY environment variable is not set")
    
    accounts_path = os.environ.get("WECHAT_FOLLOWED_ACCOUNTS_PATH", "followed_accounts.json")
    return Config(
        api_key=api_key,
        followed_accounts_path=Path(accounts_path).absolute()
    )
