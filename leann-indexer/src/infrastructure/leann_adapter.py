import shutil
import subprocess
from pathlib import Path

from config.config import config
from config.logger import logger


class LeannAdapter:
    def __init__(self):
        self.llm_config: dict = {
            "type": "ollama",
            "model": config.llm_model,
        }

    @staticmethod
    def _resolve_leann_executable() -> str:
        # In container runtime, PATH may not include /app/.venv/bin.
        for candidate in ("leann", "/app/.venv/bin/leann"):
            resolved = shutil.which(candidate)
            if resolved:
                return resolved
        raise FileNotFoundError(
            "Could not find 'leann' executable. Ensure leann[cpu] is installed in the runtime environment."
        )

    def build_index(self, index_path: str, docs_path: str):
        docs_dir = Path(docs_path)
        if not docs_dir.exists():
            logger.error(f"docs_path does not exist: {docs_path}")
            return

        leann_bin = self._resolve_leann_executable()
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
                return
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
        except Exception as e:
            logger.exception(f"failure on building LEANN index: {e}")
