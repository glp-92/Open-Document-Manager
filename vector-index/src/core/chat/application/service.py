import re
import time

import psycopg
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

    @staticmethod
    def _strip_wrapping_quotes(text: str) -> str:
        """Remove wrapping quotes and special characters from text edges."""
        if not text:
            return text
        # Strip common quote characters from both ends
        chars_to_strip = '\'""`""\'\'«»'
        return text.strip(chars_to_strip + " \n\r\t")

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
        clean_text = re.sub(r".*?Enter your question: LEANN: \s*", "", response, flags=re.DOTALL)
        clean_text = re.sub(r"The query took.*?finish\s*$", "", clean_text, flags=re.DOTALL)
        clean_text = self._strip_wrapping_quotes(clean_text)
        return Chat(model=model, text=clean_text.strip(), processing_time=processing_time)

    def _format_output(self, sections: Chat) -> str:
        sections = [
            f"🧠 **{sections.model}**",
            f"🔍\n\n{sections.text}",
            f"⏳ **{sections.processing_time} s**",
        ]
        return "\n\n".join(sections)

    def _output_pipeline(self, response: str, processing_time: str) -> str:
        logger.info("post-processing response from LLM")
        sections = self._build_content_sections(response=response, processing_time=processing_time)
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
        content = chat_request.content
        response = vector_index_adapter.chat_with_index(index_path=chat_request.workspace_id, msg=content)
        output = self._output_pipeline(
            response=response,
            processing_time=f"{time.time() - started_at:.2f}",
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
