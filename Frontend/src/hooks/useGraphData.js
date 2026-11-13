import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { graphApi } from '../services/graphApi';

const BATCH_SIZE = 2000;

/**
 * Custom hook to load, manage, and progressively merge the full Neo4j Aura Graph.
 */
export function useGraphData() {
  const [nodes, setNodes] = useState([]);
  const [links, setLinks] = useState([]);
  const [schema, setSchema] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [loadingProgress, setLoadingProgress] = useState({
    loadedNodes: 0,
    totalNodes: 0,
    loadedLinks: 0,
    totalLinks: 0,
    percentage: 0,
    phase: 'Initializing',
  });

  // Master deduplication maps stored in refs to avoid re-renders during progressive batches
  const nodeMapRef = useRef(new Map());
  const linkMapRef = useRef(new Map());
  const isFetchingRef = useRef(false);

  /**
   * Recalculates degree for each node in the map based on active links
   */
  const computeDegrees = useCallback((nodeMap, linkMap) => {
    for (const node of nodeMap.values()) {
      node.degree = 0;
    }
    for (const link of linkMap.values()) {
      const srcId = typeof link.source === 'object' ? link.source.id : link.source;
      const tgtId = typeof link.target === 'object' ? link.target.id : link.target;
      if (nodeMap.has(srcId)) nodeMap.get(srcId).degree = (nodeMap.get(srcId).degree || 0) + 1;
      if (nodeMap.has(tgtId)) nodeMap.get(tgtId).degree = (nodeMap.get(tgtId).degree || 0) + 1;
    }
  }, []);

  /**
   * Progressive loader that streams batches until the full graph is loaded
   */
  const loadFullGraph = useCallback(async () => {
    if (isFetchingRef.current) return;
    isFetchingRef.current = true;
    setIsLoading(true);
    setError(null);
    nodeMapRef.current.clear();
    linkMapRef.current.clear();

    try {
      setLoadingProgress({
        loadedNodes: 0,
        totalNodes: 0,
        loadedLinks: 0,
        totalLinks: 0,
        percentage: 5,
        phase: 'Connecting to Neo4j Aura & reading schema...',
      });

      // 1. Fetch Schema & Totals
      const schemaData = await graphApi.getSchema();
      setSchema(schemaData);

      const targetTotalNodes = schemaData?.totalNodes || 1827;
      const targetTotalLinks = schemaData?.totalRelationships || 3515;

      let skip = 0;
      let hasMore = true;
      let batchCount = 0;

      while (hasMore) {
        batchCount += 1;
        setLoadingProgress(prev => ({
          ...prev,
          totalNodes: targetTotalNodes,
          totalLinks: targetTotalLinks,
          phase: `Fetching batch ${batchCount} (offset ${skip})...`,
        }));

        const batch = await graphApi.getGraphBatch({ skip, limit: BATCH_SIZE });
        const batchNodes = batch?.nodes || [];
        const batchLinks = batch?.links || [];

        // Progressive merge into master maps
        for (const n of batchNodes) {
          if (!nodeMapRef.current.has(n.id)) {
            nodeMapRef.current.set(n.id, { ...n, degree: 0 });
          }
        }
        for (const l of batchLinks) {
          if (!linkMapRef.current.has(l.id)) {
            linkMapRef.current.set(l.id, { ...l });
          }
        }

        const currentLoadedNodes = nodeMapRef.current.size;
        const currentLoadedLinks = linkMapRef.current.size;
        const pct = Math.min(98, Math.round((currentLoadedNodes / Math.max(1, targetTotalNodes)) * 100));

        setLoadingProgress({
          loadedNodes: currentLoadedNodes,
          totalNodes: targetTotalNodes,
          loadedLinks: currentLoadedLinks,
          totalLinks: targetTotalLinks,
          percentage: pct,
          phase: `Loaded ${currentLoadedNodes.toLocaleString()} / ${targetTotalNodes.toLocaleString()} nodes`,
        });

        hasMore = batch?.pagination?.hasMore || false;
        skip += BATCH_SIZE;

        // If batch returned fewer than requested limit, we have reached the end
        if (batchNodes.length < BATCH_SIZE) {
          hasMore = false;
        }

        // Incrementally push state so the user sees nodes populating
        computeDegrees(nodeMapRef.current, linkMapRef.current);
        setNodes(Array.from(nodeMapRef.current.values()));
        setLinks(Array.from(linkMapRef.current.values()));
      }

      // Finalization
      computeDegrees(nodeMapRef.current, linkMapRef.current);
      const allFinalNodes = Array.from(nodeMapRef.current.values());
      const allFinalLinks = Array.from(linkMapRef.current.values());

      setNodes(allFinalNodes);
      setLinks(allFinalLinks);
      setLoadingProgress({
        loadedNodes: allFinalNodes.length,
        totalNodes: targetTotalNodes,
        loadedLinks: allFinalLinks.length,
        totalLinks: targetTotalLinks,
        percentage: 100,
        phase: `Full system graph ready (${allFinalNodes.length.toLocaleString()} nodes, ${allFinalLinks.length.toLocaleString()} links)`,
      });
    } catch (err) {
      console.error('[useGraphData] Error during full graph load:', err);
      setError(err.message || 'Failed to connect to Neo4j Aura database');
    } finally {
      setIsLoading(false);
      isFetchingRef.current = false;
    }
  }, [computeDegrees]);

  /**
   * Expands 1-hop neighbors of a given node and integrates them into active graph state
   */
  const expandNodeNeighbors = useCallback(async (nodeId) => {
    if (!nodeId) return;
    try {
      const result = await graphApi.expandNode(nodeId);
      const neighbors = result?.neighbors || [];
      const newLinks = result?.links || [];

      let addedCount = 0;
      for (const n of neighbors) {
        if (!nodeMapRef.current.has(n.id)) {
          nodeMapRef.current.set(n.id, { ...n, degree: 0 });
          addedCount += 1;
        }
      }
      for (const l of newLinks) {
        if (!linkMapRef.current.has(l.id)) {
          linkMapRef.current.set(l.id, { ...l });
        }
      }

      if (addedCount > 0 || newLinks.length > 0) {
        computeDegrees(nodeMapRef.current, linkMapRef.current);
        setNodes(Array.from(nodeMapRef.current.values()));
        setLinks(Array.from(linkMapRef.current.values()));
      }
      return { addedCount, totalNeighbors: neighbors.length };
    } catch (err) {
      console.warn(`[useGraphData] Expansion failed for node ${nodeId}:`, err.message);
      return null;
    }
  }, [computeDegrees]);

  // Initial load on mount
  useEffect(() => {
    loadFullGraph();
  }, [loadFullGraph]);

  return {
    nodes,
    links,
    schema,
    isLoading,
    error,
    loadingProgress,
    reloadGraph: loadFullGraph,
    expandNodeNeighbors,
  };
}
