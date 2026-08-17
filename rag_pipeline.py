"""
RAG Pipeline - Knowledge Base Management
Phase 4: RAG + MCP Integration
Phase 6: Data Isolation (client-scoped)

Per-agent knowledge base with Chroma vector store.
Each client gets isolated storage: knowledge/{client_id}/{agent_name}
"""

import os
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings

# Base directory for knowledge
KNOWLEDGE_BASE_DIR = "/Users/yorgopetsasedel/dev/opencode/ai_agency/knowledge"

# Module-level cache of client→pipeline mappings
_pipelines: Dict[str, Dict[str, 'RAGPipeline']] = {}


class RAGPipeline:
    """
    Per-agent RAG pipeline using Chroma vector store.
    Each client+agent combination has its own isolated collection.
    """

    def __init__(self, agent_name: str, client_id: str = "internal"):
        self.agent_name = agent_name.lower()
        self.client_id = client_id
        self.collection_name = f"knowledge_{self.client_id}_{self.agent_name}"
        self.client = chromadb.PersistentClient(
            path=f"{KNOWLEDGE_BASE_DIR}/{self.client_id}/{self.agent_name}",
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )

    def add_document(
        self,
        document_id: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        """Add a document to the knowledge base"""
        metadata = metadata or {}
        metadata['agent'] = self.agent_name
        metadata['client_id'] = self.client_id

        self.collection.add(
            documents=[content],
            ids=[document_id],
            metadatas=[metadata]
        )

    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> List[Dict]:
        """Search for similar documents"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where
        )

        documents = []
        for i, doc in enumerate(results['documents'][0]):
            documents.append({
                'id': results['ids'][0][i],
                'content': doc,
                'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                'distance': results['distances'][0][i] if results['distances'] else None
            })

        return documents

    def delete_document(self, document_id: str):
        """Delete a document from knowledge base"""
        self.collection.delete(ids=[document_id])

    def get_count(self) -> int:
        """Get number of documents in collection"""
        return self.count()

    def count(self) -> int:
        """Get number of documents"""
        return self.collection.count()

    def clear(self):
        """Clear all documents from collection"""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )


class KnowledgeBaseManager:
    """
    Manages knowledge bases for all agents, scoped per client.
    """

    def __init__(self, client_id: str = "internal"):
        self.client_id = client_id
        self.agents = ['researcher', 'writer', 'developer', 'designer', 'analyst']
        self.pipelines: Dict[str, RAGPipeline] = {}
        self._init_pipelines()

    def _init_pipelines(self):
        """Initialize pipelines for all agents"""
        for agent in self.agents:
            self.pipelines[agent] = RAGPipeline(agent, client_id=self.client_id)

    def get_pipeline(self, agent_name: str) -> RAGPipeline:
        """Get pipeline for specific agent"""
        agent = agent_name.lower()
        if agent not in self.pipelines:
            self.pipelines[agent] = RAGPipeline(agent, client_id=self.client_id)
        return self.pipelines[agent]

    def search_all(
        self,
        query: str,
        n_results: int = 3
    ) -> Dict[str, List[Dict]]:
        """Search across all agent knowledge bases"""
        results = {}
        for agent, pipeline in self.pipelines.items():
            results[agent] = pipeline.search(query, n_results)
        return results

    def add_to_agent(
        self,
        agent_name: str,
        document_id: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        """Add document to specific agent's knowledge base"""
        pipeline = self.get_pipeline(agent_name)
        pipeline.add_document(document_id, content, metadata)

    def get_agent_knowledge_count(self, agent_name: str) -> int:
        """Get document count for an agent"""
        pipeline = self.get_pipeline(agent_name)
        return pipeline.get_count()


def get_client_rag(client_id: str = "internal") -> KnowledgeBaseManager:
    """Get or create a client-scoped RAG pipeline manager (cached)."""
    if client_id not in _pipelines:
        _pipelines[client_id] = {}
    return _pipelines[client_id].setdefault(
        "rag", KnowledgeBaseManager(client_id=client_id)
    )


# AgentsKB API integration for DEVELOPER agent
class AgentsKBClient:
    """
    Client for AgentsKB API - free technical knowledge base.
    https://agentskb.com/docs/
    """
    
    BASE_URL = "https://agentskb-api.agentskb.com/api/free"
    
    def __init__(self):
        pass  # No API key needed
    
    def search(self, query: str, domain: str = None) -> List[Dict]:
        """
        Search AgentsKB for technical questions.
        
        Args:
            query: The question to search for
            domain: Optional domain filter (e.g., 'python', 'javascript')
        
        Returns:
            List of answers with sources
        """
        import requests
        
        url = f"{self.BASE_URL}/search"
        params = {'q': query}
        if domain:
            params['domain'] = domain
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            return []
        except Exception as e:
            print(f"AgentsKB search error: {e}")
            return []
    
    def get_answer(self, question: str) -> Optional[Dict]:
        """
        Get a direct answer to a question.
        
        Args:
            question: The question to answer
        
        Returns:
            Dict with answer and source, or None
        """
        results = self.search(question)
        if results:
            return {
                'answer': results[0].get('answer', ''),
                'source': results[0].get('source', ''),
                'confidence': results[0].get('confidence', 0)
            }
        return None


# Default instance
agentskb_client = AgentsKBClient()


if __name__ == "__main__":
    # Test client-scoped knowledge base
    kb = get_client_rag("internal")

    # Add sample document to researcher
    kb.add_to_agent(
        'researcher',
        'doc_001',
        'Machine learning is a subset of artificial intelligence that enables systems to learn from data.',
        {'source': 'test', 'topic': 'AI'}
    )

    # Search
    results = kb.search_all('What is machine learning?', n_results=2)
    for agent, docs in results.items():
        print(f"\n{agent.upper()}:")
        for doc in docs:
            print(f"  - {doc['content'][:80]}...")
