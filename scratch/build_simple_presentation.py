import os
import json

# Read the actual source files from the repository
with open('source/mainframe/EARNPREM.CBL', 'r', encoding='utf-8') as f:
    cobol_code = f.read()

with open('source/ssis/packages/Extract_Premium.dtsx', 'r', encoding='utf-8') as f:
    ssis_code = f.read()

with open('source/sql/PolicyCenter_CPP_Breakdown.sql', 'r', encoding='utf-8') as f:
    sql_code = f.read()

source_files = [
    {
        "id": "cobol",
        "title": "EARNPREM.CBL",
        "badge": "Mainframe Batch",
        "path": "source/mainframe/EARNPREM.CBL",
        "age": "30 to 50 Years Old",
        "loc": len(cobol_code.splitlines()),
        "risk": "Original Author Retired 25+ Yrs Ago",
        "engine": "Parsed via KAIRIX Knowledge Extractor",
        "ruleTitle": "Daily Earned Premium Calculation Formula",
        "ruleDesc": "Lines 559–635 contain the core business calculation: WS-EARNED = PRI-WRITTEN-PREMIUM * WS-EARNED-DAYS / WS-TERM-DAYS with leap year handling and unearned adjustments.",
        "ruleStart": 559,
        "ruleEnd": 635,
        "code": cobol_code
    },
    {
        "id": "ssis",
        "title": "Extract_Premium.dtsx",
        "badge": "Microsoft SSIS ETL",
        "path": "source/ssis/packages/Extract_Premium.dtsx",
        "age": "15 to 20 Years Old",
        "loc": len(ssis_code.splitlines()),
        "risk": "External Contractor Team Departed",
        "engine": "Parsed via KAIRIX Pipeline Parser",
        "ruleTitle": "Financial Guardrail Rules BR-07 & BR-08",
        "ruleDesc": "Lines 106–119 enforce critical financial validations: earned_premium <= written_premium (BR-07) and ABS(written - (earned + unearned)) <= 1.00 rounding tolerance.",
        "ruleStart": 106,
        "ruleEnd": 119,
        "code": ssis_code
    },
    {
        "id": "sql",
        "title": "PolicyCenter_CPP_Breakdown.sql",
        "badge": "Guidewire SQL View",
        "path": "source/sql/PolicyCenter_CPP_Breakdown.sql",
        "age": "1,000 to 2,000+ Lines",
        "loc": len(sql_code.splitlines()),
        "risk": "20+ Nested Table Joins & Fragile Views",
        "engine": "Parsed via KAIRIX SQL Logic Parser",
        "ruleTitle": "Multi-Transaction Premium & Cancellation Routing",
        "ruleDesc": "Lines 10–45 handle commercial lines breakdown, transaction type case statements (Submission, Renewal, Cancellation, Reinstatement) and effective date math.",
        "ruleStart": 10,
        "ruleEnd": 45,
        "code": sql_code
    }
]

source_files_json = json.dumps(source_files)

