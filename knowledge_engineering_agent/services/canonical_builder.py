from __future__ import annotations

import uuid
from typing import Any

from ..models.knowledge_models import (
    ArtifactKnowledgeProfile,
    CanonicalMetadata,
    GraphEdge,
    GraphNode,
    KnowledgePackage,
    ReconciliationReport,
    SourceMetadata,
    SourceSummary,
)
from .normalizer import KnowledgeNormalizer
from .validator import KnowledgeValidator


class CanonicalPackageBuilder:
    """
    Constructs CanonicalMetadata and the final unified KnowledgePackage,
    including node and edge projections directly consumable by Neo4j.
    """

    def __init__(self):
        self.normalizer = KnowledgeNormalizer()
        self.validator = KnowledgeValidator()

    def build_canonical_metadata(
        self,
        parser_output: dict[str, Any],
        summary: SourceSummary,
        knowledge_profile: ArtifactKnowledgeProfile,
        reconciliation: ReconciliationReport,
    ) -> CanonicalMetadata:
        extracted_facts = {
            "tables": [e.name for e in knowledge_profile.entities if e.entity_type == "TABLE"],
            "columns": [e.name for e in knowledge_profile.entities if e.entity_type == "COLUMN"],
            "parser_summary": parser_output.get("summary", parser_output.get("statistics", {})),
        }

        documented_knowledge = {
            "purpose": summary.purpose,
            "narrative": summary.high_level_narrative,
            "business_domain": summary.business_domain,
            "business_rules": summary.business_rules,
            "key_logic": knowledge_profile.key_logic,
        }

        inferred_knowledge = {
            "inferred_entities": reconciliation.inferred_entities,
            "transformations": [t.model_dump() for t in knowledge_profile.transformations],
            "lineage_relationships": [r.model_dump() for r in reconciliation.reconciled_relationships],
            "gaps": reconciliation.gaps_detected,
        }

        return CanonicalMetadata(
            extracted_facts=extracted_facts,
            documented_knowledge=documented_knowledge,
            inferred_knowledge=inferred_knowledge,
            overall_confidence=reconciliation.overall_confidence,
        )

    def build_graph_elements(
        self,
        source: SourceMetadata,
        knowledge_profile: ArtifactKnowledgeProfile,
        reconciliation: ReconciliationReport,
    ) -> tuple[list[GraphNode], list[GraphEdge]]:
        nodes: dict[str, GraphNode] = {}
        edges: list[GraphEdge] = []

        # 1. Source Artifact Node
        root_node_id = f"ARTIFACT:{source.file_name}"
        nodes[root_node_id] = GraphNode(
            id=root_node_id,
            label="Artifact",
            properties={
                "name": source.file_name,
                "source_type": source.source_type,
                "file_path": source.file_path,
                "total_lines": source.total_lines,
            },
        )

        # 2. Entity Nodes
        for entity in knowledge_profile.entities:
            clean_name = self.normalizer.clean_identifier(entity.name)
            node_id = f"{entity.entity_type}:{clean_name}"
            if node_id not in nodes:
                nodes[node_id] = GraphNode(
                    id=node_id,
                    label=entity.entity_type.capitalize(),
                    properties={
                        "name": clean_name,
                        "entity_type": entity.entity_type,
                        "data_type": entity.data_type,
                        "parent": entity.parent_entity,
                        "line_number": entity.line_number,
                    },
                )

            # Link Artifact -> Entity
            edges.append(
                GraphEdge(
                    source_id=root_node_id,
                    target_id=node_id,
                    type="CONTAINS",
                    properties={"source_type": source.source_type},
                )
            )

        # 3. Transformation Nodes
        for tr in knowledge_profile.transformations:
            tr_id = f"TRANSFORMATION:{source.file_name}:{tr.rule_id}"
            nodes[tr_id] = GraphNode(
                id=tr_id,
                label="Transformation",
                properties={
                    "rule_id": tr.rule_id,
                    "rule_type": tr.rule_type,
                    "description": tr.description,
                    "expression": tr.expression,
                    "line_number": tr.line_number,
                },
            )

            # Link Source Entities -> Transformation -> Target Entities
            for src in tr.source_entities:
                src_clean = self.normalizer.clean_identifier(src)
                src_id = f"COLUMN:{src_clean}" if "." in src_clean else f"TABLE:{src_clean}"
                if src_id in nodes:
                    edges.append(
                        GraphEdge(
                            source_id=src_id,
                            target_id=tr_id,
                            type="INPUT_TO",
                            properties={},
                        )
                    )

            for tgt in tr.target_entities:
                tgt_clean = self.normalizer.clean_identifier(tgt)
                tgt_id = f"COLUMN:{tgt_clean}" if "." in tgt_clean else f"TABLE:{tgt_clean}"
                if tgt_id in nodes:
                    edges.append(
                        GraphEdge(
                            source_id=tr_id,
                            target_id=tgt_id,
                            type="OUTPUT_TO",
                            properties={},
                        )
                    )

        # 4. Reconciled Lineage Edges
        for rel in reconciliation.reconciled_relationships:
            src_clean = self.normalizer.clean_identifier(rel.source)
            tgt_clean = self.normalizer.clean_identifier(rel.target)

            src_id = f"TABLE:{src_clean}"
            tgt_id = f"TABLE:{tgt_clean}"

            edges.append(
                GraphEdge(
                    source_id=src_id,
                    target_id=tgt_id,
                    type=rel.relationship_type,
                    properties={
                        "confidence": rel.confidence,
                        "evidence_line": rel.evidence_line,
                        "description": rel.description,
                    },
                )
            )

        return list(nodes.values()), edges

    def build_package(
        self,
        source: SourceMetadata,
        summary: SourceSummary,
        knowledge_profile: ArtifactKnowledgeProfile,
        reconciliation: ReconciliationReport,
        parser_output: dict[str, Any],
    ) -> KnowledgePackage:
        canonical_meta = self.build_canonical_metadata(
            parser_output=parser_output,
            summary=summary,
            knowledge_profile=knowledge_profile,
            reconciliation=reconciliation,
        )

        nodes, edges = self.build_graph_elements(
            source=source,
            knowledge_profile=knowledge_profile,
            reconciliation=reconciliation,
        )

        pkg_id = f"PKG-{source.source_type.upper()}-{source.file_name}-{uuid.uuid4().hex[:8]}"

        pkg_data = {
            "package_id": pkg_id,
            "source": source.model_dump(),
            "summary": summary.model_dump(),
            "knowledge_profile": knowledge_profile.model_dump(),
            "reconciliation": reconciliation.model_dump(),
            "canonical_metadata": canonical_meta.model_dump(),
            "graph_nodes": [n.model_dump() for n in nodes],
            "graph_edges": [e.model_dump() for e in edges],
        }

        return self.validator.validate_knowledge_package(pkg_data)
