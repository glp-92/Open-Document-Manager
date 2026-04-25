import re
import time
from typing import Literal

from config.logger import logger
from infrastructure.db_adapter import PostgresDBAdapter
from infrastructure.leann_adapter import LeannAdapter
from infrastructure.ollama_translator import OllamaTranslator
from pydantic import BaseModel


class ChatRequest(BaseModel):
    type: Literal["embeddings", "chat"]
    content: str
    owner: Literal["HUMAN", "AI"]
    message_id: str
    chat_id: str
    workspace_id: str


class ContentSections(BaseModel):
    model: str
    text: str
    processing_time: str


def _pre_process_input_pipeline(content: str, translator: OllamaTranslator) -> str:
    input_language: str = translator.detect_language(content)
    content: str = (
        translator.translate(content, source_lang=input_language, target_lang="en")
        if input_language != "en"
        else content
    )
    logger.info(f"detected input language: {input_language}")
    return content.strip(), input_language


def _post_process_output_pipeline(
    response: str, processing_time: str, translator: OllamaTranslator, input_language: str
) -> str:
    logger.info(f"post-processing response from LLM, input language: {input_language}")
    content_sections: ContentSections = _build_content_sections(response=response, processing_time=processing_time)
    content_sections.text = translator.translate(
        content_sections.text, source_lang="English", target_lang=input_language
    )
    return _format_output(response_sections=content_sections)


def _build_content_sections(response: str, processing_time: str) -> str:
    if "not found. Use 'leann build" in response:
        return ContentSections(
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
    return ContentSections(model=model, text=clean_text.strip(), processing_time=processing_time)


def _format_output(response_sections: ContentSections) -> str:
    sections = [
        f"🧠 **{response_sections.model}**",
        f"🔍\n\n{response_sections.text}",
        f"⏳ **{response_sections.processing_time} s**",
    ]
    return "\n\n".join(sections)


async def make_response_on_chat(
    payload: dict, leann_adapter: LeannAdapter, ollama_translator: OllamaTranslator, pg_adapter: PostgresDBAdapter
):
    logger.info(f"received chat message {payload}")
    ti = time.time()
    chat_request: ChatRequest = ChatRequest(**payload)
    workspace_id: str | None = chat_request.workspace_id
    if not workspace_id:
        logger.error("missing workspace_id in chat event payload")
        return
    content: str
    input_language: str
    content, input_language = _pre_process_input_pipeline(chat_request.content, translator=ollama_translator)
    response: str = leann_adapter.chat(index_path=workspace_id, msg=content)
    output: str = _post_process_output_pipeline(
        response=response,
        processing_time=f"{time.time() - ti:.2f}",
        translator=ollama_translator,
        input_language=input_language,
    )
    pg_adapter.insert_chat_message(chat_id=chat_request.chat_id, content=output, owner="AI")
    logger.info(f"finished processing chat request for workspace {workspace_id}")
    return
