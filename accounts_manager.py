"""
Accounts Manager - Client Account Management
Phase 6: Multi-Client

Manages client accounts with manual onboarding.
"""

from typing import Dict, List, Optional
from datetime import datetime
import uuid
import json
import os

ACCOUNTS_DIR = "/Users/yorgopetsasedel/dev/opencode/ai_agency/accounts"
INTERNAL_ACCOUNT = "internal"

class Account:
    """Represents a client account"""
    
    def __init__(
        self,
        account_id: str,
        name: str,
        account_type: str = "client",
        status: str = "pending"
    ):
        self.id = account_id
        self.name = name
        self.type = account_type
        self.status = status  # pending, active, inactive
        self.created_at = datetime.now().isoformat()
        self.config = {
            "agents": {},
            "knowledge_base": {},
            "preferences": {}
        }
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "status": self.status,
            "created_at": self.created_at,
            "config": self.config
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Account':
        account = cls(
            data["id"],
            data["name"],
            data.get("type", "client"),
            data.get("status", "pending")
        )
        account.created_at = data.get("created_at", datetime.now().isoformat())
        account.config = data.get("config", {})
        return account


class AccountsManager:
    """
    Manages client accounts.
    Accounts are stored as JSON files in the accounts directory.
    """
    
    def __init__(self):
        self._ensure_accounts_dir()
        self._ensure_internal_account()
    
    def _ensure_accounts_dir(self):
        """Ensure accounts directory exists"""
        os.makedirs(ACCOUNTS_DIR, exist_ok=True)
        os.makedirs(f"{ACCOUNTS_DIR}/internal/config", exist_ok=True)
    
    def _ensure_internal_account(self):
        """Ensure internal account exists"""
        internal_path = f"{ACCOUNTS_DIR}/{INTERNAL_ACCOUNT}/config/account.json"
        if not os.path.exists(internal_path):
            account = Account(
                INTERNAL_ACCOUNT,
                "AI Agency Internal",
                "internal",
                "active"
            )
            self._save_account(account)
    
    def _get_account_path(self, account_id: str) -> str:
        return f"{ACCOUNTS_DIR}/{account_id}/config/account.json"
    
    def _save_account(self, account: Account):
        """Save account to disk"""
        path = f"{ACCOUNTS_DIR}/{account.id}/config/account.json"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(account.to_dict(), f, indent=2)
    
    def _load_account(self, account_id: str) -> Optional[Account]:
        """Load account from disk"""
        path = self._get_account_path(account_id)
        if not os.path.exists(path):
            return None
        with open(path, 'r') as f:
            data = json.load(f)
        return Account.from_dict(data)
    
    def create_account(self, name: str) -> str:
        """
        Create a new client account.
        Returns the new account ID.
        """
        account_id = str(uuid.uuid4())[:8]
        
        account = Account(account_id, name, "client", "pending")
        
        # Setup default agent configs
        default_agents = {
            "research": {
                "model": "llama3",
                "temperature": 0.2,
                "max_tokens": 2048
            },
            "writer": {
                "model": "llama3",
                "temperature": 0.7,
                "max_tokens": 4096
            },
            "developer": {
                "model": "llama3",
                "temperature": 0.2,
                "max_tokens": 4096
            },
            "designer": {
                "model": "llama3",
                "temperature": 0.8,
                "max_tokens": 2048
            },
            "analyst": {
                "model": "llama3",
                "temperature": 0.3,
                "max_tokens": 2048
            },
            "reviewer": {
                "model": "llama3",
                "temperature": 0.4,
                "max_tokens": 2048
            }
        }
        account.config["agents"] = default_agents
        
        self._save_account(account)
        return account_id
    
    def get_account(self, account_id: str) -> Optional[Account]:
        """Get account by ID"""
        return self._load_account(account_id)
    
    def list_accounts(self) -> List[Dict]:
        """List all accounts"""
        accounts = []
        if not os.path.exists(ACCOUNTS_DIR):
            return accounts
        
        for account_id in os.listdir(ACCOUNTS_DIR):
            account = self._load_account(account_id)
            if account:
                accounts.append({
                    "id": account.id,
                    "name": account.name,
                    "type": account.type,
                    "status": account.status,
                    "created_at": account.created_at
                })
        
        return sorted(accounts, key=lambda a: a["created_at"], reverse=True)
    
    def activate_account(self, account_id: str) -> bool:
        """Activate a pending account"""
        account = self._load_account(account_id)
        if not account:
            return False
        
        account.status = "active"
        self._save_account(account)
        return True
    
    def deactivate_account(self, account_id: str) -> bool:
        """Deactivate an account"""
        account = self._load_account(account_id)
        if not account:
            return False
        
        account.status = "inactive"
        self._save_account(account)
        return True
    
    def delete_account(self, account_id: str) -> bool:
        """Delete an account"""
        if account_id == INTERNAL_ACCOUNT:
            return False  # Can't delete internal
        
        account = self._load_account(account_id)
        if not account:
            return False
        
        account.status = "deleted"
        self._save_account(account)
        return True
    
    def update_config(self, account_id: str, config: Dict) -> bool:
        """Update account configuration"""
        account = self._load_account(account_id)
        if not account:
            return False
        
        account.config.update(config)
        self._save_account(account)
        return True
    
    def get_agent_config(self, account_id: str, agent: str) -> Optional[Dict]:
        """Get agent configuration for an account"""
        account = self._load_account(account_id)
        if not account:
            return None
        
        return account.config.get("agents", {}).get(agent)


# Default instance
accounts_manager = AccountsManager()


if __name__ == "__main__":
    # List accounts
    accounts = accounts_manager.list_accounts()
    print(f"Total accounts: {len(accounts)}")
    
    for acc in accounts:
        status = "✅" if acc["status"] == "active" else "⏳"
        print(f"  {status} {acc['name']} ({acc['id']})")