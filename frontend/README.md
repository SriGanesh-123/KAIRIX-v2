# KAIRIX frontend

A dedicated React + TypeScript web UI foundation for KAIRIX, styled with shadcn/ui patterns and a soft-neomorphic design system.

## Stack
- React 18 + TypeScript
- Vite + Tailwind CSS
- Radix UI Slot, shadcn-style local primitives and Lucide icons

## Design tokens

| Token | Value | Usage |
| --- | --- | --- |
| Midnight teal | `#0b3048` | Navigation, typography and primary actions |
| Soft pearl | `#f2f0e9` | Canvas and raised surfaces |
| Neon lime | `#b9f12f` | Primary accent and selected navigation |

The design uses paired soft shadows, inset controls, restrained lime highlights and responsive navigation.

## Run locally

```bash
cd frontend
npm install
npm run dev
```

Production build:

```bash
npm run build
```

## Integration status

This folder currently provides the web UI foundation and page layouts. It is not yet connected to the Python services. The existing application invokes those services through Streamlit directly; a stable HTTP API contract is needed before source counts, ingestion actions, investigation queries or graph data can be presented as live frontend functionality.

Until that API layer exists, the UI deliberately shows disconnected and empty states rather than fabricated business metrics.
