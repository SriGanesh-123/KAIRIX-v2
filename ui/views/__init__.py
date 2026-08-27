"""
KAIRIX UI Pages.
"""
from ui.views.dashboard import render_dashboard
from ui.views.source_explorer import render_source_explorer
from ui.views.pipeline import render_pipeline
from ui.views.analyze import render_analyze
from ui.views.investigation import render_investigation
from ui.views.knowledge_graph import render_knowledge_graph
from ui.views.evidence import render_evidence

__all__ = [
    "render_dashboard",
    "render_source_explorer",
    "render_pipeline",
    "render_analyze",
    "render_investigation",
    "render_knowledge_graph",
    "render_evidence",
]
