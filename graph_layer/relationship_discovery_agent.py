"""
Relationship Discovery Agent — finds cross-file entity links in Neo4j.

Strategy:
1. Query Neo4j for all entity names grouped by source file.
2. Find candidate cross-file matches:
   a. Exact name matches across different source files.
   b. Fuzzy / normalised matches (snake_case → CamelCase, strip prefixes).
3. Send candidate pairs to LLM to confirm relationship type and confidence.
4. Write confirmed cross-file edges back to Neo4j with `cross_file=true` flag.

Cross-file relationship types used:
  FEEDS_INTO            — data produced by source flows into target
  SEMANTICALLY_EQUIVALENT_TO — same logical entity named differently
  DERIVES_FROM          — target is computed/derived from source
  SHARED_BY             — entity is used by both source files (read-only sharing)
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv

from .neo4j_client import Neo4jClient

load_dotenv()

# ── LLM import (reuses existing KAIRIX LLM client) ────────────────────────────
try:
    from knowledge_engineering_agent.services.llm_client import LLMClient
    _HAS_LLM = True
except ImportError:
    _HAS_LLM = False


_CROSS_FILE_PROMPT = """You are a legacy system reverse-engineering expert.

Below are pairs of entities that appear in DIFFERENT source files of a large insurance system.
Determine for each pair:
1. Are they the SAME logical entity (same table / object) referenced by different files? (yes/no)
2. If yes, what is the direction of the data relationship?
   - FEEDS_INTO: the source file produces/writes to it, the target file reads from it
   - SEMANTICALLY_EQUIVALENT_TO: same entity, no clear directional flow
   - DERIVES_FROM: target entity is derived/calculated from source entity
   - SHARED_BY: both files only READ from this entity

Source files in this system are: SQL reports, SSIS ETL packages, and COBOL mainframe programs.

Candidate pairs (JSON):
{candidates}

