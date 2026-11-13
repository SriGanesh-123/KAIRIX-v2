/**
 * Client service for Neo4j Aura Graph Gateway API
 * Communicates with the Express server proxied at /api
 */

const API_BASE = '/api';

export const graphApi = {
  /**
   * Health check
   */
  async getHealth() {
    try {
      const res = await fetch(`${API_BASE}/health`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      console.warn('[GraphAPI] Health check failed:', err.message);
      return { success: false, error: err.message };
    }
  },

  /**
   * Fetch schema labels, relationship types, and total counts
   */
  async getSchema() {
    try {
      const res = await fetch(`${API_BASE}/schema`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      return json.data || null;
    } catch (err) {
      console.error('[GraphAPI] Failed to fetch schema:', err.message);
      throw err;
    }
  },

  /**
   * Fetch batched nodes and relationships
   * @param {Object} params
   * @param {number} params.skip
   * @param {number} params.limit
   */
  async getGraphBatch({ skip = 0, limit = 2000 } = {}) {
    try {
      const url = `${API_BASE}/graph?skip=${skip}&limit=${limit}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      const json = await res.json();
      if (!json.success) throw new Error(json.error || 'Failed to load graph batch');
      return json.data;
    } catch (err) {
      console.error(`[GraphAPI] Error fetching graph batch (skip=${skip}, limit=${limit}):`, err.message);
      throw err;
    }
  },

  /**
   * Expand 1-hop neighborhood for a specific node
   * @param {string} nodeId
   */
  async expandNode(nodeId) {
    try {
      const res = await fetch(`${API_BASE}/graph/expand/${encodeURIComponent(nodeId)}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      if (!json.success) throw new Error(json.error || 'Failed to expand node');
      return json.data;
    } catch (err) {
      console.error(`[GraphAPI] Error expanding node ${nodeId}:`, err.message);
      throw err;
    }
  },
};
