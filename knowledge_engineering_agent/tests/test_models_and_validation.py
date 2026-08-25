from __future__ import annotations

import unittest
from knowledge_engineering_agent.models.knowledge_models import (
    ArtifactKnowledgeProfile,
    CanonicalMetadata,
    EntityItem,
    KnowledgePackage,
    ReconciliationReport,
    RelationshipItem,
    SourceMetadata,
    SourceSummary,
    TransformationRule,
)
from knowledge_engineering_agent.services.normalizer import KnowledgeNormalizer
from knowledge_engineering_agent.services.validator import KnowledgeValidator, KnowledgeValidationError


class TestModelsAndValidation(unittest.TestCase):

    def setUp(self):
        self.validator = KnowledgeValidator()
        self.normalizer = KnowledgeNormalizer()

    def test_normalizer(self):
        self.assertEqual(self.normalizer.clean_identifier("[dbo].[pc_policy]"), "dbo.pc_policy")
        self.assertEqual(self.normalizer.normalize_relationship_type("reads"), "READS_FROM")
        self.assertEqual(self.normalizer.normalize_relationship_type("transforms"), "TRANSFORMS")
        self.assertEqual(self.normalizer.normalize_entity_type("field"), "COLUMN")
        self.assertEqual(self.normalizer.normalize_entity_type("tables"), "TABLE")

    def test_source_summary_validation(self):
        data = {
            "purpose": "Calculate earned premium",
            "high_level_narrative": "Reads policy records and calculates earned premium by month.",
            "business_domain": "Premium Accounting",
            "inputs": ["POLICY_FILE", "TRANSACTIONS"],
            "outputs": ["EARNED_PREM_TABLE"],
            "key_transformations": ["Sum premium per policy"],
            "key_dependencies": ["COMMUN.CPY"],
            "business_rules": ["Earned premium calculated pro-rata by elapsed days."],
        }
        summary = self.validator.validate_source_summary(data)
        self.assertIsInstance(summary, SourceSummary)
        self.assertEqual(summary.purpose, "Calculate earned premium")

    def test_knowledge_package_validation(self):
        source = SourceMetadata(
            file_path="source/sql/sample.sql",
            file_name="sample.sql",
            source_type="sql",
            file_extension=".sql",
            total_lines=100,
            size_bytes=2048,
        )
        summary = SourceSummary(
            purpose="Extract customer totals",
            high_level_narrative="Joins customers with transactions.",
            business_domain="Policy",
            inputs=["customer", "transactions"],
            outputs=["customer_totals"],
            key_transformations=["SUM(amount)"],
            key_dependencies=[],
            business_rules=["Only active transactions"],
        )
        profile = ArtifactKnowledgeProfile(
            file_name="sample.sql",
            source_type="sql",
            purpose="Extract customer totals",
            inputs_outputs={"inputs": ["customer"], "outputs": ["customer_totals"]},
            key_logic=["1. Join customer on id", "2. Group by customer_id"],
            entities=[
                EntityItem(name="customer", entity_type="TABLE"),
                EntityItem(name="customer_id", entity_type="COLUMN", parent_entity="customer"),
            ],
            transformations=[
                TransformationRule(
                    rule_id="TR_01",
                    rule_type="AGGREGATION",
                    description="Aggregate sum of transactions",
                    source_entities=["amount"],
                    target_entities=["total_amount"],
                )
            ],
            business_rules=["Active status filter"],
            dependencies=["customer"],
            relationships=[
                RelationshipItem(
                    source="customer",
                    target="customer_totals",
                    relationship_type="TRANSFORMS",
                )
            ],
            confidence=0.95,
        )
        reconciliation = ReconciliationReport(
            parser_facts_count=5,
            llm_findings_count=4,
            confirmed_entities=["customer"],
            inferred_entities=["customer_totals"],
            reconciled_relationships=[
                RelationshipItem(
                    source="customer",
                    target="customer_totals",
                    relationship_type="TRANSFORMS",
                )
            ],
            discrepancies=[],
            gaps_detected=[],
            overall_confidence=0.95,
        )
        canonical = CanonicalMetadata(
            extracted_facts={"tables": ["customer"]},
            documented_knowledge={"purpose": summary.purpose},
            inferred_knowledge={"transformations": ["TR_01"]},
            overall_confidence=0.95,
        )

        pkg_data = {
            "package_id": "PKG-SQL-sample-001",
            "source": source.model_dump(),
            "summary": summary.model_dump(),
            "knowledge_profile": profile.model_dump(),
            "reconciliation": reconciliation.model_dump(),
            "canonical_metadata": canonical.model_dump(),
            "graph_nodes": [{"id": "TABLE:customer", "label": "Table", "properties": {}}],
            "graph_edges": [{"source_id": "TABLE:customer", "target_id": "TABLE:customer_totals", "type": "TRANSFORMS", "properties": {}}],
        }

        pkg = self.validator.validate_knowledge_package(pkg_data)
        self.assertIsInstance(pkg, KnowledgePackage)
        self.assertEqual(pkg.package_id, "PKG-SQL-sample-001")


if __name__ == "__main__":
    unittest.main()
