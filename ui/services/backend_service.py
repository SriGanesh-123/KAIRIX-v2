"""
Backend Service for KAIRIX UI.

Wraps connectivity checks and live graph/vector DB queries with robust exception handling.
Never exposes sensitive API keys, passwords, or raw secrets.
"""
from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()


class BackendService:
    """
    Provides safe access to backend health, dynamic database statistics, and connectivity state.
    """

    @staticmethod
    def check_neo4j_connection() -> Dict[str, Any]:
        """
        Verify Neo4j connectivity and return connection status and summary counts.
        """
        uri = os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687")
        start = time.perf_counter()
        try:
            from graph_layer.neo4j_client import Neo4jClient
            with Neo4jClient(silent=True) as client:
                res_nodes = client.run_query("MATCH (n) RETURN count(n) AS total_nodes")
                res_rels = client.run_query("MATCH ()-[r]->() RETURN count(r) AS total_rels")
                latency = round((time.perf_counter() - start) * 1000, 1)

                total_nodes = res_nodes[0]["total_nodes"] if res_nodes else 0
                total_rels = res_rels[0]["total_rels"] if res_rels else 0

                return {
                    "connected": True,
                    "status": "connected",
                    "uri": uri,
                    "latency_ms": latency,
                    "total_nodes": total_nodes,
                    "total_relationships": total_rels,
                    "message": f"Connected to {uri} ({latency}ms)",
                }
        except Exception as e:
            latency = round((time.perf_counter() - start) * 1000, 1)
            return {
                "connected": False,
                "status": "disconnected",
                "uri": uri,
                "latency_ms": latency,
                "total_nodes": 0,
                "total_relationships": 0,
                "message": f"Neo4j is currently unavailable ({e}). Please verify Neo4j service is running at {uri}.",
            }

    @staticmethod
    def check_qdrant_connection() -> Dict[str, Any]:
        """
        Verify Qdrant vector database connectivity and return collection counts.
        """
        url = os.getenv("QDRANT_URL", "http://localhost:6335")
        start = time.perf_counter()
        try:
            from vector_layer.qdrant_client_wrapper import (
                QdrantWrapper,
                COLLECTION_CHUNKS,
                COLLECTION_SUMMARIES,
            )
            with QdrantWrapper(silent=True) as qdrant:
                chunks_count = qdrant.collection_count(COLLECTION_CHUNKS)
                summaries_count = qdrant.collection_count(COLLECTION_SUMMARIES)
                latency = round((time.perf_counter() - start) * 1000, 1)

                return {
                    "connected": True,
                    "status": "connected",
                    "url": url,
                    "latency_ms": latency,
                    "chunks_count": chunks_count,
                    "summaries_count": summaries_count,
                    "total_points": chunks_count + summaries_count,
                    "message": f"Connected to {url} ({chunks_count} chunks, {summaries_count} summaries)",
                }
        except Exception as e:
            latency = round((time.perf_counter() - start) * 1000, 1)
            return {
                "connected": False,
                "status": "disconnected",
                "url": url,
                "latency_ms": latency,
                "chunks_count": 0,
                "summaries_count": 0,
                "total_points": 0,
                "message": f"Qdrant is currently unavailable ({e}). Please verify Qdrant is running at {url}.",
            }

    @staticmethod
    def check_llm_status() -> Dict[str, Any]:
        """
        Verify LLM configuration without revealing API keys or secrets.
        """
        provider = os.getenv("LLM_PROVIDER", "nim").lower().strip()
        model = os.getenv("NIM_MODEL", "openai/gpt-oss-120b")
        api_key = os.getenv("NVIDIA_NIM_API_KEY", "") or os.getenv("GROQ_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")

        is_configured = bool(api_key.strip())
        masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else ("Configured" if is_configured else "Not Set")

        return {
            "configured": is_configured,
            "status": "configured" if is_configured else "missing_key",
            "provider": provider.upper(),
            "model": model,
            "masked_key": masked_key,
            "message": f"Provider: {provider.upper()} | Model: {model}",
        }

    @staticmethod
    def check_embedding_status() -> Dict[str, Any]:
        """
        Check local embedding model configuration.
        """
        model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        return {
            "status": "ready",
            "model": model_name,
            "dimension": 384,
            "message": f"SentenceTransformer: {model_name} (dim=384)",
        }

    @classmethod
    def get_graph_statistics(cls) -> Dict[str, Any]:
        """
        Query Neo4j dynamically for comprehensive live graph counts.
        """
        fallback_stats = {
            "artifacts": 0,
            "entities": 0,
            "relationships": 0,
            "business_rules": 0,
            "transformations": 0,
            "cobol_count": 0,
            "sql_count": 0,
            "ssis_count": 0,
            "top_entities": [],
            "source_distribution": {"cobol": 0, "sql": 0, "ssis": 0},
            "connected": False,
        }

        try:
            from graph_layer.neo4j_client import Neo4jClient
            with Neo4jClient(silent=True) as client:
                # Basic node label counts
                res_art = client.run_query("MATCH (a:Artifact) RETURN count(a) AS c")
                res_ent = client.run_query("MATCH (e:Entity) RETURN count(e) AS c")
                res_rel = client.run_query("MATCH ()-[r]->() RETURN count(r) AS c")
                res_rule = client.run_query("MATCH (b:BusinessRule) RETURN count(b) AS c")
                res_tf = client.run_query("MATCH (t:Transformation) RETURN count(t) AS c")

                # Source type breakdown
                res_types = client.run_query(
                    """
                    MATCH (a:Artifact)
                    RETURN toLower(a.source_type) AS stype, count(a) AS cnt
                    """
                )
                source_dist = {"cobol": 0, "sql": 0, "ssis": 0}
                for row in res_types:
                    st = row.get("stype", "").lower()
                    if "cobol" in st or "cbl" in st:
                        source_dist["cobol"] += row.get("cnt", 0)
                    elif "sql" in st:
                        source_dist["sql"] += row.get("cnt", 0)
                    elif "ssis" in st or "dtsx" in st:
                        source_dist["ssis"] += row.get("cnt", 0)
                    else:
                        source_dist[st] = row.get("cnt", 0)

                # Most connected entities for dashboard summary
                res_top = client.run_query(
                    """
                    MATCH (e:Entity)-[r]-()
                    RETURN e.name AS name, e.entity_type AS type, e.source_file AS source_file, count(r) AS degree
                    ORDER BY degree DESC
                    LIMIT 10
                    """
                )

                artifacts = res_art[0]["c"] if res_art else 0
                entities = res_ent[0]["c"] if res_ent else 0
                relationships = res_rel[0]["c"] if res_rel else 0
                business_rules = res_rule[0]["c"] if res_rule else 0
                transformations = res_tf[0]["c"] if res_tf else 0

                return {
                    "artifacts": artifacts,
                    "entities": entities,
                    "relationships": relationships,
                    "business_rules": business_rules,
                    "transformations": transformations,
                    "cobol_count": source_dist.get("cobol", 0),
                    "sql_count": source_dist.get("sql", 0),
                    "ssis_count": source_dist.get("ssis", 0),
                    "source_distribution": source_dist,
                    "top_entities": res_top,
                    "connected": True,
                }
        except Exception:
            return fallback_stats

    @classmethod
    def get_system_health(cls) -> Dict[str, Any]:
        """
        Run full platform health check.
        """
        neo4j_info = cls.check_neo4j_connection()
        qdrant_info = cls.check_qdrant_connection()
        llm_info = cls.check_llm_status()
        embed_info = cls.check_embedding_status()

        all_ok = neo4j_info["connected"] and qdrant_info["connected"] and llm_info["configured"]
        overall_status = "healthy" if all_ok else ("degraded" if (neo4j_info["connected"] or qdrant_info["connected"]) else "offline")

        return {
            "overall_status": overall_status,
            "neo4j": neo4j_info,
            "qdrant": qdrant_info,
            "llm": llm_info,
            "embedding": embed_info,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
