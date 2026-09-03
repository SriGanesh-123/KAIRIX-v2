# 📘 Streamlit Architecture, Implementation & Requirements Guide
**Project:** KAIRIX — Legacy Intelligence & Reverse Engineering Platform  
**UI Module:** `ui/app.py` | Enterprise Workbench  

---

## 1. What is Streamlit?

[Streamlit](https://streamlit.io/) is an open-source Python framework designed for building interactive, data-driven web applications, AI dashboards, and enterprise tools directly in Python without requiring front-end frameworks (like React or Angular) or custom web servers (like Flask or FastAPI).

### Core Concepts & Execution Model
- **Pure Python UI:** UI components, data structures, and business logic are written entirely in Python.
- **Reactive Execution Model:** Whenever a user interacts with a widget (clicks a button, types a query, changes a dropdown), Streamlit re-executes the Python script from top to bottom.
- **State Management (`st.session_state`):** Provides a persistent key-value store across script reruns to maintain state such as conversation history, active background tasks, selected tabs, and navigation paths.
- **Resource & Data Caching:**
  - `@st.cache_resource`: Caches long-lived, stateful objects (e.g., database connection pools, LLM client sessions, PyTorch/Transformer embedding models) so they are initialized only once in memory.
  - `@st.cache_data`: Caches computation results and data queries with Time-To-Live (TTL) to avoid redundant backend lookups.
- **Component Extensibility (`streamlit.components.v1`):** Enables embedding custom HTML, CSS, JavaScript, and interactive visualization canvases (such as Vis.js / PyVis network graphs).

---

## 2. What Have We Done With Streamlit in KAIRIX?

In KAIRIX, Streamlit serves as the **Enterprise Intelligence Workbench** ([`ui/app.py`](file:///c:/Users/GaneshSriKumarMarimu/legacy-code-agentic-rag/ui/app.py)), bridging the underlying deterministic parsers, LangGraph investigation agents, Neo4j Knowledge Graph, and Qdrant Vector Database into an intuitive UI.

```
ui/
├── app.py                      # Main entry point and 4-page router
├── assets/                     # Logos, brand assets, and icons
├── components/                 # Reusable UI widgets
│   ├── answer_panel.py         # AI answer breakdown & citation cards
│   ├── graph_view.py           # Vis.js / PyVis interactive network canvas
│   ├── metric_cards.py         # System KPI metrics & badges
│   ├── sidebar.py              # Collapsed sidebar with live service status
│   ├── source_panel.py         # Code viewer & source metadata cards
│   └── status_panel.py         # Real-time execution indicators
├── services/                   # Backend connectors & caching layers
│   ├── backend_service.py      # Socket probes, Neo4j/Qdrant/LLM clients
│   ├── graph_service.py        # Cypher queries & PyVis HTML generation
│   ├── investigation_service.py# LangGraph agent wrapper & thread pool
│   ├── pipeline_service.py     # Background subprocess orchestration
│   └── source_service.py       # Legacy file catalog & metadata reader
├── styles/
│   └── theme.css               # Bold Neumorphism light design system (2200+ lines)
└── views/                      # 4 Core Application Pages
    ├── investigation.py        # Natural Language Q&A + AST Schema Extractor
    ├── source_explorer.py      # Legacy Code Catalog & Dynamic Registration
    ├── pipeline.py             # Pipeline Control Center & Terminal Console
    └── knowledge_graph.py      # Neo4j Interactive Graph Explorer
```

### Core Features Implemented

#### 1. Investigation Agent ([`ui/views/investigation.py`](file:///c:/Users/GaneshSriKumarMarimu/legacy-code-agentic-rag/ui/views/investigation.py))
- **Dual-Mode Experience:**
  1. **Inquiry & Lineage Investigation:** Multi-pass AI question-answering over legacy COBOL, SQL, and SSIS systems. Displays structured findings:
     - Evidence-backed answers & key takeaways.
     - Step-by-step data flow diagrams and lineage paths.
     - Mathematical rating formulas with input/output variable tables.
     - Line-anchored source code citations with exact line number ranges.
     - Confidence metrics and system gaps analysis.
  2. **Structured Template Extraction:** Deterministic SQL AST parsing that maps complex database queries into customizable markdown table schemas (e.g., `| Schema | Database | Table | Columns |`) with one-click export (Markdown, TSV, CSV, Clipboard).
- **Non-Blocking Background Execution:** Uses a `ThreadPoolExecutor` so queries run in the background without blocking the UI or losing state during page navigation.

#### 2. Source Explorer ([`ui/views/source_explorer.py`](file:///c:/Users/GaneshSriKumarMarimu/legacy-code-agentic-rag/ui/views/source_explorer.py))
- **Legacy Catalog Browser:** Interactive inspection of 22+ legacy files across Mainframe COBOL (`.cbl`, `.cpy`), SQL Stored Procedures/Queries (`.sql`), and SSIS ETL Packages (`.dtsx`).
- **Deep Source Analysis:** Displays parsed AST entities, extracted business rules, transformation logic, and downstream dependencies.
- **Dynamic Source Registration:** Allows engineers to upload or paste new code files to trigger instant parsing and knowledge package generation.

#### 3. Pipeline Control Center ([`ui/views/pipeline.py`](file:///c:/Users/GaneshSriKumarMarimu/legacy-code-agentic-rag/ui/views/pipeline.py))
- **Multi-Layer Pipeline Orchestration:**
  - Layer 1: Knowledge Engineering Agent (`python -m knowledge_engineering_agent`)
  - Layer 2: Neo4j Knowledge Graph Ingestion (`python -m graph_layer`)
  - Layer 3: Qdrant Vector Store Ingestion (`python -m vector_layer`)
- **Real-Time Terminal Console:** Monospace log streamer that filters noise and color-codes processing milestones, warnings, and errors.

#### 4. Knowledge Graph Explorer ([`ui/views/knowledge_graph.py`](file:///c:/Users/GaneshSriKumarMarimu/legacy-code-agentic-rag/ui/views/knowledge_graph.py))
- **Interactive Network Graph (Vis.js / PyVis):** Neo4j Bloom-styled graph visualization rendered inside Streamlit via `streamlit.components.v1.html`.
- **Scope & Lineage Filtering:** Filter by Full System, COBOL Mainframe, SSIS ETL, SQL Schemas, or individual source files.
- **Interactive Node Inspector:** Clickable nodes to inspect properties, connected edges, degree, and Cypher lineage.

#### 5. Custom Neumorphic Design System ([`ui/styles/theme.css`](file:///c:/Users/GaneshSriKumarMarimu/legacy-code-agentic-rag/ui/styles/theme.css))
- Light tactile Neumorphism with royal blue accents, custom raised shadow matrices (`--neo-shadow-raised`), Inter & JetBrains Mono typography, custom scrollbars, and high-contrast WCAG-compliant styling.

#### 6. Live Service Health Monitoring ([`ui/components/sidebar.py`](file:///c:/Users/GaneshSriKumarMarimu/legacy-code-agentic-rag/ui/components/sidebar.py))
- Real-time connection indicators with 50ms socket pre-checks showing status and latency for Neo4j, Qdrant, and the LLM inference provider.

---

## 3. Packages Used to Connect & Integrate

The platform integrates several specialized Python libraries to connect Streamlit with databases, models, parsers, and agents:

| Category | Package | Version | Purpose in KAIRIX |
| :--- | :--- | :--- | :--- |
| **UI & Visualization** | `streamlit` | `>=1.35.0` | Core reactive web application framework and UI engine. |
| | `pyvis` | `>=0.3.2` | Generates interactive Vis.js HTML graphs embedded into Streamlit. |
| | `pandas` | `>=2.0.0` | Tabular data manipulation, formatting, and dataframe rendering. |
| **Knowledge Graph** | `neo4j` | `>=5.0.0` | Official Bolt protocol driver for Neo4j Graph Database queries. |
| **Vector DB & Search** | `qdrant-client` | `>=1.9.0` | Client for Qdrant vector database HTTP/gRPC operations. |
| **Embeddings & ML** | `sentence-transformers` | `>=3.0.0` | Runs local dense embedding models (`all-MiniLM-L6-v2`). |
| | `torch` | `>=2.0.0` | PyTorch backend for tensor operations and embedding inference. |
| | `transformers` | `>=4.40.0` | Hugging Face model architecture and tokenization pipeline. |
| | `huggingface-hub` | `>=0.20.0` | Model hub integration for downloading transformer weights. |
| **Code Parsers (AST)** | `tree-sitter` | `==0.26.0` | Fast incremental AST parser for COBOL and C#. |
| | `tree-sitter-language-pack` | `==1.14.3` | Pre-compiled Tree-sitter grammar bundles. |
| | `sqlglot` | `>=25.0.0` | Deterministic SQL parsing, transpilation, and lineage extraction. |
| | `lxml` | `>=5.0.0` | High-performance XML parser for SSIS DTSX data flow packages. |
| **Orchestration & Agents**| `langgraph` | `>=0.2.0` | State machine graph framework for multi-agent reasoning. |
| | `langchain-core` | `>=0.3.0` | Base interfaces for prompts, tools, and message schema. |
| | `pydantic` | `>=2.0.0` | Data modeling, validation, and structured entity contracts. |
| **Networking & Utilities**| `requests` / `httpx` | `>=2.31.0` / `>=0.27.0` | HTTP clients for NVIDIA NIM and external LLM REST endpoints. |
| | `python-dotenv` | `>=1.0.0` | Loads environment configuration from `.env`. |
| | `rich` | `>=13.0.0` | Formatted terminal output and debug logging. |

---

## 4. System Requirements & Setup

### 4.1 Runtime Requirements
- **Python:** Python `>= 3.10` (Active environment: Python 3.14 / 3.11 / 3.10).
- **Operating System:** Windows 10/11, macOS, or Linux.
- **Hardware Recommended:**
  - CPU: 4+ cores (recommended for parallel parsing & embedding generation).
  - RAM: 8 GB minimum (16 GB recommended for local embedding model & Neo4j).
  - Disk: ~2 GB free disk space for virtual environment, PyTorch wheels, and cached model weights.

### 4.2 External Service Dependencies
1. **Neo4j Graph Database:**
   - Default URI: `neo4j://127.0.0.1:7687` (Bolt port)
   - HTTP Browser: `http://127.0.0.1:7474`
2. **Qdrant Vector Database:**
   - Default HTTP URL: `http://localhost:6335` (or standard `http://localhost:6333`)
3. **LLM Inference Provider:**
   - NVIDIA NIM (`NVIDIA_NIM_API_KEY` configured in `.env`) or OpenAI / Anthropic API.

### 4.3 Environment Variables (`.env`)
```ini
# LLM Configuration
LLM_PROVIDER=nim
NVIDIA_NIM_API_KEY=your_nim_api_key_here
NIM_MODEL=nvidia/nemotron-3-ultra-550b-a55b
NIM_BASE_URL=https://integrate.api.nvidia.com/v1

# Neo4j Graph Database
NEO4J_URI=neo4j://127.0.0.1:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j

# Qdrant Vector Database
QDRANT_URL=http://localhost:6335

# Embedding Model Settings
EMBEDDING_MODEL=all-MiniLM-L6-v2
HF_HUB_DISABLE_IMPLICIT_TOKEN=1
```

### 4.4 Streamlit Server Configuration ([`.streamlit/config.toml`](file:///c:/Users/GaneshSriKumarMarimu/legacy-code-agentic-rag/.streamlit/config.toml))
```toml
[theme]
base = "light"
primaryColor = "#0284C7"
backgroundColor = "#F8FAFC"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#0F172A"
font = "sans serif"

[client]
toolbarMode = "minimal"
showErrorDetails = false

[browser]
gatherUsageStats = false

[server]
headless = true
enableCORS = false
enableXsrfProtection = false
maxUploadSize = 50
```

---

## 5. How to Run the Application

To activate the environment and launch the Streamlit interface:

```powershell
# 1. Activate Python virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# 2. Start the Streamlit application
streamlit run ui/app.py
```

The application will be accessible in your web browser at:
`http://localhost:8501`
