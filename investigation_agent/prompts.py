"""
Investigation Agent prompt templates.
"""

# ── Intent Classification ──────────────────────────────────────────────────────
INTENT_CLASSIFICATION_PROMPT = """You are a system analyst working with a legacy insurance system knowledge base.

Classify the following user question into EXACTLY ONE of these intents:
- calculation      — asks how a metric/value is calculated, formulas, math logic (e.g. "How is premium calculated?", "What is the formula for earned premium?")
- lineage          — asks where an entity comes from, data flow, what reads/writes a file/table (e.g. "Where does PREMIUM-OUT come from?", "What does PREMCALC read?")
- impact_analysis  — asks what is affected if a file or component changes (e.g. "What will be affected if EARNPREM.CBL is changed?")
- relationship     — asks how multiple files/programs/tables relate to each other (e.g. "How does EARNPREM.CBL relate to PolicyCenter tables?")
- source_lookup    — asks which file/program is responsible for an action or rule (e.g. "Which COBOL program calculates written premium?")
- definition       — asks what a specific entity, variable, table or term is or means
- comparison       — asks how two programs, tables, or rules compare or differ
- validation       — asks about validation checks, error conditions, or business rule compliance
- semantic         — general conceptual or narrative question about system behavior

Question: {question}

Respond with ONLY the single intent name (e.g. calculation, lineage, impact_analysis, relationship, source_lookup, definition, comparison, validation, semantic).
"""

# ── Cypher Generation ──────────────────────────────────────────────────────────
CYPHER_GENERATION_PROMPT = """You are a Neo4j Cypher expert working with a legacy insurance system knowledge graph.

GRAPH SCHEMA:

Node types:
- :Artifact {{id, file_name, source_type, purpose, business_domain, total_lines}}
- :Entity {{id, name, entity_type, entity_label, source_file, data_type, description}}
- :BusinessRule {{id, description, source_file}}
- :Transformation {{id, rule_id, rule_type, description, expression, source_file}}

Key relationships:
- (:Artifact)-[:CONTAINS]->(:Entity) — an artifact file contains entities
- (:Artifact)-[:HAS_RULE]->(:BusinessRule) — an artifact has business rules
- (:Artifact)-[:HAS_TRANSFORMATION]->(:Transformation) — transformations
- (:Entity)-[:READS_FROM]->(:Entity) — data read lineage (edge has source_file property)
- (:Entity)-[:WRITES_TO]->(:Entity) — data write lineage (edge has source_file property)
- (:Entity)-[:CONTAINS]->(:Entity) — hierarchical (e.g. table contains columns)
- (:Entity)-[:USES]->(:Entity) — entity uses another (edge has source_file property)

IMPORTANT: Lineage edges (READS_FROM, WRITES_TO, USES, etc.) are between Entity nodes,
NOT from Artifact nodes. They have a `source_file` property on the EDGE that indicates
which file established the relationship.

QUERY PATTERNS:

To find what a specific file reads from or writes to:
  MATCH (src)-[r:READS_FROM {{source_file: 'FILENAME'}}]->(t:Entity)
  RETURN DISTINCT src.name AS program, t.name AS target, t.entity_type AS target_type

To find where an entity comes from or which programs write to it:
  MATCH (src:Entity)-[r:WRITES_TO|FEEDS_INTO|DERIVES_FROM]->(t:Entity)
  WHERE toLower(t.name) = toLower('ENTITY_NAME') OR t.id CONTAINS 'ENTITY_NAME'
  RETURN DISTINCT src.name AS writer, src.entity_type AS writer_type, r.source_file AS source_file, type(r) AS rel_type, t.name AS target

To find impact or dependencies for a file / program:
  MATCH (src)-[r {{source_file: 'FILENAME'}}]->(tgt:Entity)
  RETURN DISTINCT src.name AS from_entity, type(r) AS relationship, tgt.name AS to_entity, tgt.source_file AS target_file
  UNION
  MATCH (src:Entity)-[r]->(tgt {{source_file: 'FILENAME'}})
  RETURN DISTINCT src.name AS from_entity, src.source_file AS source_file, type(r) AS relationship, tgt.name AS to_entity

To find cross-file data flow:
  MATCH (src)-[r]->(t:Entity)<-[r2]-(other)
  WHERE r.source_file <> r2.source_file
  RETURN DISTINCT src.name, r.source_file, type(r), t.name, type(r2), r2.source_file, other.name

User question: {question}

Write a Cypher query to retrieve the most relevant graph data to answer this question.
- Use LIMIT to cap results (max 20).
- Return human-readable fields (names, descriptions, types).
- Use case-insensitive matching (e.g. toLower(t.name) = toLower('...')) for entity names.

Return ONLY the Cypher query, no explanation, no markdown.
"""

# ── Answer Synthesis ───────────────────────────────────────────────────────────
ANSWER_SYNTHESIS_PROMPT = """You are a senior insurance legacy systems reverse-engineering specialist.
You have been asked a question and retrieved evidence from a Neo4j knowledge graph and Pinecone vector database.

Question:
{question}

Graph Evidence (Neo4j results):
{graph_evidence}

Semantic Evidence (relevant source code / summaries):
{vector_evidence}

Synthesize a concise, structured, user-facing response strictly following the section headers below.

RULES:
1. Be concise, direct, and factual. Do NOT include conversation intros, outros, or internal debug details.
2. Distinguish:
   - Direct source-code evidence
   - Graph-derived relationships
   - Vector/semantic summary evidence
   - Inferences (explicitly label if an element is inferred)
3. Never present an inference as direct source-code evidence.
4. If evidence is insufficient, state that clearly under GAPS.
5. FORMULA: Only include this section when the question involves a calculation or mathematical business logic.
6. GAPS: Only include this section when important evidence is missing, incomplete, or unverified.

REQUIRED OUTPUT FORMAT (Use these exact capitalized section headers):

ANSWER
[Direct, concise answer explaining the core facts in 1-3 short paragraphs or numbered points.]

KEY POINTS
- [Bullet 1: most important fact]
- [Bullet 2: key program/table role]
- [Bullet 3: crucial business rule or behavior]

DATA FLOW
[Short readable data flow, e.g. Policy/Coverage Data → PREMCALC.CBL → Written Premium → EARNPREM.CBL → Earned / Unearned Premium]

FORMULA
[Only when applicable: exact formula or business calculation]

SOURCES
[List actual source files referenced, one per line or comma-separated]

CONFIDENCE
[High / Medium / Low — Percentage, e.g. High — 85%]

GAPS
[Only when applicable: missing tables, unverified constants, or unknown downstream consumers]

Answer:
"""

# ── Cypher Repair (fallback) ───────────────────────────────────────────────────
CYPHER_REPAIR_PROMPT = """The following Cypher query failed with the error below.
Fix the Cypher query to make it valid. Return ONLY the corrected Cypher, nothing else.

Original query:
{cypher}

Error:
{error}

Fixed query:
"""