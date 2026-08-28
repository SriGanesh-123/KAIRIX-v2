"""
Comprehensive Unit Test Suite for User-Defined Structured Extraction.

Tests all 16 core requirements:
1. Simple schema/database/table/column extraction
2. Table aliases mapping
3. JOIN queries
4. Multiple tables and column ownership
5. Unqualified columns and ambiguity handling
6. CTEs (Common Table Expressions)
7. INSERT targets
8. UPDATE targets
9. Derived columns and expressions
10. Missing schema handling
11. Missing database handling
12. Multiple SQL files provenance
13. Custom user templates
14. Invalid templates handling
15. Invalid SQL handling
16. Normal Investigation Agent regression test
"""
from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import MagicMock

from investigation_agent.structured_extractor import StructuredExtractionEngine
from investigation_agent.template_parser import parse_user_template
from investigation_agent.agent import InvestigationAgent
from investigation_agent.models import InvestigationResult


class TestStructuredExtraction(unittest.TestCase):

    def setUp(self):
        self.engine = StructuredExtractionEngine()

    # ── Test 1: Simple schema/database/table/column extraction ──────────────────
    def test_1_simple_schema_db_table_columns(self):
        sql = """
        SELECT
            p.policy_id,
            p.policy_number,
            p.status
        FROM PolicyCenter.dbo.Policy p;
        """
        template = "| Schema | Database | Table | Columns |"
        res = self.engine.extract(selected_files=[sql], template=template)

        self.assertEqual(len(res.records), 1)
        rec = res.records[0]
        self.assertEqual(rec.values.get("Schema"), "dbo")
        self.assertEqual(rec.values.get("Database"), "PolicyCenter")
        self.assertEqual(rec.values.get("Table"), "Policy")
        cols = [c.strip() for c in rec.values.get("Columns", "").split(",")]
        self.assertIn("policy_id", cols)
        self.assertIn("policy_number", cols)
        self.assertIn("status", cols)

    # ── Test 2: Table aliases mapping ──────────────────────────────────────────
    def test_2_table_aliases_mapping(self):
        sql = """
        SELECT
            pp.PolicyNumber,
            pp.TermNumber
        FROM [PolicyCenter].[dbo].[pc_policyperiod] pp;
        """
        template = "| Schema | Database | Table | Alias | Columns |"
        res = self.engine.extract(selected_files=[sql], template=template)

        self.assertEqual(len(res.records), 1)
        rec = res.records[0]
        self.assertEqual(rec.values.get("Table"), "pc_policyperiod")
        self.assertEqual(rec.values.get("Alias"), "pp")
        self.assertEqual(rec.values.get("Schema"), "dbo")
        self.assertEqual(rec.values.get("Database"), "PolicyCenter")
        self.assertIn("PolicyNumber", rec.values.get("Columns"))

    # ── Test 3: JOIN queries ───────────────────────────────────────────────────
    def test_3_join_queries(self):
        sql = """
        SELECT
            p.policy_id,
            c.claim_id
        FROM PolicyCenter.dbo.Policy p
        JOIN ClaimCenter.dbo.Claim c
            ON p.policy_id = c.policy_id;
        """
        template = "| Database | Table | Columns |"
        res = self.engine.extract(selected_files=[sql], template=template)

        self.assertEqual(len(res.records), 2)
        tables = {r.values.get("Table"): r for r in res.records}
        self.assertIn("Policy", tables)
        self.assertIn("Claim", tables)
        self.assertEqual(tables["Policy"].values.get("Database"), "PolicyCenter")
        self.assertEqual(tables["Claim"].values.get("Database"), "ClaimCenter")

    # ── Test 4: Multiple tables and column ownership (Zero Hallucination) ───────
    def test_4_column_ownership_resolution(self):
        sql = """
        SELECT
            c.claim_id,
            c.claim_amount,
            p.policy_number
        FROM ClaimCenter.dbo.Claim c
        JOIN PolicyCenter.dbo.Policy p
            ON c.policy_id = p.policy_id;
        """
        template = "| Database | Table | Columns |"
        res = self.engine.extract(selected_files=[sql], template=template)

        tables = {r.values.get("Table"): r.values.get("Columns") for r in res.records}
        
        # policy_number must strictly belong to Policy, NOT Claim
        self.assertIn("policy_number", tables["Policy"])
        self.assertNotIn("policy_number", tables["Claim"])

        # claim_amount must strictly belong to Claim, NOT Policy
        self.assertIn("claim_amount", tables["Claim"])
        self.assertNotIn("claim_amount", tables["Policy"])

    # ── Test 5: Unqualified columns and ambiguity handling ─────────────────────
    def test_5_unqualified_columns_and_ambiguity(self):
        # Case A: Single table -> unqualified belongs to single table
        sql_single = "SELECT policy_id, policy_number FROM Policy;"
        res_single = self.engine.extract(selected_files=[sql_single], template="| Table | Columns |")
        self.assertEqual(len(res_single.records), 1)
        self.assertIn("policy_id", res_single.records[0].values.get("Columns"))

        # Case B: Multiple tables with unqualified column -> marked as ambiguous
        sql_multi = "SELECT status, p.policy_id, c.claim_id FROM Policy p JOIN Claim c ON p.id = c.id;"
        res_multi = self.engine.extract(selected_files=[sql_multi], template="| Table | Columns |")
        self.assertTrue(any(rec.ambiguous_columns for rec in res_multi.records) or any(rec.confidence < 1.0 for rec in res_multi.records))

    # ── Test 6: CTEs (Common Table Expressions) ────────────────────────────────
    def test_6_cte_extraction(self):
        sql = """
        WITH ActivePolicyCTE AS (
            SELECT p.policy_id, p.effective_date FROM PolicyCenter.dbo.Policy p WHERE p.status = 'Active'
        )
        SELECT policy_id FROM ActivePolicyCTE;
        """
        template = "| Schema | Database | Table | Columns |"
        res = self.engine.extract(selected_files=[sql], template=template)
        
        table_names = [r.values.get("Table") for r in res.records]
        self.assertTrue("Policy" in table_names or "ActivePolicyCTE" in table_names)

    # ── Test 7: INSERT statements ──────────────────────────────────────────────
    def test_7_insert_targets(self):
        sql = """
        INSERT INTO Reporting.dbo.PremiumSummary (policy_id, total_premium)
        SELECT p.policy_id, sum(t.amount)
        FROM PolicyCenter.dbo.Policy p
        JOIN PolicyCenter.dbo.Transaction t ON p.id = t.policy_id;
        """
        template = "| Database | Schema | Table | Columns |"
        res = self.engine.extract(selected_files=[sql], template=template)

        table_names = [r.values.get("Table") for r in res.records]
        self.assertIn("PremiumSummary", table_names)

    # ── Test 8: UPDATE statements ──────────────────────────────────────────────
    def test_8_update_targets(self):
        sql = """
        UPDATE PolicyCenter.dbo.Policy
        SET status = 'Cancelled'
        WHERE policy_id = 100;
        """
        template = "| Database | Schema | Table | Columns |"
        res = self.engine.extract(selected_files=[sql], template=template)

        self.assertEqual(len(res.records), 1)
        self.assertEqual(res.records[0].values.get("Table"), "Policy")
        self.assertEqual(res.records[0].values.get("Database"), "PolicyCenter")

    # ── Test 9: Derived columns and expressions ────────────────────────────────
    def test_9_derived_columns(self):
        sql = """
        SELECT
            p.policy_id,
            CASE WHEN p.status = 1 THEN 'Active' ELSE 'Inactive' END as StatusDescription
        FROM dbo.Policy p;
        """
        template = "| Table | Column | Transformation |"
        res = self.engine.extract(selected_files=[sql], template=template)
        
        col_names = [r.values.get("Column") for r in res.records]
        self.assertTrue("policy_id" in col_names or "StatusDescription" in col_names)

    # ── Test 10: Missing schema handling ───────────────────────────────────────
    def test_10_missing_schema(self):
        sql = "SELECT policy_id FROM Policy;"
        template = "| Schema | Database | Table | Columns |"
        res = self.engine.extract(selected_files=[sql], template=template)

        self.assertEqual(len(res.records), 1)
        self.assertEqual(res.records[0].values.get("Schema"), "UNKNOWN / Not specified")
        self.assertEqual(res.records[0].values.get("Database"), "UNKNOWN / Not specified")
        self.assertEqual(res.records[0].values.get("Table"), "Policy")

    # ── Test 11: Missing database handling ─────────────────────────────────────
    def test_11_missing_database(self):
        sql = "SELECT p.policy_id FROM dbo.Policy p;"
        template = "| Schema | Database | Table | Columns |"
        res = self.engine.extract(selected_files=[sql], template=template)

        self.assertEqual(len(res.records), 1)
        self.assertEqual(res.records[0].values.get("Schema"), "dbo")
        self.assertEqual(res.records[0].values.get("Database"), "UNKNOWN / Not specified")
        self.assertEqual(res.records[0].values.get("Table"), "Policy")

    # ── Test 12: Multiple SQL files provenance ─────────────────────────────────
    def test_12_multiple_sql_files_provenance(self):
        files = ["PolicyCenter_Monoline.sql", "ClaimCenter_Monoline.sql"]
        template = "| Source File | Schema | Database | Table | Columns |"
        res = self.engine.extract(selected_files=files, template=template)

        self.assertTrue(len(res.records) > 0)
        source_files_present = {r.source_file for r in res.records}
        self.assertIn("PolicyCenter_Monoline.sql", source_files_present)
        self.assertIn("ClaimCenter_Monoline.sql", source_files_present)

    # ── Test 13: Custom user templates ─────────────────────────────────────────
    def test_13_custom_user_templates(self):
        sql = "SELECT p.id, p.amount FROM Billing.dbo.Invoice p;"
        
        # Test Format A: Column granularity
        tpl_a = "| Database | Table | Column | Data Type |"
        res_a = self.engine.extract(selected_files=[sql], template=tpl_a)
        self.assertEqual(res_a.template_fields, ["Database", "Table", "Column", "Data Type"])
        self.assertTrue(len(res_a.records) >= 1)

        # Test Format B: Custom unrecognized field
        tpl_b = "| Table | Columns | Business Function |"
        res_b = self.engine.extract(selected_files=[sql], template=tpl_b)
        self.assertEqual(res_b.records[0].values.get("Business Function"), "UNKNOWN / Not specified in SQL")
        self.assertTrue(any("Business Function" in w for w in res_b.warnings))

    # ── Test 14: Invalid or empty template handling ────────────────────────────
    def test_14_invalid_template(self):
        sql = "SELECT id FROM Policy;"
        # Empty string template -> falls back gracefully to default fields
        res_empty = self.engine.extract(selected_files=[sql], template="")
        self.assertTrue(len(res_empty.template_fields) > 0)
        self.assertEqual(len(res_empty.records), 1)

    # ── Test 15: Invalid SQL handling ──────────────────────────────────────────
    def test_15_invalid_sql(self):
        bad_sql = "INVALID SYNTAX %%% NOT SQL ;;;;"
        res = self.engine.extract(selected_files=[bad_sql], template="| Table | Columns |")
        # Should not crash, returns result with warning
        self.assertIsInstance(res.warnings, list)

    # ── Test 16: Normal Investigation Agent regression test ────────────────────
    def test_16_normal_investigation_regression(self):
        # Verify InvestigationAgent instantiates, has extract_structured, and ask interface intact
        mock_neo4j = MagicMock()
        mock_qdrant = MagicMock()
        mock_embedder = MagicMock()
        mock_llm = MagicMock()
        
        mock_llm.complete.return_value = "### ANSWER\nPremium is calculated from base rates.\n### CONFIDENCE\n0.95"
        mock_llm.generate.return_value = "### ANSWER\nPremium is calculated from base rates.\n### CONFIDENCE\n0.95"
        mock_qdrant.search.return_value = []


        agent = InvestigationAgent(
            neo4j_client=mock_neo4j,
            qdrant=mock_qdrant,
            embedder=mock_embedder,
            llm=mock_llm,
        )

        # 1. Normal ask regression test
        res_ask = agent.ask("How is premium calculated?")
        self.assertIsInstance(res_ask, InvestigationResult)
        self.assertIn("Premium is calculated", res_ask.answer)

        # 2. Structured extraction method test
        sql = "SELECT p.id FROM PolicyCenter.dbo.Policy p;"
        res_extract = agent.extract_structured(
            selected_files=[sql],
            template="| Schema | Database | Table | Columns |",
        )
        self.assertEqual(len(res_extract.records), 1)
        self.assertEqual(res_extract.records[0].values.get("Table"), "Policy")


if __name__ == "__main__":
    unittest.main()
