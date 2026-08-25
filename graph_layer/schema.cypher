// KAIRIX Neo4j Schema — constraints and indexes
// Applied once by GraphLoader on first run.
// Safe to re-apply: uses IF NOT EXISTS.

// ── Artifact nodes (one per source file) ──────────────────────────────────────
CREATE CONSTRAINT artifact_id IF NOT EXISTS FOR (a:Artifact) REQUIRE a.id IS UNIQUE;
CREATE INDEX artifact_name IF NOT EXISTS FOR (a:Artifact) ON (a.file_name);
CREATE INDEX artifact_type IF NOT EXISTS FOR (a:Artifact) ON (a.source_type);
CREATE INDEX artifact_domain IF NOT EXISTS FOR (a:Artifact) ON (a.business_domain);

// ── Entity nodes (tables, columns, programs, tasks, …) ────────────────────────
CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE;
CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name);
CREATE INDEX entity_type IF NOT EXISTS FOR (e:Entity) ON (e.entity_type);
CREATE INDEX entity_source IF NOT EXISTS FOR (e:Entity) ON (e.source_file);

// ── Business rule nodes ────────────────────────────────────────────────────────
CREATE CONSTRAINT rule_id IF NOT EXISTS FOR (r:BusinessRule) REQUIRE r.id IS UNIQUE;

// ── Transformation nodes ───────────────────────────────────────────────────────
CREATE CONSTRAINT transform_id IF NOT EXISTS FOR (t:Transformation) REQUIRE t.id IS UNIQUE
