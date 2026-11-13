import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import neo4j from 'neo4j-driver';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables from frontend/server/.env
dotenv.config({ path: path.join(__dirname, '.env') });

const app = express();
const PORT = process.env.PORT || 3001;

// Middlewares
app.use(cors());
app.use(express.json());

// Neo4j Driver Initialization
const uri = process.env.NEO4J_URI || 'neo4j+s://03f0aac2.databases.neo4j.io';
const username = process.env.NEO4J_USERNAME || '03f0aac2';
const password = process.env.NEO4J_PASSWORD || '';
const database = process.env.NEO4J_DATABASE || '03f0aac2';

if (!password) {
  console.warn('[Neo4j Server] WARNING: NEO4J_PASSWORD is not set. Please configure frontend/server/.env');
}

const driver = neo4j.driver(
  uri,
  neo4j.auth.basic(username, password),
  {
    maxConnectionLifetime: 3 * 60 * 60 * 1000, // 3 hours
    maxConnectionPoolSize: 50,
    connectionAcquisitionTimeout: 20000, // 20s
  }
);

// Graceful Driver Shutdown
process.on('SIGINT', async () => {
  await driver.close();
  process.exit(0);
});
process.on('SIGTERM', async () => {
  await driver.close();
  process.exit(0);
});

// Helpers: convert Neo4j types and integers safely to standard JavaScript
function formatValue(val) {
  if (val === null || val === undefined) return null;
  if (neo4j.isInt(val)) {
    return neo4j.integer.inSafeRange(val) ? val.toNumber() : val.toString();
  }
  if (Array.isArray(val)) {
    return val.map(formatValue);
  }
  if (typeof val === 'object') {
    const formatted = {};
    for (const [k, v] of Object.entries(val)) {
      formatted[k] = formatValue(v);
    }
    return formatted;
  }
  return val;
}

function formatProperties(props) {
  if (!props) return {};
  const res = {};
  for (const [k, v] of Object.entries(props)) {
    res[k] = formatValue(v);
  }
  return res;
}

function formatNode(node) {
  if (!node) return null;
  const id = node.elementId || (neo4j.isInt(node.identity) ? node.identity.toString() : String(node.identity));
  const labels = node.labels || [];
  const properties = formatProperties(node.properties || {});
  
  // Prefer properties.name, properties.label, properties.id, or labels[0]
  const label = properties.name || properties.label || properties.title || properties.id || (labels[0] || id);
  const type = properties.type || (labels.length > 0 ? labels[0] : 'Entity');
  const file = properties.source_file || properties.file || properties.file_name || properties.program || '';
  const system = properties.system || properties.system_layer || 
    (labels.includes('COBOL') ? 'COBOL Mainframe' : 
     labels.includes('SSIS') ? 'SSIS Pipeline' : 
     labels.includes('Table') || labels.includes('SQL') ? 'SQL Database' : 'Enterprise Core');

  return {
    id,
    labels,
    label,
    type,
    file,
    system,
    properties,
  };
}

function formatRelationship(rel) {
  if (!rel) return null;
  const id = rel.elementId || (neo4j.isInt(rel.identity) ? rel.identity.toString() : String(rel.identity));
  const source = rel.startNodeElementId || (neo4j.isInt(rel.start) ? rel.start.toString() : String(rel.start));
  const target = rel.endNodeElementId || (neo4j.isInt(rel.end) ? rel.end.toString() : String(rel.end));
  const type = rel.type || 'CONNECTS_TO';
  const properties = formatProperties(rel.properties || {});

  return {
    id,
    source,
    target,
    type,
    label: type,
    properties,
  };
}

// 1. Health Endpoint
app.get('/api/health', async (req, res) => {
  const startTime = Date.now();
  try {
    const serverInfo = await driver.getServerInfo();
    const latency = Date.now() - startTime;
    return res.json({
      success: true,
      data: {
        status: 'healthy',
        neo4j: {
          connected: true,
          address: serverInfo.address,
          version: serverInfo.version || 'Neo4j Aura',
          latency_ms: latency,
        },
      },
    });
  } catch (err) {
    return res.status(500).json({
      success: false,
      error: `Neo4j Aura connection failed: ${err.message}`,
      data: {
        status: 'unhealthy',
        neo4j: { connected: false, error: err.message },
      },
    });
  }
});

// 2. Schema Metadata Endpoint
app.get('/api/schema', async (req, res) => {
  const session = driver.session({ database });
  try {
    const labelsResult = await session.run('CALL db.labels() YIELD label RETURN collect(label) as labels');
    const relTypesResult = await session.run('CALL db.relationshipTypes() YIELD relationshipType RETURN collect(relationshipType) as relationshipTypes');
    const propKeysResult = await session.run('CALL db.propertyKeys() YIELD propertyKey RETURN collect(propertyKey) as propertyKeys');
    
    // Count totals
    const countsResult = await session.run(
      'MATCH (n) WITH count(n) as nodeCount MATCH ()-[r]->() RETURN nodeCount, count(r) as relCount'
    );

    const labels = labelsResult.records[0]?.get('labels') || [];
    const relationshipTypes = relTypesResult.records[0]?.get('relationshipTypes') || [];
    const propertyKeys = propKeysResult.records[0]?.get('propertyKeys') || [];
    
    let totalNodes = 0;
    let totalRelationships = 0;
    if (countsResult.records.length > 0) {
      const rec = countsResult.records[0];
      const nc = rec.get('nodeCount');
      const rc = rec.get('relCount');
      totalNodes = neo4j.isInt(nc) ? nc.toNumber() : Number(nc);
      totalRelationships = neo4j.isInt(rc) ? rc.toNumber() : Number(rc);
    }

    return res.json({
      success: true,
      data: {
        labels,
        relationshipTypes,
        propertyKeys,
        totalNodes,
        totalRelationships,
      },
    });
  } catch (err) {
    console.error('Error in /api/schema:', err);
    return res.status(500).json({ success: false, error: err.message });
  } finally {
    await session.close();
  }
});

