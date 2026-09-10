import os

target_path = r"c:\Users\GaneshSriKumarMarimu\legacy-code-agentic-rag\probleam statement\index.html"

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>KAIRIX — Complete System Architecture & Engineering Structure</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Outfit:wght@500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {
      /* Neumorphic & Theme Colors */
      --bg-base: #e9eef5;
      --surface: #e9eef5;
      --surface-card: #eef3f9;
      --surface-inset: #e0e6ee;
      
      --neu-shadow-dark: #c5ced9;
      --neu-shadow-light: #ffffff;
      
      --shadow-outset: 8px 8px 18px var(--neu-shadow-dark), -8px -8px 18px var(--neu-shadow-light);
      --shadow-outset-sm: 4px 4px 10px var(--neu-shadow-dark), -4px -4px 10px var(--neu-shadow-light);
      --shadow-inset: inset 4px 4px 8px var(--neu-shadow-dark), inset -4px -4px 8px var(--neu-shadow-light);
      --shadow-pressed: inset 2px 2px 5px var(--neu-shadow-dark), inset -2px -2px 5px var(--neu-shadow-light);

      /* Typography & Text */
      --text-main: #0f172a;
      --text-muted: #334155;
      --text-dim: #64748b;

      /* Distinct Component Colors */
      --brand-primary: #2563eb;
      --brand-gradient: linear-gradient(135deg, #1d4ed8 0%, #0284c7 100%);
      
      --cobol-color: #d97706;
      --cobol-bg: rgba(217, 119, 6, 0.1);
      
      --ssis-color: #ea580c;
      --ssis-bg: rgba(234, 88, 12, 0.1);
      
      --sql-color: #7c3aed;
      --sql-bg: rgba(124, 58, 237, 0.1);
      
      --agent-color: #0284c7;
      --agent-bg: rgba(2, 132, 199, 0.1);
      
      --graph-color: #059669;
      --graph-bg: rgba(5, 150, 105, 0.1);
      
      --vector-color: #db2777;
      --vector-bg: rgba(219, 39, 119, 0.1);
      
      --api-color: #4f46e5;
      --api-bg: rgba(79, 70, 229, 0.1);

      --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
      --font-display: 'Outfit', sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background-color: var(--bg-base);
      color: var(--text-main);
      font-family: var(--font-sans);
      line-height: 1.6;
      padding-bottom: 6rem;
      overflow-x: hidden;
      position: relative;
    }

    /* Background Animated Canvas */
    #bg-canvas {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      z-index: -1;
      pointer-events: none;
      opacity: 0.45;
    }

    /* Navigation Header */
    header.nav-header {
      background: rgba(233, 238, 245, 0.88);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid rgba(255, 255, 255, 0.7);
      padding: 0.9rem 2.5rem;
      position: sticky;
      top: 0;
      z-index: 100;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 4px 15px rgba(197, 206, 217, 0.4);
    }

    .brand-group {
      display: flex;
      align-items: center;
      gap: 1rem;
    }

    .brand-icon {
      width: 44px;
      height: 44px;
      border-radius: 12px;
      background: var(--brand-gradient);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-weight: 800;
      font-size: 1.25rem;
      box-shadow: 4px 4px 10px rgba(37, 99, 235, 0.35);
    }

    .brand-text h1 {
      font-family: var(--font-display);
      font-size: 1.35rem;
      font-weight: 800;
      color: #0f172a;
      letter-spacing: -0.02em;
    }

    .brand-text p {
      font-size: 0.75rem;
      color: var(--text-dim);
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }

    .nav-links {
      display: flex;
      gap: 0.6rem;
      align-items: center;
    }

    .nav-btn {
      padding: 0.5rem 0.9rem;
      border-radius: 999px;
      background: var(--surface);
      box-shadow: var(--shadow-outset-sm);
      text-decoration: none;
      color: var(--text-muted);
      font-size: 0.82rem;
      font-weight: 600;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      gap: 0.4rem;
      border: 1px solid rgba(255, 255, 255, 0.6);
    }

    .nav-btn:hover {
      box-shadow: var(--shadow-pressed);
      color: var(--brand-primary);
      transform: translateY(1px);
    }

    .status-badge {
      display: flex;
      align-items: center;
      gap: 0.45rem;
      padding: 0.4rem 0.85rem;
      border-radius: 999px;
      background: rgba(5, 150, 105, 0.1);
      border: 1px solid rgba(5, 150, 105, 0.3);
      color: #047857;
      font-size: 0.76rem;
      font-weight: 700;
    }

    .status-dot {
      width: 8px;
      height: 8px;
      background: #10b981;
      border-radius: 50%;
      animation: pulse-dot 2s infinite;
    }

    @keyframes pulse-dot {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.4; transform: scale(1.3); }
    }

    /* Main Container */
    main.content-wrap {
      max-width: 1400px;
      margin: 0 auto;
      padding: 2.5rem 2rem;
      display: flex;
      flex-direction: column;
      gap: 3.5rem;
    }

    /* Hero Section */
    .hero-panel {
      border-radius: 28px;
      background: var(--surface);
      box-shadow: var(--shadow-outset);
      padding: 3rem;
      position: relative;
      overflow: hidden;
      border: 1px solid rgba(255, 255, 255, 0.8);
    }

    .hero-badge {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.4rem 1rem;
      border-radius: 999px;
      background: rgba(37, 99, 235, 0.1);
      border: 1px solid rgba(37, 99, 235, 0.25);
      color: var(--brand-primary);
      font-size: 0.8rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      margin-bottom: 1.25rem;
      text-transform: uppercase;
    }

    .hero-title {
      font-family: var(--font-display);
      font-size: 2.85rem;
      font-weight: 800;
      line-height: 1.18;
      color: #0f172a;
      letter-spacing: -0.03em;
      margin-bottom: 1.2rem;
      max-width: 950px;
    }

    .hero-title span {
      background: var(--brand-gradient);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .hero-desc {
      font-size: 1.12rem;
      color: var(--text-muted);
      max-width: 860px;
      line-height: 1.65;
      margin-bottom: 2.2rem;
    }

    .kpi-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 1.5rem;
    }

    .kpi-card {
      border-radius: 18px;
      background: var(--surface);
      box-shadow: var(--shadow-inset);
      padding: 1.25rem 1.5rem;
      display: flex;
      align-items: center;
      gap: 1.1rem;
      border: 1px solid rgba(255, 255, 255, 0.5);
    }

    .kpi-icon {
      width: 48px;
      height: 48px;
      border-radius: 14px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.4rem;
      flex-shrink: 0;
      box-shadow: var(--shadow-outset-sm);
    }

    .kpi-value {
      font-family: var(--font-display);
      font-size: 1.45rem;
      font-weight: 800;
      color: #0f172a;
      line-height: 1.2;
    }

    .kpi-label {
      font-size: 0.78rem;
      color: var(--text-dim);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    /* Section Headers */
    .section-head {
      margin-bottom: 1.75rem;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      flex-wrap: wrap;
      gap: 1rem;
    }

    .section-head .tag {
      font-size: 0.78rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--brand-primary);
      margin-bottom: 0.35rem;
      display: block;
    }

    .section-head h2 {
      font-family: var(--font-display);
      font-size: 2rem;
      font-weight: 800;
      letter-spacing: -0.02em;
      color: #0f172a;
    }

    .section-head p {
      font-size: 0.95rem;
      color: var(--text-dim);
      max-width: 650px;
    }

    /* SECTION 1: Master Interactive Architecture Blueprint */
    .blueprint-wrapper {
      border-radius: 26px;
      background: var(--surface);
      box-shadow: var(--shadow-outset);
      padding: 2.25rem;
      border: 1px solid rgba(255, 255, 255, 0.8);
      position: relative;
    }

    .blueprint-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1.5rem;
      position: relative;
    }

    @media (max-width: 1100px) {
      .blueprint-grid {
        grid-template-columns: 1fr;
      }
    }

    .blueprint-col {
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
      position: relative;
    }

    .col-header {
      border-radius: 16px;
      padding: 1rem 1.25rem;
      background: var(--surface);
      box-shadow: var(--shadow-outset-sm);
      display: flex;
      align-items: center;
      gap: 0.8rem;
      border: 1px solid rgba(255, 255, 255, 0.7);
    }

    .col-num {
      width: 30px;
      height: 30px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 0.85rem;
      color: white;
      flex-shrink: 0;
    }

    .col-header-text h3 {
      font-family: var(--font-display);
      font-size: 1rem;
      font-weight: 700;
      color: #0f172a;
      line-height: 1.2;
    }

    .col-header-text span {
      font-size: 0.72rem;
      color: var(--text-dim);
      font-weight: 500;
      display: block;
    }

    /* Architecture Block Cards */
    .arch-card {
      border-radius: 18px;
      background: var(--surface-card);
      box-shadow: var(--shadow-outset-sm);
      padding: 1.25rem;
      border: 1px solid rgba(255, 255, 255, 0.8);
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      cursor: pointer;
      position: relative;
    }

    .arch-card:hover {
      transform: translateY(-3px);
      box-shadow: 10px 10px 22px var(--neu-shadow-dark), -10px -10px 22px var(--neu-shadow-light);
    }

    .arch-card.active {
      border-color: var(--brand-primary);
      box-shadow: var(--shadow-pressed), 0 0 0 2px var(--brand-primary);
      background: #f1f5fa;
    }

    .card-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 0.75rem;
    }

    .card-badge {
      font-size: 0.68rem;
      font-weight: 700;
      padding: 0.25rem 0.65rem;
      border-radius: 999px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    .card-path {
      font-family: var(--font-mono);
      font-size: 0.7rem;
      color: var(--text-dim);
      background: rgba(0,0,0,0.04);
      padding: 0.2rem 0.45rem;
      border-radius: 6px;
    }

    .card-title {
      font-family: var(--font-display);
      font-size: 1.05rem;
      font-weight: 700;
      color: #0f172a;
      margin-bottom: 0.35rem;
      display: flex;
      align-items: center;
      gap: 0.45rem;
    }

    .card-desc {
      font-size: 0.82rem;
      color: var(--text-muted);
      line-height: 1.45;
      margin-bottom: 0.85rem;
    }

    .tag-pills {
      display: flex;
      flex-wrap: wrap;
      gap: 0.35rem;
    }

    .pill {
      font-size: 0.68rem;
      font-weight: 600;
      padding: 0.18rem 0.5rem;
      border-radius: 6px;
      background: rgba(255, 255, 255, 0.7);
      border: 1px solid rgba(0,0,0,0.06);
      color: var(--text-muted);
    }

    /* Live Blueprint Inspector */
    .blueprint-inspector {
      margin-top: 1.75rem;
      border-radius: 20px;
      background: var(--surface);
      box-shadow: var(--shadow-inset);
      padding: 1.75rem;
      border: 1px solid rgba(255, 255, 255, 0.6);
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .inspector-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid rgba(0,0,0,0.06);
      padding-bottom: 0.85rem;
      flex-wrap: wrap;
      gap: 0.5rem;
    }

    .inspector-title {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }

    .inspector-title h4 {
      font-family: var(--font-display);
      font-size: 1.25rem;
      font-weight: 700;
      color: #0f172a;
    }

    .inspector-body {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 1.5rem;
    }

    @media (max-width: 900px) {
      .inspector-body { grid-template-columns: 1fr; }
    }

    .inspect-col {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }

    .inspect-col h5 {
      font-size: 0.76rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-dim);
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }

    .inspect-content {
      font-size: 0.86rem;
      color: var(--text-muted);
      line-height: 1.5;
    }

    .inspect-code {
      font-family: var(--font-mono);
      font-size: 0.76rem;
      background: #1e293b;
      color: #e2e8f0;
      padding: 0.75rem;
      border-radius: 10px;
      overflow-x: auto;
      border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* SECTION 2: 7-Stage LangGraph Flowchart */
    .langgraph-box {
      border-radius: 26px;
      background: var(--surface);
      box-shadow: var(--shadow-outset);
      padding: 2.25rem;
      border: 1px solid rgba(255, 255, 255, 0.8);
    }

    .stages-scroll {
      display: grid;
      grid-template-columns: repeat(7, 1fr);
      gap: 1rem;
      margin-top: 1.5rem;
      position: relative;
    }

    @media (max-width: 1200px) {
      .stages-scroll {
        grid-template-columns: repeat(2, 1fr);
      }
    }

    @media (max-width: 650px) {
      .stages-scroll {
        grid-template-columns: 1fr;
      }
    }

    .stage-step {
      border-radius: 16px;
      background: var(--surface-card);
      box-shadow: var(--shadow-outset-sm);
      padding: 1.1rem;
      display: flex;
      flex-direction: column;
      gap: 0.65rem;
      border: 1px solid rgba(255, 255, 255, 0.8);
      position: relative;
      transition: all 0.2s ease;
    }

    .stage-step:hover {
      transform: translateY(-2px);
      box-shadow: var(--shadow-outset);
    }

    .stage-num-badge {
      width: 26px;
      height: 26px;
      border-radius: 8px;
      background: var(--brand-gradient);
      color: white;
      font-size: 0.75rem;
      font-weight: 800;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .stage-step h4 {
      font-family: var(--font-display);
      font-size: 0.95rem;
      font-weight: 700;
      color: #0f172a;
      line-height: 1.25;
    }

    .stage-step p {
      font-size: 0.77rem;
      color: var(--text-dim);
      line-height: 1.4;
    }

    .confidence-tag {
      font-family: var(--font-mono);
      font-size: 0.68rem;
      font-weight: 600;
      padding: 0.2rem 0.45rem;
      border-radius: 6px;
      background: rgba(5, 150, 105, 0.1);
      color: #047857;
      border: 1px solid rgba(5, 150, 105, 0.2);
      width: fit-content;
    }

    /* SECTION 3: The 3 Autonomous Multi-Agent Triad */
    .agents-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1.75rem;
    }

    @media (max-width: 950px) {
      .agents-grid { grid-template-columns: 1fr; }
    }

    .agent-card {
      border-radius: 24px;
      background: var(--surface);
      box-shadow: var(--shadow-outset);
      padding: 2rem;
      border: 1px solid rgba(255, 255, 255, 0.8);
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
      position: relative;
      overflow: hidden;
    }

    .agent-top {
      display: flex;
      align-items: flex-start;
      gap: 1.1rem;
    }

    .agent-avatar {
      width: 56px;
      height: 56px;
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.75rem;
      flex-shrink: 0;
      box-shadow: var(--shadow-outset-sm);
    }

    .agent-info h3 {
      font-family: var(--font-display);
      font-size: 1.3rem;
      font-weight: 800;
      color: #0f172a;
      line-height: 1.2;
    }

    .agent-role {
      font-size: 0.78rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-top: 0.2rem;
    }

    .agent-bullets {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
    }

    .agent-bullets li {
      font-size: 0.84rem;
      color: var(--text-muted);
      display: flex;
      align-items: flex-start;
      gap: 0.6rem;
      line-height: 1.45;
    }

    .agent-bullets li::before {
      content: "✔";
      font-size: 0.75rem;
      font-weight: 800;
      color: var(--brand-primary);
      margin-top: 0.15rem;
    }

    .agent-io-box {
      border-radius: 14px;
      background: var(--surface-inset);
      box-shadow: var(--shadow-inset);
      padding: 0.9rem 1.1rem;
      display: flex;
      flex-direction: column;
      gap: 0.4rem;
    }

    .agent-io-item {
      font-size: 0.76rem;
      display: flex;
      gap: 0.5rem;
    }

    .agent-io-label {
      font-weight: 700;
      color: var(--text-dim);
      min-width: 55px;
    }

    .agent-io-val {
      font-family: var(--font-mono);
      color: #0f172a;
      font-size: 0.74rem;
    }

    /* SECTION 4: Live Interactive Dataflow Simulator */
    .simulator-box {
      border-radius: 26px;
      background: var(--surface);
      box-shadow: var(--shadow-outset);
      padding: 2.25rem;
      border: 1px solid rgba(255, 255, 255, 0.8);
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }

    .sim-controls {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 1rem;
      padding-bottom: 1rem;
      border-bottom: 1px solid rgba(0,0,0,0.06);
    }

    .sim-actions {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }

    .sim-btn {
      padding: 0.55rem 1.25rem;
      border-radius: 12px;
      border: none;
      cursor: pointer;
      font-weight: 700;
      font-size: 0.84rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      transition: all 0.2s ease;
      background: var(--surface);
      box-shadow: var(--shadow-outset-sm);
      color: var(--text-main);
    }

    .sim-btn:hover {
      box-shadow: var(--shadow-pressed);
      color: var(--brand-primary);
    }

    .sim-btn.primary {
      background: var(--brand-gradient);
      color: white;
      box-shadow: 4px 4px 12px rgba(37, 99, 235, 0.35);
    }

    .sim-pipeline {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 1rem;
      position: relative;
      margin: 1rem 0;
    }

    @media (max-width: 900px) {
      .sim-pipeline { grid-template-columns: 1fr; }
    }

    .sim-node {
      border-radius: 18px;
      background: var(--surface);
      box-shadow: var(--shadow-outset-sm);
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
      border: 2px solid transparent;
      transition: all 0.3s ease;
      position: relative;
    }

    .sim-node.active-sim {
      border-color: #2563eb;
      background: #f0f6ff;
      box-shadow: 0 0 20px rgba(37, 99, 235, 0.25);
      transform: scale(1.02);
    }

    .sim-node-num {
      font-size: 0.7rem;
      font-weight: 800;
      color: var(--text-dim);
    }

    .sim-node h4 {
      font-family: var(--font-display);
      font-size: 1rem;
      font-weight: 700;
      color: #0f172a;
    }

    .sim-node p {
      font-size: 0.77rem;
      color: var(--text-dim);
      line-height: 1.4;
    }

    .sim-status {
      font-family: var(--font-mono);
      font-size: 0.68rem;
      font-weight: 600;
      padding: 0.2rem 0.5rem;
      border-radius: 6px;
      background: rgba(0,0,0,0.05);
      width: fit-content;
    }

    .sim-detail-panel {
      border-radius: 18px;
      background: #111827;
      color: #f8fafc;
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      box-shadow: var(--shadow-inset);
    }

    .sim-detail-title {
      font-family: var(--font-display);
      font-size: 1.15rem;
      font-weight: 700;
      color: #60a5fa;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .sim-detail-text {
      font-size: 0.88rem;
      color: #cbd5e1;
      line-height: 1.6;
    }

    .sim-detail-code {
      font-family: var(--font-mono);
      font-size: 0.8rem;
      background: #1f2937;
      padding: 1rem;
      border-radius: 10px;
      color: #a7f3d0;
      border: 1px solid rgba(255, 255, 255, 0.1);
      overflow-x: auto;
    }

    /* SECTION 5: Directory Structure Tree Visualizer */
    .tree-box {
      border-radius: 26px;
      background: var(--surface);
      box-shadow: var(--shadow-outset);
      padding: 2.25rem;
      border: 1px solid rgba(255, 255, 255, 0.8);
      display: grid;
      grid-template-columns: 1.1fr 1.4fr;
      gap: 2rem;
    }

    @media (max-width: 950px) {
      .tree-box { grid-template-columns: 1fr; }
    }

    .tree-viewer {
      border-radius: 18px;
      background: var(--surface-inset);
      box-shadow: var(--shadow-inset);
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 0.4rem;
      font-family: var(--font-mono);
      font-size: 0.82rem;
    }

    .tree-item {
      padding: 0.45rem 0.75rem;
      border-radius: 8px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: space-between;
      color: #1e293b;
      transition: all 0.15s ease;
    }

    .tree-item:hover {
      background: rgba(255, 255, 255, 0.8);
      color: var(--brand-primary);
    }

    .tree-item.selected {
      background: #ffffff;
      box-shadow: var(--shadow-outset-sm);
      color: var(--brand-primary);
      font-weight: 600;
    }

    .tree-name {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .tree-badge {
      font-size: 0.65rem;
      font-weight: 700;
      padding: 0.15rem 0.45rem;
      border-radius: 4px;
      text-transform: uppercase;
    }

    .tree-info-panel {
      border-radius: 18px;
      background: var(--surface-card);
      box-shadow: var(--shadow-outset-sm);
      padding: 1.75rem;
      border: 1px solid rgba(255, 255, 255, 0.9);
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }

    .tree-info-title {
      font-family: var(--font-display);
      font-size: 1.4rem;
      font-weight: 800;
      color: #0f172a;
      display: flex;
      align-items: center;
      gap: 0.6rem;
    }

    .tree-info-path {
      font-family: var(--font-mono);
      font-size: 0.78rem;
      color: var(--text-dim);
      background: rgba(0,0,0,0.05);
      padding: 0.25rem 0.6rem;
      border-radius: 6px;
      width: fit-content;
    }

    .tree-info-desc {
      font-size: 0.92rem;
      color: var(--text-muted);
      line-height: 1.6;
    }

    .tree-file-list {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }

    .tree-file-list li {
      font-size: 0.8rem;
      font-family: var(--font-mono);
      background: rgba(255, 255, 255, 0.7);
      padding: 0.4rem 0.6rem;
      border-radius: 6px;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      border: 1px solid rgba(0,0,0,0.04);
    }

    /* SECTION 6: Traditional RAG vs KAIRIX Comparison */
    .compare-table {
      width: 100%;
      border-collapse: separate;
      border-spacing: 0;
      border-radius: 20px;
      overflow: hidden;
      box-shadow: var(--shadow-outset);
      background: var(--surface);
      border: 1px solid rgba(255, 255, 255, 0.8);
      margin-top: 1.5rem;
    }

    .compare-table th, .compare-table td {
      padding: 1.1rem 1.5rem;
      text-align: left;
    }

    .compare-table th {
      background: #e2e8f0;
      font-family: var(--font-display);
      font-size: 0.88rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #334155;
    }

    .compare-table tr:not(:last-child) td {
      border-bottom: 1px solid rgba(0,0,0,0.06);
    }

    .compare-table td {
      font-size: 0.88rem;
      line-height: 1.5;
    }

    .td-metric {
      font-weight: 700;
      color: #0f172a;
      width: 25%;
    }

    .td-trad {
      color: #dc2626;
      background: rgba(220, 38, 38, 0.03);
      width: 35%;
    }

    .td-kairix {
      color: #047857;
      font-weight: 600;
      background: rgba(5, 150, 105, 0.05);
      width: 40%;
    }

    /* Footer */
    footer.app-footer {
      text-align: center;
      padding: 3rem 1rem 1rem;
      color: var(--text-dim);
      font-size: 0.84rem;
    }

    footer .brand-sign {
      font-family: var(--font-display);
      font-weight: 700;
      color: #0f172a;
      margin-bottom: 0.35rem;
    }
  </style>
</head>
<body>

  <!-- Background Particle Network Canvas -->
  <canvas id="bg-canvas"></canvas>

  <!-- Top Sticky Header -->
  <header class="nav-header">
    <div class="brand-group">
      <div class="brand-icon">K</div>
      <div class="brand-text">
        <h1>KAIRIX</h1>
        <p>Enterprise Multi-Agent Reverse Engineering Architecture</p>
      </div>
    </div>
    <div class="nav-links">
      <a href="#blueprint" class="nav-btn">🏗️ Blueprint</a>
      <a href="#langgraph" class="nav-btn">⚡ 7-Stage Pipeline</a>
      <a href="#agents" class="nav-btn">🤖 Agent Triad</a>
      <a href="#simulator" class="nav-btn">🔄 Live Simulation</a>
      <a href="#tree" class="nav-btn">📁 Repository Tree</a>
      <div class="status-badge">
        <div class="status-dot"></div>
        <span>Architecture Active</span>
      </div>
    </div>
  </header>

  <main class="content-wrap">

    <!-- Hero Section -->
    <section class="hero-panel">
      <div class="hero-badge">🏛️ System Architecture & Structural Blueprint</div>
      <h2 class="hero-title">
        Demystifying <span>40-Year-Old Multi-Dialect Legacy Code</span> with Dual-Memory Agentic RAG
      </h2>
      <p class="hero-desc">
        KAIRIX transforms enterprise legacy codebases (Mainframe COBOL, Microsoft SSIS ETL, Guidewire SQL) into living, queryable knowledge. By orchestrating deterministic AST parsers with a 7-stage LangGraph pipeline and a dual-memory store (Neo4j Graph + Pinecone Vectors), KAIRIX achieves 100% line-anchored reverse engineering without hallucinations.
      </p>

      <div class="kpi-row">
        <div class="kpi-card">
          <div class="kpi-icon" style="background: var(--cobol-bg); color: var(--cobol-color);">📜</div>
          <div>
            <div class="kpi-value">3 Dialects</div>
            <div class="kpi-label">COBOL 85, SSIS XML, SQL</div>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon" style="background: var(--agent-bg); color: var(--agent-color);">⚡</div>
          <div>
            <div class="kpi-value">7 Stages</div>
            <div class="kpi-label">LangGraph Agent Machine</div>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon" style="background: var(--graph-bg); color: var(--graph-color);">🕸️</div>
          <div>
            <div class="kpi-value">Dual Memory</div>
            <div class="kpi-label">Neo4j Graph + Pinecone</div>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon" style="background: var(--vector-bg); color: var(--vector-color);">🎯</div>
          <div>
            <div class="kpi-value">100% Anchored</div>
            <div class="kpi-label">Deterministic Line Citations</div>
          </div>
        </div>
      </div>
    </section>

    <!-- SECTION 1: Interactive System Architecture Blueprint -->
    <section id="blueprint">
      <div class="section-head">
        <div>
          <span class="tag">End-to-End System Topology</span>
          <h2>4-Layer Architecture Blueprint</h2>
          <p>Click any architectural component to inspect its implementation, inputs, outputs, and repo mapping.</p>
        </div>
      </div>

      <div class="blueprint-wrapper">
        <div class="blueprint-grid">

          <!-- Layer 1: Ingestion -->
          <div class="blueprint-col">
            <div class="col-header">
              <div class="col-num" style="background: var(--cobol-color);">L1</div>
              <div class="col-header-text">
                <h3>Legacy Source Layer</h3>
                <span>source/ &bull; Multi-Dialect</span>
              </div>
            </div>

            <!-- Card 1: COBOL -->
            <div class="arch-card active" onclick="inspectComponent('cobol')">
              <div class="card-top">
                <span class="card-badge" style="background: var(--cobol-bg); color: var(--cobol-color);">Mainframe</span>
                <span class="card-path">source/mainframe/</span>
              </div>
              <h4 class="card-title">📜 COBOL 85 Programs</h4>
              <p class="card-desc">Batch rating algorithms, punch-card columns (1-6 seq, 7 indicator, 8-72 code), and policy math routines.</p>
              <div class="tag-pills">
                <span class="pill">EARNPREM.CBL</span>
                <span class="pill">PREMCALC.CBL</span>
                <span class="pill">Fixed 80-Col</span>
              </div>
            </div>

            <!-- Card 2: SSIS -->
            <div class="arch-card" onclick="inspectComponent('ssis')">
              <div class="card-top">
                <span class="card-badge" style="background: var(--ssis-bg); color: var(--ssis-color);">ETL Pipeline</span>
                <span class="card-path">source/ssis/</span>
              </div>
              <h4 class="card-title">🔀 SSIS DTSX Packages</h4>
              <p class="card-desc">Microsoft SQL Server Integration Services XML packages, data pipelines, and embedded business guardrails.</p>
              <div class="tag-pills">
                <span class="pill">Extract_Premium.dtsx</span>
                <span class="pill">Data Flow Tasks</span>
                <span class="pill">BR-07 / BR-08</span>
              </div>
            </div>

            <!-- Card 3: SQL -->
            <div class="arch-card" onclick="inspectComponent('sql')">
              <div class="card-top">
                <span class="card-badge" style="background: var(--sql-bg); color: var(--sql-color);">Analytics</span>
                <span class="card-path">source/sql/</span>
              </div>
              <h4 class="card-title">🗄️ Guidewire SQL Views</h4>
              <p class="card-desc">1,000+ lines of enterprise joins, staging schemas, and financial aggregation reports.</p>
              <div class="tag-pills">
                <span class="pill">PolicyCenter_CPP.sql</span>
                <span class="pill">ClaimCenter.sql</span>
                <span class="pill">Multi-Table Joins</span>
              </div>
            </div>
          </div>

          <!-- Layer 2: Knowledge Engineering -->
          <div class="blueprint-col">
            <div class="col-header">
              <div class="col-num" style="background: var(--agent-color);">L2</div>
              <div class="col-header-text">
                <h3>Extraction & Agents</h3>
                <span>knowledge_engineering_agent/</span>
              </div>
            </div>

            <!-- Card 4: Deterministic Parsers -->
            <div class="arch-card" onclick="inspectComponent('parsers')">
              <div class="card-top">
                <span class="card-badge" style="background: var(--agent-bg); color: var(--agent-color);">AST Parsers</span>
                <span class="card-path">parsers/</span>
              </div>
              <h4 class="card-title">🌲 Deterministic AST</h4>
              <p class="card-desc">Tree-sitter & SQLGlot parse raw dialects into syntax trees, extracting tables, rules, and variables with 1.0 confidence.</p>
              <div class="tag-pills">
                <span class="pill">tree-sitter-cobol</span>
                <span class="pill">sqlglot AST</span>
                <span class="pill">Zero Hallucination</span>
              </div>
            </div>

            <!-- Card 5: LangGraph Pipeline -->
            <div class="arch-card" onclick="inspectComponent('langgraph')">
              <div class="card-top">
                <span class="card-badge" style="background: var(--agent-bg); color: var(--agent-color);">Orchestration</span>
                <span class="card-path">knowledge_engineering_agent/</span>
              </div>
              <h4 class="card-title">⚡ 7-Stage LangGraph</h4>
              <p class="card-desc">Cyclic state machine reconciling parser facts with NVIDIA NIM LLM multi-pass business logic discovery.</p>
              <div class="tag-pills">
                <span class="pill">Pydantic v2</span>
                <span class="pill">Reconciliation</span>
                <span class="pill">Line Anchoring</span>
              </div>
            </div>

            <!-- Card 6: Canonical Packages -->
            <div class="arch-card" onclick="inspectComponent('canonical')">
              <div class="card-top">
                <span class="card-badge" style="background: var(--agent-bg); color: var(--agent-color);">Artifacts</span>
                <span class="card-path">output/knowledge/</span>
              </div>
              <h4 class="card-title">📦 Canonical Packages</h4>
              <p class="card-desc">Standardized JSON artifacts containing nodes, edges, line-number citations, and Markdown functional summaries.</p>
              <div class="tag-pills">
                <span class="pill">*_knowledge_package.json</span>
                <span class="pill">*_summary.md</span>
              </div>
            </div>
          </div>

          <!-- Layer 3: Dual-Memory Knowledge Store -->
          <div class="blueprint-col">
            <div class="col-header">
              <div class="col-num" style="background: var(--graph-color);">L3</div>
              <div class="col-header-text">
                <h3>Dual-Memory Store</h3>
                <span>graph_layer/ & vector_layer/</span>
              </div>
            </div>

            <!-- Card 7: Neo4j Aura -->
            <div class="arch-card" onclick="inspectComponent('neo4j')">
              <div class="card-top">
                <span class="card-badge" style="background: var(--graph-bg); color: var(--graph-color);">Knowledge Graph</span>
                <span class="card-path">graph_layer/</span>
              </div>
              <h4 class="card-title">🕸️ Neo4j Aura Graph</h4>
              <p class="card-desc">Stores nodes (:Program, :Table, :BusinessRule) and relationships (:FEEDS_INTO, :CALLS, :DERIVES_FROM) for lineage.</p>
              <div class="tag-pills">
                <span class="pill">Cypher Queries</span>
                <span class="pill">Lineage Paths</span>
                <span class="pill">Cross-System Nodes</span>
              </div>
            </div>

            <!-- Card 8: Relationship Discovery Agent -->
            <div class="arch-card" onclick="inspectComponent('rda')">
              <div class="card-top">
                <span class="card-badge" style="background: var(--graph-bg); color: var(--graph-color);">Bridge Agent</span>
                <span class="card-path">graph_layer/rda.py</span>
              </div>
              <h4 class="card-title">🌉 Relationship Discovery</h4>
              <p class="card-desc">Autonomous LLM agent that connects disparate systems across time (COBOL batch &rarr; SSIS ETL &rarr; SQL views).</p>
              <div class="tag-pills">
                <span class="pill">Cross-File Linker</span>
                <span class="pill">FEEDS_INTO</span>
                <span class="pill">Lineage Healing</span>
              </div>
            </div>

            <!-- Card 9: Vector Layer -->
            <div class="arch-card" onclick="inspectComponent('vector')">
              <div class="card-top">
                <span class="card-badge" style="background: var(--vector-bg); color: var(--vector-color);">Vector DB</span>
                <span class="card-path">vector_layer/</span>
              </div>
              <h4 class="card-title">🎯 Pinecone / Qdrant</h4>
              <p class="card-desc">Stores 50-line sliding window code chunks and functional summaries embedded with all-MiniLM-L6-v2 (384-dim).</p>
              <div class="tag-pills">
                <span class="pill">kairix_chunks</span>
                <span class="pill">kairix_summaries</span>
                <span class="pill">384 Dimensions</span>
              </div>
            </div>
          </div>

          <!-- Layer 4: Investigation & Modernization -->
          <div class="blueprint-col">
            <div class="col-header">
              <div class="col-num" style="background: var(--api-color);">L4</div>
              <div class="col-header-text">
                <h3>Investigation & Modernization</h3>
                <span>investigation_agent/ & ui/</span>
              </div>
            </div>

            <!-- Card 10: Investigation Agent -->
            <div class="arch-card" onclick="inspectComponent('investigation')">
              <div class="card-top">
                <span class="card-badge" style="background: var(--api-bg); color: var(--api-color);">Hybrid RAG</span>
                <span class="card-path">investigation_agent/</span>
              </div>
              <h4 class="card-title">🔎 Investigation Agent</h4>
              <p class="card-desc">Intersects graph traversal with vector similarity, routing questions to Cypher, Vector, or Hybrid retrieval.</p>
              <div class="tag-pills">
                <span class="pill">Intent Classifier</span>
                <span class="pill">Text-to-Cypher</span>
                <span class="pill">Zero Hallucination</span>
              </div>
            </div>

            <!-- Card 11: Modernization -->
            <div class="arch-card" onclick="inspectComponent('modernization')">
              <div class="card-top">
                <span class="card-badge" style="background: var(--api-bg); color: var(--api-color);">Cloud Native</span>
                <span class="card-path">FastAPI Microservice</span>
              </div>
              <h4 class="card-title">🚀 Re-engineered APIs</h4>
              <p class="card-desc">Translates extracted legacy business rules into modern Python/FastAPI microservices with cloud-native REST endpoints.</p>
              <div class="tag-pills">
                <span class="pill">FastAPI</span>
                <span class="pill">REST Endpoints</span>
                <span class="pill">JSON Schemas</span>
              </div>
            </div>

            <!-- Card 12: Streamlit Dashboard -->
            <div class="arch-card" onclick="inspectComponent('dashboard')">
              <div class="card-top">
                <span class="card-badge" style="background: var(--api-bg); color: var(--api-color);">Interface</span>
                <span class="card-path">Frontend/ & ui/</span>
              </div>
              <h4 class="card-title">🖥️ Interactive UI</h4>
              <p class="card-desc">Multi-page dashboard for interactive graph exploration, PyVis network visualization, and natural language queries.</p>
              <div class="tag-pills">
                <span class="pill">Streamlit 1.35+</span>
                <span class="pill">PyVis Physics</span>
                <span class="pill">Live Citations</span>
              </div>
            </div>

          </div>
        </div>

        <!-- Dynamic Component Inspector -->
        <div class="blueprint-inspector" id="blueprint-inspector">
          <div class="inspector-head">
            <div class="inspector-title">
              <span id="inspect-icon" style="font-size: 1.5rem;">📜</span>
              <div>
                <h4 id="inspect-name">Mainframe COBOL Programs (.cbl, .cpy)</h4>
                <span id="inspect-path" style="font-family: var(--font-mono); font-size: 0.76rem; color: var(--brand-primary);">source/mainframe/</span>
              </div>
            </div>
            <div class="card-badge" id="inspect-badge" style="background: var(--cobol-bg); color: var(--cobol-color);">Layer 1 Component</div>
          </div>

          <div class="inspector-body">
            <div class="inspect-col">
              <h5>🎯 Purpose & Role in Architecture</h5>
              <div class="inspect-content" id="inspect-purpose">
                Contains core enterprise insurance calculations written in COBOL 85 with strict fixed 80-column punch-card layouts. Houses vital mathematical rating, proration formulas, and status routines that drive premium earning.
              </div>
            </div>

            <div class="inspect-col">
              <h5>⚙️ Tech Stack & Key Files</h5>
              <div class="inspect-content" id="inspect-tech">
                <strong>Target Files:</strong> <code>EARNPREM.CBL</code>, <code>PREMCALC.CBL</code>, <code>POLSTATUS.CBL</code><br>
                <strong>Structure:</strong> IDENTIFICATION, ENVIRONMENT, DATA, and PROCEDURE divisions with 88-level condition names.
              </div>
            </div>

            <div class="inspect-col">
              <h5>📥 Contract & Output Data</h5>
              <div class="inspect-code" id="inspect-contract">
COMPUTE WS-EARNED-PREM ROUNDED =
  WS-TOTAL-PREMIUM *
  (WS-DAYS-RUN / WS-TOTAL-DAYS).
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- SECTION 2: 7-Stage LangGraph Cyclical Pipeline -->
    <section id="langgraph">
      <div class="section-head">
        <div>
          <span class="tag">Deterministic + Generative Intelligence</span>
          <h2>The 7-Stage LangGraph Pipeline</h2>
          <p>How the Knowledge Engineering Agent transforms raw, undocumented legacy files into canonical, line-anchored knowledge packages without hallucinations.</p>
        </div>
      </div>

      <div class="langgraph-box">
        <div class="stages-scroll">

          <div class="stage-step">
            <div class="stage-num-badge">1</div>
            <h4>Classification</h4>
            <p>Identifies dialect (.cbl &rarr; COBOL, .sql &rarr; SQL, .dtsx &rarr; SSIS) and sets syntax expectations.</p>
            <div class="confidence-tag">Dialect: Detected</div>
          </div>

          <div class="stage-step">
            <div class="stage-num-badge">2</div>
            <h4>Deterministic Parsing</h4>
            <p>Tree-sitter & SQLGlot extract AST nodes, tables, columns, copybooks, and variables.</p>
            <div class="confidence-tag">Confidence: 1.0 (Parser)</div>
          </div>

          <div class="stage-step">
            <div class="stage-num-badge">3</div>
            <h4>Evidence Anchoring</h4>
            <p>Every construct is anchored to exact 1-indexed source line numbers (e.g. Lines 214-238).</p>
            <div class="confidence-tag">Line Numbers: Exact</div>
          </div>

          <div class="stage-step">
            <div class="stage-num-badge">4</div>
            <h4>LLM Deep Review</h4>
            <p>NVIDIA NIM inspects code chunks to identify undocumented business rules and implicit data flows.</p>
            <div class="confidence-tag">Confidence: 0.85 (LLM)</div>
          </div>

          <div class="stage-step">
            <div class="stage-num-badge">5</div>
            <h4>Pydantic Profile</h4>
            <p>Normalizes findings into typed schema models (KnowledgeProfile, BusinessRule, Transformation).</p>
            <div class="confidence-tag">Schema: Pydantic v2</div>
          </div>

          <div class="stage-step">
            <div class="stage-num-badge">6</div>
            <h4>Reconciliation</h4>
            <p>Cross-validates parser facts against LLM discoveries, auto-resolving name discrepancies.</p>
            <div class="confidence-tag">Validation: Merged</div>
          </div>

          <div class="stage-step">
            <div class="stage-num-badge">7</div>
            <h4>Canonical Package</h4>
            <p>Emits standardized JSON artifacts and Markdown summaries into output/knowledge/.</p>
            <div class="confidence-tag">Artifact: JSON Emitted</div>
          </div>

        </div>
      </div>
    </section>

    <!-- SECTION 3: The 3 Autonomous Multi-Agent Triad -->
    <section id="agents">
      <div class="section-head">
        <div>
          <span class="tag">Specialized Multi-Agent Swarm</span>
          <h2>The 3 Autonomous AI Agents</h2>
          <p>Each agent possesses a dedicated architectural role, specialized tools, and strict validation boundaries.</p>
        </div>
      </div>

      <div class="agents-grid">

        <!-- Agent 1: KEA -->
        <div class="agent-card">
          <div class="agent-top">
            <div class="agent-avatar" style="background: var(--agent-bg); color: var(--agent-color);">🔬</div>
            <div class="agent-info">
              <h3>Knowledge Engineering Agent</h3>
              <div class="agent-role" style="color: var(--agent-color);">The Reverse Engineer & Extractor</div>
            </div>
          </div>

          <ul class="agent-bullets">
            <li>Executes the 7-node cyclical LangGraph pipeline over all source files.</li>
            <li>Runs deterministic AST engines (Tree-sitter & SQLGlot) with 1.0 confidence.</li>
            <li>Anchors all discovered entities to precise 1-indexed source line ranges.</li>
            <li>Reconciles parser facts with LLM reasoning to prevent hallucinations.</li>
          </ul>

          <div class="agent-io-box">
            <div class="agent-io-item">
              <span class="agent-io-label">Input:</span>
              <span class="agent-io-val">source/ (COBOL, SSIS, SQL)</span>
            </div>
            <div class="agent-io-item">
              <span class="agent-io-label">Output:</span>
              <span class="agent-io-val">output/knowledge/*_package.json</span>
            </div>
          </div>
        </div>

        <!-- Agent 2: RDA -->
        <div class="agent-card">
          <div class="agent-top">
            <div class="agent-avatar" style="background: var(--graph-bg); color: var(--graph-color);">🌉</div>
            <div class="agent-info">
              <h3>Relationship Discovery Agent</h3>
              <div class="agent-role" style="color: var(--graph-color);">The Cross-System Bridge Builder</div>
            </div>
          </div>

          <ul class="agent-bullets">
            <li>Identifies cross-file dependencies between disparate legacy technologies.</li>
            <li>Links COBOL batch math &rarr; SSIS ETL pipelines &rarr; SQL reporting views.</li>
            <li>Creates Neo4j graph edges (:FEEDS_INTO, :CALLS, :DERIVES_FROM).</li>
            <li>Solves 40 years of architectural drift and undocumented data coupling.</li>
          </ul>

          <div class="agent-io-box">
            <div class="agent-io-item">
              <span class="agent-io-label">Input:</span>
              <span class="agent-io-val">All Canonical Packages</span>
            </div>
            <div class="agent-io-item">
              <span class="agent-io-label">Output:</span>
              <span class="agent-io-val">Neo4j Cross-System Lineage Edges</span>
            </div>
          </div>
        </div>

        <!-- Agent 3: IA -->
        <div class="agent-card">
          <div class="agent-top">
            <div class="agent-avatar" style="background: var(--vector-bg); color: var(--vector-color);">🔎</div>
            <div class="agent-info">
              <h3>Investigation Agent</h3>
              <div class="agent-role" style="color: var(--vector-color);">The Line-Anchored Detective</div>
            </div>
          </div>

          <ul class="agent-bullets">
            <li>Classifies user questions into Lineage, Semantic, or Combined intent.</li>
            <li>Converts natural language into executable Neo4j Cypher queries with auto-repair.</li>
            <li>Performs hybrid retrieval: Cypher graph traversal + Pinecone vector chunks.</li>
            <li>Synthesizes executive answers with 100% verified source code line citations.</li>
          </ul>

          <div class="agent-io-box">
            <div class="agent-io-item">
              <span class="agent-io-label">Input:</span>
              <span class="agent-io-val">Natural Language Question</span>
            </div>
            <div class="agent-io-item">
              <span class="agent-io-label">Output:</span>
              <span class="agent-io-val">Evidence-Backed Answer with Line Numbers</span>
            </div>
          </div>
        </div>

      </div>
    </section>

    <!-- SECTION 4: Live Interactive Dataflow Simulator -->
    <section id="simulator">
      <div class="section-head">
        <div>
          <span class="tag">Real-Time Data Pipeline Simulation</span>
          <h2>Live System Data Flow Simulator</h2>
          <p>Watch how a business rule moves from raw legacy punch-card code through AST extraction, dual-memory storage, and investigation response.</p>
        </div>
      </div>

      <div class="simulator-box">
        <div class="sim-controls">
          <div class="sim-actions">
            <button class="sim-btn primary" id="sim-play-btn" onclick="toggleSimPlay()">▶ Start Simulation</button>
            <button class="sim-btn" onclick="stepSim(1)">Next Step ⏭</button>
            <button class="sim-btn" onclick="resetSim()">↺ Reset</button>
          </div>
          <div style="font-size: 0.84rem; font-weight: 600; color: var(--text-dim);" id="sim-step-indicator">
            Step 1 of 5: Legacy Code Ingestion
          </div>
        </div>

        <div class="sim-pipeline">
          <div class="sim-node active-sim" id="s-node-1" onclick="jumpSim(1)">
            <span class="sim-node-num">01 / INGESTION</span>
            <h4>Raw Legacy Code</h4>
            <p>Mainframe COBOL & SSIS XML files read from disk.</p>
            <span class="sim-status">Status: Loaded</span>
          </div>

          <div class="sim-node" id="s-node-2" onclick="jumpSim(2)">
            <span class="sim-node-num">02 / PARSING</span>
            <h4>Deterministic AST</h4>
            <p>Tree-sitter & SQLGlot decompose syntax trees.</p>
            <span class="sim-status">Status: Waiting</span>
          </div>

          <div class="sim-node" id="s-node-3" onclick="jumpSim(3)">
            <span class="sim-node-num">03 / RECONCILE</span>
            <h4>LangGraph Agents</h4>
            <p>7-stage state machine anchors line evidence.</p>
            <span class="sim-status">Status: Waiting</span>
          </div>

          <div class="sim-node" id="s-node-4" onclick="jumpSim(4)">
            <span class="sim-node-num">04 / DUAL STORE</span>
            <h4>Neo4j & Vectors</h4>
            <p>Graph nodes + Pinecone chunks synchronized.</p>
            <span class="sim-status">Status: Waiting</span>
          </div>

          <div class="sim-node" id="s-node-5" onclick="jumpSim(5)">
            <span class="sim-node-num">05 / QUERY</span>
            <h4>Investigation Q&A</h4>
            <p>Hybrid RAG delivers zero-hallucination answer.</p>
            <span class="sim-status">Status: Waiting</span>
          </div>
        </div>

        <div class="sim-detail-panel">
          <div class="sim-detail-title" id="sim-panel-title">
            <span>⚡ Step 1: Raw Legacy Punch-Card Code Ingested</span>
          </div>
          <div class="sim-detail-text" id="sim-panel-text">
            The platform reads <code>EARNPREM.CBL</code>, <code>Extract_Premium.dtsx</code>, and <code>PolicyCenter_CPP_Breakdown.sql</code> directly from the workspace. COBOL programs contain strict column constraints and punch-card math routines that have been running in batch mode for decades.
          </div>
          <div class="sim-detail-code" id="sim-panel-code">
002140 COMPUTE WS-EARNED-PREM ROUNDED =
002150     WS-TOTAL-PREMIUM * (WS-DAYS-RUN / WS-TOTAL-DAYS).
002160 IF WS-POLICY-STATUS = 'CAN'
002170     PERFORM 4000-PROCESS-CANCEL
          </div>
        </div>
      </div>
    </section>

    <!-- SECTION 5: Repository Directory Structure Visualizer -->
    <section id="tree">
      <div class="section-head">
        <div>
          <span class="tag">Physical Repository Blueprint</span>
          <h2>Repository Directory & File Structure</h2>
          <p>Click any directory in the project tree to inspect its purpose, key files, and architectural boundary.</p>
        </div>
      </div>

      <div class="tree-box">
        <div class="tree-viewer">
          <div class="tree-item selected" onclick="selectTreeItem('source')">
            <div class="tree-name">📁 source/</div>
            <span class="tree-badge" style="background: var(--cobol-bg); color: var(--cobol-color);">Layer 1</span>
          </div>
          <div class="tree-item" onclick="selectTreeItem('parsers')">
            <div class="tree-name">&nbsp;&nbsp;📁 parsers/</div>
            <span class="tree-badge" style="background: var(--agent-bg); color: var(--agent-color);">AST Engine</span>
          </div>
          <div class="tree-item" onclick="selectTreeItem('kea')">
            <div class="tree-name">📁 knowledge_engineering_agent/</div>
            <span class="tree-badge" style="background: var(--agent-bg); color: var(--agent-color);">Layer 2</span>
          </div>
          <div class="tree-item" onclick="selectTreeItem('graph')">
            <div class="tree-name">📁 graph_layer/</div>
            <span class="tree-badge" style="background: var(--graph-bg); color: var(--graph-color);">Neo4j Graph</span>
          </div>
          <div class="tree-item" onclick="selectTreeItem('vector')">
            <div class="tree-name">📁 vector_layer/</div>
            <span class="tree-badge" style="background: var(--vector-bg); color: var(--vector-color);">Pinecone DB</span>
          </div>
          <div class="tree-item" onclick="selectTreeItem('ia')">
            <div class="tree-name">📁 investigation_agent/</div>
            <span class="tree-badge" style="background: var(--api-bg); color: var(--api-color);">Hybrid RAG</span>
          </div>
          <div class="tree-item" onclick="selectTreeItem('output')">
            <div class="tree-name">📁 output/</div>
            <span class="tree-badge" style="background: rgba(0,0,0,0.06); color: var(--text-dim);">JSON Artifacts</span>
          </div>
          <div class="tree-item" onclick="selectTreeItem('ui')">
            <div class="tree-name">📁 Frontend/ & ui/</div>
            <span class="tree-badge" style="background: var(--brand-primary); color: white;">Dashboards</span>
          </div>
        </div>

        <div class="tree-info-panel">
          <div class="tree-info-title" id="tree-title">📁 source/ — Legacy Source Artifacts</div>
          <div class="tree-info-path" id="tree-path">Path: c:\Users\GaneshSriKumarMarimu\legacy-code-agentic-rag\source\</div>
          <div class="tree-info-desc" id="tree-desc">
            Houses the target enterprise legacy assets across 3 distinct generations of enterprise technology: Mainframe COBOL (batch calculation), SSIS ETL packages (data pipeline staging), and Guidewire SQL (reporting views).
          </div>
          <ul class="tree-file-list" id="tree-files">
            <li>📄 mainframe/EARNPREM.CBL — COBOL 85 Earned Premium Batch Rating</li>
            <li>📄 mainframe/PREMCALC.CBL — COBOL 85 Policy Rating & Factor Calculator</li>
            <li>📄 ssis/packages/Extract_Premium.dtsx — SSIS XML ETL Pipeline (BR-07, BR-08)</li>
            <li>📄 sql/PolicyCenter_CPP_Breakdown.sql — 1,000+ line Guidewire Reporting View</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- SECTION 6: Traditional RAG vs KAIRIX Comparison -->
    <section>
      <div class="section-head">
        <div>
          <span class="tag">The Paradigm Shift</span>
          <h2>Traditional RAG vs. KAIRIX Agentic Architecture</h2>
          <p>Why generic vector embeddings fail on multi-generational legacy codebases and how KAIRIX solves it.</p>
        </div>
      </div>

      <table class="compare-table">
        <thead>
          <tr>
            <th>Architectural Capability</th>
            <th>Traditional RAG (Vector Only)</th>
            <th>KAIRIX Dual-Memory Multi-Agent</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="td-metric">Code Parsing & Chunking</td>
            <td class="td-trad">❌ Arbitrary character/token chunking splits COBOL loops and procedures in half.</td>
            <td class="td-kairix">✔ Deterministic AST chunking (Tree-sitter & SQLGlot) preserves exact procedural boundaries.</td>
          </tr>
          <tr>
            <td class="td-metric">Cross-System Lineage</td>
            <td class="td-trad">❌ Completely blind to relationships across files and technologies.</td>
            <td class="td-kairix">✔ Neo4j Knowledge Graph traces COBOL batch output &rarr; SSIS ETL &rarr; SQL views.</td>
          </tr>
          <tr>
            <td class="td-metric">Fact Verification</td>
            <td class="td-trad">❌ High hallucination rate on complex mathematical rating formulas.</td>
            <td class="td-kairix">✔ 100% line-anchored citations with deterministic parser reconciliation.</td>
          </tr>
          <tr>
            <td class="td-metric">Query Execution</td>
            <td class="td-trad">❌ Only similarity search; cannot perform topological graph hops.</td>
            <td class="td-kairix">✔ Hybrid: Natural language converted to Neo4j Cypher + Pinecone dense search.</td>
          </tr>
        </tbody>
      </table>
    </section>

  </main>

  <footer class="app-footer">
    <div class="brand-sign">🌌 KAIRIX Enterprise Architecture Blueprint</div>
    <p>Legacy Reverse Engineering Platform &bull; Built with LangGraph, Neo4j Aura, Pinecone, and Tree-sitter</p>
  </footer>

  <script>
    /* Data Dictionary for Blueprint Components */
    const components = {
      cobol: {
        icon: "📜",
        name: "Mainframe COBOL Programs (.cbl, .cpy)",
        path: "source/mainframe/",
        badge: "Layer 1: Legacy Code",
        badgeColor: "var(--cobol-color)",
        badgeBg: "var(--cobol-bg)",
        purpose: "Contains mission-critical insurance calculation routines written in COBOL 85 with strict fixed 80-column punch-card layouts. Houses mathematical rating, proration formulas, and status routines that compute earned premiums across fiscal quarters.",
        tech: "<strong>Files:</strong> EARNPREM.CBL, PREMCALC.CBL, POLSTATUS.CBL<br><strong>Grammar:</strong> IDENTIFICATION, ENVIRONMENT, DATA, and PROCEDURE divisions with 88-level condition flags.",
        code: "COMPUTE WS-EARNED-PREM ROUNDED =\\n  WS-TOTAL-PREMIUM *\\n  (WS-DAYS-RUN / WS-TOTAL-DAYS)."
      },
      ssis: {
        icon: "🔀",
        name: "SSIS DTSX Packages (.dtsx)",
        path: "source/ssis/packages/",
        badge: "Layer 1: ETL Pipeline",
        badgeColor: "var(--ssis-color)",
        badgeBg: "var(--ssis-bg)",
        purpose: "Enterprise Microsoft SQL Server Integration Services ETL packages. Contains XML pipelines that ingest policy transactions from raw files, apply derived column transformations, enforce financial guardrails (BR-07, BR-08), and populate reporting data warehouses.",
        tech: "<strong>Files:</strong> Extract_Premium.dtsx, Extract_Policy.dtsx<br><strong>Format:</strong> Microsoft DTSX XML schemas, Executable Data Flow tasks, OLE DB destinations.",
        code: "<DTS:Executable DTS:ExecutableType=\\"Microsoft.Pipeline\\">\\n  <property name=\\"DerivedColumn\\">\\n    EarnedPremium == 0 ? StagingVal : EarnedPremium\\n  </property>\\n</DTS:Executable>"
      },
      sql: {
        icon: "🗄️",
        name: "Guidewire SQL Analytic Views (.sql)",
        path: "source/sql/",
        badge: "Layer 1: Database Analytics",
        badgeColor: "var(--sql-color)",
        badgeBg: "var(--sql-bg)",
        purpose: "1,000+ line enterprise reporting scripts and views. Joins multi-line policy records, transactions, coverage details, and claims to power downstream executive dashboards and financial audits.",
        tech: "<strong>Files:</strong> PolicyCenter_CPP_Breakdown.sql, PolicyCenter_Monoline.sql<br><strong>Dialect:</strong> ANSI SQL & T-SQL complex multi-table joins, subqueries, and window functions.",
        code: "SELECT p.PolicyNumber, b.EarnedPremium,\\n       SUM(t.TransactionAmount) AS TotalTxn\\nFROM pc_policy p\\nJOIN pc_breakdown b ON p.ID = b.PolicyID\\nGROUP BY p.PolicyNumber, b.EarnedPremium;"
      },
      parsers: {
        icon: "🌲",
        name: "Deterministic AST Parsers",
        path: "parsers/",
        badge: "Layer 2: AST Extraction",
        badgeColor: "var(--agent-color)",
        badgeBg: "var(--agent-bg)",
        purpose: "Deterministic Abstract Syntax Tree (AST) parsing infrastructure that extracts code constructs into verifiable facts without relying on LLM guesswork. Employs tree-sitter-cobol for COBOL, sqlglot for SQL, and python xml.etree for SSIS.",
        tech: "<strong>Tech:</strong> Tree-sitter (v0.26+), SQLGlot (v25+), XML Parser<br><strong>Guarantee:</strong> 100% deterministic entity discovery, zero hallucination (confidence 1.0).",
        code: "def parse_cobol_ast(source_code: str):\\n    tree = cobol_parser.parse(bytes(source_code, 'utf8'))\\n    return extract_divisions_and_paragraphs(tree.root_node)"
      },
      langgraph: {
        icon: "⚡",
        name: "7-Stage LangGraph Cyclical Pipeline",
        path: "knowledge_engineering_agent/",
        badge: "Layer 2: State Machine",
        badgeColor: "var(--agent-color)",
        badgeBg: "var(--agent-bg)",
        purpose: "Cyclical state machine engine that orchestrates the entire reverse engineering workflow: classification, deterministic AST extraction, line anchoring, multi-pass LLM review with NVIDIA NIM, Pydantic normalization, and fact reconciliation.",
        tech: "<strong>Tech:</strong> LangGraph v0.2+, Pydantic v2, NVIDIA NIM (nematron-3-ultra)<br><strong>Flow:</strong> 7 sequential nodes with persistent hash-based incremental caching.",
        code: "workflow = StateGraph(PipelineState)\\nworkflow.add_node('classify', classify_source)\\nworkflow.add_node('deterministic_parse', run_ast)\\nworkflow.add_node('reconciliation', reconcile_facts)\\nworkflow.set_entry_point('classify')"
      },
      canonical: {
        icon: "📦",
        name: "Canonical Knowledge Packages",
        path: "output/knowledge/",
        badge: "Layer 2: Artifacts",
        badgeColor: "var(--agent-color)",
        badgeBg: "var(--agent-bg)",
        purpose: "Unified, standardized JSON payloads emitted by LangGraph. Each file contains all extracted nodes (tables, columns, rules, formulas), relationships, exact line-anchored source citations, and human-readable functional summaries.",
        tech: "<strong>Artifacts:</strong> *_knowledge_package.json, *_summary.md<br><strong>Validation:</strong> Validated against Pydantic KnowledgeProfile schema before disk write.",
        code: "{\\n  \\"artifact_name\\": \\"EARNPREM.CBL\\",\\n  \\"dialect\\": \\"COBOL-85\\",\\n  \\"business_rules\\": [\\n    {\\"id\\": \\"BR-01\\", \\"name\\": \\"PRORATION-MATH\\", \\"lines\\": [214, 238]}\\n  ]\\n}"
      },
      neo4j: {
        icon: "🕸️",
        name: "Neo4j Aura Enterprise Graph",
        path: "graph_layer/",
        badge: "Layer 3: Knowledge Graph",
        badgeColor: "var(--graph-color)",
        badgeBg: "var(--graph-bg)",
        purpose: "Enterprise cloud property graph database storing the structural fabric and end-to-end data lineage of the entire legacy estate. Enables instantaneous graph traversals across decades of multi-dialect software.",
        tech: "<strong>Tech:</strong> Neo4j Aura Cloud, Bolt Driver, Cypher Query Language<br><strong>Nodes:</strong> :Program, :Table, :Column, :BusinessRule, :Transformation",
        code: "MATCH (c:Program {name: 'EARNPREM.CBL'})\\n-[:FEEDS_INTO]->(s:Package {name: 'Extract_Premium.dtsx'})\\n-[:WRITES_TO]->(t:Table {name: 'pc_breakdown'})\\nRETURN c, s, t;"
      },
      rda: {
        icon: "🌉",
        name: "Relationship Discovery Agent",
        path: "graph_layer/relationship_discovery_agent.py",
        badge: "Layer 3: Cross-System Bridge",
        badgeColor: "var(--graph-color)",
        badgeBg: "var(--graph-bg)",
        purpose: "Autonomous reasoning agent that discovers implicit, cross-file connections. It bridges the gap between COBOL batch output files, SSIS staging tables, and SQL reporting queries, solving enterprise legacy documentation drift.",
        tech: "<strong>Tech:</strong> LLM Cross-System Matching, Cypher edge creation<br><strong>Edges Created:</strong> :FEEDS_INTO, :CALLS, :DERIVES_FROM, :TRANSFORMS",
        code: "MATCH (cobol_out:Column {name: 'WS-EARNED-PREM'}),\\n      (ssis_in:Column {name: 'EarnedPremium'})\\nMERGE (cobol_out)-[:FEEDS_INTO {confidence: 0.94}]->(ssis_in)"
      },
      vector: {
        icon: "🎯",
        name: "Pinecone / Qdrant Vector Store",
        path: "vector_layer/",
        badge: "Layer 3: Vector Memory",
        badgeColor: "var(--vector-color)",
        badgeBg: "var(--vector-bg)",
        purpose: "High-dimensional dense vector store for semantic code search. Implements a dual vector collection architecture: 50-line sliding window code chunks and functional executive summaries.",
        tech: "<strong>Tech:</strong> Pinecone Serverless / Qdrant, all-MiniLM-L6-v2 (384 dimensions)<br><strong>Collections:</strong> kairix_chunks (code snippets), kairix_summaries (markdown)",
        code: "vectors = embedder.encode(chunks)\\npinecone_index.upsert(vectors=zip(chunk_ids, vectors, metadata))"
      },
      investigation: {
        icon: "🔎",
        name: "Investigation Agent (Hybrid RAG)",
        path: "investigation_agent/",
        badge: "Layer 4: Hybrid RAG",
        badgeColor: "var(--api-color)",
        badgeBg: "var(--api-bg)",
        purpose: "Interactive investigative query engine. Analyzes user questions, classifies intent (Lineage, Semantic, or Combined), generates auto-healing Neo4j Cypher, retrieves Pinecone vector chunks, and synthesizes line-anchored answers.",
        tech: "<strong>Tech:</strong> Text-to-Cypher generator, Hybrid Retrieval Engine, Line Citation Validator<br><strong>Accuracy:</strong> Zero hallucinations by anchoring all answers to verified code lines.",
        code: "result = investigation_agent.investigate(\\n  question=\\"Where is earned premium calculated across systems?\\"\\n)\\n# Returns verified evidence, Cypher paths, and line citations"
      },
      modernization: {
        icon: "🚀",
        name: "Re-engineered Cloud Microservices",
        path: "FastAPI / Modernization",
        badge: "Layer 4: Cloud Native",
        badgeColor: "var(--api-color)",
        badgeBg: "var(--api-bg)",
        purpose: "Automatically transpires extracted legacy business logic into modern, cloud-native Python and FastAPI microservices. Replaces ancient batch mainframe jobs with scalable, event-driven REST APIs.",
        tech: "<strong>Tech:</strong> Python 3.12, FastAPI, Pydantic Schemas, Docker containers<br><strong>Benefit:</strong> 100% mathematical fidelity with legacy algorithms, sub-millisecond response times.",
        code: "@app.post('/api/v1/rating/earned-premium')\\ndef calculate_earned_premium(req: PremiumRequest) -> PremiumResponse:\\n    earned = (req.days_run / req.total_days) * req.total_premium\\n    return PremiumResponse(earned_premium=round(earned, 2))"
      },
      dashboard: {
        icon: "🖥️",
        name: "Streamlit UI & Graph Visualizer",
        path: "Frontend/ & ui/",
        badge: "Layer 4: Presentation",
        badgeColor: "var(--api-color)",
        badgeBg: "var(--api-bg)",
        purpose: "Interactive enterprise user dashboard for analysts and engineers. Includes dynamic PyVis physics-based graph rendering, file ingestion management, and natural language investigation consoles.",
        tech: "<strong>Tech:</strong> Streamlit (v1.35+), PyVis (v0.3+), HTML5 Canvas<br><strong>Features:</strong> Interactive query console, graph node filtering, live source code inspection.",
        code: "st.title('KAIRIX Legacy Investigation Console')\\nquery = st.text_input('Ask a question about legacy systems:')\\nif st.button('Investigate'):\\n    render_investigation_result(ia.query(query))"
      }
    };

    function inspectComponent(key) {
      const data = components[key];
      if (!data) return;

      // Update Card Active State
      document.querySelectorAll('.arch-card').forEach(card => card.classList.remove('active'));
      event.currentTarget.classList.add('active');

      // Update Inspector Panel
      document.getElementById('inspect-icon').textContent = data.icon;
      document.getElementById('inspect-name').textContent = data.name;
      document.getElementById('inspect-path').textContent = data.path;
      
      const badge = document.getElementById('inspect-badge');
      badge.textContent = data.badge;
      badge.style.color = data.badgeColor;
      badge.style.background = data.badgeBg;

      document.getElementById('inspect-purpose').innerHTML = data.purpose;
      document.getElementById('inspect-tech').innerHTML = data.tech;
      document.getElementById('inspect-contract').textContent = data.code.replace(/\\\\n/g, '\\n');

      // Smooth scroll to inspector if on mobile
      if (window.innerWidth < 900) {
        document.getElementById('blueprint-inspector').scrollIntoView({ behavior: 'smooth' });
      }
    }

    /* Simulation Steps Data */
    const simSteps = [
      {
        num: 1,
        title: "⚡ Step 1: Raw Legacy Punch-Card Code Ingested",
        text: "The platform ingests EARNPREM.CBL, Extract_Premium.dtsx, and PolicyCenter_CPP_Breakdown.sql directly from the workspace. COBOL programs contain strict column constraints and punch-card math routines that have run in batch mode for decades.",
        code: "002140 COMPUTE WS-EARNED-PREM ROUNDED =\\n002150     WS-TOTAL-PREMIUM * (WS-DAYS-RUN / WS-TOTAL-DAYS).\\n002160 IF WS-POLICY-STATUS = 'CAN'\\n002170     PERFORM 4000-PROCESS-CANCEL"
      },
      {
        num: 2,
        title: "🌲 Step 2: Deterministic AST Parsing (Tree-sitter & SQLGlot)",
        text: "Deterministic parsers execute without LLM involvement. Tree-sitter maps COBOL tokens to AST syntax trees, while SQLGlot transpiles SQL views. Every variable, paragraph, and table is indexed with 100% confidence (1.0).",
        code: "AST_NODE: procedure_division\\n  PARAGRAPH: 3000-CALC-EARNED-PREM (Lines 214-238)\\n  COMPUTE_STMT: target='WS-EARNED-PREM'\\n  OPERATORS: ['*', '/'], OPERANDS: ['WS-TOTAL-PREMIUM', 'WS-DAYS-RUN', 'WS-TOTAL-DAYS']"
      },
      {
        num: 3,
        title: "⚡ Step 3: LangGraph 7-Stage Multi-Pass Reasoning",
        text: "The cyclical state machine kicks off. NVIDIA NIM performs multi-pass code analysis to extract implicit business rules. The Reconciliation Engine compares parser facts with LLM discoveries, emitting canonical JSON packages.",
        code: "ReconciliationEngine.merge(\\n  parser_entities={'WS-EARNED-PREM': LineAnchor(start=214, end=238)},\\n  llm_business_rules=[BusinessRule(id='BR-01', name='Pro-Rata Earning', confidence=0.92)]\\n) -> CanonicalPackage(status='reconciled')"
      },
      {
        num: 4,
        title: "🕸️ Step 4: Dual-Memory Sync (Neo4j Graph + Pinecone Vectors)",
        text: "The Canonical Package is loaded into Neo4j Aura, creating :Program, :Table, and :BusinessRule nodes. Concurrently, sliding-window code chunks are embedded into Pinecone Serverless. The Relationship Discovery Agent creates cross-system :FEEDS_INTO edges linking COBOL to SSIS.",
        code: "NEO4J: MERGE (p:Program {name: 'EARNPREM.CBL'})-[:FEEDS_INTO]->(s:Package {name: 'Extract_Premium.dtsx'})\\nPINECONE: Upserted 48 vectors into 'kairix_chunks' (384-dim all-MiniLM-L6-v2)"
      },
      {
        num: 5,
        title: "🔎 Step 5: Investigation Agent Responds with Line Citations",
        text: "An enterprise analyst asks: 'Where is the earned premium calculation rule defined across systems?' The Investigation Agent executes Cypher traversal across Neo4j and vector search over Pinecone, producing a complete, verified answer with exact line numbers!",
        code: "ANSWER: Earned premium is calculated in EARNPREM.CBL at Lines 214-238 using the pro-rata formula\\nEARNED = TOTAL_PREM * (DAYS_RUN / TOTAL_DAYS).\\nThis value is ingested by SSIS package Extract_Premium.dtsx (DataFlow 'Extract_Premium')\\nand loaded into pc_breakdown.earned_premium table view for Guidewire reporting."
      }
    ];

    let currentSimStep = 1;
    let simInterval = null;

    function jumpSim(step) {
      currentSimStep = step;
      updateSimUI();
    }

    function stepSim(delta) {
      currentSimStep = ((currentSimStep - 1 + delta + simSteps.length) % simSteps.length) + 1;
      updateSimUI();
    }

    function resetSim() {
      if (simInterval) clearInterval(simInterval);
      simInterval = null;
      document.getElementById('sim-play-btn').textContent = "▶ Start Simulation";
      currentSimStep = 1;
      updateSimUI();
    }

    function toggleSimPlay() {
      const btn = document.getElementById('sim-play-btn');
      if (simInterval) {
        clearInterval(simInterval);
        simInterval = null;
        btn.textContent = "▶ Start Simulation";
      } else {
        btn.textContent = "⏸ Pause";
        simInterval = setInterval(() => {
          stepSim(1);
        }, 3200);
      }
    }

    function updateSimUI() {
      const stepData = simSteps[currentSimStep - 1];

      // Update Node States
      for (let i = 1; i <= 5; i++) {
        const node = document.getElementById(`s-node-${i}`);
        const status = node.querySelector('.sim-status');
        if (i === currentSimStep) {
          node.className = "sim-node active-sim";
          status.textContent = "Status: Active ⚡";
        } else if (i < currentSimStep) {
          node.className = "sim-node";
          status.textContent = "Status: Completed ✔";
        } else {
          node.className = "sim-node";
          status.textContent = "Status: Waiting";
        }
      }

      // Update Details
      document.getElementById('sim-step-indicator').textContent = `Step ${currentSimStep} of 5: ${stepData.title.split(':')[1] || stepData.title}`;
      document.getElementById('sim-panel-title').innerHTML = `<span>${stepData.title}</span>`;
      document.getElementById('sim-panel-text').textContent = stepData.text;
      document.getElementById('sim-panel-code').textContent = stepData.code.replace(/\\\\n/g, '\\n');
    }

    /* Repository Tree Explorer Data */
    const treeData = {
      source: {
        title: "📁 source/ — Legacy Source Landscape",
        path: "legacy-code-agentic-rag/source/",
        desc: "Houses raw multi-generational enterprise codebases across 3 disparate technologies: Mainframe COBOL routines, Microsoft SSIS ETL packages, and Guidewire SQL analytics.",
        files: [
          "📄 mainframe/EARNPREM.CBL — COBOL 85 Earned Premium Batch Rating",
          "📄 mainframe/PREMCALC.CBL — COBOL 85 Policy Rating & Factor Calculator",
          "📄 ssis/packages/Extract_Premium.dtsx — SSIS XML ETL Pipeline (BR-07, BR-08)",
          "📄 sql/PolicyCenter_CPP_Breakdown.sql — 1,000+ line Guidewire Reporting View"
        ]
      },
      parsers: {
        title: "📁 parsers/ — Deterministic AST Extraction",
        path: "legacy-code-agentic-rag/parsers/",
        desc: "Contains rule-based parsers that extract exact syntax trees without LLM hallucinations. Anchors every entity to 1-indexed source line ranges.",
        files: [
          "📄 cobol/parse.py — Tree-sitter COBOL grammar parser & AST builder",
          "📄 sql/parse.py — SQLGlot SQL syntax analyzer & table-column lineage extractor",
          "📄 ssis/parse.py — XML parser for SSIS Pipeline components and dataflows"
        ]
      },
      kea: {
        title: "📁 knowledge_engineering_agent/ — LangGraph Pipeline",
        path: "legacy-code-agentic-rag/knowledge_engineering_agent/",
        desc: "7-node cyclical state machine engine. Orchestrates classification, deterministic AST extraction, line anchoring, multi-pass LLM review, and fact reconciliation.",
        files: [
          "📄 graph.py — LangGraph 7-stage state machine workflow definition",
          "📄 agent.py — Orchestrator with persistent file-hash incremental caching",
          "📄 state.py — Pipeline state schemas and evidence collections",
          "📁 services/ — Classifier, Reviewer, Extractor, and Reconciliation engines"
        ]
      },
      graph: {
        title: "📁 graph_layer/ — Neo4j Knowledge Graph",
        path: "legacy-code-agentic-rag/graph_layer/",
        desc: "Manages Neo4j Aura cloud graph database connection, Cypher schema constraints, bulk package ingestion, and autonomous cross-system relationship discovery.",
        files: [
          "📄 neo4j_client.py — Bolt driver connection and Cypher transaction runner",
          "📄 schema.cypher — Node indexes and uniqueness constraints",
          "📄 graph_loader.py — Bulk canonical JSON package loader",
          "📄 relationship_discovery_agent.py — Autonomous cross-file relationship matcher"
        ]
      },
      vector: {
        title: "📁 vector_layer/ — Vector Memory & Embeddings",
        path: "legacy-code-agentic-rag/vector_layer/",
        desc: "Generates 384-dimensional dense vector embeddings using local all-MiniLM-L6-v2 models and synchronizes with Pinecone Serverless / Qdrant.",
        files: [
          "📄 vector_ingestion.py — 50-line sliding window chunker with 10-line overlap",
          "📄 embedder.py — SentenceTransformers embedding wrapper",
          "📄 qdrant_client_wrapper.py — Vector database collections management"
        ]
      },
      ia: {
        title: "📁 investigation_agent/ — Hybrid RAG Query Engine",
        path: "legacy-code-agentic-rag/investigation_agent/",
        desc: "Interactive question answering agent. Classifies user intent into Lineage, Semantic, or Combined, executes Cypher and vector retrieval, and outputs verified citations.",
        files: [
          "📄 agent.py — Query router, hybrid retrieval coordinator, and answer synthesizer",
          "📄 models.py — Pydantic InvestigationResult data contracts",
          "📄 prompts.py — Natural language to Cypher translation & synthesis prompts"
        ]
      },
      output: {
        title: "📁 output/ — Emitted Canonical Artifacts",
        path: "legacy-code-agentic-rag/output/",
        desc: "Storage for all generated artifacts. Contains standardized canonical JSON packages, functional Markdown summaries, and incremental cache records.",
        files: [
          "📁 knowledge/ — Canonical *_knowledge_package.json files",
          "📁 summaries/ — High-level functional Markdown summaries (*_summary.md)",
          "📁 cache/ — Hash-based incremental run state cache"
        ]
      },
      ui: {
        title: "📁 Frontend/ & ui/ — Enterprise User Dashboard",
        path: "legacy-code-agentic-rag/Frontend/ and ui/",
        desc: "User interfaces for interactive exploration. Features multi-page Streamlit dashboards, physics-based PyVis knowledge graphs, and live query consoles.",
        files: [
          "📄 app.py — Streamlit multi-page dashboard application",
          "📁 pages/ — Ingestion, Graph Explorer, Pipeline, and Investigation pages",
          "📁 components/ — PyVis physics graph rendering and lineage views"
        ]
      }
    };

    function selectTreeItem(key) {
      const data = treeData[key];
      if (!data) return;

      document.querySelectorAll('.tree-item').forEach(el => el.classList.remove('selected'));
      event.currentTarget.classList.add('selected');

      document.getElementById('tree-title').textContent = data.title;
      document.getElementById('tree-path').textContent = `Path: ${data.path}`;
      document.getElementById('tree-desc').textContent = data.desc;

      const fileList = document.getElementById('tree-files');
      fileList.innerHTML = '';
      data.files.forEach(file => {
        const li = document.createElement('li');
        li.textContent = file;
        fileList.appendChild(li);
      });
    }

    /* Ambient Background Network Animation */
    (function initBackgroundCanvas() {
      const canvas = document.getElementById('bg-canvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      let w = canvas.width = window.innerWidth;
      let h = canvas.height = window.innerHeight;

      window.addEventListener('resize', () => {
        w = canvas.width = window.innerWidth;
        h = canvas.height = window.innerHeight;
      });

      const nodes = [];
      const count = Math.min(45, Math.floor(w / 35));
      for (let i = 0; i < count; i++) {
        nodes.push({
          x: Math.random() * w,
          y: Math.random() * h,
          vx: (Math.random() - 0.5) * 0.45,
          vy: (Math.random() - 0.5) * 0.45,
          radius: Math.random() * 2.5 + 1.5,
          color: ['rgba(37, 99, 235, 0.4)', 'rgba(5, 150, 105, 0.35)', 'rgba(217, 119, 6, 0.35)'][Math.floor(Math.random() * 3)]
        });
      }

      function draw() {
        ctx.clearRect(0, 0, w, h);
        for (let i = 0; i < nodes.length; i++) {
          const n = nodes[i];
          n.x += n.vx;
          n.y += n.vy;
          if (n.x < 0 || n.x > w) n.vx *= -1;
          if (n.y < 0 || n.y > h) n.vy *= -1;

          ctx.beginPath();
          ctx.arc(n.x, n.y, n.radius, 0, Math.PI * 2);
          ctx.fillStyle = n.color;
          ctx.fill();

          for (let j = i + 1; j < nodes.length; j++) {
            const m = nodes[j];
            const dist = Math.hypot(n.x - m.x, n.y - m.y);
            if (dist < 120) {
              ctx.beginPath();
              ctx.moveTo(n.x, n.y);
              ctx.lineTo(m.x, m.y);
              ctx.strokeStyle = `rgba(148, 163, 184, ${0.25 * (1 - dist / 120)})`;
              ctx.lineWidth = 1;
              ctx.stroke();
            }
          }
        }
        requestAnimationFrame(draw);
      }
      draw();
    })();
  </script>
</body>
</html>
"""

with open(target_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print("Successfully written pure structure architecture index.html to", target_path)