Return ONLY a JSON array:
[
  {{
    "source_entity_id": "...",
    "target_entity_id": "...",
    "relationship_type": "FEEDS_INTO|SEMANTICALLY_EQUIVALENT_TO|DERIVES_FROM|SHARED_BY|UNRELATED",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
  }},
  ...
]
Return UNRELATED for pairs that are NOT the same entity.
"""


class RelationshipDiscoveryAgent:
    """
    LLM-powered cross-file relationship discovery.

    Usage:
        agent = RelationshipDiscoveryAgent(neo4j_client)
        result = agent.discover()
        print(f"Found {result['cross_file_edges']} cross-file relationships")
    """

    def __init__(
        self,
        client: Neo4jClient,
        confidence_threshold: float = 0.6,
        max_candidates_per_batch: int = 20,
    ):
        self.client = client
        self.confidence_threshold = confidence_threshold
        self.max_candidates_per_batch = max_candidates_per_batch
        self._llm: Optional[Any] = None
        if _HAS_LLM:
            self._llm = LLMClient()

    # ── Public API ─────────────────────────────────────────────────────────────

    def discover(self) -> Dict[str, int]:
        """
        Run full cross-file relationship discovery pipeline.

        Returns stats dict.
        """
        print("[RelationshipDiscovery] Querying Neo4j for all entities...")
        candidates = self._find_candidates()
        print(f"[RelationshipDiscovery] Found {len(candidates)} candidate cross-file pairs.")

        if not candidates:
            print("[RelationshipDiscovery] No candidates found. Graph may need entities loaded first.")
            return {"candidates": 0, "cross_file_edges": 0}

        confirmed = self._classify_with_llm(candidates)
        written = self._write_edges(confirmed)

        print(f"[RelationshipDiscovery] Written {written} cross-file edges to Neo4j.")
        return {"candidates": len(candidates), "cross_file_edges": written}

    # ── Step 1: Find candidate pairs ──────────────────────────────────────────

    def _find_candidates(self) -> List[Dict[str, Any]]:
        """
        Find entities with the same normalised name appearing in different source files.
        """
        # Query all entities with their source file
        records = self.client.run_query(
            """
            MATCH (e:Entity)
            WHERE e.name IS NOT NULL AND e.source_file IS NOT NULL
            RETURN e.id AS id, e.name AS name, e.entity_type AS entity_type,
                   e.source_file AS source_file
            """
        )

        # Group by normalised name
        from collections import defaultdict
        name_groups: Dict[str, List[Dict]] = defaultdict(list)
        for rec in records:
            norm = self._normalise_name(rec.get("name", ""))
            if norm:
                name_groups[norm].append(rec)

        candidates = []
        for norm_name, entities in name_groups.items():
            # Only interested in entities appearing in MULTIPLE files
            source_files = {e["source_file"] for e in entities}
            if len(source_files) < 2:
                continue

            # Generate pairs across different files
            for i, e1 in enumerate(entities):
                for e2 in entities[i + 1 :]:
                    if e1["source_file"] != e2["source_file"]:
                        candidates.append(
                            {
                                "source_entity_id": e1["id"],
                                "source_entity_name": e1["name"],
                                "source_entity_type": e1.get("entity_type", ""),
                                "source_file": e1["source_file"],
                                "target_entity_id": e2["id"],
                                "target_entity_name": e2["name"],
                                "target_entity_type": e2.get("entity_type", ""),
                                "target_file": e2["source_file"],
                                "normalised_name": norm_name,
                            }
                        )

        return candidates

    # ── Step 2: LLM classification ────────────────────────────────────────────

    def _classify_with_llm(
        self, candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Send candidate batches to LLM for relationship classification."""
        if not self._llm:
            print("[RelationshipDiscovery] No LLM available — using heuristic fallback.")
            return self._heuristic_classify(candidates)

        confirmed = []
        for i in range(0, len(candidates), self.max_candidates_per_batch):
            batch = candidates[i : i + self.max_candidates_per_batch]
            print(
                f"[RelationshipDiscovery] LLM classifying batch "
                f"{i // self.max_candidates_per_batch + 1} "
                f"({len(batch)} pairs)..."
            )
            try:
                prompt = _CROSS_FILE_PROMPT.format(
                    candidates=json.dumps(batch, indent=2)
                )
                response = self._llm.complete(prompt, temperature=0.1)
                results = self._parse_llm_response(response)
                confirmed.extend(results)
            except Exception as e:
                print(f"[RelationshipDiscovery] LLM batch error: {e}. Using heuristic.")
                confirmed.extend(self._heuristic_classify(batch))

        return [
            r for r in confirmed
            if r.get("relationship_type", "UNRELATED") != "UNRELATED"
            and r.get("confidence", 0.0) >= self.confidence_threshold
        ]

    def _parse_llm_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse JSON array from LLM response."""
        # Strip markdown code fences if present
        cleaned = re.sub(r"```(?:json)?", "", response).strip().strip("`")
        # Find JSON array
        match = re.search(r"\[.*\]", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return []

    def _heuristic_classify(
        self, candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Simple heuristic fallback when LLM is unavailable.
        Assumes exact name matches across SSIS + SQL are FEEDS_INTO.
        COBOL + SQL pairs are DERIVES_FROM.
        Others are SEMANTICALLY_EQUIVALENT_TO.
        """
        results = []
        for c in candidates:
            src_file = c.get("source_file", "")
            tgt_file = c.get("target_file", "")
            if (".dtsx" in src_file and ".sql" in tgt_file) or (
                ".sql" in src_file and ".dtsx" in tgt_file
            ):
                rel = "FEEDS_INTO"
            elif ".cbl" in src_file.lower() or ".cbl" in tgt_file.lower():
                rel = "DERIVES_FROM"
            else:
                rel = "SEMANTICALLY_EQUIVALENT_TO"

            results.append(
                {
                    "source_entity_id": c["source_entity_id"],
                    "target_entity_id": c["target_entity_id"],
                    "relationship_type": rel,
                    "confidence": 0.7,
                    "reasoning": "Heuristic: file type cross-reference",
                }
            )
        return results

    # ── Step 3: Write confirmed edges ──────────────────────────────────────────

    def _write_edges(self, confirmed: List[Dict[str, Any]]) -> int:
        """Write confirmed cross-file edges into Neo4j."""
        written = 0
        for edge in confirmed:
            rel_type = edge.get("relationship_type", "RELATES_TO").upper().replace(" ", "_")
            try:
                self.client.run_write(
                    f"""
                    MATCH (src:Entity {{id: $src_id}})
                    MATCH (tgt:Entity {{id: $tgt_id}})
                    MERGE (src)-[r:{rel_type}]->(tgt)
                    SET r.confidence  = $confidence,
                        r.reasoning   = $reasoning,
                        r.cross_file  = true,
                        r.discovered_by = 'RelationshipDiscoveryAgent'
                    """,
                    {
                        "src_id": edge["source_entity_id"],
                        "tgt_id": edge["target_entity_id"],
                        "confidence": edge.get("confidence", 0.7),
                        "reasoning": edge.get("reasoning", ""),
                    },
                )
                written += 1
            except Exception as ex:
                print(f"[RelationshipDiscovery] Edge write error: {ex}")
        return written

    # ── Utilities ──────────────────────────────────────────────────────────────

    @staticmethod
    def _normalise_name(name: str) -> str:
        """
        Normalise entity names for comparison:
          - lowercase
          - strip common prefixes (pc_, cc_, pcx_, bc_)
          - replace non-alphanumeric with underscores
          - strip trailing underscores
        """
        if not name:
            return ""
        n = name.lower().strip()
        # Strip common Guidewire table prefixes
        for prefix in ("pcx_", "pc_", "ccx_", "cc_", "bc_", "ab_"):
            if n.startswith(prefix):
                n = n[len(prefix):]
                break
        n = re.sub(r"[^a-z0-9]+", "_", n).strip("_")
        return n
