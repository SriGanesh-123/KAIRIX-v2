// Authentic KAIRIX Palette from Streamlit ui/services/graph_service.py
export const NODE_PALETTE = {
  Artifact: { bg: '#E0E7FF', border: '#4338CA', highlight: '#C7D2FE', font: '#312E81', size: 30 },
  Program: { bg: '#DBEAFE', border: '#1D4ED8', highlight: '#BFDBFE', font: '#1E3A8A', size: 30 },
  Package: { bg: '#D1FAE5', border: '#047857', highlight: '#A7F3D0', font: '#064E3B', size: 30 },
  Table: { bg: '#EDE9FE', border: '#6D28D9', highlight: '#DDD6FE', font: '#4C1D95', size: 28 },
  Column: { bg: '#CFFAFE', border: '#0891B2', highlight: '#A5F3FC', font: '#164E63', size: 18 },
  BusinessRule: { bg: '#FEF3C7', border: '#D97706', highlight: '#FDE68A', font: '#78350F', size: 24 },
  Transformation: { bg: '#FFEDD5', border: '#EA580C', highlight: '#FED7AA', font: '#7C2D12', size: 24 },
  CodeBlock: { bg: '#FCE7F3', border: '#BE185D', highlight: '#FBCFE8', font: '#831843', size: 20 },
  Procedure: { bg: '#FCE7F3', border: '#BE185D', highlight: '#FBCFE8', font: '#831843', size: 20 },
  Branch: { bg: '#E0F2FE', border: '#0284C7', highlight: '#BAE6FD', font: '#0369A1', size: 16 },
  Loop: { bg: '#D1FAE5', border: '#059669', highlight: '#A7F3D0', font: '#065F46', size: 16 },
  Statement: { bg: '#F1F5F9', border: '#64748B', highlight: '#E2E8F0', font: '#334155', size: 14 },
  Entity: { bg: '#E2E8F0', border: '#475569', highlight: '#CBD5E1', font: '#0F172A', size: 18 },
};

export const EDGE_PALETTE = {
  READS_FROM: { color: '#0284C7', width: 2.0 },
  WRITES_TO: { color: '#DC2626', width: 2.0 },
  TRANSFORMS: { color: '#EA580C', width: 2.0 },
  CONTAINS: { color: '#94A3B8', width: 1.2 },
  HAS_RULE: { color: '#D97706', width: 1.8 },
  HAS_TRANSFORMATION: { color: '#F97316', width: 1.8 },
  FEEDS_INTO: { color: '#7C3AED', width: 2.2 },
  CALLS: { color: '#4F46E5', width: 2.0 },
  USES: { color: '#059669', width: 1.5 },
  RELATES_TO: { color: '#64748B', width: 1.2 },
  DEFAULT: { color: '#94A3B8', width: 1.2 },
};

export function getNodeColor(type) {
  if (!type) return '#3B82F6';
  const norm = String(type).trim().toLowerCase();
  for (const [key, val] of Object.entries(NODE_PALETTE)) {
    if (norm.includes(key.toLowerCase())) return val.border;
  }
  return '#3B82F6';
}
