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

---

# 🛡️ Enterprise Parser & Neo4j Graph Layer Refactoring Walkthrough

## 1. Executive Summary
Following rigorous architectural review and zero-hardcoding principles, we executed an enterprise-grade refactoring across the COBOL Parser, SSIS Parser, Knowledge Engineering serialization pipeline, and the Neo4j Graph database layer. All fixes are generic, grammar-driven, and validated across all 21 system artifacts.

---

## 2. Completed Architecture Improvements

### Component 1: COBOL Parser ([`parsers/cobol/parse.py`](file:///c:/Users/GaneshSriKumarMarimu/legacy-code-agentic-rag/parsers/cobol/parse.py))
- **Standard Reference Format Normalization**:
  - Automatically handles punch-card sequence columns (1–6) and punch-card identification area (73–80).
  - Trailing 6-8 digit sequence numbers are cleanly stripped so numbers (e.g. `00045000`) never leak into formulas or conditions as operands.
  - Terminating periods are preserved without loss.
- **Full Multi-line Statement Buffering (`_consume_multiline_statement`)**:
  - Dynamically consumes multi-line `PERFORM ... UNTIL ...`, `COMPUTE ...`, `IF ...` statements until terminating period or next COBOL verb.
  - Prevents condition truncation (e.g. `UNTIL PREM-EOF OR FATAL-ERROR`).
- **Comprehensive Arithmetic Capture**:
  - Added full expression extraction for `COMPUTE`, `ADD ... GIVING`, `SUBTRACT ... FROM ... GIVING`, `MULTIPLY ... BY ... GIVING`, and `DIVIDE ... INTO ... GIVING ... REMAINDER`.
  - Captured complete insurance rating formulas (e.g., `COMPUTE WS-EARNED ROUNDED = PRI-WRITTEN-PREMIUM * WS-EARNED-DAYS / WS-TERM-DAYS`).
- **Full Variable & Level 88 Condition Capture**:
  - Added support for Levels `01`, `02`, `03`, `05`, `10`, `15`, `77`, and `88`.
  - Level 88 condition names (e.g., `PREM-EOF`, `FATAL-ERROR`) mapped as `CONDITION_FLAG`.
  - Group items without `PIC` clauses mapped as `GROUP_ITEM`.
- **DATA DIVISION Bounding & Write-to-File Lineage**:
  - Procedural logic is prevented from leaking into record layouts by strictly bounding record extraction before `PROCEDURE DIVISION`.
  - Maps `01` records back to their parent `FD` file definitions so `WRITE <record>` creates accurate `WRITES` relationships to the parent file.

### Component 2: SSIS Parser ([`parsers/ssis/parse.py`](file:///c:/Users/GaneshSriKumarMarimu/legacy-code-agentic-rag/parsers/ssis/parse.py))
- **Recursive Container & EventHandler Traversal (`_iter_all_executables`)**:
  - Traverses sequence containers (`STOCK:SEQUENCE`), loop containers (`STOCK:FOREACHLOOP`), and error handling EventHandlers (`<DTS:EventHandlers><DTS:EventHandler>`).
  - Total tasks discovered increased from **42 to 53** across all 11 packages.
  - Captured previously missing 13th task (`SQL - Log Master Failure`) in `Master_ETL_Guidewire.dtsx`.
- **Recursive Precedence Constraints**:
  - Uses `root.iter()` to capture all `<DTS:PrecedenceConstraint>` tags at any container nesting level, eliminating disconnected orphan tasks.

### Component 3: Knowledge Engineering Pipeline ([`parser_evidence.py`](file:///c:/Users/GaneshSriKumarMarimu/legacy-code-agentic-rag/knowledge_engineering_agent/services/parser_evidence.py))
- **Token-Efficient Compact Edge Notation**:
  - Replaced arbitrary `MAX_RELATIONSHIPS = 20` cap with compact edge format:
    ```
    (EARNPREM)-[READS]->(POLICY_IN)
    (EARNPREM)-[WRITES]->(PREM_OUT)
    (EARNPREM)-[CALLS]->(DATEVAL)
    ```
  - Preserves up to 250 relationships dynamically within ~300 tokens without blowing prompt token limits.

