# 🏛️ KAIRIX System Architecture & Engineering Blueprint

An interactive, visual single-page application explaining the **entire system architecture, multi-agent pipeline, and repository structure** of the KAIRIX Legacy Reverse Engineering Platform.

---

## 📑 Core Architecture Sections

### 1. 4-Layer Architecture Blueprint (`#blueprint`)
- **Interactive Component Cards**:
  - **Layer 1 (Legacy Source Landscape)**: Mainframe COBOL 85 (`source/mainframe/`), SSIS DTSX XML Pipelines (`source/ssis/`), Guidewire SQL (`source/sql/`).
  - **Layer 2 (Knowledge Engineering & AST)**: Deterministic AST parsers (`parsers/`), 7-stage LangGraph pipeline (`knowledge_engineering_agent/`), Canonical Packages (`output/knowledge/`).
  - **Layer 3 (Dual-Memory Knowledge Store)**: Neo4j Aura Graph Database (`graph_layer/`), Relationship Discovery Agent (`rda.py`), Pinecone/Qdrant Vector DB (`vector_layer/`).
  - **Layer 4 (Investigation & Modernization)**: Line-anchored Investigation Agent (`investigation_agent/`), Re-engineered FastAPI microservices, Streamlit interactive dashboard (`Frontend/`).
- **Dynamic Component Inspector**:
  - Click any card to inspect its exact workspace directory, architectural role, inputs, outputs, and sample code constructs.

---

### 2. The 7-Stage LangGraph Cyclical Pipeline (`#langgraph`)
Visual walkthrough of how raw legacy files are converted into canonical packages without hallucinations:
1. **Classification**: Dialect detection (.cbl $\rightarrow$ COBOL, .sql $\rightarrow$ SQL, .dtsx $\rightarrow$ SSIS).
2. **Deterministic Parsing**: Tree-sitter & SQLGlot AST extraction (confidence 1.0).
3. **Evidence Anchoring**: 100% line-anchored source line numbers.
4. **LLM Deep Review**: NVIDIA NIM multi-pass business logic discovery.
5. **Pydantic Profile**: Schema normalization (`KnowledgeProfile`, `BusinessRule`).
6. **Reconciliation**: Parser facts cross-validated with LLM discoveries.
7. **Canonical Package**: Emitted `*_knowledge_package.json` artifacts.

---

### 3. The 3 Autonomous Multi-Agent Triad (`#agents`)
Visual breakdown of the 3 specialized AI agents:
- 🔬 **Knowledge Engineering Agent (KEA)**: The Reverse Engineer (AST parsing, line anchoring, reconciliation).
- 🌉 **Relationship Discovery Agent (RDA)**: The Bridge Builder (cross-file lineage, linking COBOL $\rightarrow$ SSIS $\rightarrow$ SQL).
- 🔎 **Investigation Agent (IA)**: The Line-Anchored Detective (intent routing, text-to-Cypher, verified answers).

---

### 4. Real-Time Data Pipeline Simulator (`#simulator`)
An animated, interactive step-by-step simulator tracing a legacy business rule (`EARNPREM.CBL` calculation) as it travels through:
- Ingestion $\rightarrow$ Deterministic AST Parsing $\rightarrow$ LangGraph Reconciliation $\rightarrow$ Dual-Memory Sync $\rightarrow$ Investigation Agent Q&A.

---

### 5. Repository Directory & File Structure Explorer (`#tree`)
- Interactive physical folder tree of the repository:
  - `source/`, `parsers/`, `knowledge_engineering_agent/`, `graph_layer/`, `vector_layer/`, `investigation_agent/`, `output/`, `Frontend/`.
- Displays file paths, summaries, and key source artifacts for each folder on click.

---

### 6. Architectural Paradigm Comparison
- Comparison matrix between **Traditional Vector-Only RAG** vs. **KAIRIX Dual-Memory Multi-Agent Architecture**.

---

## 🎨 Design & Aesthetics
- **Neumorphic Soft UI & Frosted Glass**: Modern slate palette (`#e9eef5`) with soft inset and outset shadows.
- **Lightweight Particle Graph Canvas**: Ambient animated background representing knowledge graph node relationships.
- **Pure Visual Focus**: Clean badges, chips, code previews, and cards — zero cluttered or unformatted text blocks.

---

## 🚀 How to View

### Live HTTP Server (Port 8080)
```powershell
python -m http.server 8080
```
Open: [http://localhost:8080/probleam%20statement/index.html](http://localhost:8080/probleam%20statement/index.html)

### Direct Browser Launch
```powershell
Start-Process "probleam statement/index.html"
```