// 3. Batched Graph Retrieval Endpoint
app.get('/api/graph', async (req, res) => {
  const session = driver.session({ database });
  try {
    const limit = Math.min(Math.max(parseInt(req.query.limit, 10) || 2000, 100), 5000);
    const skip = Math.max(parseInt(req.query.skip, 10) || 0, 0);

    // Total counts query
    const countRes = await session.run(
      'MATCH (n) WITH count(n) as nodeCount MATCH ()-[r]->() RETURN nodeCount, count(r) as relCount'
    );
    let totalNodes = 1006;
    let totalRelationships = 2822;
    if (countRes.records.length > 0) {
      const rec = countRes.records[0];
      const nc = rec.get('nodeCount');
      const rc = rec.get('relCount');
      totalNodes = neo4j.isInt(nc) ? nc.toNumber() : Number(nc);
      totalRelationships = neo4j.isInt(rc) ? rc.toNumber() : Number(rc);
    }

    // Batched node & link retrieval
    const graphQuery = `
      MATCH (n)
      WITH n SKIP $skip LIMIT $limit
      OPTIONAL MATCH (n)-[r]->(m)
      RETURN collect(DISTINCT n) as primaryNodes,
             collect(DISTINCT m) as neighborNodes,
             collect(DISTINCT r) as rels
    `;

    const result = await session.run(graphQuery, {
      skip: neo4j.int(skip),
      limit: neo4j.int(limit),
    });

    const nodeMap = new Map();
    const linkMap = new Map();

    if (result.records.length > 0) {
      const record = result.records[0];
      const primaryNodes = record.get('primaryNodes') || [];
      const neighborNodes = record.get('neighborNodes') || [];
      const rels = record.get('rels') || [];

      // Add all primary nodes
      for (const rawNode of primaryNodes) {
        const fn = formatNode(rawNode);
        if (fn && !nodeMap.has(fn.id)) nodeMap.set(fn.id, fn);
      }

      // Add neighbor nodes
      for (const rawNode of neighborNodes) {
        if (!rawNode) continue;
        const fn = formatNode(rawNode);
        if (fn && !nodeMap.has(fn.id)) nodeMap.set(fn.id, fn);
      }

      // Add all relationships
      for (const rawRel of rels) {
        if (!rawRel) continue;
        const fr = formatRelationship(rawRel);
        if (fr && !linkMap.has(fr.id)) {
          linkMap.set(fr.id, fr);
        }
      }
    }

    const nodes = Array.from(nodeMap.values());
    // Only include links whose source & target exist in the nodes set
    const validLinks = Array.from(linkMap.values()).filter(
      l => nodeMap.has(l.source) && nodeMap.has(l.target)
    );

    const hasMore = skip + limit < totalNodes;

    return res.json({
      success: true,
      data: {
        nodes,
        links: validLinks,
        pagination: {
          skip,
          limit,
          returnedNodes: nodes.length,
          totalNodes,
          totalRelationships,
          hasMore,
        },
      },
    });
  } catch (err) {
    console.error('Error in /api/graph:', err);
    return res.status(500).json({ success: false, error: err.message });
  } finally {
    await session.close();
  }
});

// 4. Node Expand Neighborhood Endpoint
app.get('/api/graph/expand/:nodeId', async (req, res) => {
  const session = driver.session({ database });
  const { nodeId } = req.params;

  try {
    const expandQuery = `
      MATCH (n)
      WHERE n.id = $nodeId OR n.name = $nodeId OR elementId(n) = $nodeId
      MATCH (n)-[r]-(m)
      RETURN collect(DISTINCT m) as neighbors, collect(DISTINCT r) as rels
      LIMIT 100
    `;

    const result = await session.run(expandQuery, { nodeId });
    const neighborNodes = [];
    const neighborLinks = [];

    if (result.records.length > 0) {
      const rec = result.records[0];
      const neighbors = rec.get('neighbors') || [];
      const rels = rec.get('rels') || [];

      for (const n of neighbors) {
        const fn = formatNode(n);
        if (fn) neighborNodes.push(fn);
      }
      for (const r of rels) {
        const fr = formatRelationship(r);
        if (fr) neighborLinks.push(fr);
      }
    }

    return res.json({
      success: true,
      data: {
        nodeId,
        neighbors: neighborNodes,
        links: neighborLinks,
      },
    });
  } catch (err) {
    console.error(`Error in /api/graph/expand/${nodeId}:`, err);
    return res.status(500).json({ success: false, error: err.message });
  } finally {
    await session.close();
  }
});

app.listen(PORT, () => {
  console.log(`[Neo4j Express Gateway] Running on http://localhost:${PORT}`);
  console.log(`[Neo4j Express Gateway] Connected target: ${uri}`);
});
