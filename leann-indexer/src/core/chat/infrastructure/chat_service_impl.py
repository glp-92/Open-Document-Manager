import re
import time

from config.logger import logger
from core.chat.application.chat_service import ChatService
from core.chat.application.translation_service import TranslationService
from core.chat.domain.model import Chat, ChatRequest
from db.db_adapter import PostgresDBAdapter
from vector_index.vector_index import VectorIndex


class ChatServiceImpl(ChatService):
    def __init__(
        self,
        vector_index: VectorIndex,
        translation_service: TranslationService,
        db_adapter: PostgresDBAdapter,
    ):
        self.vector_index = vector_index
        self.translation_service = translation_service
        self.db_adapter = db_adapter

    def _pre_process_input(self, content: str) -> tuple[str, str]:
        input_language = self.translation_service.detect_language(content)
        normalized_content = (
            self.translation_service.translate(content, source_lang=input_language, target_lang="en")
            if input_language != "en"
            else content
        )
        logger.info(f"detected input language: {input_language}")
        return normalized_content.strip(), input_language

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
        model_match = re.search(r"Using (.*?)\\s\\(", response)
        model = model_match.group(1) if model_match else "unknown"
        clean_text = re.sub(r".*?Enter your question:.*?\\n+", "", response, flags=re.DOTALL)
        clean_text = re.sub(r"The query took.*finish", "", clean_text).strip()
        clean_text = re.sub(r"^LEANN:\\s*", "", clean_text)
        return Chat(model=model, text=clean_text.strip(), processing_time=processing_time)

    def _format_output(self, sections: Chat) -> str:
        blocks = [
            f"🧠 **{sections.model}**",
            f"🔍\\n\\n{sections.text}",
            f"⏳ **{sections.processing_time} s**",
        ]
        return "\\n\\n".join(blocks)

    def _post_process_output(self, response: str, processing_time: str, input_language: str) -> str:
        logger.info(f"post-processing response from LLM, input language: {input_language}")
        sections = self._build_content_sections(response=response, processing_time=processing_time)
        sections.text = self.translation_service.translate(
            sections.text,
            source_lang="English",
            target_lang=input_language,
        )
        return self._format_output(sections)

    async def process(self, payload: dict) -> None:
        logger.info(f"received chat message {payload}")
        started_at = time.time()
        chat_request = ChatRequest(**payload)

        if not chat_request.workspace_id:
            logger.error("missing workspace_id in chat event payload")
            return

        content, input_language = self._pre_process_input(chat_request.content)
        response = self.vector_index.chat_with_index(index_path=chat_request.workspace_id, msg=content)
        output = self._post_process_output(
            response=response,
            processing_time=f"{time.time() - started_at:.2f}",
            input_language=input_language,
        )
        self.db_adapter.insert_chat_message(
            chat_id=chat_request.chat_id,
            content=output,
            owner="AI",
        )
        logger.info(f"finished processing chat request for workspace {chat_request.workspace_id}")
