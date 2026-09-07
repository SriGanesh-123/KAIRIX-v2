# 🛠️ KAIRIX — Tech Stack & Architecture Guide

KAIRIX is an enterprise multi-agent reverse engineering platform designed to analyze, reconcile, and query legacy codebases (**COBOL, SQL, SSIS**) using **Knowledge Graphs (Neo4j Aura)**, **Vector Search (Pinecone)**, and **Multi-Agent RAG**.

 *

## 🏗️ 1. Complete Tech Stack Overview

| Category | Technology | Purpose & Implementation |
| --- | --- | --- |
| **Frontend / UI** | **Streamlit (v1.35+)** | Multi-page web dashboard for ingestion, graph exploration, and interactive investigation. |
| **Graph Visualization** | **PyVis (v0.3+)** | Interactive physics-based network graph rendering inside Streamlit. |
| **Deterministic Parsers** | **Tree-sitter (v0.26+)** | Abstract Syntax Tree (AST) parsing for COBOL programs and copybooks. |
|  | **SQLGlot (v25+)** | SQL AST analysis, dialect transpilation, and table/column lineage extraction. |
|  | **Python `xml.etree`** | SSIS `.dtsx` pipeline component and control/data flow extraction. |
| **Agent Orchestration** | **LangGraph (v0.2+)** | 7-node cyclical state machine pipeline for knowledge extraction & reconciliation. |
| **Data Validation** | **Pydantic v2** | Strict typing and schema enforcement for profiles, business rules, and packages. |
| **LLM & Reasoning** | **NVIDIA NIM (`nematron-3-ultra`)** | Multi-pass code review, business rule extraction, Cypher generation, and answer synthesis. |
| **Embedding Model** | **`all-MiniLM-L6-v2` (384-dim)** | Dense vector embeddings via `sentence-transformers` for code chunks and functional summaries. |
| **Vector Database** | **Pinecone Serverless** | High-performance vector database storing code chunks and summary embeddings for semantic retrieval. |
| **Knowledge Graph** | **Neo4j Aura (Cloud)** | Enterprise managed cloud graph database for data lineage, cross-system dependencies, and Cypher traversal. |

 *

## 🔄 2. End-to-End Architectural Flow

The system operates across **4 distinct layers**:

```mermaid
flowchart TD
    subgraph L1["Layer 1: Legacy Code Sources"]
        COBOL["Mainframe COBOL (.cbl, .cpy)"]
        SQL["SQL Scripts & Queries (.sql)"]
        SSIS["SSIS ETL Packages (.dtsx)"]
    end

    subgraph L2["Layer 2: Knowledge Engineering Agent (LangGraph)"]
        P1["Deterministic Parsing (Tree-sitter / SQLGlot / XML)"]
        P2["Line-Anchored Evidence Building"]
        P3["LLM Multi-Pass Analysis (NVIDIA NIM)"]
        P4["Reconciliation Engine (Parser 1.0 vs LLM 0.85)"]
        P5["Canonical Knowledge Package (*_knowledge_package.json)"]
        
        P1 --> P2 --> P3 --> P4 --> P5
    end

    subgraph L3["Layer 3: Storage & Knowledge Layer"]
        N4J[("Neo4j Aura\n(Knowledge Graph)")]
        PNC[("Pinecone\n(Vector Database)")]
        
        P5 -->|Nodes & Relationships| N4J
        P5 -->|Embeddings (all-MiniLM-L6-v2)| PNC
        L1 -->|Sliding Window Chunks| PNC
    end

    subgraph L4["Layer 4: Investigation Agent (Hybrid RAG)"]
        USER["Analyst / User Question"] --> ROUTER{"Intent Router\n(Lineage / Semantic / Combined)"}
        
        ROUTER -->|Lineage Path| CYPHER["Text-to-Cypher Generator"] --> N4J
        ROUTER -->|Semantic Path| VEC["Pinecone Similarity Search"] --> PNC
        ROUTER -->|Combined Path| HYBRID["Hybrid Retrieval\n(Graph + Vector)"]
        
        N4J --> SYN["LLM Answer Synthesis Engine"]
        PNC --> SYN
        HYBRID --> SYN
        SYN --> OUT["Evidence-Backed Answer with Lineage & Confidence"]
    end

    L1 --> P1
```

 *

## 📑 3. Detailed Layer Breakdown

### Layer 1: Source Artifacts (`source/`)

*   **COBOL**: Legacy insurance calculation routines, rating algorithms, and status programs (`EARNPREM.CBL`, `PREMCALC.CBL`).
*   **SQL**: Complex multi-table joins, reporting queries, and database views (`PolicyCenter_Monoline.sql`).
*   **SSIS**: Guidewire ETL pipelines transforming operational data into data warehouse staging tables (`Extract_Policy.dtsx`).

### Layer 2: Knowledge Engineering Agent (`knowledge_engineering_agent/`)

Uses a **LangGraph** state machine with 7 sequential nodes:

1. Classification: Detects file dialect and structure.
2. Deterministic Extraction: Rule-based parsing using Tree-sitter and SQLGlot (zero hallucination, confidence 1.0).
3. Evidence Anchoring: Maps every variable, rule, and table to exact source code line numbers.
4. LLM Deep Review: Employs NVIDIA NIM to identify implicit business rules and undocumented logic.
5. Knowledge Profile: Formats findings into standardized Pydantic models.
6. Reconciliation Engine: Merges parser facts with LLM discoveries, flagging discrepancies.
7. Canonical Package: Emits unified JSON artifacts into output/knowledge/.

### Layer 3: Knowledge Graph & Vector Storage

*   **Neo4j Aura (`graph_layer/`):**
    *   Stores nodes: `:Artifact`, `:Program`, `:Table`, `:Column`, `:BusinessRule`, `:Transformation`.
    *   Stores edges: `CALLS`, `READS_FROM`, `WRITES_TO`, `FEEDS_INTO`, `DERIVES_FROM`.
    *   Cross-system relationship discovery connects COBOL batch outputs to downstream SQL reports and SSIS packages.
*   **Pinecone (`vector_layer/`):**
    *   **Code Chunks (`kairix_chunks`):** 50-line sliding window chunks with 10-line overlap.
    *   **Functional Summaries (`kairix_summaries`):** High-level markdown summary embeddings.
    *   Vector dimensionality: **384** (via `all-MiniLM-L6-v2`).

### Layer 4: Investigation Agent (`investigation_agent/`)

*   **Intent Classification:** Classifies incoming questions into:
    *   `lineage`: Tracing data flow across systems $\rightarrow$ Queries **Neo4j Aura**.
    *   `semantic`: Explaining logic or finding code snippets $\rightarrow$ Searches **Pinecone**.
    *   `combined`: Full reverse-engineering questions $\rightarrow$ Concurrent retrieval from both.
*   **Text-to-Cypher:** Converts plain English into Cypher queries with syntax repair routines.
*   **Evidence Synthesis:** Fuses structured graph triples and vector code snippets into an executive answer with verifiable line citations.