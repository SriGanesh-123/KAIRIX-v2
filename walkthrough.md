# 🚀 Walkthrough: KAIRIX Streamlit UI Full Implementation in `frontend/`

We have thoroughly analyzed the Streamlit Enterprise Workbench UI (`ui/app.py`, `ui/views/`, `ui/components/`, `ui/styles/theme.css`) and fully replicated all views, components, controls, and workflows inside **[`frontend/`](file:///c:/Users/GaneshSriKumarMarimu/legacy-code-agentic-rag/frontend/)** with **strict folder isolation** (zero modifications outside `frontend/`).

---

## 🖥️ Overview of Features Implemented in `frontend/`

### 1. 🔍 Investigation Agent (`frontend/src/views/InvestigationView.jsx`)
- **Default Landing Page**: Configured as the home view matching Streamlit.
- **Prominent Dual-Mode Switcher**:
  - **Mode 1: Inquiry & Lineage Investigation**:
    - Hero header: *"How can I help you? Ask questions about system logic, trace calculations & lineage..."*
    - Natural language inquiry search bar with `Run Investigation` and `Clear History` buttons.
    - 6 Sample prompt chips (`How is earned premium calculated?`, `Which SSIS packages populate PolicyCenter tables?`, etc.).
    - Real-time 4-stage execution stepper (*1. Intent Analysis* ➔ *2. Neo4j Traversal* ➔ *3. Vector Retrieval* ➔ *4. LLM Synthesis*).
    - Synthesis Answer Card with key takeaways, extracted mathematical rating formula, step-by-step lineage diagram, and line-anchored citations.
    - Previous Investigations in Session history list with quick reload.
  - **Mode 2: User-Defined Structured Template Extraction**:
    - Preset categories for **SQL**, **COBOL**, **SSIS**, and **ALL**.
    - Standard template preset selector (e.g. `| Schema | Database | Table | Columns |`).
    - Editable custom markdown table template input box.
    - Target source file selector (all repository files or specific modules).
    - `Extract Structured Schema` deterministic execution button.
    - Dynamic interactive data table with column headers extracted from template.
    - 4 Export Options matching Streamlit: `Export CSV`, `Export TSV`, `Export Markdown`, and `Copy Table`.

---

### 2. 📁 Source Explorer (`frontend/src/views/SourceExplorerView.jsx`)
- **Top Header & Controls**: Title, description, `+ Add Source` toggle button, and `Refresh` button.
- **Expandable Registration Form**:
  - Technology selector (`COBOL`, `SQL`, `SSIS`).
  - Source file name with auto-extension (`.cbl`, `.sql`, `.dtsx`).
  - Drag-and-drop file uploader & direct code paste textarea.
  - Checkbox: *"Run Knowledge Extraction Pipeline immediately after upload"*.
  - Add Source and Cancel actions with auto-refresh into the catalog.
- **Filter Segmented Radio Bar**: All Files (`21`), COBOL (`6`), SQL (`4`), SSIS (`11`) with active dots.
- **4 Key Metric Cards**: Lines of Code, Extracted Entities, Business Rules, and Downstream Links.
- **4 Detail Tabs**:
  1. **Source Code**: Syntax-highlighted code viewer with sticky line numbers and copy code action.
  2. **Extracted Entities**: Table of AST records, fields, variables, tables, and copybooks.
  3. **Business Rules**: Extracted logic, rating formulas, and boundary rules.
  4. **Cross-System Lineage**: Connected programs, SSIS inputs/outputs, and downstream DW tables.
- **"Investigate with AI →"**: Instant route action to the Investigation Agent with pre-filled question.

---

### 3. ⚙️ Pipeline Control Center (`frontend/src/views/PipelineView.jsx`)
- **Top Header & Global Actions**: `Refresh Status` and `Stop All` buttons.
- **Two Symmetrical Pipeline Operation Cards**:
  - **Card 1: Layer 2: Knowledge Engineering Agent**:
    - Status badge (`READY`, `RUNNING %`, `COMPLETED`, `STOPPED`).
    - Live progress bar and current step display.
    - Scope dropdown: *"All Source Files (Full Repository)"* or individual source file.
    - Checkbox: *"Force re-extract files (bypass local cache)"*.
    - `Run Knowledge Engineering Agent` / `🛑 Stop` controls.
  - **Card 2: Layer 3: Knowledge Graph & Vector Store Ingestion**:
    - Split dual mini-panels for **Neo4j Graph** and **Pinecone Vector DB** with independent progress bars and status.
    - Scope selector: `Ingest Both`, `Neo4j Only`, or `Pinecone Only`.
    - Checkboxes: `Discover cross-file links` and `Recreate namespaces`.
    - `Ingest Both...` / `🛑 Stop` controls.
- **Real-Time Live Monospace Terminal Console**:
  - macOS-style window frame dots (red, yellow, green), title, and `Live Stream` badge.
  - Colored milestone logs (green for completed, cyan for processing, yellow for found, red for error, purple for Neo4j, emerald for Pinecone).
- **Source Files Processing Status Table**:
  - Lists all 21+ files with Technology, File Name, Knowledge Package status, Graph Lineage status, and Quick Re-extract actions.

---

### 4. 🌐 Knowledge Graph Explorer (`frontend/src/views/KnowledgeGraphView.jsx`)
- **Node Entity Schema Legend**: Visual color pills matching Streamlit (`Program: #1D4ED8`, `Package: #047857`, `Table: #6D28D9`, `Column: #0891B2`, `Business Rule: #D97706`, `Transformation: #EA580C`).
- **Graph Controls Toolbar**: Single-select scope dropdown (`Full System Graph`, `COBOL Mainframe`, `SSIS ETL`, `SQL`, or specific file), Node Type filter, and Entity Search input.
- **Interactive Graph Canvas**: Responsive SVG canvas with colored nodes, pulse rings, directional edge markers, and edge labels.
- **Neo4j Bloom-Styled Node Details Inspector**:
  - Node Label, Name, and Neo4j Element ID.
  - Key-Value properties table (`name`, `type`, `file_origin`, `system_layer`, `line_anchor`, `extracted_formula`).
  - Connected Lineage Edges list with directional badges (`OUTGOING ➔`, `INCOMING ⬅`) and clickable target nodes.
  - `Copy Cypher Query` and `Focus Lineage` actions.

---

### 5. 📑 Navigation & Layout (`frontend/src/components/Sidebar.jsx` & `frontend/src/App.jsx`)
- **Brand Header**: Official KAIRIX Logo with *"KAIRIX / INVESTIGATION AGENT"*.
- **4 Core Navigation Items**: Investigation Agent (default), Source Explorer, Pipeline, Knowledge Graph.
- **Active Task Notification Toast**: Sidebar toast indicating background investigation or AST extraction status.
- **Backend Services Monitor**: Inset card displaying live status and latency for Neo4j Graph (`12.4ms`), Pinecone DB (`18.2ms`), and LLM Provider (`NIM`).

---

## 🔒 Verification & Strict Folder Isolation

1. **Strict Folder Isolation Verified**:
   ```bash
   git status --porcelain
   ```
   **Output**:
   ```
    M Frontend/src/App.css
    M Frontend/src/App.jsx
    M Frontend/src/components/Sidebar.jsx
    M Frontend/src/views/InvestigationView.jsx
    M Frontend/src/views/KnowledgeGraphView.jsx
    M Frontend/src/views/PipelineView.jsx
    M Frontend/src/views/SourceExplorerView.jsx
   ?? "probleam statement/"
   ```
   Zero files outside `frontend/` were modified.

2. **Production Build Verified**:
   ```bash
   npm run build
   ```
   Output: `✓ built in 9.13s` with zero errors.

3. **Live Server**:
   - Running at: **[http://localhost:5173/](http://localhost:5173/)**
