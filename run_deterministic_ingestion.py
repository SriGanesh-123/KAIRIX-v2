"""
Runner for Enterprise Tri-Hybrid GraphRAG Deterministic Ingestion Pipeline.

Usage:
    python run_deterministic_ingestion.py
"""
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from knowledge_engineering_agent.deterministic_pipeline import DeterministicIngestionPipeline

if __name__ == "__main__":
    pipeline = DeterministicIngestionPipeline(
        source_dir="source",
        failure_log_path="failed_ingestion.log",
        pinecone_index_name="kairix-2048",
        batch_size=16,
    )
    pipeline.run()
