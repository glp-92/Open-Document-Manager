import subprocess

from config.config import config
from config.logger import logger
from leann import LeannChat, LeannSearcher


class LeannAdapter:
    def __init__(self):
        self.searcher: LeannSearcher | None = None
        self.llm_config: dict = {
            "type": "ollama",
            "model": config.llm_model,
        }

    def build_index(self, index_path: str, docs_path: str):
        command = [
            "leann",
            "build",
            index_path,
            "--docs",
            docs_path,
            "--embedding-mode",
            "ollama",
            "--embedding-model",
            config.embedding_model,
            "--backend",
            "hnsw",
            "--force",
        ]
        logger.info(f"building index on {index_path}...")
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            for line in process.stdout:
                logger.debug(f"[LEANN]: {line.strip()}")
            process.wait()
        except Exception as e:
            logger.exception(f"failure on building LEANN index: {e}")

    def chat(self, index_path: str, msg: str) -> str:
        chat = LeannChat(index_path=index_path, llm_config=self.llm_config)
        return chat.ask(
            msg,
            top_k=30,
        )