### Component 4: Neo4j Schema & Graph Loader ([`graph_layer/`](file:///c:/Users/GaneshSriKumarMarimu/legacy-code-agentic-rag/graph_layer/))
- **Schema Constraints ([`schema.cypher`](file:///c:/Users/GaneshSriKumarMarimu/legacy-code-agentic-rag/graph_layer/schema.cypher))**:
  - Added uniqueness constraints for `:Loop (loop_id)`, `:CodeBlock (block_id)`, `:Branch (branch_id)`, and `:Statement (stmt_id)`.
- **Label-Aware Static MERGE Dispatch**:
  - Uses `_resolve_label(node_id)` to dispatch prefixes (`ARTIFACT:`, `TRANSFORMATION:`, `RULE:`, `LOOP:`, `BLOCK:`, `BRANCH:`, `STMT:`).
  - Groups entity batches by resolved static label in Python before executing parameterized Cypher queries, preventing duplicate untyped `:Entity` creation.
- **Phantom Null Entity Pruning (`prune_phantom_null_entities`)**:
  - Verified 204 duplicate untyped phantom nodes where `entity_type IS NULL AND name IS NULL`.
  - Safely purged all 204 phantom nodes using `DETACH DELETE`.
  - Remaining phantom null entities in Neo4j: **0**.

---

## 3. Verification Results

| Metric / Check | Before | After | Status |
| :--- | :---: | :---: | :---: |
| **COBOL Batch Parsing** | Missing `COMPUTE`, level 88 flags | 6/6 parsed, full arithmetic & 88 flags | ✅ PASS |
| **SSIS Total Tasks** | 42 tasks | 53 tasks (11 packages) | ✅ PASS |
| **Master ETL Tasks** | 12 tasks | 13 tasks (including Log Master Failure) | ✅ PASS |
| **SSIS Precedence Constraints** | 31 constraints | 33 constraints (all containers) | ✅ PASS |
| **Neo4j Phantom Null Entities** | 204 nodes | **0 nodes** | ✅ PASS |
| **Neo4j Valid Entities** | 1007 (mixed) | 803 clean business entities | ✅ PASS |
| **Neo4j Transformations** | 224 nodes | 448 nodes (all typed properly) | ✅ PASS |
---

# 🌳 4-Tier Hierarchical Graph Transformation (Star Topology Elimination)

## 1. Problem Addressed: Graph Fan-out Explosion
Previously, all nodes were linked directly to the root `(Artifact)` node (`CONTAINS`, `HAS_STATEMENT`, `HAS_BRANCH`, `HAS_LOOP`), creating a flat **174-spoke pinwheel star topology** (hub-and-spoke) centered on `ARTIFACT:EARNPREM.CBL`. This caused visual clutter in Neo4j and led to graph traversal fan-out explosion.

## 2. Transformation Executed
We converted the flat star into a deep, structured **4-Tier Tree Hierarchy**:
1. **Tier 1 (Artifact Root)**:
   - Links only to top-level structural divisions: `(:Artifact)-[:ENTRY_POINT]->(:CodeBlock {name: 'MAIN'})`, `(:Artifact)-[:DECLARES_FILE]->(:Entity {entity_type: 'File'})`, and `(:Artifact)-[:HAS_STORAGE]->(:Entity {entity_type: 'Storage'})`.
   - Outgoing edges from `ARTIFACT:EARNPREM.CBL` dropped from **174 to 33**.
2. **Tier 2 (Execution Call-Graph Hierarchy)**:
   - Paragraphs invoke each other via `[:CALLS_BLOCK]`:
     `MAIN ➔ OPEN-FILES, READ-POLICY, PROCESS-PREMIUM, CLOSE-FILES`
     `PROCESS-PREMIUM ➔ FIND-POLICY, VALIDATE-DATES, WRITE-ERROR`
     `VALIDATE-DATES ➔ VALIDATE-CALENDAR-DATE ➔ SET-MAX-DAY ➔ CHECK-LEAP-YEAR`
     `VALIDATE-DATES ➔ CALCULATE-EARNED ➔ WRITE-RESULT`
3. **Tier 3 (AST Block Containment)**:
   - Statements, Branches, and Loops are nested under their specific `CodeBlock` (Paragraph):
     - `(CodeBlock:MAIN)-[:CONTAINS_LOOP]->(Loop:PERFORM UNTIL PREM-EOF OR FATAL-ERROR)`
     - `(CodeBlock:CALCULATE-EARNED)-[:CONTAINS_STATEMENT]->(Statement:COMPUTE WS-EARNED = ...)`
     - `(CodeBlock:CALCULATE-EARNED)-[:CONTAINS_BRANCH]->(Branch:IF WS-TERM-DAYS > 0)`
4. **Tier 4 (Data Hierarchy)**:
   - Pure tree structure: `(:Artifact) ➔ (:Entity:File) ➔ (:Entity:Record) ➔ (:Entity:Variable/Field)`.
   - Storage tree: `(:Artifact) ➔ (:Entity:Storage) ➔ (:Entity:Record) ➔ (:Entity:Variable/Field)`.

## 3. Recommended Neo4j Aura Queries for Visual Tree Inspection

### View the Clean Program Execution Call-Tree:
```cypher
MATCH (a:Artifact {file_name: "EARNPREM.CBL"})-[:ENTRY_POINT]->(main:CodeBlock)
MATCH path = (main)-[:CALLS_BLOCK*1..4]->(sub:CodeBlock)
RETURN path;
```

### View Paragraphs and their Nested AST Statements & Loops:
```cypher
MATCH (b:CodeBlock {source_file: "EARNPREM.CBL"})-[r:CONTAINS_STATEMENT|CONTAINS_LOOP|CONTAINS_BRANCH]->(ast)
RETURN b, r, ast
LIMIT 100;
```

### View Data Hierarchy (File ➔ Record ➔ Field):
```cypher
MATCH path = (a:Artifact {file_name: "EARNPREM.CBL"})-[:DECLARES_FILE|HAS_STORAGE]->()-[:HAS_RECORD]->()-[:HAS_FIELD]->()
RETURN path;
```
