import re
import time
import traceback

import psycopg
import requests
from config.config import config
from config.logger import logger
from core.chat.domain.model import Chat
from core.chat.infrastructure.repository_impl import ChatRepositoryImpl
from core.chat.schemas.requests import ChatRequest
from vector_index.leann_adapter import LeannAdapter


class ChatService:
    def __init__(
        self,
        chat_repository_impl: ChatRepositoryImpl,
    ):
        self.chat_repository_impl = chat_repository_impl

    def _detect_language(self, text: str) -> str:
        sample_text = text[:200].strip()
        if not sample_text:
            return "English"
        prompt = f"""
            Identify the language name of the text below.

            Rules:
            - Answer ONLY with the language name (e.g., 'English', 'Spanish', 'French').
            - Do not add periods, labels, or explanations.

            Text:
            {sample_text}
            """
        try:
            response = requests.post(
                f"{config.ollama_url}/api/generate",
                json={
                    "model": config.translator_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0, "num_predict": 10},
                },
            )
            result: dict = response.json()
            raw_lang = result.get("response", "").strip()
            clean_lang = re.sub(r"[^\w]", "", raw_lang.split("\n")[0].split(" ")[-1])
            return clean_lang if clean_lang else "English"
        except Exception:
            traceback.print_exc()
            return "English"

    def _translate(self, text: str, source_lang: str, target_lang: str) -> str:
        if not text.strip():
            return text
        prompt = f"""You are a professional translator.

            Translate the text from {source_lang} to {target_lang}.

            STRICT RULES:
            - Output ONLY the translated text.
            - Do NOT add explanations, notes, or formatting.
            - Do NOT repeat the original text.
            - Preserve meaning exactly.
            - If the input is ambiguous, translate it as-is.

            TEXT:
            {text}
            """
        try:
            response = requests.post(
                f"{config.ollama_url}/api/generate",
                json={
                    "model": config.translator_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0},
                },
            )
            result: dict = response.json()
            return result.get("response", "").strip()
        except Exception:
            traceback.print_exc()
            return text

    def _build_content_sections(self, response: str, processing_time: str) -> Chat:
        if "not found. Use 'leann build" in response:
            return Chat(
                model="unknown",
                text=(
                    "Document index was not found. Compute document embeddings "
                    "before asking questions. Please check the docs for more details"
                ),
                processing_time=processing_time,
            )
        model_match = re.search(r"Using (.*?)\s\(", response)
        model = model_match.group(1) if model_match else "unknown"
        clean_text = re.sub(r".*?Enter your question:.*?\n+", "", response, flags=re.DOTALL)
        clean_text = re.sub(r"The query took.*finish", "", clean_text).strip()
        clean_text = re.sub(r"^LEANN:\s*", "", clean_text)
        return Chat(model=model, text=clean_text.strip(), processing_time=processing_time)

    def _format_output(self, sections: Chat) -> str:
        sections = [
            f"🧠 **{sections.model}**",
            f"🔍\n\n{sections.text}",
            f"⏳ **{sections.processing_time} s**",
        ]
        return "\n\n".join(sections)

    def _input_pipeline(self, content: str) -> tuple[str, str]:
        input_language = self._detect_language(content)
        normalized_content = (
            self._translate(content, source_lang=input_language, target_lang="en")
            if input_language != "en"
            else content
        )
        logger.info(f"detected input language: {input_language}")
        return normalized_content.strip(), input_language

    def _output_pipeline(self, response: str, processing_time: str, input_language: str) -> str:
        logger.info(f"post-processing response from LLM, input language: {input_language}")
        sections = self._build_content_sections(response=response, processing_time=processing_time)
        sections.text = self._translate(
            sections.text,
            source_lang="English",
            target_lang=input_language,
        )
        return self._format_output(sections)

    async def process(
        self,
        payload: dict,
        db_unit_of_work: psycopg.Connection,
        vector_index_adapter: LeannAdapter,
    ) -> None:
        logger.info(f"received chat message {payload}")
        started_at = time.time()
        chat_request = ChatRequest(**payload)
        if not chat_request.workspace_id:
            logger.error("missing workspace_id in chat event payload")
            return
        content, input_language = self._input_pipeline(chat_request.content)
        response = vector_index_adapter.chat_with_index(index_path=chat_request.workspace_id, msg=content)
        output = self._output_pipeline(
            response=response,
            processing_time=f"{time.time() - started_at:.2f}",
            input_language=input_language,
        )
        with db_unit_of_work() as conn, conn.cursor() as cur:
            self.chat_repository_impl.insert_chat_message(
                cursor=cur,
                chat_id=chat_request.chat_id,
                content=output,
                owner="AI",
            )
            conn.commit()
        logger.info(f"finished processing chat request for workspace {chat_request.workspace_id}")
