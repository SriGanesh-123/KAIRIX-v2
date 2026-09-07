export const SYSTEM_METRICS = {
  totalFiles: 21,
  cobolPrograms: 8,
  sqlScripts: 7,
  ssisPackages: 6,
  graphEntities: 1135,
  graphRelationships: 1231,
  businessRules: 152,
  transformations: 93,
  pineconeChunks: 1420,
  pineconeSummaries: 21,
  embeddingDimension: 384,
  activeEmbeddingModel: "all-MiniLM-L6-v2",
  llmEngine: "NVIDIA NIM (nematron-3-ultra)",
  graphStorage: "Neo4j Aura (Managed Cloud)",
  vectorStorage: "Pinecone Serverless (us-east-1)"
};

export const PIPELINE_LAYERS = [
  {
    id: "layer-1",
    name: "Layer 1: Legacy Code Landscape",
    tech: "COBOL, SQL, SSIS",
    status: "ACTIVE",
    badge: "Deterministic",
    description: "Multi-system enterprise artifacts across Mainframe batch routines, SQL stored procedures, and Guidewire SSIS ETL packages."
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
    description: "Dual-storage memory: Neo4j Aura for cross-system entity lineage + Pinecone serverless for dense semantic vector chunks."
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

export const SOURCE_FILES = [
  {
    id: "cbl-1",
    name: "EARNPREM.CBL",
    type: "COBOL",
    category: "Mainframe Batch",
    lines: 642,
    rulesCount: 14,
    description: "Core earned premium calculation routine using 365/366 day prorated accounting schedule.",
    codeSnippet: `000100 IDENTIFICATION DIVISION.
000200 PROGRAM-ID. EARNPREM.
000300 ENVIRONMENT DIVISION.
000400 DATA DIVISION.
000500 WORKING-STORAGE SECTION.
000600 01  WS-POLICY-RECORD.
000700     05 WS-POL-NUM         PIC X(10).
000800     05 WS-POL-EFF-DATE    PIC 9(8).
000900     05 WS-POL-EXP-DATE    PIC 9(8).
001000     05 WS-WRITTEN-PREM    PIC 9(9)V99.
001100     05 WS-EARNED-PREM     PIC 9(9)V99.
001200     05 WS-DAYS-IN-FORCE   PIC 9(4).
001300     05 WS-TERM-DAYS       PIC 9(4).
001400 PROCEDURE DIVISION.
001500 0000-MAIN-LOGIC.
001600     PERFORM 1000-CALC-EARNED-PREM.
001700     GOBACK.
001800 1000-CALC-EARNED-PREM.
001900     COMPUTE WS-DAYS-IN-FORCE = FUNCTION CURRENT-DATE(1:8) - WS-POL-EFF-DATE
002000     COMPUTE WS-TERM-DAYS = WS-POL-EXP-DATE - WS-POL-EFF-DATE
002100     IF WS-DAYS-IN-FORCE > WS-TERM-DAYS
002200         MOVE WS-TERM-DAYS TO WS-DAYS-IN-FORCE
002300     END-IF.
002400     COMPUTE WS-EARNED-PREM ROUNDED = 
002500         (WS-DAYS-IN-FORCE / WS-TERM-DAYS) * WS-WRITTEN-PREM.`,
    readsFrom: ["POLICY_MASTER", "CPY_PREMCALC"],
    writesTo: ["STG_EARNED_PREM"]
  },
  {
    id: "sql-1",
    name: "PolicyCenter_Monoline.sql",
    type: "SQL",
    category: "Analytics & Views",
    lines: 184,
    rulesCount: 8,
    description: "Cross-system reporting query joining policy transaction records with commercial auto lines.",
    codeSnippet: `SELECT 
    p.PolicyNumber,
    p.EffectiveDate,
    p.ExpirationDate,
    ep.EarnedPremiumAmount,
    cov.CoverageCode,
    cov.LimitAmount
FROM dbo.pc_policy p
INNER JOIN dbo.STG_EARNED_PREM ep 
    ON p.PolicyNumber = ep.PolicyNumber
LEFT JOIN dbo.pc_coverage cov 
    ON p.ID = cov.PolicyID
WHERE p.PolicyStatus = 'InForce' 
  AND cov.IsActive = 1;`,
    readsFrom: ["STG_EARNED_PREM", "pc_policy", "pc_coverage"],
    writesTo: ["RPT_MONOLINE_ACTIVE"]
  },
  {
    id: "ssis-1",
    name: "Extract_Policy.dtsx",
    type: "SSIS",
    category: "ETL Package",
    lines: 412,
    rulesCount: 11,
    description: "Guidewire operational store ETL pipeline extracting policy revisions and staging into reporting warehouse.",
    codeSnippet: `<DTS:Executable xmlns:DTS="www.microsoft.com/SqlServer/Dts">
  <DTS:Property DTS:Name="PackageFormatVersion">8</DTS:Property>
  <DTS:Property DTS:Name="ObjectName">Extract_Policy</DTS:Property>
  <DTS:Pipeline ComponentClassID="Microsoft.Pipeline">
    <DTS:Components>
      <DTS:Component ObjectName="OLE_SRC_Guidewire_PC" ComponentClassID="Microsoft.OLEDBSource" />
      <DTS:Component ObjectName="DER_ProratedFactor" ComponentClassID="Microsoft.DerivedColumn" />
      <DTS:Component ObjectName="OLE_DST_DataWarehouse" ComponentClassID="Microsoft.OLEDBDestination" />
    </DTS:Components>
  </DTS:Pipeline>
</DTS:Executable>`,
    readsFrom: ["pc_policy"],
    writesTo: ["EDW_POL_DIM"]
  }
];

export const MOCK_GRAPH_DATA = {
  nodes: [
    { id: "EARNPREM", label: "EARNPREM", type: "Program", system: "COBOL Mainframe", status: "Active", x: 180, y: 140 },
    { id: "PREMCALC", label: "PREMCALC", type: "Program", system: "COBOL Mainframe", status: "Active", x: 100, y: 280 },
    { id: "STG_EARNED_PREM", label: "STG_EARNED_PREM", type: "Table", system: "Staging RDBMS", status: "Active", x: 380, y: 190 },
    { id: "PolicyCenter_Monoline", label: "PC_Monoline.sql", type: "Script", system: "SQL Analytics", status: "Active", x: 580, y: 140 },
    { id: "Extract_Policy", label: "Extract_Policy.dtsx", type: "Package", system: "SSIS ETL", status: "Active", x: 420, y: 340 },
    { id: "EDW_POL_DIM", label: "EDW_POL_DIM", type: "Table", system: "Data Warehouse", status: "Active", x: 680, y: 310 },
    { id: "RULE_300", label: "Rule 300 (Prorate)", type: "BusinessRule", system: "Logic", status: "Verified", x: 260, y: 50 }
  ],
  links: [
    { source: "EARNPREM", target: "STG_EARNED_PREM", label: "WRITES_TO", type: "lineage" },
    { source: "PREMCALC", target: "EARNPREM", label: "CALLS", type: "dependency" },
    { source: "EARNPREM", target: "RULE_300", label: "DEFINES", type: "rule" },
    { source: "PolicyCenter_Monoline", target: "STG_EARNED_PREM", label: "READS_FROM", type: "lineage" },
    { source: "Extract_Policy", target: "STG_EARNED_PREM", label: "FEEDS_INTO", type: "etl" },
    { source: "Extract_Policy", target: "EDW_POL_DIM", label: "WRITES_TO", type: "lineage" }
  ]
};

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
