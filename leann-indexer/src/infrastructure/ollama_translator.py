import re
import traceback

import requests
from config.config import config


class OllamaTranslator:
    def __init__(self):
        self.model = config.translator_model
        self.url = config.ollama_url

    def detect_language(self, text: str) -> str:
        sample_text = text[:200].strip()
        if not sample_text:
            return "English"
        prompt = f"""
            Identify the ISO 639-1 language name of the text below.

            Rules:
            - Answer ONLY with the language name (e.g., 'English', 'Spanish', 'French').
            - Do not add periods, labels, or explanations.

            Text:
            {sample_text}
            """
        try:
            response = requests.post(
                f"{self.url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 1, "num_predict": 10},
                },
            )
            result: dict = response.json()
            raw_lang = result.get("response", "").strip()
            clean_lang = re.sub(r"[^\w]", "", raw_lang.split("\n")[0].split(" ")[-1])
            return clean_lang if clean_lang else "English"
        except Exception:
            traceback.print_exc()
            return "English"

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        if not text.strip():
            return text
        prompt = f"""
            Task: Translate the text from {source_lang} to {target_lang}.

            Rules:
            - You MUST translate all parts of the text, including any non-English words, technical terms, or nouns.
            - Do not include anything that is not included in the original context text.
            - Only translate the text as is, without adding or removing any content.
            - Do not add any explanations, labels, or formatting. Only provide the translated text.

            Text to translate:
            {text}
            """
        try:
            response = requests.post(
                f"{self.url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 1},
                },
            )
            result: dict = response.json()
            return result.get("response", "").strip()
        except Exception:
            traceback.print_exc()
            return text
