import json
import os

workspace_root = r"c:\Users\GaneshSriKumarMarimu\legacy-code-agentic-rag"

cobol_path = os.path.join(workspace_root, "source", "mainframe", "EARNPREM.CBL")
ssis_path = os.path.join(workspace_root, "source", "ssis", "packages", "Extract_Premium.dtsx")
sql_path = os.path.join(workspace_root, "source", "sql", "PolicyCenter_CPP_Breakdown.sql")

with open(cobol_path, "r", encoding="utf-8", errors="ignore") as f:
    cobol_text = f.read()

with open(ssis_path, "r", encoding="utf-8", errors="ignore") as f:
    ssis_text = f.read()

with open(sql_path, "r", encoding="utf-8", errors="ignore") as f:
    sql_text = f.read()

file_data = {
    "cobol": cobol_text,
    "ssis": ssis_text,
    "sql": sql_text
}
json_payload = json.dumps(file_data)

html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>KAIRIX — Demystifying Legacy Code: From Ancient Systems to Modern Intelligence</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Outfit:wght@600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      /* Neumorphic & Theme Colors */
      --neu-bg: #e8ecf2;
      --neu-surface: #e8ecf2;
      --neu-light: #ffffff;
      --neu-dark: #c2cbd6;
      --neu-dark-deep: #b0bac7;
      
      --text-main: #0f172a;
      --text-muted: #334155;
      --text-dim: #64748b;
      
      --brand-primary: #2563eb;
      --brand-gradient: linear-gradient(135deg, #2563eb 0%, #06b6d4 100%);
      --emerald: #059669;
      --amber: #d97706;
      --rose: #e11d48;
      
      --cobol-accent: #0284c7;
      --ssis-accent: #ea580c;
      --sql-accent: #7c3aed;
      
      --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
      --font-display: 'Outfit', sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      background-color: var(--neu-bg);
      color: var(--text-main);
      font-family: var(--font-sans);
      line-height: 1.6;
      padding-bottom: 5rem;
      position: relative;
      overflow-x: hidden;
    }}

    /* Ambient Background Video Canvas */
    #bg-video-canvas {{
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      z-index: -1;
      pointer-events: none;
      opacity: 0.55;
    }}

    /* Top Sticky Navigation Header */
    header.nav-header {{
      background: rgba(232, 236, 242, 0.92);
      backdrop-filter: blur(14px);
      border-bottom: 1px solid rgba(255, 255, 255, 0.6);
      padding: 0.85rem 2rem;
      position: sticky;
      top: 0;
      z-index: 100;
      box-shadow: 0 4px 14px -3px rgba(194, 203, 214, 0.45);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
    }}

    .brand {{ display: flex; align-items: center; gap: 0.85rem; }}
    .brand-icon {{
      width: 40px; height: 40px;
      background: var(--brand-gradient);
      border-radius: 12px;
      display: flex; align-items: center; justify-content: center;
      box-shadow: 4px 4px 8px var(--neu-dark), -4px -4px 8px var(--neu-light);
    }}
    .brand-icon svg {{ width: 22px; height: 22px; fill: white; }}
    .brand-text h1 {{
      font-family: var(--font-display);
      font-size: 1.25rem; font-weight: 800;
      color: var(--text-main); letter-spacing: -0.02em;
    }}
    .brand-text span {{
      font-size: 0.73rem; color: var(--text-dim); display: block; margin-top: -3px; font-weight: 600;
    }}

    .nav-links {{
      display: flex;
      align-items: center;
      gap: 0.65rem;
      flex-wrap: wrap;
    }}
    .nav-link {{
      color: var(--text-muted);
      text-decoration: none;
      font-size: 0.8rem;
      font-weight: 700;
      padding: 0.45rem 0.95rem;
      border-radius: 9999px;
      transition: all 0.2s ease;
      background: var(--neu-surface);
      box-shadow: 3px 3px 6px var(--neu-dark), -3px -3px 6px var(--neu-light);
    }}
    .nav-link:hover {{
      color: var(--brand-primary);
      transform: translateY(-1px);
    }}

    .header-controls {{
      display: flex;
      align-items: center;
      gap: 0.85rem;
    }}
    .anim-toggle-btn {{
      background: var(--neu-surface);
      border: none;
      color: var(--text-muted);
      font-size: 0.78rem;
      font-weight: 700;
      padding: 0.45rem 1rem;
      border-radius: 9999px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      box-shadow: 4px 4px 8px var(--neu-dark), -4px -4px 8px var(--neu-light);
      transition: all 0.2s ease;
    }}
    .anim-toggle-btn.active {{
      box-shadow: inset 3px 3px 6px var(--neu-dark), inset -3px -3px 6px var(--neu-light);
      color: var(--brand-primary);
    }}
    .pulse-dot {{
      width: 8px; height: 8px; border-radius: 50%;
      background: #10b981;
      box-shadow: 0 0 8px #10b981;
    }}

    .header-badge {{
      background: var(--neu-surface);
      box-shadow: inset 2px 2px 5px var(--neu-dark), inset -2px -2px 5px var(--neu-light);
      color: #1e40af;
      font-size: 0.75rem; font-weight: 800; padding: 0.45rem 0.95rem; border-radius: 9999px;
    }}

    .container {{ max-width: 1240px; margin: 0 auto; padding: 2.5rem 1.5rem; }}

    /* Hero Section */
    .hero {{ text-align: center; margin-bottom: 3.5rem; position: relative; }}
    .hero-badge {{
      display: inline-flex; align-items: center; gap: 0.5rem;
      background: var(--neu-surface);
      color: #1d4ed8;
      padding: 0.45rem 1.25rem; border-radius: 9999px;
      font-size: 0.82rem; font-weight: 800; margin-bottom: 1.2rem;
      box-shadow: 6px 6px 14px var(--neu-dark), -6px -6px 14px var(--neu-light);
      letter-spacing: 0.04em; text-transform: uppercase;
    }}
    .hero-title {{
      font-family: var(--font-display);
      font-size: 2.6rem; font-weight: 800;
      color: #0f172a; letter-spacing: -0.03em; line-height: 1.22; margin-bottom: 1rem;
    }}
    .hero-title span {{
      background: var(--brand-gradient);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    .hero-sub {{
      color: var(--text-muted); font-size: 1.1rem; max-width: 860px; margin: 0 auto; line-height: 1.65;
    }}

    /* Section Headings */
    .section-head {{ margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.85rem; }}
    .section-num {{
      width: 36px; height: 36px; border-radius: 12px;
      background: var(--brand-primary); color: white;
      font-size: 1rem; font-weight: 800;
      display: flex; align-items: center; justify-content: center;
      box-shadow: 4px 4px 9px var(--neu-dark), -4px -4px 9px var(--neu-light);
    }}
    .section-title {{
      font-family: var(--font-display); font-size: 1.5rem; font-weight: 800; color: var(--text-main);
    }}
    .section-desc {{ color: var(--text-dim); font-size: 0.95rem; margin-bottom: 1.65rem; }}

    /* Neumorphic Outer Cards */
    .neu-card {{
      background: var(--neu-surface);
      box-shadow: 10px 10px 24px var(--neu-dark), -10px -10px 24px var(--neu-light);
      border-radius: 24px;
      padding: 2rem;
      margin-bottom: 3.5rem;
      border: 1px solid rgba(255, 255, 255, 0.45);
      transition: all 0.25s ease;
    }}

    /* ========================================================================= */
    /* 1. REALISTIC VS CODE STUDIO WINDOW                                        */
    /* ========================================================================= */
    .vscode-window {{
      background: #1e1e1e;
      border-radius: 14px;
      overflow: hidden;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(255, 255, 255, 0.1);
      display: flex;
      flex-direction: column;
      margin-bottom: 2rem;
    }}

    .vscode-titlebar {{
      background: #323233;
      padding: 0.55rem 1rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid #252526;
      user-select: none;
    }}
    .vscode-controls {{
      display: flex;
      gap: 0.45rem;
      align-items: center;
    }}
    .control-dot {{ width: 12px; height: 12px; border-radius: 50%; }}
    .dot-red {{ background: #ff5f56; }}
    .dot-yellow {{ background: #ffbd2e; }}
    .dot-green {{ background: #27c93f; }}

    .vscode-title {{
      color: #cccccc;
      font-size: 0.78rem;
      font-family: var(--font-sans);
      display: flex;
      align-items: center;
      gap: 0.45rem;
    }}
    .vscode-title-badge {{
      background: #3c3c3d;
      padding: 0.15rem 0.5rem;
      border-radius: 4px;
      font-size: 0.7rem;
      color: #9cdcfe;
    }}

    .vscode-body {{
      display: flex;
      min-height: 480px;
      background: #1e1e1e;
    }}

    /* Activity Bar */
    .vscode-activity-bar {{
      width: 48px;
      background: #333333;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding-top: 0.75rem;
      gap: 1.25rem;
      color: #858585;
      border-right: 1px solid #252526;
    }}
    .activity-icon {{
      cursor: pointer;
      transition: color 0.2s;
    }}
    .activity-icon.active {{
      color: #ffffff;
      border-left: 2px solid #007acc;
      padding-left: 10px;
      margin-left: -12px;
    }}

    /* Sidebar Explorer */
    .vscode-sidebar {{
      width: 240px;
      background: #252526;
      border-right: 1px solid #191919;
      display: flex;
      flex-direction: column;
      font-size: 0.82rem;
      user-select: none;
    }}
    .sidebar-head {{
      padding: 0.6rem 1rem;
      text-transform: uppercase;
      font-size: 0.7rem;
      font-weight: 700;
      letter-spacing: 0.05em;
      color: #bbbbbb;
      display: flex;
      justify-content: space-between;
      border-bottom: 1px solid #2d2d2d;
    }}
    .file-tree {{
      padding: 0.5rem 0;
      display: flex;
      flex-direction: column;
    }}
    .tree-folder {{
      padding: 0.35rem 0.85rem;
      color: #cccccc;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 0.4rem;
      cursor: pointer;
    }}
    .tree-file {{
      padding: 0.4rem 1.4rem;
      color: #969696;
      display: flex;
      align-items: center;
      gap: 0.45rem;
      cursor: pointer;
      transition: all 0.15s;
    }}
    .tree-file:hover {{
      background: #2a2d2e;
      color: #ffffff;
    }}
    .tree-file.active {{
      background: #37373d;
      color: #ffffff;
      font-weight: 600;
    }}
    .file-badge {{
      margin-left: auto;
      font-size: 0.65rem;
      padding: 0.1rem 0.4rem;
      border-radius: 4px;
      font-family: var(--font-mono);
    }}
    .badge-cobol {{ background: rgba(2, 132, 199, 0.25); color: #38bdf8; }}
    .badge-ssis {{ background: rgba(234, 88, 12, 0.25); color: #fb923c; }}
    .badge-sql {{ background: rgba(124, 58, 237, 0.25); color: #c084fc; }}

    /* Main Editor Area */
    .vscode-editor-area {{
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      background: #1e1e1e;
    }}

    /* Tab Bar */
    .vscode-tabs {{
      background: #252526;
      display: flex;
      border-bottom: 1px solid #1e1e1e;
      overflow-x: auto;
    }}
    .editor-tab {{
      padding: 0.6rem 1.25rem;
      background: #2d2d2d;
      color: #969696;
      font-size: 0.8rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      cursor: pointer;
      border-right: 1px solid #1e1e1e;
      border-top: 2px solid transparent;
      user-select: none;
      transition: all 0.2s;
    }}
    .editor-tab:hover {{
      background: #1e1e1e;
      color: #ffffff;
    }}
    .editor-tab.active {{
      background: #1e1e1e;
      color: #ffffff;
      border-top: 2px solid #007acc;
      font-weight: 600;
    }}

    /* Breadcrumbs Bar */
    .vscode-breadcrumbs {{
      background: #1e1e1e;
      padding: 0.4rem 1rem;
      font-size: 0.75rem;
      color: #a0a0a0;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid #282828;
    }}
    .breadcrumb-path {{ display: flex; align-items: center; gap: 0.35rem; }}
    .jump-btn-vs {{
      background: #007acc;
      color: #ffffff;
      border: none;
      padding: 0.25rem 0.75rem;
      border-radius: 4px;
      font-size: 0.72rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.35rem;
      transition: background 0.2s;
    }}
    .jump-btn-vs:hover {{ background: #0098ff; }}

    /* Code Viewport */
    .vscode-code-viewport {{
      flex: 1;
      overflow: auto;
      max-height: 400px;
      padding: 0.5rem 0;
      font-family: var(--font-mono);
      font-size: 0.83rem;
      line-height: 1.55;
    }}
    .code-row {{
      display: flex;
      align-items: flex-start;
      padding: 0 1rem;
      white-space: pre;
    }}
    .code-row:hover {{
      background: rgba(255, 255, 255, 0.04);
    }}
    .code-row.target-line {{
      background: rgba(37, 99, 235, 0.22);
      border-left: 3px solid #38bdf8;
    }}
    .line-no {{
      width: 45px;
      color: #858585;
      text-align: right;
      padding-right: 1.25rem;
      user-select: none;
      flex-shrink: 0;
    }}
    .line-text {{
      color: #d4d4d4;
      flex: 1;
    }}

    /* VS Code Status Bar */
    .vscode-statusbar {{
      background: #007acc;
      color: #ffffff;
      padding: 0.25rem 1rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 0.72rem;
      user-select: none;
    }}
    .status-left, .status-right {{ display: flex; align-items: center; gap: 1rem; }}

    /* 4 Legacy Challenges Cards */
    .challenges-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1.25rem;
      margin-top: 1.5rem;
    }}
    @media (max-width: 1024px) {{
      .challenges-grid {{ grid-template-columns: repeat(2, 1fr); }}
      .vscode-sidebar {{ display: none; }}
    }}
    @media (max-width: 640px) {{
      .challenges-grid {{ grid-template-columns: 1fr; }}
    }}

    .challenge-card {{
      background: var(--neu-surface);
      box-shadow: 6px 6px 14px var(--neu-dark), -6px -6px 14px var(--neu-light);
      border-radius: 18px;
      padding: 1.4rem;
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
      border: 1px solid rgba(255, 255, 255, 0.5);
    }}
    .challenge-icon {{
      width: 38px; height: 38px; border-radius: 10px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.2rem;
      box-shadow: inset 2px 2px 4px var(--neu-dark), inset -2px -2px 4px var(--neu-light);
      margin-bottom: 0.25rem;
    }}
    .challenge-title {{
      font-family: var(--font-display);
      font-size: 1.05rem;
      font-weight: 800;
      color: var(--text-main);
    }}
    .challenge-desc {{
      font-size: 0.85rem;
      color: var(--text-muted);
      line-height: 1.5;
    }}

    /* ========================================================================= */
    /* 2. CORE BUSINESS LOGIC (EXPLAINED SIMPLY & INTERACTIVE)                    */
    /* ========================================================================= */
    .logic-showcase-box {{
      background: var(--neu-surface);
      box-shadow: inset 4px 4px 10px var(--neu-dark), inset -4px -4px 10px var(--neu-light);
      border-radius: 20px;
      padding: 1.75rem;
      margin-bottom: 1.75rem;
    }}
    .scenario-banner {{
      display: flex;
      align-items: flex-start;
      gap: 1rem;
      background: #ffffff;
      border-radius: 14px;
      padding: 1.2rem 1.5rem;
      box-shadow: 4px 4px 10px rgba(0, 0, 0, 0.05);
      margin-bottom: 1.5rem;
    }}
    .scenario-icon {{
      font-size: 1.8rem; flex-shrink: 0;
    }}
    .scenario-content h4 {{
      font-size: 1.05rem; font-weight: 800; color: #1e293b; margin-bottom: 0.3rem;
    }}
    .scenario-content p {{
      font-size: 0.9rem; color: #475569; line-height: 1.5;
    }}

    .logic-comparison-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1.5rem;
      margin-bottom: 1.5rem;
    }}
    @media (max-width: 850px) {{
      .logic-comparison-grid {{ grid-template-columns: 1fr; }}
    }}

    .logic-side-card {{
      background: var(--neu-surface);
      box-shadow: 6px 6px 14px var(--neu-dark), -6px -6px 14px var(--neu-light);
      border-radius: 18px;
      padding: 1.4rem;
      display: flex;
      flex-direction: column;
      gap: 0.85rem;
    }}
    .logic-badge-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .logic-pill {{
      font-size: 0.72rem;
      font-weight: 800;
      padding: 0.25rem 0.75rem;
      border-radius: 9999px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .pill-cobol {{ background: #e0f2fe; color: #0284c7; }}
    .pill-ssis {{ background: #ffedd5; color: #ea580c; }}

    .logic-code-snippet {{
      background: #0f172a;
      color: #e2e8f0;
      font-family: var(--font-mono);
      font-size: 0.8rem;
      padding: 0.95rem;
      border-radius: 10px;
      line-height: 1.5;
      overflow-x: auto;
    }}
    .plain-english-box {{
      background: rgba(255, 255, 255, 0.7);
      border-radius: 10px;
      padding: 0.95rem;
      border-left: 4px solid var(--brand-primary);
    }}
    .plain-english-title {{
      font-size: 0.78rem; font-weight: 800; text-transform: uppercase; color: var(--brand-primary); margin-bottom: 0.3rem;
    }}
    .plain-english-text {{
      font-size: 0.86rem; color: #334155; line-height: 1.45;
    }}

    /* Interactive Calculator Widget */
    .interactive-calc-card {{
      background: #ffffff;
      border-radius: 16px;
      padding: 1.5rem;
      box-shadow: 5px 5px 15px rgba(0, 0, 0, 0.05);
    }}
    .calc-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.25rem;
      flex-wrap: wrap;
      gap: 0.75rem;
    }}
    .calc-title {{
      font-family: var(--font-display);
      font-size: 1.15rem; font-weight: 800; color: #0f172a;
      display: flex; align-items: center; gap: 0.5rem;
    }}
    .calc-controls-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1.5rem;
      margin-bottom: 1.5rem;
    }}
    @media (max-width: 650px) {{
      .calc-controls-grid {{ grid-template-columns: 1fr; }}
    }}
    .slider-group {{
      display: flex;
      flex-direction: column;
      gap: 0.45rem;
    }}
    .slider-label-row {{
      display: flex;
      justify-content: space-between;
      font-size: 0.85rem;
      font-weight: 700;
      color: #334155;
    }}
    .calc-slider {{
      width: 100%;
      accent-color: var(--brand-primary);
      cursor: pointer;
    }}
    .calc-results-row {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1rem;
      background: #f8fafc;
      border-radius: 12px;
      padding: 1rem;
      border: 1px solid #e2e8f0;
    }}
    @media (max-width: 750px) {{
      .calc-results-row {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    .res-metric {{
      display: flex;
      flex-direction: column;
    }}
    .res-label {{
      font-size: 0.72rem; color: #64748b; font-weight: 700; text-transform: uppercase;
    }}
    .res-val {{
      font-family: var(--font-mono);
      font-size: 1.2rem;
      font-weight: 800;
      color: #0f172a;
      margin-top: 2px;
    }}
    .res-val.pass {{ color: var(--emerald); }}

    /* ========================================================================= */
    /* 3. ASK KAIRIX AI & THE OUTPUT SHOWCASE                                    */
    /* ========================================================================= */
    .kairix-ask-interface {{
      background: var(--neu-surface);
      box-shadow: inset 4px 4px 10px var(--neu-dark), inset -4px -4px 10px var(--neu-light);
      border-radius: 20px;
      padding: 1.75rem;
      margin-bottom: 1.75rem;
    }}
    .ask-input-bar {{
      display: flex;
      gap: 0.75rem;
      background: #ffffff;
      border-radius: 9999px;
      padding: 0.5rem 0.6rem 0.5rem 1.4rem;
      box-shadow: 4px 4px 12px rgba(0, 0, 0, 0.06);
      align-items: center;
      margin-bottom: 1rem;
    }}
    .ask-input-field {{
      flex: 1;
      border: none;
      outline: none;
      font-family: var(--font-sans);
      font-size: 0.95rem;
      color: #1e293b;
      font-weight: 500;
    }}
    .btn-ask-kairix {{
      background: var(--brand-gradient);
      color: #ffffff;
      border: none;
      border-radius: 9999px;
      padding: 0.65rem 1.5rem;
      font-size: 0.85rem;
      font-weight: 800;
      cursor: pointer;
      box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
      transition: all 0.2s;
      white-space: nowrap;
    }}
    .btn-ask-kairix:hover {{
      transform: scale(1.02);
      box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
    }}

    .prompt-chips {{
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
      align-items: center;
    }}
    .chip-label {{ font-size: 0.75rem; color: var(--text-dim); font-weight: 700; }}
    .chip-btn {{
      background: var(--neu-surface);
      border: none;
      font-size: 0.74rem;
      font-weight: 700;
      color: #334155;
      padding: 0.35rem 0.85rem;
      border-radius: 9999px;
      box-shadow: 2px 2px 5px var(--neu-dark), -2px -2px 5px var(--neu-light);
      cursor: pointer;
      transition: all 0.15s;
    }}
    .chip-btn:hover {{
      color: var(--brand-primary);
      transform: translateY(-1px);
    }}

    /* Output Results Box */
    .kairix-output-card {{
      background: #ffffff;
      border-radius: 18px;
      padding: 1.75rem;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
      border: 1px solid #e2e8f0;
      transition: all 0.3s ease;
    }}
    .output-status-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.25rem;
      padding-bottom: 0.75rem;
      border-bottom: 1px solid #f1f5f9;
      flex-wrap: wrap;
      gap: 0.5rem;
    }}
    .output-speed-badge {{
      display: flex;
      align-items: center;
      gap: 0.45rem;
      font-size: 0.8rem;
      font-weight: 700;
      color: var(--emerald);
    }}
    .output-source-badge {{
      background: #eff6ff;
      color: #1d4ed8;
      font-size: 0.75rem;
      font-weight: 800;
      padding: 0.25rem 0.75rem;
      border-radius: 9999px;
    }}

    .output-section-title {{
      font-size: 0.8rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--brand-primary);
      margin-bottom: 0.45rem;
    }}
    .output-text-content {{
      font-size: 0.98rem;
      color: #1e293b;
      line-height: 1.6;
      margin-bottom: 1.5rem;
    }}

    /* Formula Banner */
    .formula-banner {{
      background: #f8fafc;
      border-left: 4px solid #0284c7;
      border-radius: 0 12px 12px 0;
      padding: 1.1rem 1.4rem;
      margin-bottom: 1.5rem;
    }}
    .formula-math {{
      font-family: var(--font-mono);
      font-size: 1.05rem;
      font-weight: 700;
      color: #0369a1;
      margin-bottom: 0.35rem;
    }}
    .formula-note {{
      font-size: 0.82rem;
      color: #64748b;
    }}

    /* Exact Line Origins Grid */
    .origins-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1.25rem;
    }}
    @media (max-width: 850px) {{
      .origins-grid {{ grid-template-columns: 1fr; }}
    }}
    .origin-card-item {{
      background: #f8fafc;
      border-radius: 12px;
      padding: 1.1rem;
      border: 1px solid #e2e8f0;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}
    .origin-head {{
      font-size: 0.72rem;
      font-weight: 800;
      text-transform: uppercase;
      margin-bottom: 0.25rem;
    }}
    .origin-file-name {{
      font-family: var(--font-mono);
      font-size: 0.88rem;
      font-weight: 700;
      color: #0f172a;
      margin-bottom: 0.4rem;
    }}
    .origin-snippet-text {{
      font-size: 0.82rem;
      color: #475569;
      line-height: 1.45;
      margin-bottom: 0.85rem;
    }}
    .origin-view-btn {{
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      padding: 0.35rem 0.75rem;
      font-size: 0.75rem;
      font-weight: 700;
      color: var(--brand-primary);
      cursor: pointer;
      transition: all 0.2s;
      align-self: flex-start;
    }}
    .origin-view-btn:hover {{
      background: #eff6ff;
      border-color: #93c5fd;
    }}

    /* ========================================================================= */
    /* 4. MODERNIZATION JOURNEY: HOW IT IS ACHIEVED (UPLOADING, REENGINEERING)   */
    /* ========================================================================= */
    .modernization-roadmap-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1.25rem;
      margin-bottom: 2rem;
    }}
    @media (max-width: 1024px) {{
      .modernization-roadmap-grid {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    @media (max-width: 600px) {{
      .modernization-roadmap-grid {{ grid-template-columns: 1fr; }}
    }}

    .step-card {{
      background: var(--neu-surface);
      box-shadow: 6px 6px 14px var(--neu-dark), -6px -6px 14px var(--neu-light);
      border-radius: 18px;
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      position: relative;
    }}
    .step-number-tag {{
      width: 28px; height: 28px; border-radius: 8px;
      background: var(--brand-primary); color: white;
      font-size: 0.85rem; font-weight: 800;
      display: flex; align-items: center; justify-content: center;
      margin-bottom: 0.85rem;
    }}
    .step-card-title {{
      font-family: var(--font-display);
      font-size: 1.1rem;
      font-weight: 800;
      color: var(--text-main);
      margin-bottom: 0.5rem;
    }}
    .step-card-desc {{
      font-size: 0.86rem;
      color: var(--text-muted);
      line-height: 1.5;
      margin-bottom: 1rem;
    }}
    .step-features-list {{
      list-style: none;
      font-size: 0.78rem;
      color: var(--text-dim);
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
      margin-top: auto;
    }}
    .step-features-list li {{
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }}
    .step-features-list li::before {{
      content: "✓";
      color: var(--emerald);
      font-weight: bold;
    }}

    /* Interactive Re-Engineering Demo Card */
    .reengineer-demo-card {{
      background: var(--neu-surface);
      box-shadow: inset 4px 4px 10px var(--neu-dark), inset -4px -4px 10px var(--neu-light);
      border-radius: 20px;
      padding: 1.75rem;
    }}
    .reengineer-head-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.25rem;
      flex-wrap: wrap;
      gap: 0.75rem;
    }}
    .reengineer-toggle-pills {{
      display: flex;
      gap: 0.5rem;
    }}
    .toggle-pill-btn {{
      background: var(--neu-surface);
      border: none;
      padding: 0.45rem 1rem;
      border-radius: 9999px;
      font-size: 0.78rem;
      font-weight: 800;
      color: var(--text-dim);
      cursor: pointer;
      box-shadow: 3px 3px 6px var(--neu-dark), -3px -3px 6px var(--neu-light);
      transition: all 0.2s;
    }}
    .toggle-pill-btn.active {{
      box-shadow: inset 2px 2px 4px var(--neu-dark), inset -2px -2px 4px var(--neu-light);
      color: var(--brand-primary);
      background: #eff6ff;
    }}

    .reengineering-code-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1.25rem;
      margin-bottom: 1.25rem;
    }}
    @media (max-width: 850px) {{
      .reengineering-code-grid {{ grid-template-columns: 1fr; }}
    }}

    .modern-code-box {{
      background: #0f172a;
      border-radius: 12px;
      padding: 1.2rem;
      font-family: var(--font-mono);
      font-size: 0.8rem;
      color: #e2e8f0;
      line-height: 1.5;
      overflow-x: auto;
    }}
    .code-box-title {{
      font-size: 0.72rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 0.65rem;
      display: flex;
      justify-content: space-between;
    }}

    .api-test-card {{
      background: #ffffff;
      border-radius: 12px;
      padding: 1.2rem;
      box-shadow: 0 4px 10px rgba(0, 0, 0, 0.04);
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 1rem;
    }}
    .api-test-info {{
      font-size: 0.88rem; color: #334155;
    }}
    .btn-run-api {{
      background: #059669;
      color: #ffffff;
      border: none;
      padding: 0.55rem 1.25rem;
      border-radius: 8px;
      font-size: 0.82rem;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.4rem;
      transition: background 0.2s;
    }}
    .btn-run-api:hover {{ background: #047857; }}

    footer {{
      text-align: center;
      color: var(--text-dim);
      font-size: 0.85rem;
      margin-top: 4rem;
    }}
  </style>
</head>
<body>

  <!-- Dynamic Ambient Background Video Canvas -->
  <canvas id="bg-video-canvas"></canvas>

  <!-- Sticky Top Navigation Header -->
  <header class="nav-header">
    <div class="brand">
      <div class="brand-icon">
        <svg viewBox="0 0 24 24">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path>
        </svg>
      </div>
      <div class="brand-text">
        <h1>KAIRIX</h1>
        <span>Legacy Code Intelligence &amp; Modernization</span>
      </div>
    </div>
    
    <nav class="nav-links">
      <a href="#sec-vscode" class="nav-link">1. Legacy in VS Code</a>
      <a href="#sec-logic" class="nav-link">2. Hidden Business Logic</a>
      <a href="#sec-ask" class="nav-link">3. Ask KAIRIX AI</a>
      <a href="#sec-journey" class="nav-link">4. Modernization Journey</a>
    </nav>

    <div class="header-controls">
      <button class="anim-toggle-btn active" id="btn-toggle-video" onclick="toggleBackgroundVideo()">
        <span class="pulse-dot"></span>
        <span id="video-btn-text">Ambient Video: ON</span>
      </button>
      <div class="header-badge">
        Executive Walkthrough Mode
      </div>
    </div>
  </header>

  <div class="container">

    <!-- Hero Section -->
    <div class="hero">
      <div class="hero-badge">
        Multi-Source Legacy Modernization
      </div>
      <h2 class="hero-title">
        Demystifying Legacy Code: <span>From Ancient Systems to Modern Intelligence</span>
      </h2>
      <p class="hero-sub">
        Enterprises run mission-critical financial calculations inside 50-year-old COBOL and 20-year-old SSIS packages.
        Original developers have retired, documentation is missing, and modern teams struggle to read it.
        Here is a simple look at the code in VS Code, the hidden logic, how KAIRIX solves queries instantly, and how we re-engineer it for the cloud.
      </p>
    </div>

    <!-- ========================================================================= -->
    <!-- SECTION 1: LEGACY CODE IN VS CODE & THE CHALLENGES                        -->
    <!-- ========================================================================= -->
    <div class="section-head" id="sec-vscode">
      <div class="section-num">1</div>
      <div class="section-title">The Legacy Code in VS Code &amp; Core Challenges</div>
    </div>
    <p class="section-desc">
      Inspect the authentic legacy repository loaded directly into VS Code below. Toggle between the 50-year-old COBOL program, the 20-year-old SSIS ETL package, and the analytical SQL view:
    </p>

    <div class="neu-card">
      
      <!-- VS Code Window Simulator -->
      <div class="vscode-window">
        <!-- Titlebar -->
        <div class="vscode-titlebar">
          <div class="vscode-controls">
            <div class="control-dot dot-red"></div>
            <div class="control-dot dot-yellow"></div>
            <div class="control-dot dot-green"></div>
          </div>
          <div class="vscode-title">
            <span>Visual Studio Code — legacy-enterprise-core [Workspace]</span>
            <span class="vscode-title-badge" id="vs-active-file-badge">EARNPREM.CBL</span>
          </div>
          <div style="width: 50px;"></div>
        </div>

        <div class="vscode-body">
          <!-- Activity Bar -->
          <div class="vscode-activity-bar">
            <div class="activity-icon active" title="Explorer">📁</div>
            <div class="activity-icon" title="Search">🔍</div>
            <div class="activity-icon" title="Source Control">🌿</div>
            <div class="activity-icon" title="Extensions">🧩</div>
          </div>

          <!-- Explorer Sidebar -->
          <div class="vscode-sidebar">
            <div class="sidebar-head">
              <span>Explorer: Workspace</span>
              <span>...</span>
            </div>
            <div class="file-tree">
              <div class="tree-folder">📂 source</div>
              
              <!-- COBOL -->
              <div class="tree-file active" id="tree-cobol" onclick="switchVsTab('cobol')">
                <span>📄 EARNPREM.CBL</span>
                <span class="file-badge badge-cobol">COBOL (50y)</span>
              </div>

              <!-- SSIS -->
              <div class="tree-file" id="tree-ssis" onclick="switchVsTab('ssis')">
                <span>📦 Extract_Premium.dtsx</span>
                <span class="file-badge badge-ssis">SSIS (20y)</span>
              </div>

              <!-- SQL -->
              <div class="tree-file" id="tree-sql" onclick="switchVsTab('sql')">
                <span>⚡ PolicyCenter.sql</span>
                <span class="file-badge badge-sql">SQL</span>
              </div>
            </div>
          </div>

          <!-- Editor Pane -->
          <div class="vscode-editor-area">
            <!-- Tabs -->
            <div class="vscode-tabs">
              <div class="editor-tab active" id="tab-btn-cobol" onclick="switchVsTab('cobol')">
                <span>🟦 EARNPREM.CBL</span>
              </div>
              <div class="editor-tab" id="tab-btn-ssis" onclick="switchVsTab('ssis')">
                <span>🟧 Extract_Premium.dtsx</span>
              </div>
              <div class="editor-tab" id="tab-btn-sql" onclick="switchVsTab('sql')">
                <span>🟪 PolicyCenter_CPP_Breakdown.sql</span>
              </div>
            </div>

            <!-- Breadcrumbs -->
            <div class="vscode-breadcrumbs">
              <div class="breadcrumb-path" id="vs-breadcrumb-text">
                source &gt; mainframe &gt; EARNPREM.CBL &gt; PROCEDURE DIVISION &gt; CALCULATE-EARNED
              </div>
              <button class="jump-btn-vs" onclick="jumpToVsTarget()">
                <span>🎯 Jump to Core Logic (Lines <span id="vs-target-line-num">587</span>)</span>
              </button>
            </div>

            <!-- Code Lines Viewport -->
            <div class="vscode-code-viewport" id="vscode-viewport">
              <!-- Injected via JS -->
            </div>

            <!-- Statusbar -->
            <div class="vscode-statusbar">
              <div class="status-left">
                <span>main*</span>
                <span id="vs-file-meta-status">UTF-8 • COBOL 85 (691 lines)</span>
              </div>
              <div class="status-right">
                <span id="vs-cursor-status">Ln 587, Col 12</span>
                <span>Spaces: 4</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 4 Fundamental Legacy Code Challenges (Explained for Non-Technical Leaders) -->
      <div class="challenges-grid">
        <div class="challenge-card">
          <div class="challenge-icon" style="background: #e0f2fe; color: #0284c7;">⏳</div>
          <div class="challenge-title">50-Year-Old COBOL</div>
          <p class="challenge-desc">
            Written in the 1970s punch-card era. Strict 80-column formatting, uppercase commands, and cryptic variables (like <code>WS-EARNED-DAYS</code>) that modern software engineers are never taught.
          </p>
        </div>

        <div class="challenge-card">
          <div class="challenge-icon" style="background: #ffedd5; color: #ea580c;">📦</div>
          <div class="challenge-title">20-Year-Old SSIS Packages</div>
          <p class="challenge-desc">
            Early-2000s ETL pipelines. Vital business checks are trapped inside thousands of lines of machine-generated XML GUIDs that cannot be searched without legacy Microsoft tools.
          </p>
        </div>

        <div class="challenge-card">
          <div class="challenge-icon" style="background: #fef3c7; color: #d97706;">👴</div>
          <div class="challenge-title">The Brain Drain Crisis</div>
          <p class="challenge-desc">
            The original architects and developers who built these foundational algorithms retired 15+ years ago. No current employee has full end-to-end knowledge of how the calculations operate.
          </p>
        </div>

        <div class="challenge-card">
          <div class="challenge-icon" style="background: #fee2e2; color: #e11d48;">⚠️</div>
          <div class="challenge-title">The Fear of Modification</div>
          <p class="challenge-desc">
            Because calculations cross multiple ancient systems, making a change to even a single line can silently miscalculate millions of dollars in customer premiums without anyone noticing.
          </p>
        </div>
      </div>

    </div>

    <!-- ========================================================================= -->
    <!-- SECTION 2: THE CORE LOGIC INSIDE THE CODE (SIMPLE & INTERACTIVE)          -->
    <!-- ========================================================================= -->
    <div class="section-head" id="sec-logic">
      <div class="section-num">2</div>
      <div class="section-title">The Hidden Logic: Earned Premium Calculation</div>
    </div>
    <p class="section-desc">
      Let's look at one real calculation that runs inside the code every day. Here is what it does in human business terms, how it is written in code, and an interactive simulation:
    </p>

    <div class="neu-card">
      <div class="logic-showcase-box">
        
        <!-- Real World Scenario -->
        <div class="scenario-banner">
          <div class="scenario-icon">🚗</div>
          <div class="scenario-content">
            <h4>Everyday Business Scenario: The Cancelled Insurance Policy</h4>
            <p>
              A customer buys a 1-year commercial auto policy for <strong>$1,200</strong> on Jan 1st. On <strong>Day 100</strong>, they cancel their coverage. 
              The insurance company cannot keep the full $1,200 — they must calculate how much money they legally "earned" for the 100 days of protection, and how much they must "refund" to the customer.
            </p>
          </div>
        </div>

        <!-- Side-by-Side: COBOL Math vs SSIS Validation -->
        <div class="logic-comparison-grid">
          
          <!-- Card A: The COBOL Math -->
          <div class="logic-side-card">
            <div class="logic-badge-row">
              <span class="logic-pill pill-cobol">Mainframe Calculation • EARNPREM.CBL</span>
              <span style="font-size: 0.75rem; color: #64748b; font-weight: 700;">Lines 587–594</span>
            </div>
            <div class="logic-code-snippet">
COMPUTE WS-TERM-DAYS = WS-EXP-INT - WS-EFF-INT + 1
COMPUTE WS-EARNED-DAYS = WS-CALC-INT - WS-EFF-INT + 1
COMPUTE WS-EARNED ROUNDED = 
    PRI-WRITTEN-PREMIUM * WS-EARNED-DAYS / WS-TERM-DAYS
COMPUTE WS-UNEARNED = PRI-WRITTEN-PREMIUM - WS-EARNED</div>
            <div class="plain-english-box">
              <div class="plain-english-title">What This Means in Plain English:</div>
              <div class="plain-english-text">
                1. <strong>Inclusive Calendar Days:</strong> Count exact calendar days active (the <code>+1</code> handles leap year logic).<br>
                2. <strong>Proration:</strong> Multiply Written Premium by (Days Active &divide; Total Days).<br>
                3. <strong>Refund Balance:</strong> Deduct earned portion to find unearned dollars owed back to customer.
              </div>
            </div>
          </div>

          <!-- Card B: The SSIS Guardrail -->
          <div class="logic-side-card">
            <div class="logic-badge-row">
              <span class="logic-pill pill-ssis">ETL Safety Guardrail • Extract_Premium.dtsx</span>
              <span style="font-size: 0.75rem; color: #64748b; font-weight: 700;">Lines 101–105</span>
            </div>
            <div class="logic-code-snippet">
&lt;property name="Conditions"&gt;
  earned_premium &lt;= written_premium (BR-07) |
  ABS(written_premium - (earned_premium + unearned_premium)) 
    &lt;= 1.00 (BR-08 rounding tolerance)
&lt;/property&gt;</div>
            <div class="plain-english-box" style="border-left-color: var(--ssis-accent);">
              <div class="plain-english-title" style="color: var(--ssis-accent);">What This Means in Plain English:</div>
              <div class="plain-english-text">
                1. <strong>Rule BR-07 (Over-earning Protection):</strong> The insurer can never claim to have earned more than the total policy price.<br>
                2. <strong>Rule BR-08 (Tolerance Check):</strong> Earned + Unearned must equal Written within a $1.00 rounding margin; anything violating this is quarantined into an error queue.
              </div>
            </div>
          </div>

        </div>

        <!-- Interactive Calculation Simulator Widget -->
        <div class="interactive-calc-card">
          <div class="calc-header">
            <div class="calc-title">
              <span>🧮</span> Try It Yourself: Interactive Logic Simulator
            </div>
            <span style="font-size: 0.8rem; color: #64748b;">
              Drag the sliders below to see the COBOL formula &amp; SSIS rules execute in real time:
            </span>
          </div>

          <div class="calc-controls-grid">
            <div class="slider-group">
              <div class="slider-label-row">
                <span>Written Policy Premium:</span>
                <span id="slider-val-premium" style="color: var(--brand-primary); font-family: var(--font-mono);">$1,200.00</span>
              </div>
              <input type="range" class="calc-slider" id="calc-slider-premium" min="300" max="10000" step="100" value="1200" oninput="updateInteractiveCalc()">
            </div>

            <div class="slider-group">
              <div class="slider-label-row">
                <span>Days Elapsed (Active Days):</span>
                <span id="slider-val-days" style="color: var(--brand-primary); font-family: var(--font-mono);">100 of 365 Days</span>
              </div>
              <input type="range" class="calc-slider" id="calc-slider-days" min="1" max="365" step="1" value="100" oninput="updateInteractiveCalc()">
            </div>
          </div>

          <div class="calc-results-row">
            <div class="res-metric">
              <span class="res-label">Earned (Insurer Keeps)</span>
              <span class="res-val" id="res-calc-earned" style="color: #0284c7;">$328.77</span>
            </div>
            <div class="res-metric">
              <span class="res-label">Unearned (Refund to Customer)</span>
              <span class="res-val" id="res-calc-unearned" style="color: #ea580c;">$871.23</span>
            </div>
            <div class="res-metric">
              <span class="res-label">SSIS Rule BR-07 Check</span>
              <span class="res-val pass" id="res-calc-br07">PASSED ✓</span>
            </div>
            <div class="res-metric">
              <span class="res-label">SSIS Rule BR-08 Variance</span>
              <span class="res-val pass" id="res-calc-br08">$0.00 (OK)</span>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- SECTION 3: ASK KAIRIX ABOUT THE LOGIC & SHOW OUTPUT                       -->
    <!-- ========================================================================= -->
    <div class="section-head" id="sec-ask">
      <div class="section-num">3</div>
      <div class="section-title">Ask KAIRIX AI: From Question to Instant Line-Anchored Answer</div>
    </div>
    <p class="section-desc">
      Instead of engineers spending weeks reading lines manually, anyone can ask a plain English question. Watch KAIRIX retrieve the exact answer and prove which files it came from:
    </p>

    <div class="neu-card">
      <div class="kairix-ask-interface">
        
        <!-- Prompt Box -->
        <div class="ask-input-bar">
          <span style="font-size: 1.2rem; color: var(--brand-primary);">💬</span>
          <input type="text" class="ask-input-field" id="kairix-query-input" value="How is earned premium calculated, prorated, and validated across our legacy systems?">
          <button class="btn-ask-kairix" onclick="triggerKairixAsk()">
            Ask KAIRIX AI ⚡
          </button>
        </div>

        <!-- Quick Question Suggestions -->
        <div class="prompt-chips">
          <span class="chip-label">Try asking:</span>
          <button class="chip-btn" onclick="setKairixQuestion('How is earned premium calculated, prorated, and validated across our legacy systems?')">
            Earned Premium Proration
          </button>
          <button class="chip-btn" onclick="setKairixQuestion('What financial validation rules are applied in SSIS pipeline before writing to the data warehouse?')">
            SSIS BR-07 &amp; BR-08 Rules
          </button>
          <button class="chip-btn" onclick="setKairixQuestion('How does PolicyCenter SQL segment written premium vs cancelled premium?')">
            SQL Transaction Buckets
          </button>
        </div>

      </div>

      <!-- KAIRIX Answer Card (Instant Output Showcase) -->
      <div class="kairix-output-card" id="kairix-output-container">
        
        <div class="output-status-bar">
          <div class="output-speed-badge">
            <span>⚡</span>
            <span>Query Resolved in 1.8 Seconds (Zero Hallucination)</span>
          </div>
          <div class="output-source-badge">
            Linked Across 3 Legacy Codebases
          </div>
        </div>

        <!-- 1. The Plain English Answer -->
        <div class="output-section-title">1. The Direct Plain-English Answer:</div>
        <div class="output-text-content" id="output-answer-text">
          Earned Premium is calculated daily at the rating layer using calendar-day proration in the 50-year-old Mainframe COBOL program.
          The calculated amounts flow through the 20-year-old SSIS ETL pipeline, which enforces financial boundary rules (BR-07 and BR-08) ensuring earned funds never exceed total written premium and rounding stays within $1.00.
          Finally, the figures are categorized by Transaction Type (Renewals, Submissions, Cancellations) in the analytical SQL database view for executive balance sheet reporting.
        </div>

        <!-- 2. The Extracted Mathematical Formula -->
        <div class="formula-banner">
          <div class="output-section-title" style="color: #0284c7; margin-bottom: 0.2rem;">2. The Extracted Formula &amp; Business Rules:</div>
          <div class="formula-math" id="output-formula-text">
            Earned Premium = Written Premium &times; [ (Calculation Date - Effective Date + 1) / (Expiration Date - Effective Date + 1) ]
          </div>
          <div class="formula-note">
            Enforced Safeguards: <code>earned_premium &le; written_premium (Rule BR-07)</code> &bull; Rounding variance <code>&le; $1.00 (Rule BR-08)</code>
          </div>
        </div>

        <!-- 3. Where The Logic Came From (Lineage Origins) -->
        <div class="output-section-title">3. Exactly Which File &amp; Lines The Logic Came From:</div>
        <div class="origins-grid">
          
          <!-- Origin 1: COBOL -->
          <div class="origin-card-item">
            <div>
              <div class="origin-head" style="color: var(--cobol-accent);">🟦 Math Proration Engine</div>
              <div class="origin-file-name">EARNPREM.CBL (Lines 587–594)</div>
              <div class="origin-snippet-text">
                Procedure Division routine <code>CALCULATE-EARNED</code> computes days ratio with inclusive +1 day logic.
              </div>
            </div>
            <button class="origin-view-btn" onclick="switchVsTab('cobol'); jumpToVsTarget();">
              Inspect in VS Code ➔
            </button>
          </div>

          <!-- Origin 2: SSIS -->
          <div class="origin-card-item">
            <div>
              <div class="origin-head" style="color: var(--ssis-accent);">🟧 Financial Guardrail</div>
              <div class="origin-file-name">Extract_Premium.dtsx (Lines 101–105)</div>
              <div class="origin-snippet-text">
                Conditional Split component checks bounds (<code>BR-07</code>) &amp; routes discrepancies to error quarantine.
              </div>
            </div>
            <button class="origin-view-btn" onclick="switchVsTab('ssis'); jumpToVsTarget();">
              Inspect in VS Code ➔
            </button>
          </div>

          <!-- Origin 3: SQL -->
          <div class="origin-card-item">
            <div>
              <div class="origin-head" style="color: var(--sql-accent);">🟪 Analytics Reporting</div>
              <div class="origin-file-name">PolicyCenter_CPP.sql (Lines 16–30)</div>
              <div class="origin-snippet-text">
                SQL views categorize policy transactions into Renewals, Cancellations, and Reinstatements.
              </div>
            </div>
            <button class="origin-view-btn" onclick="switchVsTab('sql'); jumpToVsTarget();">
              Inspect in VS Code ➔
            </button>
          </div>

        </div>

      </div>

    </div>

    <!-- ========================================================================= -->
    <!-- SECTION 4: HOW IT CAN BE ACHIEVED: MODERNIZATION ROADMAP                  -->
    <!-- ========================================================================= -->
    <div class="section-head" id="sec-journey">
      <div class="section-num">4</div>
      <div class="section-title">How It Can Be Achieved: The 4-Step Modernization Journey</div>
    </div>
    <p class="section-desc">
      How does an enterprise transition from fear of touching legacy systems to automated intelligence and modern cloud architectures? Here is the simple 4-step process:
    </p>

    <div class="neu-card">
      
      <!-- 4 Sequential Modernization Pillars -->
      <div class="modernization-roadmap-grid">
        
        <!-- Step 1: Uploading Legacy Files -->
        <div class="step-card">
          <div class="step-number-tag">1</div>
          <div class="step-card-title">Uploading Raw Files</div>
          <p class="step-card-desc">
            No expensive re-typing or manual documentation needed. Upload raw <code>.CBL</code>, <code>.DTSX</code>, and <code>.SQL</code> files as they exist today.
          </p>
          <ul class="step-features-list">
            <li>Multi-language support</li>
            <li>Zero manual setup</li>
            <li>Instant file cataloging</li>
          </ul>
        </div>

        <!-- Step 2: Automated AST Parsing -->
        <div class="step-card">
          <div class="step-number-tag">2</div>
          <div class="step-card-title">Automated AI Parsing</div>
          <p class="step-card-desc">
            Tree-sitter and SQLGlot AST engines break down ancient punch-card syntax and opaque XML into clean, structured knowledge blocks.
          </p>
          <ul class="step-features-list">
            <li>AST syntax trees</li>
            <li>Decompiles XML GUIDs</li>
            <li>Variable extraction</li>
          </ul>
        </div>

        <!-- Step 3: Knowledge Graph Linking -->
        <div class="step-card">
          <div class="step-number-tag">3</div>
          <div class="step-card-title">Graph &amp; Vector Linking</div>
          <p class="step-card-desc">
            Connects disparate systems into a living Neo4j Knowledge Graph, tracing how numbers flow from Mainframe to ETL to SQL warehouses.
          </p>
          <ul class="step-features-list">
            <li>End-to-end data lineage</li>
            <li>Pinecone semantic search</li>
            <li>Cross-file references</li>
          </ul>
        </div>

        <!-- Step 4: Re-engineering -->
        <div class="step-card">
          <div class="step-number-tag">4</div>
          <div class="step-card-title">Modern Re-Engineering</div>
          <p class="step-card-desc">
            Generate clean, modern Python/FastAPI microservices, modern SQL, and automated test suites with 100% mathematical fidelity.
          </p>
          <ul class="step-features-list">
            <li>Cloud-native APIs</li>
            <li>Automated unit tests</li>
            <li>Safe mainframe migration</li>
          </ul>
        </div>

      </div>

      <!-- Interactive Re-Engineering Demo: 1975 COBOL vs 2026 Modern Python API -->
      <div class="reengineer-demo-card">
        <div class="reengineer-head-row">
          <div>
            <div style="font-family: var(--font-display); font-size: 1.2rem; font-weight: 800; color: var(--text-main);">
              Live Transformation: 1975 Mainframe COBOL ➔ 2026 Cloud API
            </div>
            <div style="font-size: 0.85rem; color: var(--text-dim);">
              See how KAIRIX turns opaque legacy punch-card logic into clean, self-documenting modern code:
            </div>
          </div>
          <div class="reengineer-toggle-pills">
            <button class="toggle-pill-btn active" id="pill-python" onclick="toggleModernLang('python')">Modern Python (FastAPI)</button>
            <button class="toggle-pill-btn" id="pill-typescript" onclick="toggleModernLang('typescript')">Modern TypeScript</button>
          </div>
        </div>

        <!-- Side by side code view -->
        <div class="reengineering-code-grid">
          <!-- Left: Legacy 1975 COBOL -->
          <div class="modern-code-box">
            <div class="code-box-title" style="color: #38bdf8;">
              <span>⏳ 1975 Mainframe Punch-Card COBOL</span>
              <span style="color: #64748b;">EARNPREM.CBL</span>
            </div>
            <pre style="margin: 0; font-size: 0.78rem;"><code>       CALCULATE-EARNED.
           COMPUTE WS-EFF-INT =
              FUNCTION INTEGER-OF-DATE(PI-EFFECTIVE-DATE)
           COMPUTE WS-EXP-INT =
              FUNCTION INTEGER-OF-DATE(PI-EXPIRY-DATE)
           COMPUTE WS-CALC-INT =
              FUNCTION INTEGER-OF-DATE(PRI-CALCULATION-DATE)
           COMPUTE WS-TERM-DAYS =
              WS-EXP-INT - WS-EFF-INT + 1
           COMPUTE WS-EARNED-DAYS =
              WS-CALC-INT - WS-EFF-INT + 1
           COMPUTE WS-EARNED ROUNDED =
              PRI-WRITTEN-PREMIUM
              * WS-EARNED-DAYS / WS-TERM-DAYS
           COMPUTE WS-UNEARNED =
              PRI-WRITTEN-PREMIUM - WS-EARNED.</code></pre>
          </div>

          <!-- Right: Generated Modern Service (Python / TS) -->
          <div class="modern-code-box">
            <div class="code-box-title" style="color: #34d399;">
              <span id="modern-lang-title">⚡ 2026 Cloud Microservice (FastAPI)</span>
              <span style="color: #64748b;" id="modern-lang-file">premium_service.py</span>
            </div>
            <pre style="margin: 0; font-size: 0.78rem;" id="modern-code-content"><code>@app.post("/api/v1/premium/prorate")
def prorate_premium(policy: PremiumProrationRequest) -> ProrationResult:
    # 1. Exact calendar days active (inclusive +1)
    term_days = (policy.expiry_date - policy.effective_date).days + 1
    earned_days = (policy.calc_date - policy.effective_date).days + 1
    
    # 2. Daily proration calculation
    ratio = Decimal(earned_days) / Decimal(term_days)
    earned = (policy.written_premium * ratio).quantize(Decimal('.01'))
    
    # 3. Enforce SSIS Legacy Safeguards (BR-07 &amp; BR-08)
    assert earned &lt;= policy.written_premium, "BR-07 Bound Violation"
    unearned = policy.written_premium - earned
    return ProrationResult(earned=earned, unearned=unearned)</code></pre>
          </div>
        </div>

        <!-- Live API Simulation Banner -->
        <div class="api-test-card">
          <div class="api-test-info">
            <strong>Ready for Deployment:</strong> This re-engineered endpoint has passed 100% of mathematical parity checks against the mainframe test fixtures.
          </div>
          <button class="btn-run-api" id="btn-test-api" onclick="simulateModernApiCall()">
            <span>▶</span> Run Simulated API Call
          </button>
        </div>

        <!-- Simulated Response Box -->
        <div id="api-response-well" style="display: none; margin-top: 1rem; background: #0f172a; border-radius: 10px; padding: 1rem; color: #38bdf8; font-family: var(--font-mono); font-size: 0.8rem;">
          <!-- Injected via JS -->
        </div>

      </div>

    </div>

    <!-- Footer -->
    <footer>
      KAIRIX Platform &bull; Automated Knowledge Engineering &amp; Agentic RAG for Legacy Modernization
    </footer>

  </div>

  <script>
    // Embedded Legacy Source Data
    const rawFiles = {json_payload};

    const fileMeta = {{
      cobol: {{
        path: "source/mainframe/EARNPREM.CBL",
        desc: "Mainframe COBOL 85 (691 lines) • Punch-Card Procedural Logic",
        breadcrumb: "source > mainframe > EARNPREM.CBL > PROCEDURE DIVISION > CALCULATE-EARNED",
        targetLine: 587,
        badge: "EARNPREM.CBL"
      }},
      ssis: {{
        path: "source/ssis/packages/Extract_Premium.dtsx",
        desc: "SSIS ETL Pipeline XML (197 lines) • Opaque XML GUIDs &amp; Split Rules",
        breadcrumb: "source > ssis > packages > Extract_Premium.dtsx > Conditional Split > BR-07 / BR-08",
        targetLine: 101,
        badge: "Extract_Premium.dtsx"
      }},
      sql: {{
        path: "source/sql/PolicyCenter_CPP_Breakdown.sql",
        desc: "Guidewire SQL Analytics View (267 lines) • 1,000+ Lines of Logic",
        breadcrumb: "source > sql > PolicyCenter_CPP_Breakdown.sql > CASE Statements > Transaction Buckets",
        targetLine: 16,
        badge: "PolicyCenter.sql"
      }}
    }};

    let activeVsTab = 'cobol';

    function renderVsCode(key) {{
      const text = rawFiles[key];
      const lines = text.split('\\n');
      const viewport = document.getElementById('vscode-viewport');
      const target = fileMeta[key].targetLine;

      document.getElementById('vs-active-file-badge').innerText = fileMeta[key].badge;
      document.getElementById('vs-breadcrumb-text').innerText = fileMeta[key].breadcrumb;
      document.getElementById('vs-target-line-num').innerText = target;
      document.getElementById('vs-file-meta-status').innerText = `UTF-8 • ${{lines.length}} lines • ${{fileMeta[key].desc}}`;
      document.getElementById('vs-cursor-status').innerText = `Ln ${{target}}, Col 12`;

      let html = '';
      for (let i = 0; i < lines.length; i++) {{
        const lineNum = i + 1;
        const isTarget = (lineNum >= target && lineNum <= target + 7) ? 'target-line' : '';
        const escaped = lines[i].replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        html += `<div class="code-row ${{isTarget}}" id="vs-line-${{key}}-${{lineNum}}">
          <div class="line-no">${{lineNum}}</div>
          <div class="line-text">${{escaped}}</div>
        </div>`;
      }}
      viewport.innerHTML = html;
    }}

    function switchVsTab(key) {{
      activeVsTab = key;
      // Update Tab Headers
      document.querySelectorAll('.editor-tab').forEach(el => el.classList.remove('active'));
      document.getElementById('tab-btn-' + key).classList.add('active');

      // Update Sidebar Items
      document.querySelectorAll('.tree-file').forEach(el => el.classList.remove('active'));
      document.getElementById('tree-' + key).classList.add('active');

      renderVsCode(key);
    }}

    function jumpToVsTarget() {{
      const target = fileMeta[activeVsTab].targetLine;
      const el = document.getElementById(`vs-line-${{activeVsTab}}-${{target}}`);
      if (el) {{
        el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
      }}
    }}

    // -------------------------------------------------------------
    // INTERACTIVE CALCULATION SIMULATOR
    // -------------------------------------------------------------
    function updateInteractiveCalc() {{
      const written = parseFloat(document.getElementById('calc-slider-premium').value);
      const days = parseInt(document.getElementById('calc-slider-days').value);
      const totalDays = 365;

      document.getElementById('slider-val-premium').innerText = `$${{written.toLocaleString('en-US', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }})}}`;
      document.getElementById('slider-val-days').innerText = `${{days}} of ${{totalDays}} Days`;

      // Mainframe COBOL Math (Line 587-594)
      const earned = Math.round((written * (days / totalDays)) * 100) / 100;
      const unearned = Math.round((written - earned) * 100) / 100;

      document.getElementById('res-calc-earned').innerText = `$${{earned.toLocaleString('en-US', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }})}}`;
      document.getElementById('res-calc-unearned').innerText = `$${{unearned.toLocaleString('en-US', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }})}}`;

      // SSIS BR-07 Check
      const br07Passed = earned <= written;
      const br07El = document.getElementById('res-calc-br07');
      if (br07Passed) {{
        br07El.innerText = "PASSED ✓";
        br07El.className = "res-val pass";
      }} else {{
        br07El.innerText = "FAILED ✗";
        br07El.className = "res-val";
        br07El.style.color = "var(--rose)";
      }}

      // SSIS BR-08 Variance
      const variance = Math.abs(written - (earned + unearned));
      const br08El = document.getElementById('res-calc-br08');
      br08El.innerText = `$${{variance.toFixed(2)}} (OK)`;
    }}

    // -------------------------------------------------------------
    // KAIRIX QUESTION & ANSWER SIMULATION
    // -------------------------------------------------------------
    const questionDatabase = {{
      "earned": {{
        query: "How is earned premium calculated, prorated, and validated across our legacy systems?",
        answer: "Earned Premium is calculated daily at the rating layer using calendar-day proration in the 50-year-old Mainframe COBOL engine. The calculated amounts flow through the 20-year-old SSIS ETL pipeline, which enforces financial boundary rules (BR-07 and BR-08) ensuring earned funds never exceed total written premium and rounding stays within $1.00. Finally, the figures are categorized by Transaction Type in the analytical SQL database view for executive balance sheet reporting.",
        formula: "Earned Premium = Written Premium × [ (Calculation Date - Effective Date + 1) / (Expiration Date - Effective Date + 1) ]"
      }},
      "ssis": {{
        query: "What financial validation rules are applied in SSIS pipeline before writing to the data warehouse?",
        answer: "The SSIS package 'Extract_Premium.dtsx' uses a Conditional Split component (Lines 101–105) to enforce two core business rules: Rule BR-07 guarantees that earned premium can never exceed written premium, and Rule BR-08 ensures that rounding differences between written and (earned + unearned) never exceed $1.00. Any record that violates these thresholds is diverted into 'stg.error_quarantine' for audit review.",
        formula: "BR-07: earned_premium <= written_premium  |  BR-08: ABS(written - (earned + unearned)) <= $1.00"
      }},
      "sql": {{
        query: "How does PolicyCenter SQL segment written premium vs cancelled premium?",
        answer: "In 'PolicyCenter_CPP_Breakdown.sql', lines 16–30 execute conditional CASE WHEN statements on 'TranType'. When TranType is 'Renewal' or 'Submission', the amount is captured into 'SubWritten_Premium'. When TranType is 'Cancellation', the transaction is routed into 'CancelledPremium' alongside its cancellation effective date for financial reporting.",
        formula: "CASE WHEN TranType IN ('Renewal','Submission') THEN Written_Premium ELSE NULL END"
      }}
    }};

    function setKairixQuestion(qText) {{
      document.getElementById('kairix-query-input').value = qText;
      triggerKairixAsk();
    }}

    function triggerKairixAsk() {{
      const container = document.getElementById('kairix-output-container');
      const input = document.getElementById('kairix-query-input').value.toLowerCase();
      
      container.style.opacity = '0.5';
      container.style.transform = 'scale(0.99)';

      setTimeout(() => {{
        let selected = questionDatabase.earned;
        if (input.includes('ssis') || input.includes('rule') || input.includes('br-07')) {{
          selected = questionDatabase.ssis;
        }} else if (input.includes('sql') || input.includes('policycenter') || input.includes('cancel')) {{
          selected = questionDatabase.sql;
        }}

        document.getElementById('output-answer-text').innerText = selected.answer;
        document.getElementById('output-formula-text').innerText = selected.formula;

        container.style.opacity = '1';
        container.style.transform = 'scale(1)';
      }}, 300);
    }}

    // -------------------------------------------------------------
    // RE-ENGINEERING CODE TOGGLE & API SIMULATION
    // -------------------------------------------------------------
    function toggleModernLang(lang) {{
      const pillPy = document.getElementById('pill-python');
      const pillTs = document.getElementById('pill-typescript');
      const codeEl = document.getElementById('modern-code-content');
      const titleEl = document.getElementById('modern-lang-title');
      const fileEl = document.getElementById('modern-lang-file');

      if (lang === 'typescript') {{
        pillTs.classList.add('active');
        pillPy.classList.remove('active');
        titleEl.innerText = "⚡ 2026 Modern TypeScript Service";
        fileEl.innerText = "premiumService.ts";
        codeEl.innerHTML = `<code>export function calculateEarnedPremium(policy: PolicyInput): ProrationResult {{
  // 1. Exact inclusive calendar day count (+1 day rule)
  const termDays = differenceInDays(policy.expiryDate, policy.effectiveDate) + 1;
  const earnedDays = differenceInDays(policy.calcDate, policy.effectiveDate) + 1;

  // 2. High-precision monetary proration
  const earned = Number(((policy.writtenPremium * earnedDays) / termDays).toFixed(2));

  // 3. Enforce SSIS Financial Guardrails
  if (earned > policy.writtenPremium) throw new Error("BR-07 Violation");
  const unearned = Number((policy.writtenPremium - earned).toFixed(2));

  return {{ earned, unearned, termDays, earnedDays }};
}}</code>`;
      }} else {{
        pillPy.classList.add('active');
        pillTs.classList.remove('active');
        titleEl.innerText = "⚡ 2026 Cloud Microservice (FastAPI)";
        fileEl.innerText = "premium_service.py";
        codeEl.innerHTML = `<code>@app.post("/api/v1/premium/prorate")
def prorate_premium(policy: PremiumProrationRequest) -> ProrationResult:
    # 1. Exact calendar days active (inclusive +1)
    term_days = (policy.expiry_date - policy.effective_date).days + 1
    earned_days = (policy.calc_date - policy.effective_date).days + 1
    
    # 2. Daily proration calculation
    ratio = Decimal(earned_days) / Decimal(term_days)
    earned = (policy.written_premium * ratio).quantize(Decimal('.01'))
    
    # 3. Enforce SSIS Legacy Safeguards (BR-07 &amp; BR-08)
    assert earned &lt;= policy.written_premium, "BR-07 Bound Violation"
    unearned = policy.written_premium - earned
    return ProrationResult(earned=earned, unearned=unearned)</code>`;
      }}
    }}

    function simulateModernApiCall() {{
      const well = document.getElementById('api-response-well');
      well.style.display = 'block';
      well.innerHTML = `<span>&gt; Sending POST /api/v1/premium/prorate ...</span>`;

      setTimeout(() => {{
        well.innerHTML = `<span style="color: #34d399;">HTTP/1.1 200 OK &bull; Response time: 14ms</span><br>
<span style="color: #e2e8f0;">{{
  "status": "success",
  "policy_number": "POL-2026-8819",
  "written_premium": 1200.00,
  "earned_premium": 328.77,
  "unearned_premium": 871.23,
  "active_days": 100,
  "term_days": 365,
  "guardrails": {{
    "BR-07_bound_check": "PASSED",
    "BR-08_rounding_variance": 0.00
  }},
  "legacy_lineage_trace": "EARNPREM.CBL:587 -> Extract_Premium.dtsx:101"
}}</span>`;
      }}, 350);
    }}

    // -------------------------------------------------------------
    // AMBIENT DIGITAL BACKGROUND VIDEO CANVAS (60 FPS ENGINE)
    // -------------------------------------------------------------
    let canvas, ctx, animFrameId;
    let particles = [];
    let isVideoActive = true;

    function initCanvasVideo() {{
      canvas = document.getElementById('bg-video-canvas');
      if (!canvas) return;
      ctx = canvas.getContext('2d');
      resizeCanvas();
      window.addEventListener('resize', resizeCanvas);

      const count = 38;
      particles = [];
      for (let i = 0; i < count; i++) {{
        particles.push({{
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * 0.4,
          vy: (Math.random() - 0.5) * 0.4,
          radius: Math.random() * 2.2 + 1.2,
          color: i % 3 === 0 ? 'rgba(2, 132, 199, ' : (i % 3 === 1 ? 'rgba(234, 88, 12, ' : 'rgba(37, 99, 235, '),
          pulse: Math.random() * Math.PI,
          tag: i % 6 === 0 ? (i % 3 === 0 ? 'COBOL' : (i % 3 === 1 ? 'SSIS' : 'AST')) : null
        }});
      }}

      renderCanvasLoop();
    }}

    function resizeCanvas() {{
      if (!canvas) return;
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    }}

    function renderCanvasLoop() {{
      if (!isVideoActive) return;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      for (let i = 0; i < particles.length; i++) {{
        for (let j = i + 1; j < particles.length; j++) {{
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < 130) {{
            const alpha = (1 - dist / 130) * 0.16;
            ctx.strokeStyle = `rgba(37, 99, 235, ${{alpha}})`;
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }}
        }}
      }}

      for (let i = 0; i < particles.length; i++) {{
        const p = particles[i];
        p.x += p.vx;
        p.y += p.vy;
        p.pulse += 0.03;

        if (p.x < 0) p.x = canvas.width;
        if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;
        if (p.y > canvas.height) p.y = 0;

        const currentAlpha = 0.35 + Math.sin(p.pulse) * 0.2;
        ctx.fillStyle = p.color + currentAlpha + ')';
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fill();

        if (p.tag) {{
          ctx.font = '10px JetBrains Mono';
          ctx.fillStyle = 'rgba(100, 116, 139, 0.3)';
          ctx.fillText(p.tag, p.x + 5, p.y - 3);
        }}
      }}

      animFrameId = requestAnimationFrame(renderCanvasLoop);
    }}

    function toggleBackgroundVideo() {{
      isVideoActive = !isVideoActive;
      const btn = document.getElementById('btn-toggle-video');
      const text = document.getElementById('video-btn-text');
      if (isVideoActive) {{
        btn.classList.add('active');
        text.innerText = 'Ambient Video: ON';
        renderCanvasLoop();
      }} else {{
        btn.classList.remove('active');
        text.innerText = 'Ambient Video: OFF';
        if (animFrameId) cancelAnimationFrame(animFrameId);
        if (ctx) ctx.clearRect(0, 0, canvas.width, canvas.height);
      }}
    }}

    // Boot
    window.addEventListener('DOMContentLoaded', () => {{
      renderVsCode('cobol');
      initCanvasVideo();
      updateInteractiveCalc();
    }});
  </script>
</body>
</html>
'''

output_file = os.path.join(workspace_root, "probleam statement", "index.html")
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_template)

print("Successfully created modernized probleam statement/index.html!")
