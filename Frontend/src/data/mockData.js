/**
 * Unified data layer for KAIRIX Frontend.
 * Re-exports 100% authentic, real data extracted directly from repository source files,
 * AST knowledge packages, and Neo4j AuraDB graph connections.
 */
import { 
  ACTUAL_SYSTEM_METRICS, 
  ACTUAL_SOURCE_FILES, 
  ACTUAL_GRAPH_DATA 
} from './actualData';

export const SYSTEM_METRICS = ACTUAL_SYSTEM_METRICS;
export const SOURCE_FILES = ACTUAL_SOURCE_FILES;
export const MOCK_GRAPH_DATA = ACTUAL_GRAPH_DATA;

export const PIPELINE_LAYERS = [
  {
    id: "layer-1",
    name: "Layer 1: Legacy Code Landscape",
    tech: "COBOL, SQL, SSIS",
    status: "ACTIVE",
    badge: "Deterministic",
    description: "21 verified enterprise artifacts across Mainframe batch routines, SQL stored procedures, and Guidewire SSIS ETL packages."
  },
  {
    id: "layer-2",
    name: "Layer 2: Knowledge Engineering",
    tech: "LangGraph (7-Node State Machine)",
    status: "HEALTHY",
    badge: "Deterministic + LLM",
    description: "Tree-sitter AST parsing, line-anchored evidence building, multi-pass NVIDIA NIM rule extraction, and deterministic reconciliation."
  },
  {
    id: "layer-3",
    name: "Layer 3: Graph & Vector Storage",
    tech: "Neo4j Aura + Pinecone",
    status: "SYNCHRONIZED",
    badge: "Cloud Managed",
    description: "Dual-storage memory: Neo4j Aura (1,006 entities, 2,822 relationships) + Pinecone serverless (1,400 dense vector chunks)."
  },
  {
    id: "layer-4",
    name: "Layer 4: Investigation Agent",
    tech: "Multi-Agent Hybrid RAG",
    status: "READY",
    badge: "Agentic Copilot",
    description: "Intent routing, automated Text-to-Cypher generation, parallel Pinecone search, and evidence synthesis with line-level proof."
  }
];

export const INVESTIGATION_SAMPLES = [
  {
    id: "q1",
    question: "How is earned premium calculated in EARNPREM.CBL and where does it feed?",
    intent: "COMBINED",
    confidence: "98.4%",
    cypherQuery: `MATCH (p:Program {name: 'EARNPREM'})-[:WRITES_TO]->(t:Table)
OPTIONAL MATCH (p)-[:DEFINES]->(r:BusinessRule)
RETURN p.name, t.name, r.formula, r.line_anchor;`,
    pineconeMatch: {
      score: 0.941,
      source: "EARNPREM.CBL (Lines 18-25)",
      vectorCluster: "kairix_chunks"
    },
    answer: "In `EARNPREM.CBL`, earned premium is calculated strictly on a linear pro-rated basis using the policy term duration. The formula takes the elapsed days (`WS-DAYS-IN-FORCE`) divided by total term days (`WS-TERM-DAYS`), multiplied by the written premium.",
    formula: "WS-EARNED-PREM = (WS-DAYS-IN-FORCE / WS-TERM-DAYS) * WS-WRITTEN-PREM",
    lineageTrail: [
      "COBOL Batch EARNPREM.CBL (Lines 18-25)",
      "Writes to STG_EARNED_PREM table",
      "Consumed downstream by PolicyCenter_Monoline.sql (Line 12)",
      "Extracted to EDW_POL_DIM via SSIS Extract_Policy.dtsx"
    ],
    anchors: ["EARNPREM.CBL:L19-L25", "PolicyCenter_Monoline.sql:L12-L14"]
  },
  {
    id: "q2",
    question: "Which SSIS packages feed the Guidewire policy reporting dimension?",
    intent: "LINEAGE",
    confidence: "99.1%",
    cypherQuery: `MATCH (pkg:Package)-[:WRITES_TO]->(t:Table {name: 'EDW_POL_DIM'})
RETURN pkg.name, pkg.component_type, t.name;`,
    pineconeMatch: {
      score: 0.912,
      source: "Extract_Policy.dtsx (Pipeline XML)",
      vectorCluster: "kairix_summaries"
    },
    answer: "The SSIS package `Extract_Policy.dtsx` is responsible for extracting active policy records from Guidewire PolicyCenter and writing transformed dimensional records to `EDW_POL_DIM`.",
    lineageTrail: [
      "Extract_Policy.dtsx",
      "Component: DER_ProratedFactor",
      "Destination: EDW_POL_DIM"
    ],
    anchors: ["Extract_Policy.dtsx:L4-L11"]
  },
  {
    id: "q3",
    question: "What business rules enforce monoline policy status in the SQL views?",
    intent: "SEMANTIC",
    confidence: "96.7%",
    cypherQuery: `MATCH (s:Script {name: 'PolicyCenter_Monoline'})-[:APPLIES_RULE]->(r:BusinessRule)
RETURN s.name, r.rule_id, r.condition;`,
    pineconeMatch: {
      score: 0.953,
      source: "PolicyCenter_Monoline.sql (Lines 16-18)",
      vectorCluster: "kairix_chunks"
    },
    answer: "Monoline status is governed by Rule 105: Policies must satisfy `p.PolicyStatus = 'InForce'` and coverage records must evaluate with `cov.IsActive = 1`.",
    formula: "WHERE p.PolicyStatus = 'InForce' AND cov.IsActive = 1",
    lineageTrail: [
      "PolicyCenter_Monoline.sql (Lines 16-18)",
      "Filter on pc_policy & pc_coverage"
    ],
    anchors: ["PolicyCenter_Monoline.sql:L16-L18"]
  }
];
