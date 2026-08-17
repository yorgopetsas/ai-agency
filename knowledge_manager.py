"""
Knowledge Manager - Per-Agent Knowledge Base
Phase 4: RAG + MCP
Phase 6: Data Isolation (client-scoped)

Manages knowledge bases for each agent.
Storage: knowledge/{client_id}/{agent_name}/
"""

import os
import json
from typing import Dict, List, Optional

KNOWLEDGE_DIR = "/Users/yorgopetsasedel/dev/opencode/ai_agency/knowledge"

# Module-level cache of client→manager mappings
_managers: Dict[str, 'KnowledgeManager'] = {}


class KnowledgeManager:
    """
    Manages knowledge bases for each agent, scoped per client.
    Simple file-based storage for documents.
    """

    def __init__(self, client_id: str = "internal"):
        self.client_id = client_id
        self.agents = ['researcher', 'writer', 'developer', 'designer', 'analyst']
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure knowledge directories exist"""
        for agent in self.agents:
            path = f"{KNOWLEDGE_DIR}/{self.client_id}/{agent}"
            os.makedirs(path, exist_ok=True)

    def _get_agent_path(self, agent: str) -> str:
        return f"{KNOWLEDGE_DIR}/{self.client_id}/{agent.lower()}"

    def add_document(
        self,
        agent: str,
        doc_id: str,
        title: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Add a document to agent's knowledge base"""
        try:
            agent_path = self._get_agent_path(agent)
            doc_path = f"{agent_path}/{doc_id}.json"

            doc_data = {
                "id": doc_id,
                "title": title,
                "content": content,
                "metadata": metadata or {},
                "client_id": self.client_id,
                "created_at": self._timestamp()
            }

            with open(doc_path, 'w') as f:
                json.dump(doc_data, f, indent=2)

            return True
        except Exception as e:
            print(f"Error adding document: {e}")
            return False

    def get_document(self, agent: str, doc_id: str) -> Optional[Dict]:
        """Get a document from agent's knowledge base"""
        try:
            agent_path = self._get_agent_path(agent)
            doc_path = f"{agent_path}/{doc_id}.json"

            if not os.path.exists(doc_path):
                return None

            with open(doc_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error getting document: {e}")
            return None

    def list_documents(self, agent: str) -> List[Dict]:
        """List all documents in agent's knowledge base"""
        try:
            agent_path = self._get_agent_path(agent)
            documents = []

            for filename in os.listdir(agent_path):
                if filename.endswith('.json'):
                    doc_path = f"{agent_path}/{filename}"
                    with open(doc_path, 'r') as f:
                        doc = json.load(f)
                        documents.append({
                            "id": doc.get("id"),
                            "title": doc.get("title"),
                            "metadata": doc.get("metadata", {})
                        })

            return documents
        except Exception as e:
            print(f"Error listing documents: {e}")
            return []

    def search(self, agent: str, query: str) -> List[Dict]:
        """Simple keyword search in agent's knowledge base"""
        try:
            agent_path = self._get_agent_path(agent)
            results = []
            query_lower = query.lower()

            for filename in os.listdir(agent_path):
                if filename.endswith('.json'):
                    doc_path = f"{agent_path}/{filename}"
                    with open(doc_path, 'r') as f:
                        doc = json.load(f)
                        content = doc.get("content", "").lower()
                        if query_lower in content:
                            results.append({
                                "id": doc.get("id"),
                                "title": doc.get("title"),
                                "snippet": content[:200]
                            })

            return results
        except Exception as e:
            print(f"Error searching: {e}")
            return []

    def delete_document(self, agent: str, doc_id: str) -> bool:
        """Delete a document from agent's knowledge base"""
        try:
            agent_path = self._get_agent_path(agent)
            doc_path = f"{agent_path}/{doc_id}.json"

            if os.path.exists(doc_path):
                os.remove(doc_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False

    def get_count(self, agent: str) -> int:
        """Get document count for agent"""
        try:
            agent_path = self._get_agent_path(agent)
            return len([f for f in os.listdir(agent_path) if f.endswith('.json')])
        except Exception:
            return 0

    def _timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()


def get_client_knowledge(client_id: str = "internal") -> KnowledgeManager:
    """Get or create a client-scoped knowledge manager (cached)."""
    if client_id not in _managers:
        _managers[client_id] = KnowledgeManager(client_id=client_id)
    return _managers[client_id]


# Default instance (backward compat — uses "internal" client)
knowledge_manager = KnowledgeManager(client_id="internal")


if __name__ == "__main__":
    km = get_client_knowledge("internal")

    # Add sample document
    km.add_document(
        'researcher',
        'doc_001',
        'AI Introduction',
        'Artificial Intelligence is a broad field of computer science...',
        {'topic': 'AI', 'source': 'test'}
    )

    # List documents
    docs = km.list_documents('researcher')
    print(f"Researcher has {len(docs)} documents")

    # Search
    results = km.search('researcher', 'Artificial Intelligence')
    print(f"Found {len(results)} results")