# Build the complete presentation HTML with unified Light Theme, 3 Clean Cards, and Problem/Solution Card
html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>KAIRIX — Enterprise Legacy Code Intelligence</title>
  <link rel="icon" type="image/png" href="kairix_official_logo.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-base: #f8fafc;
      --bg-surface: #ffffff;
      --bg-subtle: #f1f5f9;
      --border-color: #e2e8f0;
      
      --text-main: #0f172a;
      --text-body: #334155;
      --text-muted: #64748b;
      
      --primary: #0284c7;
      --primary-light: #e0f2fe;
      --primary-dark: #0369a1;
      
      --danger: #ef4444;
      --danger-light: #fef2f2;
      --danger-border: #fecaca;
      
      --success: #10b981;
      --success-light: #ecfdf5;
      --success-border: #a7f3d0;
      
      --warning: #f59e0b;
      --warning-light: #fffbeb;
      --warning-border: #fde68a;
      
      --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
      --font-display: 'Outfit', sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
      
      --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.05);
      --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
      --shadow-lg: 0 10px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.04);
      --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.04);
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      background-color: var(--bg-base);
      color: var(--text-body);
      font-family: var(--font-sans);
      line-height: 1.6;
      padding-bottom: 7rem;
      overflow-x: hidden;
    }}

    /* Slower & Silky Cinematic Morph Transitions */
    @keyframes morphIn {{
      0% {{
        opacity: 0;
        transform: translateY(22px) scale(0.985);
        filter: blur(6px);
      }}
      100% {{
        opacity: 1;
        transform: translateY(0) scale(1);
        filter: blur(0);
      }}
    }}

    .screen-view {{
      display: none;
      opacity: 0;
      transform: translateY(22px) scale(0.985);
      transition: opacity 0.75s cubic-bezier(0.16, 1, 0.3, 1), transform 0.75s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    .screen-view.active-screen {{
      display: block;
      opacity: 1;
      transform: translateY(0) scale(1);
      animation: morphIn 0.88s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }}

    body.scroll-mode .screen-view {{
      display: block !important;
      opacity: 1 !important;
      transform: none !important;
      animation: none !important;
      margin-bottom: 5rem;
    }}

    /* Header Bar */
    header.top-header {{
      background: rgba(255, 255, 255, 0.96);
      backdrop-filter: blur(14px);
      border-bottom: 1px solid var(--border-color);
      padding: 0.75rem 2.5rem;
      position: sticky;
      top: 0;
      z-index: 100;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: var(--shadow-sm);
    }}

    .brand-wrap {{
      display: flex;
      align-items: center;
      gap: 0.95rem;
      text-decoration: none;
    }}

    .brand-logo-img {{
      height: 48px;
      width: 48px;
      object-fit: contain;
      border-radius: 10px;
      background: #ffffff;
      padding: 2px;
      border: 1px solid var(--border-color);
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
      display: block;
    }}

    .brand-info h1 {{
      font-family: var(--font-display);
      font-size: 1.25rem;
      font-weight: 800;
      color: var(--text-main);
      line-height: 1.15;
      letter-spacing: -0.01em;
    }}

    .brand-info p {{
      font-size: 0.73rem;
      color: var(--text-muted);
      font-weight: 600;
      letter-spacing: 0.01em;
    }}

    .top-nav {{
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }}

    .screen-nav-btn {{
      padding: 0.5rem 0.9rem;
      border-radius: 8px;
      border: 1px solid transparent;
      background: transparent;
      color: var(--text-body);
      font-size: 0.84rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.25s ease;
      display: flex;
      align-items: center;
      gap: 0.35rem;
    }}

    .screen-nav-btn:hover {{
      background: var(--bg-subtle);
      color: var(--primary);
    }}

    .screen-nav-btn.active {{
      background: var(--primary-light);
      border-color: rgba(2, 132, 199, 0.3);
      color: var(--primary-dark);
      font-weight: 700;
    }}

    .inspector-nav-btn {{
      background: #f0f9ff;
      border: 1px solid rgba(2, 132, 199, 0.35);
      color: var(--primary-dark);
      font-weight: 700;
      margin-left: 0.4rem;
    }}

    .inspector-nav-btn:hover {{
      background: var(--primary);
      color: #ffffff;
    }}

    .mode-toggle-chip {{
      display: flex;
      align-items: center;
      gap: 0.45rem;
      background: var(--bg-subtle);
      border: 1px solid var(--border-color);
      color: var(--text-muted);
      font-size: 0.74rem;
      font-weight: 700;
      padding: 0.4rem 0.85rem;
      border-radius: 999px;
      font-family: var(--font-mono);
      cursor: pointer;
      margin-left: 0.75rem;
      transition: all 0.2s ease;
    }}

    .mode-toggle-chip:hover {{
      border-color: var(--primary);
      color: var(--primary);
    }}

    .pulse-dot {{
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--success);
      animation: pulse 2s infinite;
      display: inline-block;
    }}

    @keyframes pulse {{
      0%, 100% {{ opacity: 1; transform: scale(1); }}
      50% {{ opacity: 0.4; transform: scale(1.2); }}
    }}

    /* Viewport Container */
    main.viewport-container {{
      max-width: 1280px;
      margin: 0 auto;
      padding: 2.5rem 1.5rem;
    }}

    /* Section Headers */
    .sec-head {{
      text-align: center;
      max-width: 860px;
      margin: 0 auto 2.25rem auto;
    }}

    .sec-eyebrow {{
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      background: var(--primary-light);
      color: var(--primary-dark);
      font-family: var(--font-mono);
      font-size: 0.76rem;
      font-weight: 700;
      padding: 0.3rem 0.85rem;
      border-radius: 999px;
      margin-bottom: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}

    .sec-title {{
      font-family: var(--font-display);
      font-size: 2.3rem;
      font-weight: 800;
      color: var(--text-main);
      line-height: 1.2;
      margin-bottom: 0.75rem;
    }}

    .sec-subtitle {{
      font-size: 1.05rem;
      color: var(--text-muted);
      line-height: 1.6;
    }}

    /* =========================================================================
       SHARED CARD STYLES (MATCHING COBOL CARD USER PREFERENCE)
       ========================================================================= */
    .pipeline-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1.25rem;
      margin-bottom: 2rem;
    }}

    .pipeline-grid-3 {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1.35rem;
      margin-bottom: 2.25rem;
    }}

    @media (max-width: 1000px) {{
      .pipeline-grid {{ grid-template-columns: 1fr 1fr; }}
      .pipeline-grid-3 {{ grid-template-columns: 1fr; }}
    }}
    @media (max-width: 600px) {{
      .pipeline-grid {{ grid-template-columns: 1fr; }}
    }}

    .step-card {{
      background: var(--bg-surface);
      border: 2px solid var(--border-color);
      border-radius: 16px;
      padding: 1.75rem 1.5rem;
      display: flex;
      flex-direction: column;
      gap: 0.85rem;
      box-shadow: var(--shadow-sm);
      position: relative;
      cursor: pointer;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    .step-card:hover, .step-card.active {{
      border-color: var(--primary);
      transform: translateY(-4px);
      box-shadow: var(--shadow-lg);
    }}

    .step-card.active {{
      background: #f0f9ff;
    }}

    .step-card-top-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;
    }}

    .step-number-badge {{
      width: 32px;
      height: 32px;
      border-radius: 8px;
      background: var(--primary-light);
      color: var(--primary-dark);
      font-family: var(--font-display);
      font-weight: 800;
      font-size: 0.95rem;
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .layer-badge {{
      display: inline-flex;
      align-items: center;
      padding: 0.32rem 0.8rem;
      border-radius: 8px;
      background: var(--primary-light);
      color: var(--primary-dark);
      border: 1px solid rgba(2, 132, 199, 0.25);
      font-family: var(--font-mono);
      font-weight: 800;
      font-size: 0.74rem;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      white-space: nowrap;
      transition: all 0.25s ease;
    }}

    .step-card.active .layer-badge {{
      background: var(--primary);
      color: #ffffff;
      border-color: var(--primary);
      box-shadow: 0 2px 8px rgba(2, 132, 199, 0.35);
    }}

    .layer-card-icon {{
      font-size: 1.45rem;
      line-height: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      width: 38px;
      height: 38px;
      background: #f8fafc;
      border-radius: 10px;
      border: 1px solid var(--border-color);
      transition: all 0.25s ease;
    }}

    .step-card.active .layer-card-icon,
    .step-card:hover .layer-card-icon {{
      background: #ffffff;
      border-color: rgba(2, 132, 199, 0.35);
      transform: scale(1.08);
    }}

    .step-inspect-pill {{
      font-family: var(--font-mono);
      font-size: 0.72rem;
      font-weight: 700;
      color: var(--primary);
      background: #ffffff;
      border: 1px solid rgba(2, 132, 199, 0.3);
      padding: 0.25rem 0.65rem;
      border-radius: 999px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.3rem;
      transition: all 0.2s ease;
    }}

    .step-inspect-pill:hover {{
      background: var(--primary);
      color: #ffffff;
      border-color: var(--primary);
      transform: scale(1.05);
    }}

    .step-icon {{
      font-size: 2rem;
      margin: 0.25rem 0;
    }}

    .step-card h3 {{
      font-family: var(--font-display);
      font-size: 1.15rem;
      font-weight: 700;
      color: var(--text-main);
      line-height: 1.25;
    }}

    .step-card p {{
      font-size: 0.85rem;
      color: var(--text-body);
      line-height: 1.5;
    }}

    .step-card-footer {{
      margin-top: auto;
      font-family: var(--font-mono);
      font-size: 0.72rem;
      color: var(--primary);
      font-weight: 700;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 0.5rem;
      border-top: 1px solid rgba(0, 0, 0, 0.04);
    }}

    .step-card-footer span.inspect-action {{
      color: var(--primary);
      text-decoration: underline;
      cursor: pointer;
    }}

    /* =========================================================================
       SCREEN 1: TEAM KAIRIX HERO BANNER
       ========================================================================= */
    .team-hero-card {{
      background: var(--bg-surface);
      border: 2px solid var(--border-color);
      border-radius: 18px;
      overflow: hidden;
      box-shadow: var(--shadow-md);
      margin-bottom: 2.75rem;
      transition: all 0.3s ease;
    }}

    .team-hero-card:hover {{
      box-shadow: var(--shadow-lg);
      border-color: rgba(2, 132, 199, 0.35);
    }}

    .team-hero-img {{
      width: 100%;
      height: auto;
      display: block;
      object-fit: cover;
    }}

    /* =========================================================================
       SCREEN 1: VIDEO SHOWCASE SECTION
       ========================================================================= */
    .video-showcase-section {{
      margin-bottom: 2.25rem;
    }}

    .video-card-container {{
      background: var(--bg-surface);
      border: 2px solid var(--border-color);
      border-radius: 16px;
      padding: 1.5rem;
      box-shadow: var(--shadow-md);
      transition: all 0.3s ease;
    }}

    .video-card-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 1.15rem;
      flex-wrap: wrap;
      gap: 0.75rem;
    }}

    .video-header-left {{
      display: flex;
      align-items: center;
      gap: 0.85rem;
      flex-wrap: wrap;
    }}

    .video-pill-badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      padding: 0.28rem 0.75rem;
      border-radius: 999px;
      background: #eff6ff;
      color: #1d4ed8;
      border: 1px solid rgba(29, 78, 216, 0.2);
      font-family: var(--font-mono);
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }}

    .video-section-title {{
      font-family: var(--font-display);
      font-size: 1.18rem;
      font-weight: 800;
      color: var(--text-main);
      line-height: 1.2;
    }}

    .video-upload-btn {{
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      padding: 0.45rem 0.9rem;
      background: var(--bg-subtle);
      border: 1px solid var(--border-color);
      color: var(--text-main);
      border-radius: 8px;
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .video-upload-btn:hover {{
      background: var(--primary);
      color: #ffffff;
      border-color: var(--primary);
    }}

    .video-player-frame {{
      position: relative;
      width: 100%;
      background: #090d16;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.16);
      border: 1px solid rgba(0, 0, 0, 0.12);
      aspect-ratio: 16 / 9;
      max-height: 520px;
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .video-player-frame video {{
      width: 100%;
      height: 100%;
      object-fit: contain;
      display: block;
      background: #000000;
    }}

    .video-player-frame iframe {{
      width: 100%;
      height: 100%;
      border: none;
    }}

    .video-placeholder-overlay {{
      position: absolute;
      inset: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 0.85rem;
      background: radial-gradient(circle at center, rgba(15, 23, 42, 0.72) 0%, rgba(2, 6, 23, 0.94) 100%);
      color: #ffffff;
      text-align: center;
      padding: 1.5rem;
      cursor: pointer;
      transition: all 0.3s ease;
      z-index: 2;
    }}

    .video-placeholder-overlay:hover {{
      background: radial-gradient(circle at center, rgba(15, 23, 42, 0.6) 0%, rgba(2, 6, 23, 0.88) 100%);
    }}

    .play-btn-circle {{
      width: 68px;
      height: 68px;
      border-radius: 50%;
      background: var(--primary);
      color: #ffffff;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 0 0 8px rgba(2, 132, 199, 0.25), 0 8px 20px rgba(2, 132, 199, 0.4);
      transition: all 0.25s ease;
    }}

    .video-placeholder-overlay:hover .play-btn-circle {{
      transform: scale(1.1);
      box-shadow: 0 0 0 12px rgba(2, 132, 199, 0.35), 0 10px 25px rgba(2, 132, 199, 0.5);
    }}

    .play-icon {{
      font-size: 1.6rem;
      margin-left: 4px;
    }}

    .video-placeholder-text {{
      font-size: 0.98rem;
      color: #f1f5f9;
      max-width: 520px;
      line-height: 1.45;
    }}

    .video-placeholder-text code {{
      background: rgba(255, 255, 255, 0.15);
      color: #38bdf8;
      padding: 0.15rem 0.45rem;
      border-radius: 4px;
      font-family: var(--font-mono);
      font-size: 0.85rem;
    }}

    .video-placeholder-sub {{
      font-size: 0.76rem;
      color: #94a3b8;
    }}

    .video-card-footer {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-top: 0.95rem;
      font-size: 0.76rem;
      color: var(--text-muted);
      flex-wrap: wrap;
      gap: 0.5rem;
    }}

    .video-footer-info {{
      display: flex;
      align-items: center;
      gap: 0.45rem;
      font-family: var(--font-mono);
    }}

    .video-link-toggle-btn {{
      background: transparent;
      border: 1px solid var(--border-color);
      color: var(--text-body);
      padding: 0.28rem 0.65rem;
      border-radius: 6px;
      font-size: 0.74rem;
      cursor: pointer;
      font-weight: 600;
      transition: all 0.2s ease;
    }}

    .video-link-toggle-btn:hover {{
      border-color: var(--primary);
      color: var(--primary);
    }}

    /* =========================================================================
       SCREEN 1: QUESTION, PROBLEM & HOW KAIRIX SOLVES IT CARD
       ========================================================================= */
    .hook-banner {{
      background: var(--bg-surface);
      border: 2px solid var(--border-color);
      border-radius: 16px;
      padding: 2.25rem;
      box-shadow: var(--shadow-md);
      display: flex;
      flex-direction: column;
      gap: 1.75rem;
      transition: all 0.3s ease;
    }}

    .hook-banner-top {{
      text-align: center;
      max-width: 900px;
      margin: 0 auto;
    }}

    .hook-question-title {{
      font-family: var(--font-display);
      font-size: 1.6rem;
      font-weight: 800;
      color: var(--text-main);
      line-height: 1.3;
      margin-top: 0.5rem;
    }}

    .hook-columns-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1.5rem;
      align-items: stretch;
    }}

    @media (max-width: 850px) {{
      .hook-columns-grid {{ grid-template-columns: 1fr; }}
    }}

    .hook-col {{
      border-radius: 12px;
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }}

    .hook-col.problem-col {{
      background: #fffcfc;
      border: 1.5px solid var(--danger-border);
    }}

    .hook-col.solution-col {{
      background: #fdfffe;
      border: 1.5px solid var(--success-border);
    }}

    .hook-badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      font-family: var(--font-mono);
      font-size: 0.75rem;
      font-weight: 700;
      padding: 0.3rem 0.7rem;
      border-radius: 6px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}

    .danger-badge {{
      background: var(--danger-light);
      color: var(--danger);
      border: 1px solid var(--danger-border);
    }}

    .success-badge {{
      background: var(--success-light);
      color: var(--success);
      border: 1px solid var(--success-border);
    }}

    .hook-points-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 0.85rem;
    }}

    .hook-points-list li {{
      font-size: 0.88rem;
      color: var(--text-body);
      line-height: 1.55;
    }}

    .hook-points-list li strong {{
      color: var(--text-main);
    }}

    .hook-banner-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 1.5rem;
      padding-top: 1.25rem;
      border-top: 1px solid var(--border-color);
      flex-wrap: wrap;
    }}

    .hook-footer-note {{
      font-size: 0.85rem;
      color: var(--text-muted);
    }}

    .hook-footer-note strong {{
      color: var(--text-main);
    }}

    .hook-cta-btn {{
      background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
      color: #ffffff;
      border: none;
      padding: 0.85rem 1.6rem;
      border-radius: 999px;
      font-size: 0.92rem;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      box-shadow: 0 4px 14px rgba(2, 132, 199, 0.4);
      transition: all 0.25s ease;
      white-space: nowrap;
    }}

    .hook-cta-btn:hover {{
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(2, 132, 199, 0.5);
    }}

    /* =========================================================================
       SCREEN 2: STEP DETAIL BOX (FOR SOLUTION SCREEN)
       ========================================================================= */
    .step-detail-box {{
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 2rem;
      box-shadow: var(--shadow-md);
      display: grid;
      grid-template-columns: 1fr 1.2fr;
      gap: 2rem;
      align-items: stretch;
      margin-bottom: 2rem;
    }}

    @media (max-width: 900px) {{
      .step-detail-box {{ grid-template-columns: 1fr; }}
    }}

    .detail-text {{
      display: flex;
      flex-direction: column;
      justify-content: center;
    }}

    .detail-text h4 {{
      font-family: var(--font-display);
      font-size: 1.35rem;
      font-weight: 800;
      color: var(--text-main);
      margin-bottom: 0.5rem;
    }}

    .detail-text p {{
      font-size: 0.93rem;
      color: var(--text-body);
      line-height: 1.65;
      margin-bottom: 1rem;
    }}

    .detail-bullets {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      margin-bottom: 1.25rem;
    }}

    .detail-bullets li {{
      font-size: 0.88rem;
      color: var(--text-body);
      display: flex;
      align-items: flex-start;
      gap: 0.55rem;
      line-height: 1.45;
    }}

    .detail-bullets li strong {{
      color: var(--text-main);
    }}

    .detail-code-preview-wrap {{
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
      background: #f8fafc;
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 1rem 1.25rem;
      box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.03);
    }}

    .preview-header-bar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-bottom: 0.4rem;
      border-bottom: 1px solid var(--border-color);
    }}

    .preview-badge-pill {{
      font-family: var(--font-mono);
      font-size: 0.74rem;
      font-weight: 700;
      color: var(--primary-dark);
      background: var(--primary-light);
      padding: 0.25rem 0.65rem;
      border-radius: 6px;
    }}

    .detail-code-preview {{
      background: #ffffff;
      border-radius: 8px;
      padding: 1.25rem;
      color: #0f172a;
      font-family: var(--font-mono);
      font-size: 0.85rem;
      line-height: 1.65;
      overflow-y: auto;
      overflow-x: auto;
      border: 1px solid var(--border-color);
      white-space: pre-wrap;
      min-height: 160px;
      max-height: 240px;
      box-shadow: var(--shadow-sm);
    }}

    /* =========================================================================
       SCREEN 3: LIVE QUESTION COMPARISON
       ========================================================================= */
    .question-tabs-row {{
      display: flex;
      gap: 0.75rem;
      justify-content: center;
      margin-bottom: 2rem;
      flex-wrap: wrap;
    }}

    .q-tab-btn {{
      padding: 0.65rem 1.25rem;
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 999px;
      font-size: 0.88rem;
      font-weight: 600;
      color: var(--text-body);
      cursor: pointer;
      transition: all 0.2s ease;
      box-shadow: var(--shadow-sm);
    }}

    .q-tab-btn:hover {{
      border-color: var(--primary);
      color: var(--primary);
    }}

    .q-tab-btn.active {{
      background: var(--primary);
      color: #ffffff;
      border-color: var(--primary);
      box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
    }}

    .comparison-grid {{
      display: grid;
      grid-template-columns: 1fr 1.3fr;
      gap: 2rem;
      align-items: stretch;
      margin-bottom: 2rem;
    }}

    @media (max-width: 900px) {{
      .comparison-grid {{ grid-template-columns: 1fr; }}
    }}

    .compare-side {{
      background: var(--bg-surface);
      border-radius: 16px;
      padding: 2rem;
      box-shadow: var(--shadow-md);
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }}

    .compare-side.old-way {{
      border: 2px solid var(--danger-border);
      background: #fffcfc;
    }}

    .compare-side.kairix-way {{
      border: 2px solid var(--success-border);
      background: #fdfffe;
      position: relative;
    }}

    .side-badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      font-family: var(--font-mono);
      font-size: 0.75rem;
      font-weight: 700;
      padding: 0.25rem 0.65rem;
      border-radius: 6px;
      width: fit-content;
      text-transform: uppercase;
    }}

    .side-badge.danger {{
      background: var(--danger-light);
      color: var(--danger);
      border: 1px solid var(--danger-border);
    }}

    .side-badge.success {{
      background: var(--success-light);
      color: var(--success);
      border: 1px solid var(--success-border);
    }}

    .side-title {{
      font-family: var(--font-display);
      font-size: 1.4rem;
      font-weight: 800;
      color: var(--text-main);
    }}

    .side-items-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 0.85rem;
    }}

    .side-items-list li {{
      font-size: 0.9rem;
      display: flex;
      align-items: flex-start;
      gap: 0.6rem;
      line-height: 1.5;
    }}

    .answer-preview-card {{
      margin-top: auto;
      background: var(--bg-subtle);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 1rem 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 0.4rem;
    }}

    .answer-preview-card.verified {{
      background: #ecfdf5;
      border-color: #a7f3d0;
    }}

    .answer-label {{
      font-family: var(--font-mono);
      font-size: 0.72rem;
      font-weight: 700;
      color: var(--text-muted);
      text-transform: uppercase;
    }}

    .answer-text {{
      font-size: 0.88rem;
      font-weight: 600;
      color: var(--text-main);
    }}

    .citation-tag {{
      font-family: var(--font-mono);
      font-size: 0.74rem;
      color: var(--success);
      font-weight: 700;
    }}

    /* =========================================================================
       SCREEN 4: SYSTEM ARCHITECTURE
       ========================================================================= */
    .arch-simple-flow {{
      display: grid;
      grid-template-columns: 1fr 60px 1.4fr 60px 1fr;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 2.5rem;
    }}

    @media (max-width: 950px) {{
      .arch-simple-flow {{
        grid-template-columns: 1fr;
        text-align: center;
        gap: 1.5rem;
      }}
      .arch-connector {{ transform: rotate(90deg); margin: 0.5rem 0; }}
    }}

    .arch-block {{
      background: var(--bg-surface);
      border: 2px solid var(--border-color);
      border-radius: 16px;
      padding: 1.75rem;
      box-shadow: var(--shadow-md);
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }}

    .arch-block-head {{
      display: flex;
      align-items: center;
      gap: 0.6rem;
    }}

    .arch-block-icon {{
      font-size: 1.75rem;
    }}

    .arch-block-title {{
      font-family: var(--font-display);
      font-size: 1.15rem;
      font-weight: 700;
      color: var(--text-main);
    }}

    .arch-block-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }}

    .arch-block-list li {{
      font-size: 0.85rem;
      background: var(--bg-subtle);
      border: 1px solid var(--border-color);
      padding: 0.45rem 0.75rem;
      border-radius: 6px;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}

    .arch-connector {{
      display: flex;
      justify-content: center;
      font-size: 1.75rem;
      color: var(--primary);
      font-weight: bold;
    }}

    /* Floating Presentation Navigation Bar */
    .presentation-bar {{
      position: fixed;
      bottom: 1.5rem;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(15, 23, 42, 0.92);
      backdrop-filter: blur(16px);
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 999px;
      padding: 0.5rem 1.25rem;
      display: flex;
      align-items: center;
      gap: 1.25rem;
      box-shadow: var(--shadow-xl);
      z-index: 999;
      color: #ffffff;
      transition: all 0.3s ease;
    }}

    .bar-btn {{
      background: rgba(255, 255, 255, 0.12);
      border: none;
      color: #ffffff;
      padding: 0.45rem 1rem;
      border-radius: 999px;
      font-size: 0.84rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.4rem;
      transition: all 0.2s ease;
    }}

    .bar-btn:hover {{
      background: var(--primary);
      transform: translateY(-1px);
    }}

    .bar-indicator {{
      font-family: var(--font-mono);
      font-size: 0.8rem;
      color: #94a3b8;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }}

    .bar-indicator strong {{
      color: #ffffff;
    }}

    /* =========================================================================
       FULL-SCREEN SOURCE FILE INSPECTOR MODAL — CLEAN ENTERPRISE LIGHT THEME
       ========================================================================= */
    .source-modal-backdrop {{
      position: fixed;
      inset: 0;
      z-index: 10000;
      background: rgba(15, 23, 42, 0.55);
      backdrop-filter: blur(8px);
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0.75rem;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.25s ease;
    }}

    .source-modal-backdrop.modal-open {{
      opacity: 1;
      pointer-events: auto;
    }}

    .source-modal-window {{
      background: #ffffff;
      border: 1px solid var(--border-color);
      border-radius: 16px;
      width: 98vw;
      max-width: 1500px;
      height: 96vh;
      display: flex;
      flex-direction: column;
      box-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.25), 0 0 0 1px rgba(0, 0, 0, 0.05);
      overflow: hidden;
      transform: scale(0.99);
      transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    .source-modal-backdrop.modal-open .source-modal-window {{
      transform: scale(1);
    }}

    /* Streamlined Modal Header (50px tall) */
    .source-modal-header {{
      background: #ffffff;
      border-bottom: 1px solid var(--border-color);
      padding: 0.65rem 1.25rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.85rem;
      flex-shrink: 0;
    }}

    .modal-header-brand {{
      display: flex;
      align-items: center;
      gap: 0.65rem;
    }}

    .modal-logo {{
      height: 34px;
      width: 34px;
      object-fit: contain;
      border-radius: 6px;
      background: #ffffff;
      padding: 2px;
      border: 1px solid var(--border-color);
    }}

    .modal-file-title {{
      font-family: var(--font-mono);
      font-size: 0.86rem;
      font-weight: 700;
      color: var(--text-main);
      background: var(--bg-subtle);
      padding: 0.25rem 0.6rem;
      border-radius: 6px;
      border: 1px solid var(--border-color);
    }}

    /* File Switcher Tabs in Header */
    .source-modal-tabs {{
      display: flex;
      gap: 0.35rem;
      background: var(--bg-subtle);
      padding: 0.25rem;
      border-radius: 10px;
      border: 1px solid var(--border-color);
    }}

    .modal-tab-btn {{
      background: transparent;
      border: 1px solid transparent;
      color: var(--text-body);
      padding: 0.35rem 0.85rem;
      border-radius: 8px;
      font-family: var(--font-mono);
      font-size: 0.78rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.35rem;
      transition: all 0.2s ease;
      white-space: nowrap;
    }}

    .modal-tab-btn:hover {{
      color: var(--primary);
      background: #ffffff;
    }}

    .modal-tab-btn.active {{
      background: var(--primary);
      color: #ffffff;
      font-weight: 700;
      box-shadow: 0 2px 6px rgba(2, 132, 199, 0.3);
    }}

    /* Header Controls */
    .modal-header-actions {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}

    .subbar-search-box {{
      display: flex;
      align-items: center;
      gap: 0.35rem;
      background: var(--bg-subtle);
      border: 1px solid var(--border-color);
      padding: 0.3rem 0.65rem;
      border-radius: 8px;
      color: var(--text-body);
      font-size: 0.76rem;
      transition: all 0.2s ease;
    }}

    .subbar-search-box:focus-within {{
      border-color: var(--primary);
      background: #ffffff;
      box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.1);
    }}

    .subbar-search-box input {{
      background: transparent;
      border: none;
      outline: none;
      color: var(--text-main);
      font-family: var(--font-mono);
      font-size: 0.76rem;
      width: 170px;
    }}

    .match-count-badge {{
      font-family: var(--font-mono);
      font-size: 0.68rem;
      color: var(--primary);
      font-weight: 700;
    }}

    .modal-action-btn {{
      background: #ffffff;
      border: 1px solid var(--border-color);
      color: var(--text-body);
      padding: 0.35rem 0.75rem;
      border-radius: 8px;
      font-family: var(--font-mono);
      font-size: 0.76rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.35rem;
      transition: all 0.2s ease;
    }}

    .modal-action-btn:hover {{
      background: var(--bg-subtle);
      border-color: var(--primary);
      color: var(--primary);
    }}

    .rule-jump-btn {{
      background: #fffbeb;
      border-color: #fde68a;
      color: #b45309;
      font-weight: 700;
    }}

    .rule-jump-btn:hover {{
      background: #f59e0b;
      color: #ffffff;
      border-color: #f59e0b;
    }}

    .modal-close-btn {{
      background: #fef2f2;
      border: 1px solid #fecaca;
      color: #ef4444;
      width: 32px;
      height: 32px;
      border-radius: 8px;
      font-size: 1rem;
      font-weight: bold;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .modal-close-btn:hover {{
      background: #ef4444;
      color: #ffffff;
      transform: scale(1.05);
    }}

    /* Compact Context & Rule Strip (Only 34px tall!) */
    .source-modal-subbar {{
      background: #f8fafc;
      border-bottom: 1px solid var(--border-color);
      padding: 0.35rem 1.25rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      flex-shrink: 0;
      font-size: 0.74rem;
    }}

    .subbar-left {{
      display: flex;
      align-items: center;
      gap: 0.45rem;
      flex-wrap: wrap;
    }}

    .subbar-tag {{
      font-family: var(--font-mono);
      font-size: 0.72rem;
      font-weight: 600;
      color: var(--text-muted);
      background: #ffffff;
      padding: 0.15rem 0.5rem;
      border-radius: 5px;
      border: 1px solid var(--border-color);
    }}

    .subbar-tag.tag-loc {{
      color: var(--primary-dark);
      background: var(--primary-light);
      border-color: rgba(2, 132, 199, 0.25);
      font-weight: 700;
    }}

    .subbar-tag.tag-risk {{
      color: #b91c1c;
      background: #fef2f2;
      border-color: #fecaca;
    }}

    .subbar-rule-indicator {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      cursor: pointer;
      color: #78350f;
      background: #fef3c7;
      border: 1px solid #fde68a;
      padding: 0.2rem 0.65rem;
      border-radius: 6px;
      font-family: var(--font-mono);
      font-size: 0.72rem;
      transition: all 0.2s ease;
    }}

    .subbar-rule-indicator:hover {{
      background: #fde68a;
      border-color: #f59e0b;
    }}

    .subbar-rule-indicator strong {{
      color: #92400e;
    }}

    .jump-pill {{
      background: #f59e0b;
      color: #ffffff;
      font-weight: 700;
      padding: 0.1rem 0.4rem;
      border-radius: 4px;
      font-size: 0.68rem;
    }}

    /* EXPANSIVE CODE AREA (Occupies 90%+ of Window!) */
    .source-modal-body {{
      flex: 1;
      overflow-y: auto;
      overflow-x: auto;
      background: #ffffff;
      position: relative;
    }}

    .code-gutter-and-lines {{
      display: table;
      width: 100%;
      font-family: var(--font-mono);
      font-size: 0.86rem;
      line-height: 1.65;
      padding: 0.75rem 0;
    }}

    .code-row {{
      display: table-row;
      transition: background 0.15s ease;
    }}

    .code-row:hover {{
      background: #f1f5f9;
    }}

    .code-row.highlight-rule-line {{
      background: #fef9c3 !important;
    }}

    .code-row.search-match {{
      background: #e0f2fe !important;
    }}

    .line-num {{
      display: table-cell;
      width: 60px;
      min-width: 60px;
      text-align: right;
      padding-right: 1.25rem;
      padding-left: 0.75rem;
      color: #94a3b8;
      background: #f8fafc;
      user-select: none;
      vertical-align: top;
      border-right: 1px solid var(--border-color);
      font-weight: 500;
    }}

    .code-row.highlight-rule-line .line-num {{
      color: #b45309;
      background: #fef08a;
      font-weight: 800;
    }}

    .line-content {{
      display: table-cell;
      padding-left: 1.25rem;
      padding-right: 2rem;
      color: var(--text-main);
      white-space: pre;
      position: relative;
    }}

    .code-row.highlight-rule-line .line-content {{
      border-left: 3px solid #f59e0b;
      color: #78350f;
    }}

    .rule-tag-badge {{
      display: inline-block;
      margin-left: 1.5rem;
      font-size: 0.7rem;
      font-weight: 800;
      background: #f59e0b;
      color: #ffffff;
      padding: 0.15rem 0.55rem;
      border-radius: 4px;
      vertical-align: middle;
      box-shadow: 0 1px 3px rgba(245, 158, 11, 0.3);
    }}

    /* Light Theme Syntax Colors */
    .syn-comment {{ color: #64748b; font-style: italic; }}
    .syn-kw {{ color: #0284c7; font-weight: 700; }}
    .syn-str {{ color: #059669; }}
    .syn-num {{ color: #d97706; font-weight: 600; }}
    .syn-tag {{ color: #4f46e5; font-weight: 700; }}
    .syn-attr {{ color: #7c3aed; }}
    .syn-var {{ color: #db2777; font-weight: 600; }}

    /* Streamlined Modal Footer (34px tall) */
    .source-modal-footer {{
      background: #f8fafc;
      border-top: 1px solid var(--border-color);
      padding: 0.4rem 1.25rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      flex-shrink: 0;
      font-size: 0.74rem;
    }}

    .footer-left-status {{
      font-family: var(--font-mono);
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}

    .footer-nav-shortcuts {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}

    .footer-step-btn {{
      background: #ffffff;
      border: 1px solid var(--border-color);
      color: var(--text-body);
      padding: 0.25rem 0.65rem;
      border-radius: 6px;
      font-family: var(--font-mono);
      font-size: 0.72rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .footer-step-btn:hover {{
      background: var(--primary);
      color: #ffffff;
      border-color: var(--primary);
    }}

    .key-hint {{
      font-family: var(--font-mono);
      font-size: 0.7rem;
      color: var(--text-muted);
    }}

    .key-hint kbd {{
      background: #ffffff;
      border: 1px solid var(--border-color);
      color: var(--text-main);
      padding: 0.1rem 0.35rem;
      border-radius: 4px;
      font-size: 0.68rem;
    }}

    /* Footer */
    footer.page-footer {{
      text-align: center;
      margin-top: 4rem;
      padding: 2rem 1rem;
      color: var(--text-muted);
      font-size: 0.82rem;
      border-top: 1px solid var(--border-color);
    }}
  </style>
</head>
<body>

  <!-- TOP HEADER -->
  <header class="top-header">
    <a href="#" class="brand-wrap">
      <img src="kairix_official_logo.png" alt="KAIRIX Logo" class="brand-logo-img">
      <div class="brand-info">
        <h1>KAIRIX</h1>
        <p>Value in Every Idea. Momentum in Every Step.</p>
      </div>
    </a>

    <nav class="top-nav">
      <button class="screen-nav-btn active" onclick="morphToScreen(0)">
        <span>1.</span> The Challenge
      </button>
      <button class="screen-nav-btn" onclick="morphToScreen(1)">
        <span>2.</span> The 4 Layers
      </button>
      <button class="screen-nav-btn" onclick="morphToScreen(2)">
        <span>3.</span> Live Question Demo
      </button>
      <button class="screen-nav-btn" onclick="morphToScreen(3)">
        <span>4.</span> Architecture
      </button>

      <button class="screen-nav-btn inspector-nav-btn" onclick="openSourceInspector(0)" title="Open Full Screen Source File Viewer">
        <span>⛶</span> Inspect Source
      </button>

      <div class="mode-toggle-chip" onclick="togglePresentationMode()">
        <span class="pulse-dot"></span>
        <span id="mode-label">Screen Mode</span>
      </div>
    </nav>
  </header>

  <main class="viewport-container">

    <!-- =========================================================================
         SCREEN 1: THE 3 REAL CODE ARTIFACTS + PROBLEM & HOW KAIRIX SOLVES IT
         ========================================================================= -->
    <section class="screen-view active-screen" id="screen-0">

      <!-- 1. TEAM KAIRIX HERO BANNER (FIRST DISPLAYED ON SCREEN 1) -->
      <div class="team-hero-card">
        <img src="kairix_team_hero.png" alt="Team KAIRIX — Value in every idea, momentum in every step" class="team-hero-img">
      </div>

      <div class="sec-head">
        <div class="sec-eyebrow">The Real Problem</div>
        <h2 class="sec-title">3 Generations of Code. 1 Business Question.</h2>
        <p class="sec-subtitle">
          To understand why legacy reverse-engineering is broken, look at the actual source files running the business today:
        </p>
      </div>

      <!-- Exactly 3 Step Cards matching COBOL Card Style -->
      <div class="pipeline-grid-3">
        <!-- Artifact 1: COBOL -->
        <div class="step-card active" onclick="openSourceInspector(0, event)">
          <div class="step-card-top-row">
            <div class="step-number-badge">1</div>
            <button class="step-inspect-pill" onclick="openSourceInspector(0, event)" title="View full 691 lines of EARNPREM.CBL in fullscreen">
              <span>⛶</span> Inspect File
            </button>
          </div>
          <div class="step-icon">📜</div>
          <h3>Mainframe COBOL Batch</h3>
          <p>Built 30 to 50 years ago (<code>EARNPREM.CBL</code>). Runs critical daily earned premium calculations, but original authors retired decades ago.</p>
          <div class="step-card-footer">
            <span>⏳ Built 30 to 50 Years Ago</span>
            <span class="inspect-action" onclick="openSourceInspector(0, event)">Full Code &rarr;</span>
          </div>
        </div>

        <!-- Artifact 2: SSIS -->
        <div class="step-card" onclick="openSourceInspector(1, event)">
          <div class="step-card-top-row">
            <div class="step-number-badge">2</div>
            <button class="step-inspect-pill" onclick="openSourceInspector(1, event)" title="View full 198 lines of Extract_Premium.dtsx in fullscreen">
              <span>⛶</span> Inspect File
            </button>
          </div>
          <div class="step-icon">🔀</div>
          <h3>Microsoft SSIS ETL</h3>
          <p>Built 15 to 20 years ago (<code>Extract_Premium.dtsx</code>). Enforces critical financial rules buried inside thousands of lines of pipeline XML.</p>
          <div class="step-card-footer">
            <span>⏳ Built 15 to 20 Years Ago</span>
            <span class="inspect-action" onclick="openSourceInspector(1, event)">Full Code &rarr;</span>
          </div>
        </div>

        <!-- Artifact 3: SQL -->
        <div class="step-card" onclick="openSourceInspector(2, event)">
          <div class="step-card-top-row">
            <div class="step-number-badge">3</div>
            <button class="step-inspect-pill" onclick="openSourceInspector(2, event)" title="View full 267 lines of PolicyCenter_CPP_Breakdown.sql in fullscreen">
              <span>⛶</span> Inspect File
            </button>
          </div>
          <div class="step-icon">🗄️</div>
          <h3>Guidewire SQL Views</h3>
          <p>Spans 1,000 to 2,000+ lines (<code>PolicyCenter_CPP_Breakdown.sql</code>) with 20+ joins. Fragile dependencies make manual verification painful.</p>
          <div class="step-card-footer">
            <span>⏳ 1,000 to 2,000+ Lines</span>
            <span class="inspect-action" onclick="openSourceInspector(2, event)">Full Code &rarr;</span>
          </div>
        </div>
      </div>

      <!-- =========================================================================
           VIDEO WALKTHROUGH SECTION (PERMANENTLY EMBEDDED)
           ========================================================================= -->
      <div class="video-showcase-section">
        <div class="video-card-container">
          <div class="video-card-header">
            <div class="video-header-left">
              <span class="video-pill-badge">🎬 Product Demo</span>
              <h3 class="video-section-title">See the Legacy Reverse Engineering in Action</h3>
            </div>
            <div class="video-header-actions">
              <span class="video-duration-pill" style="font-family: var(--font-mono); font-size: 0.74rem; font-weight: 700; color: var(--primary-dark); background: var(--primary-light); padding: 0.3rem 0.7rem; border-radius: 6px;">▶ Click to Play</span>
            </div>
          </div>

          <div class="video-player-frame" id="video-frame">
            <video id="screen1-video-player" controls preload="auto" poster="kairix_official_logo.png" style="width: 100%; height: 100%; object-fit: contain; background: #0b0f19;">
              <source src="kairix_demo.mp4" type="video/mp4">
              Your browser does not support HTML5 video.
            </video>
          </div>

          <div class="video-card-footer">
            <div class="video-footer-info">
              <span class="pulse-dot"></span>
              <span id="video-status-text">Video ready • <code>kairix_demo.mp4</code> (8.7 MB HD)</span>
            </div>
            <div class="video-footer-controls">
              <label for="video-file-input" class="video-link-toggle-btn" style="cursor: pointer;" title="Change to another video file">
                <span>📁</span> Change Video
              </label>
              <input type="file" id="video-file-input" accept="video/*" style="display: none;" onchange="loadLocalVideo(event)">
            </div>
          </div>
        </div>
      </div>

      <!-- QUESTION, PROBLEM IN THAT, & HOW KAIRIX SOLVES IT CARD -->
      <div class="hook-banner">
        <div class="hook-banner-top">
          <div class="sec-eyebrow">🚨 The Central Business Question</div>
          <h3 class="hook-question-title">"Where does this Earned Premium calculation come from, and which rule validates it?"</h3>
        </div>

        <div class="hook-columns-grid">
          <!-- The Problem Today -->
          <div class="hook-col problem-col">
            <div class="hook-col-header">
              <span class="hook-badge danger-badge">❌ The Problem Today (Manual Nightmare)</span>
            </div>
            <ul class="hook-points-list">
              <li>
                <strong>⏳ 3 to 4 Weeks of Manual Digging:</strong> Engineers must manually comb through 50-year-old COBOL batch files, decipher SSIS pipelines, and trace 1,500 lines of nested SQL joins.
              </li>
              <li>
                <strong>👤 Zero Living Context:</strong> Original developers retired decades ago; zero living documentation exists to explain hidden calculations or business rules.
              </li>
              <li>
                <strong>💸 High Consultant Costs & Guesswork:</strong> Enterprises spend tens of thousands on contractors, and still risk deploying breaking changes based on inaccurate assumptions.
              </li>
            </ul>
          </div>

          <!-- How KAIRIX Solves It -->
          <div class="hook-col solution-col">
            <div class="hook-col-header">
              <span class="hook-badge success-badge">⚡ How KAIRIX Solves It</span>
            </div>
            <ul class="hook-points-list">
              <li>
                <strong>🚀 Automated Verified Answers:</strong> KAIRIX translates business questions into direct code analysis, answering in under a minute instead of 3 to 4 weeks.
              </li>
              <li>
                <strong>🎯 100% Precise Code Citations:</strong> Pins every answer directly to exact source files and line numbers (e.g. <code>EARNPREM.CBL</code> lines 559–635 and SSIS <code>Rule BR-07</code>).
              </li>
              <li>
                <strong>🌉 Automated Cross-System Connections:</strong> Discovers and maps how mainframe batch feeds into SSIS staging and SQL views without altering any system.
              </li>
            </ul>
          </div>
        </div>

        <div class="hook-banner-footer">
          <div class="hook-footer-note">
            💡 <strong>Zero System Disruption:</strong> Safely reads code without changing any of your live databases or running systems.
          </div>
          <button class="hook-cta-btn" onclick="morphToScreen(1)">
            Explore the 4-Layer Solution <span>➔</span>
          </button>
        </div>
      </div>
    </section>

    <!-- =========================================================================
         SCREEN 2: THE 4-LAYER SOLUTION (LAYER 1, 2, 3, 4)
         ========================================================================= -->
    <section class="screen-view" id="screen-1">
      <div class="sec-head">
        <div class="sec-eyebrow">The 4-Layer Architecture</div>
        <h2 class="sec-title">From Codebase Chaos to Instant Answers</h2>
        <p class="sec-subtitle">
          KAIRIX processes legacy software through 4 intelligent layers to deliver verified, line-by-line business answers:
        </p>
      </div>

      <div class="pipeline-grid">
        <!-- Layer 1 -->
        <div class="step-card active" onclick="selectStep(0, this)">
          <div class="step-card-top-row">
            <span class="layer-badge">Layer 1</span>
            <span class="layer-card-icon">📥</span>
          </div>
          <h3>Code Artifacts</h3>
          <p>Collects your COBOL programs, SSIS packages, and complex SQL views without changing your systems.</p>
          <div class="step-card-footer"><span>Zero System Disruption &rarr;</span></div>
        </div>

        <!-- Layer 2 -->
        <div class="step-card" onclick="selectStep(1, this)">
          <div class="step-card-top-row">
            <span class="layer-badge">Layer 2</span>
            <span class="layer-card-icon">🌲</span>
          </div>
          <h3>Knowledge Engineering Agent</h3>
          <p>Pulls out exact business calculations, rules, and guardrails directly from code—with 100% accuracy.</p>
          <div class="step-card-footer"><span>Line-by-Line Truth &rarr;</span></div>
        </div>

        <!-- Layer 3 -->
        <div class="step-card" onclick="selectStep(2, this)">
          <div class="step-card-top-row">
            <span class="layer-badge">Layer 3</span>
            <span class="layer-card-icon">🧠</span>
          </div>
          <h3>Relationship Agent</h3>
          <p>Maps how data and logic flow between COBOL, SSIS, and SQL, linking related rules across files.</p>
          <div class="step-card-footer"><span>Connected Memory &rarr;</span></div>
        </div>

        <!-- Layer 4 -->
        <div class="step-card" onclick="selectStep(3, this)">
          <div class="step-card-top-row">
            <span class="layer-badge">Layer 4</span>
            <span class="layer-card-icon">💬</span>
          </div>
          <h3>Investigation Agent</h3>
          <p>Ask questions in plain English and get clear answers backed by exact source files and line numbers.</p>
          <div class="step-card-footer"><span>Instant Plain English &rarr;</span></div>
        </div>
      </div>

      <div class="step-detail-box" id="step-detail-panel">
        <div class="detail-text">
          <h4 id="detail-title">Layer 1: Code Artifacts (Automated Source Ingestion)</h4>
          <p id="detail-desc">
            KAIRIX scans your codebase across systems, including mainframe COBOL files (.cbl), Microsoft SSIS packages (.dtsx), and database SQL views (.sql).
          </p>
          <ul class="detail-bullets" id="detail-bullets">
            <li><span>✔</span> <div>Scans different legacy file types into one unified catalog</div></li>
            <li><span>✔</span> <div>Zero changes to your live databases or running systems</div></li>
            <li><span>✔</span> <div>Smart scanning that automatically detects what was updated</div></li>
          </ul>
        </div>
        <div class="detail-code-preview-wrap">
          <div class="preview-header-bar">
            <span class="preview-badge-pill">Discovery Output</span>
          </div>
          <div class="detail-code-preview" id="detail-preview">// Discovered Legacy Assets:
[COBOL]  source/mainframe/EARNPREM.CBL (Rating Logic)
[SSIS]   source/ssis/packages/Extract_Premium.dtsx (Data Pipeline)
[SQL]    source/sql/PolicyCenter_CPP_Breakdown.sql (Reporting Logic)
// Status: Files scanned successfully. Ready to extract knowledge.</div>
        </div>
      </div>
    </section>

    <!-- =========================================================================
         SCREEN 3: LIVE BUSINESS QUESTION (CLEAN BEFORE VS AFTER)
         ========================================================================= -->
    <section class="screen-view" id="screen-2">
      <div class="sec-head">
        <div class="sec-eyebrow">Real-World Demo</div>
        <h2 class="sec-title">What Happens When You Ask a Business Question?</h2>
        <p class="sec-subtitle">
          Select a common business question below and see the difference between weeks of manual reverse-engineering and KAIRIX:
        </p>
      </div>

      <div class="question-tabs-row">
        <button class="q-tab-btn active" onclick="selectQuestion(0, this)">
          "Where is Earned Premium calculated?"
        </button>
        <button class="q-tab-btn" onclick="selectQuestion(1, this)">
          "Which rules check for negative premium?"
        </button>
        <button class="q-tab-btn" onclick="selectQuestion(2, this)">
          "How are policy cancellations handled?"
        </button>
      </div>

      <div class="comparison-grid" id="comp-grid">
        <!-- Without KAIRIX -->
        <div class="compare-side old-way">
          <div class="side-badge danger">Traditional Manual Way</div>
          <div class="side-title">Without KAIRIX</div>
          <ul class="side-items-list" id="old-items">
            <li>⏳ <strong>3 to 4 Weeks</strong> of manual file hunting across unfamiliar code.</li>
            <li>👤 <strong>Zero Developer Context:</strong> Code author retired; nobody knows the rationale.</li>
            <li>🔍 <strong>Multi-Language Blindspot:</strong> Engineers miss the link between COBOL batch and SSIS ETL.</li>
            <li>💸 <strong>High Cost:</strong> Heavy expenditure in external legacy consultants and developer hours.</li>
          </ul>
          <div class="answer-preview-card">
            <span class="answer-label">Result</span>
            <span class="answer-text" id="old-result">"We think it is calculated somewhere in the batch job, but we are still verifying."</span>
          </div>
        </div>

        <!-- With KAIRIX -->
        <div class="compare-side kairix-way">
          <div class="side-badge success">The KAIRIX Advantage</div>
          <div class="side-title">With KAIRIX Code Intelligence</div>
          <ul class="side-items-list" id="new-items">
            <li>⚡ <strong>Answered in Under a Minute:</strong> Instant automated search across connected systems.</li>
            <li>🎯 <strong>100% Verified Citations:</strong> Points directly to file and exact line numbers.</li>
            <li>🌉 <strong>Full End-to-End Connections:</strong> Shows how COBOL feeds into SSIS staging and SQL views.</li>
            <li>💰 <strong>Zero Consultant Fees:</strong> Completely automated reverse-engineering.</li>
          </ul>
          <div class="answer-preview-card verified">
            <span class="answer-label">Verified Answer</span>
            <span class="answer-text" id="new-result">
              Calculated in <strong>EARNPREM.CBL</strong> (Lines 214-238) using formula: <code>WS-TOTAL-PREMIUM * (WS-DAYS-RUN / WS-TOTAL-DAYS)</code>, then validated by SSIS <strong>Rule BR-07</strong> in <code>Extract_Premium.dtsx</code>.
            </span>
            <span class="citation-tag" id="new-citation">✔ Verified in source code & system connections</span>
          </div>
        </div>
      </div>
    </section>

    <!-- =========================================================================
         SCREEN 4: SYSTEM ARCHITECTURE (PREVIOUS 3 CONNECTED BLOCKS)
         ========================================================================= -->
    <section class="screen-view" id="screen-3">
      <div class="sec-head">
        <div class="sec-eyebrow">System Architecture</div>
        <h2 class="sec-title">Clean, Jargon-Free Architecture</h2>
        <p class="sec-subtitle">
          How raw legacy code transforms into instant business intelligence:
        </p>
      </div>

      <div class="arch-simple-flow">
        <!-- Block 1 -->
        <div class="arch-block">
          <div class="arch-block-head">
            <span class="arch-block-icon">📁</span>
            <div class="arch-block-title">1. Legacy Code</div>
          </div>
          <ul class="arch-block-list">
            <li>📜 Mainframe COBOL (Rating)</li>
            <li>🔀 SSIS ETL Packages (Rules)</li>
            <li>🗄️ Guidewire SQL Views</li>
          </ul>
        </div>

        <div class="arch-connector">&rarr;</div>

        <!-- Block 2 -->
        <div class="arch-block" style="border-color: var(--primary);">
          <div class="arch-block-head">
            <span class="arch-block-icon">🧠</span>
            <div class="arch-block-title">2. KAIRIX Intelligent Brain</div>
          </div>
          <ul class="arch-block-list">
            <li>🌲 <strong>Knowledge Extraction:</strong> Extracts exact formulas & rules</li>
            <li>🕸️ <strong>Relationship Map:</strong> Connects files across systems</li>
            <li>🎯 <strong>Smart Search:</strong> Fast natural-language code lookup</li>
            <li>⚡ <strong>Fact Verification:</strong> Validates answers against source code</li>
          </ul>
        </div>

        <div class="arch-connector">&rarr;</div>

        <!-- Block 3 -->
        <div class="arch-block" style="border-color: var(--success-border);">
          <div class="arch-block-head">
            <span class="arch-block-icon">🚀</span>
            <div class="arch-block-title">3. Verified Outputs</div>
          </div>
          <ul class="arch-block-list">
            <li>💬 Plain English Business Answers</li>
            <li>📍 Line-by-Line Code Citations</li>
            <li>🌐 Visual System Map</li>
            <li>☁️ Ready for Modernization</li>
          </ul>
        </div>
      </div>
    </section>

  </main>

  <!-- =========================================================================
       FULL-SCREEN SOURCE FILE INSPECTOR MODAL — EXPANSIVE LIGHT THEME
       ========================================================================= -->
  <div class="source-modal-backdrop" id="source-inspector-modal" onclick="handleBackdropClick(event)">
    <div class="source-modal-window">
      
      <!-- Compact Streamlined Header -->
      <div class="source-modal-header">
        <div class="modal-header-brand">
          <img src="kairix_official_logo.png" alt="KAIRIX Logo" class="modal-logo">
          <span class="modal-file-title" id="modal-filename-title">source/mainframe/EARNPREM.CBL</span>
        </div>

        <!-- File Switcher Tabs -->
        <div class="source-modal-tabs">
          <button class="modal-tab-btn active" id="modal-tab-0" onclick="switchInspectorFile(0)">
            <span>📜</span> EARNPREM.CBL (691 LOC)
          </button>
          <button class="modal-tab-btn" id="modal-tab-1" onclick="switchInspectorFile(1)">
            <span>🔀</span> Extract_Premium.dtsx (198 LOC)
          </button>
          <button class="modal-tab-btn" id="modal-tab-2" onclick="switchInspectorFile(2)">
            <span>🗄️</span> PolicyCenter_CPP.sql (267 LOC)
          </button>
        </div>

        <!-- Modal Controls -->
        <div class="modal-header-actions">
          <div class="subbar-search-box">
            <span>🔍</span>
            <input type="text" id="inspector-search-input" placeholder="Search code..." oninput="handleInspectorSearch()">
            <span id="inspector-match-count" class="match-count-badge"></span>
          </div>

          <button class="modal-action-btn rule-jump-btn" onclick="jumpToCriticalRule()" title="Jump to the critical business rule">
            <span>⚡</span> Jump to Rule
          </button>
          <button class="modal-action-btn" id="modal-copy-btn" onclick="copyCurrentFileCode()" title="Copy entire file to clipboard">
            <span>📋</span> Copy Code
          </button>
          <button class="modal-close-btn" onclick="closeSourceInspector()" title="Close Inspector (Esc)">
            ✕
          </button>
        </div>
      </div>

      <!-- Slim Metadata & Rule Strip -->
      <div class="source-modal-subbar">
        <div class="subbar-left">
          <span class="subbar-tag" id="subbar-age-tag">⏳ Age: 30 to 50 Years</span>
          <span class="subbar-tag tag-loc" id="subbar-loc-tag">📏 691 Lines</span>
          <span class="subbar-tag tag-risk" id="subbar-risk-tag">⚠️ Author Retired Decades Ago</span>
        </div>
        <div class="subbar-rule-indicator" onclick="jumpToCriticalRule()" title="Click to scroll directly to the highlighted rule lines">
          <span>🎯</span>
          <span>Target: <strong id="callout-title">Daily Earned Premium Formula</strong> (Lines <span id="callout-range">559–635</span>)</span>
          <span class="jump-pill">Jump ↓</span>
        </div>
      </div>

      <!-- Massive Code Area (90%+ of height!) -->
      <div class="source-modal-body" id="source-modal-scroll-area">
        <div class="code-gutter-and-lines" id="modal-code-container">
          <!-- Dynamically populated line by line -->
        </div>
      </div>

      <!-- Slim Footer -->
      <div class="source-modal-footer">
        <div class="footer-left-status">
          <span class="pulse-dot"></span>
          <span id="modal-footer-status">Viewing source/mainframe/EARNPREM.CBL • Full raw enterprise source file</span>
        </div>
        <div class="footer-nav-shortcuts">
          <button class="footer-step-btn" onclick="prevInspectorFile()">◀ Prev File</button>
          <span class="key-hint"><kbd>1</kbd> COBOL</span>
          <span class="key-hint"><kbd>2</kbd> SSIS</span>
          <span class="key-hint"><kbd>3</kbd> SQL</span>
          <span class="key-hint"><kbd>Esc</kbd> Close</span>
          <button class="footer-step-btn" onclick="nextInspectorFile()">Next File ▶</button>
        </div>
      </div>

    </div>
  </div>

  <!-- FLOATING PRESENTATION CONTROLLER -->
  <div class="presentation-bar" id="presentation-controller">
    <button class="bar-btn" onclick="prevScreen()">
      <span>◀</span> Prev
    </button>
    <div class="bar-indicator">
      Screen <strong id="bar-current-idx">1</strong> of 4: <strong id="bar-screen-name" style="color:#ffffff;">The Challenge</strong>
    </div>
    <button class="bar-btn" onclick="nextScreen()">
      Next <span>▶</span>
    </button>
  </div>

  <footer class="page-footer">
    <div style="font-weight: 700; color: var(--text-main); margin-bottom: 0.35rem; display: flex; align-items: center; justify-content: center; gap: 0.65rem;">
      <img src="kairix_official_logo.png" alt="KAIRIX Logo" style="height: 28px; width: 28px; border-radius: 6px; object-fit: contain; background: #ffffff; padding: 2px; border: 1px solid var(--border-color);">
      <span>KAIRIX — Value in Every Idea. Momentum in Every Step.</span>
    </div>
    <p>Enterprise Legacy Code Intelligence & Automated Reverse Engineering Platform</p>
  </footer>

  <script>
    /* EMBEDDED REAL SOURCE FILES FROM WORKSPACE */
    const sourceFilesData = {source_files_json};

    /* 1. SMOOTH MORPH TRANSITION HELPER */
    function smoothMorph(element, updateCallback, duration = 380) {{
      if (!element) {{
        updateCallback();
        return;
      }}
      element.style.transition = 'opacity 0.38s cubic-bezier(0.16, 1, 0.3, 1), transform 0.38s cubic-bezier(0.16, 1, 0.3, 1), filter 0.38s ease';
      element.style.opacity = '0';
      element.style.transform = 'translateY(12px) scale(0.985)';
      element.style.filter = 'blur(3px)';

      setTimeout(() => {{
        updateCallback();
        element.style.opacity = '1';
        element.style.transform = 'translateY(0) scale(1)';
        element.style.filter = 'blur(0)';
      }}, duration);
    }}

    /* 2. SCREEN SWITCHING WITH GENTLE MORPH TIMINGS */
    const screenNames = [
      "The Challenge (Manual Pain)",
      "The 4-Step Solution",
      "Live Question Demo",
      "System Architecture"
    ];

    let currentScreenIdx = 0;
    let isPresentationMode = true;
    let isScreenTransitioning = false;

    function morphToScreen(targetIdx) {{
      if (isScreenTransitioning) return;
      if (targetIdx === currentScreenIdx && isPresentationMode) return;

      const outgoingScreen = document.getElementById(`screen-${{currentScreenIdx}}`);
      const incomingScreen = document.getElementById(`screen-${{targetIdx}}`);

      // Update Nav Buttons
      document.querySelectorAll('.screen-nav-btn').forEach((b, idx) => {{
        if (idx === targetIdx) b.classList.add('active');
        else b.classList.remove('active');
      }});

      if (!isPresentationMode) {{
        if (incomingScreen) incomingScreen.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        currentScreenIdx = targetIdx;
        return;
      }}

      isScreenTransitioning = true;

      // Smooth Morph Switch - Relaxed Dissolve Out
      if (outgoingScreen) {{
        outgoingScreen.style.transition = 'opacity 0.52s cubic-bezier(0.16, 1, 0.3, 1), transform 0.52s cubic-bezier(0.16, 1, 0.3, 1), filter 0.52s ease';
        outgoingScreen.style.opacity = '0';
        outgoingScreen.style.transform = 'translateY(-16px) scale(0.985)';
        outgoingScreen.style.filter = 'blur(4px)';
      }}

      setTimeout(() => {{
        if (outgoingScreen) {{
          outgoingScreen.classList.remove('active-screen');
          outgoingScreen.style.opacity = '';
          outgoingScreen.style.transform = '';
          outgoingScreen.style.filter = '';
          outgoingScreen.style.transition = '';
        }}

        currentScreenIdx = targetIdx;
        if (incomingScreen) {{
          incomingScreen.classList.add('active-screen');
        }}

        // Update Bottom Presentation Bar
        document.getElementById('bar-current-idx').textContent = (currentScreenIdx + 1);
        document.getElementById('bar-screen-name').textContent = screenNames[currentScreenIdx];

        window.scrollTo({{ top: 140, behavior: 'smooth' }});

        setTimeout(() => {{
          isScreenTransitioning = false;
        }}, 850);
      }}, 530);
    }}

    function nextScreen() {{
      const nextIdx = (currentScreenIdx + 1) % 4;
      morphToScreen(nextIdx);
    }}

    function prevScreen() {{
      const prevIdx = (currentScreenIdx - 1 + 4) % 4;
      morphToScreen(prevIdx);
    }}

    function togglePresentationMode() {{
      isPresentationMode = !isPresentationMode;
      const body = document.body;
      const label = document.getElementById('mode-label');
      const bar = document.getElementById('presentation-controller');

      if (isPresentationMode) {{
        body.classList.remove('scroll-mode');
        label.textContent = "Screen Mode";
        bar.style.display = "flex";
        morphToScreen(currentScreenIdx);
      }} else {{
        body.classList.add('scroll-mode');
        label.textContent = "Scroll View";
        bar.style.display = "none";
      }}
    }}

    /* 3. FULL SCREEN SOURCE FILE INSPECTOR SYSTEM — LIGHT THEME */
    let currentInspectorFileIdx = 0;

    function escapeHtml(text) {{
      return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
    }}

    function highlightSyntax(rawLine, fileType) {{
      let line = escapeHtml(rawLine);

      if (fileType === 'cobol') {{
        // COBOL comment
        if (rawLine.trim().startsWith('*') || (rawLine.length >= 7 && rawLine.charAt(6) === '*')) {{
          return `<span class="syn-comment">${{line}}</span>`;
        }}
        // Strings
        line = line.replace(/('(?:[^'\\\\]|\\\\.)*')/g, '<span class="syn-str">$1</span>');
        // Keywords
        const kwRegex = /\\b(IDENTIFICATION|DIVISION|PROGRAM-ID|ENVIRONMENT|DATA|FILE|WORKING-STORAGE|SECTION|PROCEDURE|PERFORM|COMPUTE|IF|ELSE|END-IF|END-PERFORM|READ|WRITE|DISPLAY|GOBACK|MOVE|TO|SELECT|ASSIGN|PIC|VALUE|ZERO|ROUNDED|FUNCTION|UNTIL|NOT|AND|OR|AT|END|INPUT-OUTPUT|INPUT|OUTPUT|EXIT|INTEGER-OF-DATE|EVALUATE|WHEN|END-EVALUATE|SET|TRUE)\\b/g;
        line = line.replace(kwRegex, '<span class="syn-kw">$1</span>');
        // Numbers
        line = line.replace(/\\b(\\d+)\\b/g, '<span class="syn-num">$1</span>');
        return line;
      }}

      if (fileType === 'ssis') {{
        // XML comments
        if (line.includes('&lt;!--')) {{
          return line.replace(/(&lt;!--.*?--&gt;)/g, '<span class="syn-comment">$1</span>');
        }}
        // Attributes & values
        line = line.replace(/([a-zA-Z0-9_:-]+)=(&quot;.*?&quot;|".*?")/g, '<span class="syn-attr">$1</span>=<span class="syn-str">$2</span>');
        // Tag names
        line = line.replace(/(&lt;\\/?)([a-zA-Z0-9_:-]+)/g, '$1<span class="syn-tag">$2</span>');
        return line;
      }}

      if (fileType === 'sql') {{
        // Comments
        if (rawLine.trim().startsWith('--')) {{
          return `<span class="syn-comment">${{line}}</span>`;
        }}
        // Variables
        line = line.replace(/(@[a-zA-Z0-9_]+)/g, '<span class="syn-var">$1</span>');
        // Strings
        line = line.replace(/('(?:[^'\\\\]|\\\\.)*')/g, '<span class="syn-str">$1</span>');
        // SQL keywords
        const sqlKw = /\\b(SELECT|FROM|WHERE|JOIN|LEFT|RIGHT|INNER|ON|GROUP BY|ORDER BY|CASE|WHEN|THEN|ELSE|END|AS|DECLARE|SET|IN|AND|OR|NOT|IS|NULL|SUM|COUNT|DATE|INT|CONCAT|MONTH|YEAR|GETUTCDATE|GETDATE)\\b/gi;
        line = line.replace(sqlKw, '<span class="syn-kw">$1</span>');
        return line;
      }}

      return line;
    }}

    function openSourceInspector(fileIdx = 0, event = null) {{
      if (event) event.stopPropagation();
      currentInspectorFileIdx = fileIdx;

      const modal = document.getElementById('source-inspector-modal');
      modal.style.display = 'flex';
      setTimeout(() => {{
        modal.classList.add('modal-open');
      }}, 10);

      document.body.style.overflow = 'hidden';
      switchInspectorFile(fileIdx);
    }}

    function closeSourceInspector() {{
      const modal = document.getElementById('source-inspector-modal');
      modal.classList.remove('modal-open');
      setTimeout(() => {{
        modal.style.display = 'none';
        document.body.style.overflow = '';
      }}, 250);
    }}

    function handleBackdropClick(event) {{
      if (event.target.id === 'source-inspector-modal') {{
        closeSourceInspector();
      }}
    }}

    function switchInspectorFile(fileIdx) {{
      currentInspectorFileIdx = fileIdx;
      const file = sourceFilesData[fileIdx];

      // Update Tabs
      document.querySelectorAll('.modal-tab-btn').forEach((tab, idx) => {{
        if (idx === fileIdx) tab.classList.add('active');
        else tab.classList.remove('active');
      }});

      // Update Header & Subbar Titles
      document.getElementById('modal-filename-title').textContent = file.path;
      document.getElementById('subbar-age-tag').textContent = `⏳ Age: ${{file.age}}`;
      document.getElementById('subbar-loc-tag').textContent = `📏 ${{file.loc}} Lines`;
      document.getElementById('subbar-risk-tag').textContent = `⚠️ ${{file.risk}}`;

      // Update Subbar Rule Callout
      document.getElementById('callout-title').textContent = file.ruleTitle;
      document.getElementById('callout-range').textContent = `${{file.ruleStart}}–${{file.ruleEnd}}`;

      // Update Footer
      document.getElementById('modal-footer-status').textContent = `Viewing ${{file.path}} • ${{file.loc}} lines loaded • Ready for Agentic Ingestion`;

      // Clear search
      document.getElementById('inspector-search-input').value = '';
      document.getElementById('inspector-match-count').textContent = '';

      renderInspectorCode(file);
    }}

    function renderInspectorCode(file, searchQuery = '') {{
      const container = document.getElementById('modal-code-container');
      const lines = file.code.split('\\n');
      let htmlBuffer = '';
      let matchCount = 0;
      let firstMatchRowId = null;

      const queryLower = searchQuery.toLowerCase().trim();

      for (let i = 0; i < lines.length; i++) {{
        const lineNum = i + 1;
        const rawLine = lines[i];
        const isRuleLine = (lineNum >= file.ruleStart && lineNum <= file.ruleEnd);
        let isSearchMatch = false;

        if (queryLower && rawLine.toLowerCase().includes(queryLower)) {{
          isSearchMatch = true;
          matchCount++;
          if (!firstMatchRowId) firstMatchRowId = `row-line-${{lineNum}}`;
        }}

        const rowClasses = [
          'code-row',
          isRuleLine ? 'highlight-rule-line' : '',
          isSearchMatch ? 'search-match' : ''
        ].filter(Boolean).join(' ');

        const targetIdAttr = (lineNum === file.ruleStart) ? 'id="rule-line-target"' : `id="row-line-${{lineNum}}"`;

        let highlightedContent = highlightSyntax(rawLine, file.id);

        let ruleTagHtml = '';
        if (lineNum === file.ruleStart) {{
          ruleTagHtml = `<span class="rule-tag-badge">★ BUSINESS RULE TARGET (Lines ${{file.ruleStart}}–${{file.ruleEnd}})</span>`;
        }}

        htmlBuffer += `
          <div class="${{rowClasses}}" ${{targetIdAttr}}>
            <span class="line-num">${{lineNum}}</span>
            <span class="line-content">${{highlightedContent}}${{ruleTagHtml}}</span>
          </div>
        `;
      }}

      container.innerHTML = htmlBuffer;

      // Update match count badge
      const countBadge = document.getElementById('inspector-match-count');
      if (queryLower) {{
        countBadge.textContent = `${{matchCount}} match${{matchCount === 1 ? '' : 'es'}}`;
        if (firstMatchRowId) {{
          const el = document.getElementById(firstMatchRowId);
          if (el) el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
        }}
      }} else {{
        countBadge.textContent = '';
      }}
    }}

    function jumpToCriticalRule() {{
      const target = document.getElementById('rule-line-target');
      if (target) {{
        target.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
      }}
    }}

    function handleInspectorSearch() {{
      const query = document.getElementById('inspector-search-input').value;
      const file = sourceFilesData[currentInspectorFileIdx];
      renderInspectorCode(file, query);
    }}

    function copyCurrentFileCode() {{
      const file = sourceFilesData[currentInspectorFileIdx];
      navigator.clipboard.writeText(file.code).then(() => {{
        const btn = document.getElementById('modal-copy-btn');
        const oldText = btn.innerHTML;
        btn.innerHTML = '<span>✔</span> Copied!';
        btn.style.background = '#ecfdf5';
        btn.style.color = '#059669';
        btn.style.borderColor = '#a7f3d0';
        setTimeout(() => {{
          btn.innerHTML = oldText;
          btn.style.background = '';
          btn.style.color = '';
          btn.style.borderColor = '';
        }}, 2000);
      }}).catch(() => {{
        alert('Code copied to clipboard!');
      }});
    }}

    function nextInspectorFile() {{
      const nextIdx = (currentInspectorFileIdx + 1) % sourceFilesData.length;
      switchInspectorFile(nextIdx);
    }}

    function prevInspectorFile() {{
      const prevIdx = (currentInspectorFileIdx - 1 + sourceFilesData.length) % sourceFilesData.length;
      switchInspectorFile(prevIdx);
    }}

    /* KEYBOARD SHORTCUTS */
    window.addEventListener('keydown', (e) => {{
      const modal = document.getElementById('source-inspector-modal');
      const isModalOpen = modal && modal.classList.contains('modal-open');

      if (isModalOpen) {{
        if (e.key === 'Escape') {{
          closeSourceInspector();
        }} else if (e.key === '1' && e.target.tagName !== 'INPUT') {{
          switchInspectorFile(0);
        }} else if (e.key === '2' && e.target.tagName !== 'INPUT') {{
          switchInspectorFile(1);
        }} else if (e.key === '3' && e.target.tagName !== 'INPUT') {{
          switchInspectorFile(2);
        }}
        return;
      }}

      if (e.key === 'ArrowRight') nextScreen();
      else if (e.key === 'ArrowLeft') prevScreen();
    }});

    /* 4. SCREEN 2: PIPELINE STEP SELECTION (LAYERS 1 - 4) */
    const stepData = [
      {{
        title: "Layer 1: Code Artifacts (Automated Source Ingestion)",
        desc: "KAIRIX scans your codebase across systems, including mainframe COBOL files (.cbl), Microsoft SSIS packages (.dtsx), and database SQL views (.sql).",
        bullets: [
          "Scans different legacy file types into one unified catalog",
          "Zero changes to your live databases or running systems",
          "Smart scanning that automatically detects what was updated"
        ],
        preview: `// Discovered Legacy Assets:
[COBOL]  source/mainframe/EARNPREM.CBL (Rating Logic)
[SSIS]   source/ssis/packages/Extract_Premium.dtsx (Data Pipeline)
[SQL]    source/sql/PolicyCenter_CPP_Breakdown.sql (Reporting Logic)
// Status: Files scanned successfully. Ready to extract knowledge.`
      }},
      {{
        title: "Layer 2: Knowledge Engineering Agent",
        desc: "Instead of AI guessing, the Knowledge Engineering Agent reads the actual code logic directly to pull out exact calculations, conditions, and business rules with 100% precision.",
        bullets: [
          "Extracts business rules and formulas with complete precision",
          "Pins every rule and formula to exact source line numbers",
          "Eliminates AI guesswork and inaccurate assumptions"
        ],
        preview: `// Extracted Business Logic (EARNPREM.CBL):
Rule: Daily Earned Premium Calculation (Lines 214-238)
Formula: WS-EARNED-PREM = WS-TOTAL-PREMIUM * (WS-DAYS-RUN / WS-TOTAL-DAYS)
Guardrail: Validates active days do not exceed total term days`
      }},
      {{
        title: "Layer 3: Relationship Agent",
        desc: "The Relationship Agent links files across systems (showing how COBOL programs feed into SSIS staging tables) and indexes code meanings for instant plain-English search.",
        bullets: [
          "Tracks how data and business logic flow between different files",
          "Enables plain-English search across complex legacy systems",
          "Automatically connects related rules across multiple languages"
        ],
        preview: `// Cross-System Connection Map:
Link: EARNPREM.CBL (COBOL) feeds into Extract_Premium.dtsx (SSIS)
Knowledge Store: All business rules indexed for instant queries
Lineage: Full end-to-end trace from mainframe batch to SQL view`
      }},
      {{
        title: "Layer 4: Investigation Agent",
        desc: "When someone asks a business question, the Investigation Agent searches across all connected code to deliver a clear plain-English answer backed by verified line-by-line evidence.",
        bullets: [
          "Translates business questions into precise code lookups",
          "Combines cross-system links with smart logic search",
          "Delivers clear answers backed by exact source line numbers"
        ],
        preview: `// Automated Answer Process:
Question: "Where is earned premium calculated?"
Found in: EARNPREM.CBL (Lines 214-238) & Extract_Premium.dtsx (Rule BR-07)
Result: Clear business answer with exact file & line number citations`
      }}
    ];

    function selectStep(idx, el) {{
      document.querySelectorAll('#screen-1 .step-card').forEach(c => c.classList.remove('active'));
      if (el) el.classList.add('active');

      const data = stepData[idx];
      const panel = document.getElementById('step-detail-panel');

      smoothMorph(panel, () => {{
        document.getElementById('detail-title').textContent = data.title;
        document.getElementById('detail-desc').textContent = data.desc;
        
        const list = document.getElementById('detail-bullets');
        list.innerHTML = '';
        data.bullets.forEach(b => {{
          const li = document.createElement('li');
          li.innerHTML = `<span>✔</span> <div>${{b}}</div>`;
          list.appendChild(li);
        }});

        document.getElementById('detail-preview').textContent = data.preview;
      }}, 350);
    }}

    /* 5. SCREEN 3: LIVE BUSINESS QUESTION COMPARISON */
    const questionData = [
      {{
        oldResult: '"We think it is calculated somewhere in the batch rating jobs, but we need 3 weeks to read the COBOL files and confirm."',
        newResult: `Calculated in <strong>EARNPREM.CBL</strong> (Lines 214-238) using formula: <code>WS-TOTAL-PREMIUM * (WS-DAYS-RUN / WS-TOTAL-DAYS)</code>, then ingested and validated by SSIS <strong>Rule BR-07</strong> in <code>Extract_Premium.dtsx</code>.`,
        citation: `✔ Verified in source code & system connections`
      }},
      {{
        oldResult: '"There might be a check in the database view or SSIS pipeline, but developers have to trace 1,000 lines of SQL manually."',
        newResult: `Enforced by <strong>Rule BR-07</strong> in <code>Extract_Premium.dtsx</code> (Line 412). It checks that <code>EarnedPremium <= WrittenPremium</code>, and marks violation records for staging audit.`,
        citation: `✔ Verified in SSIS rule definition`
      }},
      {{
        oldResult: '"The documentation does not mention cancellation math. We need to hire an external mainframe contractor to inspect."',
        newResult: `Handled by paragraph <strong>4000-PROCESS-CANCEL</strong> in <code>EARNPREM.CBL</code> (Lines 280-310). When policy status is 'CAN', short-rate cancellation factor 0.90 is applied to unearned premium.`,
        citation: `✔ Verified in COBOL calculation logic`
      }}
    ];

    function selectQuestion(idx, el) {{
      document.querySelectorAll('.q-tab-btn').forEach(b => b.classList.remove('active'));
      if (el) el.classList.add('active');

      const data = questionData[idx];
      const panel = document.getElementById('comp-grid');

      smoothMorph(panel, () => {{
        document.getElementById('old-result').textContent = data.oldResult;
        document.getElementById('new-result').innerHTML = data.newResult;
        document.getElementById('new-citation').textContent = data.citation;
      }}, 350);
    }}

    /* 6. SCREEN 1: VIDEO PLAYER HELPERS */
    function triggerVideoUpload() {{
      const input = document.getElementById('video-file-input');
      if (input) input.click();
    }}

    function loadLocalVideo(event) {{
      const file = event.target.files && event.target.files[0];
      if (!file) return;

      const videoPlayer = document.getElementById('screen1-video-player');
      const placeholder = document.getElementById('video-placeholder');
      const statusText = document.getElementById('video-status-text');

      const fileUrl = URL.createObjectURL(file);
      videoPlayer.src = fileUrl;
      videoPlayer.load();

      if (placeholder) placeholder.style.display = 'none';
      if (statusText) statusText.textContent = `Playing: ${{file.name}} (${{(file.size / (1024 * 1024)).toFixed(1)}} MB)`;

      videoPlayer.play().catch(() => {{}});
    }}

    function promptVideoUrl() {{
      const url = prompt("Enter video URL (Direct .mp4/.webm link or YouTube video/embed link):");
      if (!url) return;

      const videoFrame = document.getElementById('video-frame');
      const placeholder = document.getElementById('video-placeholder');
      const statusText = document.getElementById('video-status-text');

      if (url.includes('youtube.com') || url.includes('youtu.be')) {{
        let embedUrl = url;
        if (url.includes('watch?v=')) {{
          embedUrl = url.replace('watch?v=', 'embed/');
        }} else if (url.includes('youtu.be/')) {{
          embedUrl = url.replace('youtu.be/', 'www.youtube.com/embed/');
        }}
        videoFrame.innerHTML = `<iframe src="${{embedUrl}}?autoplay=1" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>`;
        if (statusText) statusText.textContent = `Playing YouTube Video: ${{url}}`;
      }} else {{
        const videoPlayer = document.getElementById('screen1-video-player');
        videoPlayer.src = url;
        videoPlayer.load();
        if (placeholder) placeholder.style.display = 'none';
        if (statusText) statusText.textContent = `Streaming video: ${{url}}`;
        videoPlayer.play().catch(() => {{}});
      }}
    }}

    window.addEventListener('DOMContentLoaded', () => {{
      const videoPlayer = document.getElementById('screen1-video-player');
      const placeholder = document.getElementById('video-placeholder');
      if (videoPlayer) {{
        videoPlayer.addEventListener('loadeddata', () => {{
          if (placeholder && videoPlayer.readyState >= 2) {{
            placeholder.style.display = 'none';
          }}
        }});
        videoPlayer.addEventListener('play', () => {{
          if (placeholder) placeholder.style.display = 'none';
        }});
      }}
    }});
  </script>
</body>
</html>
'''

target_path = r'c:\Users\GaneshSriKumarMarimu\legacy-code-agentic-rag\probleam statement\index.html'
with open(target_path, 'w', encoding='utf-8') as f:
    f.write(html_template)

print(f"Successfully generated clean index.html with 3 perfect cards + problem/solution card at {target_path}")
