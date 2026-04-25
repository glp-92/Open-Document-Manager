import shutil
import subprocess
from pathlib import Path

from config.config import config
from config.logger import logger
from core.shared.runs import RunStatus


class LeannAdapter:
    def __init__(self):
        pass

    @staticmethod
    def _resolve_leann_executable() -> str:
        for candidate in ("leann", "/app/.venv/bin/leann"):
            resolved = shutil.which(candidate)
            if resolved:
                return resolved
        raise FileNotFoundError(
            "Could not find 'leann' executable. Ensure leann[cpu] is installed in the runtime environment."
        )

    @staticmethod
    def build_index(index_path: str, docs_path: str) -> RunStatus:
        docs_dir = Path(docs_path)
        if not docs_dir.exists():
            logger.error(f"docs_path does not exist: {docs_path}")
            return RunStatus.ERROR
        leann_bin = LeannAdapter._resolve_leann_executable()
        command = [
            leann_bin,
            "build",
            index_path,
            "--docs",
            str(docs_dir),
            "--embedding-mode",
            "ollama",
            "--embedding-model",
            config.embedding_model,
            "--backend",
            "hnsw",
            "--force",
        ]
        logger.info(f"building index on {index_path}...")
        logger.info("running command: " + " ".join(command))
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            if process.stdout is None:
                logger.error("leann process stdout is not available")
                return RunStatus.ERROR
            buffer = ""
            while True:
                ch = process.stdout.read(1)
                if ch == "" and process.poll() is not None:
                    break
                if ch in ("\n", "\r"):
                    line = buffer.strip()
                    if line:
                        logger.info(f"[LEANN] {line}")
                    buffer = ""
                else:
                    buffer += ch
            if buffer.strip():
                logger.info(f"[LEANN] {buffer.strip()}")
            rc = process.wait()
            if rc == 0:
                logger.info(f"index build finished successfully for workspace/index {index_path}")
            else:
                logger.error(f"index build failed for workspace/index {index_path} with return code {rc}")
                return RunStatus.ERROR
        except Exception as e:
            logger.exception(f"failure on building LEANN index: {e}")
            return RunStatus.ERROR
        return RunStatus.COMPLETED

    @staticmethod
    def chat_with_index(index_path: str, msg: str) -> str:
        leann_bin = LeannAdapter._resolve_leann_executable()
        command = [
            leann_bin,
            "ask",
            index_path,
            "--model",
            config.llm_model,
            "--top-k",
            "3",
        ]
        logger.info("running command: " + " ".join(command))
        try:
            process = subprocess.Popen(
                command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            if process.stdin is None or process.stdout is None:
                logger.error("leann process stdin or stdout is not available")
                return ""
            logger.info(f"sending message to leann: {msg}")
            process.stdin.write(msg + "\n")
            process.stdin.flush()
            response = ""
            while True:
                line = process.stdout.readline()
                if line == "" and process.poll() is not None:
                    break
                if line:
                    logger.info(f"[LEANN] {line.strip()}")
                    response += line
            rc = process.wait()
            if rc != 0:
                logger.error(f"leann chat process exited with return code {rc}")
                return ""
            return response.strip()
        except Exception as e:
            logger.exception(f"failure on leann chat: {e}")
            return ""
