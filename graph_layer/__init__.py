"""
Graph Layer — Neo4j Knowledge Graph for KAIRIX.

Exposes:
  Neo4jClient          — low-level driver wrapper
  GraphLoader          — bulk-loads KnowledgePackages into Neo4j
  RelationshipDiscoveryAgent — cross-file relationship discovery via LLM
"""

from .neo4j_client import Neo4jClient
from .graph_loader import GraphLoader
from .relationship_discovery_agent import RelationshipDiscoveryAgent

__all__ = ["Neo4jClient", "GraphLoader", "RelationshipDiscoveryAgent"]
