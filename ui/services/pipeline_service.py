"""
Pipeline Service for KAIRIX UI.

Manages thread-safe asynchronous execution of the three core KAIRIX pipeline layers:
  1. Layer 2 — Knowledge Engineering: python -m knowledge_engineering_agent <path>
  2. Layer 3 (Graph) — Graph Layer:   python -m graph_layer
  3. Layer 3 (Vector) — Vector Layer: python -m vector_layer

Captures real-time stdout and stderr in-memory buffers, tracks execution duration,
exit codes, and status states (READY, RUNNING, COMPLETED, FAILED) without blocking the UI.
"""
from __future__ import annotations

import logging
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("kairix.ui.pipeline_service")
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

# Thread-safe global pipeline run registry
_LOCK = threading.Lock()
_PIPELINE_STATES: Dict[str, Dict[str, Any]] = {
    "knowledge_engineering": {
        "name": "Knowledge Engineering",
        "command_label": "python -m knowledge_engineering_agent",
        "description": "Deterministic AST parsing, evidence building, multi-pass LLM review, and canonical package generation.",
        "status": "READY",
        "start_time": None,
        "end_time": None,
        "duration": None,
        "exit_code": None,
        "logs": [],
        "error": None,
    },
    "graph_layer": {
        "name": "Graph Layer",
        "command_label": "python -m graph_layer",
        "description": "Ingest canonical knowledge packages, AST symbols, and cross-file relationships into Neo4j Knowledge Graph.",
        "status": "READY",
        "start_time": None,
        "end_time": None,
        "duration": None,
        "exit_code": None,
        "logs": [],
        "error": None,
    },
    "vector_layer": {
        "name": "Vector Layer",
        "command_label": "python -m vector_layer",
        "description": "Chunk source files, embed with SentenceTransformer, and ingest into Qdrant collections (chunks & summaries).",
        "status": "READY",
        "start_time": None,
        "end_time": None,
        "duration": None,
        "exit_code": None,
        "logs": [],
        "error": None,
    },
}


class PipelineService:
    """
    Service to execute and monitor background pipeline runs.
    """

    @classmethod
    def get_layer_state(cls, layer_key: str) -> Dict[str, Any]:
        """Returns the current state dictionary for a specific layer."""
        with _LOCK:
            return dict(_PIPELINE_STATES.get(layer_key, {}))

    @classmethod
    def get_all_states(cls) -> Dict[str, Dict[str, Any]]:
        """Returns the state dictionary for all layers."""
        with _LOCK:
            return {k: dict(v) for k, v in _PIPELINE_STATES.items()}

    @classmethod
    def is_layer_running(cls, layer_key: str) -> bool:
        """Checks if a layer is currently in the RUNNING state."""
        with _LOCK:
            return _PIPELINE_STATES.get(layer_key, {}).get("status") == "RUNNING"

    @classmethod
    def run_layer(
        cls,
        layer_key: str,
        target_path: Optional[str] = None,
        force_refresh: bool = False,
    ) -> bool:
        """
        Launches the specified pipeline layer in a background worker thread.
        Prevents starting multiple concurrent runs of the same layer.
        """
        with _LOCK:
            layer = _PIPELINE_STATES.get(layer_key)
            if not layer:
                return False
            if layer["status"] == "RUNNING":
                return False

            # Reset state for a fresh execution
            layer["status"] = "RUNNING"
            layer["start_time"] = time.time()
            layer["end_time"] = None
            layer["duration"] = None
            layer["exit_code"] = None
            layer["logs"] = []
            layer["error"] = None

        # Build CLI command arguments
        python_exe = sys.executable
        cmd: List[str] = [python_exe, "-m"]

        if layer_key == "knowledge_engineering":
            cmd.append("knowledge_engineering_agent")
            target = target_path or "source/mainframe/"
            cmd.append(target)
            if force_refresh:
                cmd.append("--force-refresh")

        elif layer_key == "graph_layer":
            cmd.append("graph_layer")
            if force_refresh:
                cmd.append("--discover")

        elif layer_key == "vector_layer":
            cmd.append("vector_layer")
            if force_refresh:
                cmd.append("--force")
        else:
            return False

        # Launch worker thread
        worker = threading.Thread(
            target=cls._execution_worker,
            args=(layer_key, cmd),
            daemon=True,
            name=f"kairix-pipeline-{layer_key}",
        )
        worker.start()
        return True

    @classmethod
    def _execution_worker(cls, layer_key: str, cmd: List[str]) -> None:
        """Worker function that runs the subprocess and streams stdout/stderr."""
        logger.info("Starting pipeline execution for %s: %s", layer_key, " ".join(cmd))

        with _LOCK:
            _PIPELINE_STATES[layer_key]["logs"].append(
                f"[{time.strftime('%H:%M:%S')}] Launching command: {' '.join(cmd)}"
            )

        start_time = time.time()
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"

        try:
            process = subprocess.Popen(
                cmd,
                cwd=str(ROOT_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                encoding="utf-8",
                errors="replace",
                env=env,
            )

            # Stream output line-by-line
            if process.stdout:
                for raw_line in iter(process.stdout.readline, ""):
                    line = raw_line.rstrip()
                    if line:
                        with _LOCK:
                            _PIPELINE_STATES[layer_key]["logs"].append(line)
                            # Keep maximum 1000 lines in buffer
                            if len(_PIPELINE_STATES[layer_key]["logs"]) > 1000:
                                _PIPELINE_STATES[layer_key]["logs"] = _PIPELINE_STATES[layer_key]["logs"][-1000:]

            process.wait()
            exit_code = process.returncode
            end_time = time.time()
            duration = round(end_time - start_time, 2)

            with _LOCK:
                _PIPELINE_STATES[layer_key]["end_time"] = end_time
                _PIPELINE_STATES[layer_key]["duration"] = duration
                _PIPELINE_STATES[layer_key]["exit_code"] = exit_code

                if exit_code == 0:
                    _PIPELINE_STATES[layer_key]["status"] = "COMPLETED"
                    _PIPELINE_STATES[layer_key]["logs"].append(
                        f"[{time.strftime('%H:%M:%S')}] Execution completed successfully in {duration}s."
                    )
                else:
                    _PIPELINE_STATES[layer_key]["status"] = "FAILED"
                    err_msg = f"Process exited with non-zero code: {exit_code}"
                    _PIPELINE_STATES[layer_key]["error"] = err_msg
                    _PIPELINE_STATES[layer_key]["logs"].append(
                        f"[{time.strftime('%H:%M:%S')}] {err_msg} (Duration: {duration}s)"
                    )

            # Invalidate relevant caches on completion
            try:
                from ui.services.source_service import SourceService
                SourceService.refresh_sources()
            except Exception:
                pass

        except Exception as e:
            end_time = time.time()
            duration = round(end_time - start_time, 2)
            logger.error("Pipeline worker exception for %s: %s", layer_key, e, exc_info=True)

            with _LOCK:
                _PIPELINE_STATES[layer_key]["end_time"] = end_time
                _PIPELINE_STATES[layer_key]["duration"] = duration
                _PIPELINE_STATES[layer_key]["exit_code"] = -1
                _PIPELINE_STATES[layer_key]["status"] = "FAILED"
                _PIPELINE_STATES[layer_key]["error"] = str(e)
                _PIPELINE_STATES[layer_key]["logs"].append(
                    f"[{time.strftime('%H:%M:%S')}] Execution exception: {e}"
                )
