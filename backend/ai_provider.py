import logging
import re
from typing import List, Optional

from config import http_request

logger = logging.getLogger(__name__)


SINGLE_CHOICE_PROMPT = (
    "This image shows a single-choice question slide. "
    "Read the question and all options from the image carefully. "
    "Choose exactly ONE correct answer from: %s. "
    "Reply with ONLY the option letter, nothing else."
)

MULTI_CHOICE_PROMPT = (
    "This image shows a multiple-choice question slide. "
    "Read the question and all options from the image carefully. "
    "Choose ALL correct answers from: %s. "
    "Reply with ONLY the option letters separated by commas, nothing else. "
    "Example: A,C"
)

SHORT_ANSWER_PROMPT = (
    "This image shows a short-answer question slide. "
    "Read the question from the image carefully. "
    "Provide a concise, accurate answer to the question. "
    "Reply with ONLY the answer text, nothing else."
)


class AIProvider:
    def _fetch_image(self, url: str) -> bytes:
        resp = http_request("GET", url)
        resp.raise_for_status()
        return resp.content

    def answer_choice(self, cover_url: str, options: List[str], problem_type: int) -> List[str]:
        raise NotImplementedError

    def answer_short(self, cover_url: str) -> str:
        raise NotImplementedError

    def test_call(self, image_bytes: Optional[bytes] = None) -> str:
        raise NotImplementedError


class GeminiProvider(AIProvider):

    def __init__(self, api_key: str, model: str = "gemini-flash-latest"):
        from google import genai
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def _image_part(self, cover_url: str):
        from google.genai import types
        return types.Part.from_bytes(data=self._fetch_image(cover_url), mime_type="image/jpeg")

    def answer_choice(self, cover_url: str, options: List[str], problem_type: int) -> List[str]:
        options_str = ", ".join(options)
        template = SINGLE_CHOICE_PROMPT if problem_type == 1 else MULTI_CHOICE_PROMPT
        instruction = template % options_str

        response = self.client.models.generate_content(
            model=self.model,
            contents=[self._image_part(cover_url), instruction],
        )

        raw = (response.text or "").strip().upper()
        logger.info("Gemini raw response for choice: %s", raw)

        parsed = [s.strip() for s in re.split(r"[,\s]+", raw) if s.strip()]
        return [p for p in parsed if p in options]

    def answer_short(self, cover_url: str) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=[self._image_part(cover_url), SHORT_ANSWER_PROMPT],
        )

        answer = (response.text or "").strip()
        logger.info("Gemini raw response for short answer: %s", answer)
        return answer

    def test_call(self, image_bytes: Optional[bytes] = None) -> str:
        from google.genai import types
        
        contents = ["Please act as a Yuketang class assistant. Look at the image and solve the problem. If it is a choice question, reply with ONLY the correct choice letter(s). If it is a short answer, reply with ONLY the answer text. Reply with nothing else."]
        if image_bytes:
            contents.insert(0, types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"))

        logger.info("Gemini test call: model=%s, has_image=%s", self.model, image_bytes is not None)
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
            )
            result = (response.text or "").strip()
            logger.info("Gemini test call successful: %s", result[:50] + "..." if len(result) > 50 else result)
            return result
        except Exception as e:
            logger.error("Gemini test call failed: %s", str(e), exc_info=True)
            raise


class QwenProvider(AIProvider):
    BASE_URL = "https://api-inference.modelscope.cn/v1"
    DEFAULT_MODEL = "Qwen/Qwen3.5-397B-A17B"

    def __init__(self, api_key: str, model: str = None):
        from openai import OpenAI
        self.client = OpenAI(base_url=self.BASE_URL, api_key=api_key)
        self.model = model or self.DEFAULT_MODEL

    def _chat(self, cover_url: str, text: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": cover_url}},
                {"type": "text", "text": text},
            ]}],
        )
        return (response.choices[0].message.content or "").strip()

    def answer_choice(self, cover_url: str, options: List[str], problem_type: int) -> List[str]:
        options_str = ", ".join(options)
        template = SINGLE_CHOICE_PROMPT if problem_type == 1 else MULTI_CHOICE_PROMPT
        raw = self._chat(cover_url, template % options_str).upper()
        logger.info("Qwen raw response for choice: %s", raw)
        parsed = [s.strip() for s in re.split(r"[,\s]+", raw) if s.strip()]
        return [p for p in parsed if p in options]

    def answer_short(self, cover_url: str) -> str:
        answer = self._chat(cover_url, SHORT_ANSWER_PROMPT)
        logger.info("Qwen raw response for short answer: %s", answer)
        return answer

    def test_call(self, image_bytes: Optional[bytes] = None) -> str:
        import base64
        
        content = []
        if image_bytes:
            img_b64 = base64.b64encode(image_bytes).decode()
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}})
        content.append({"type": "text", "text": "Please act as a Yuketang class assistant. Look at the image and solve the problem. If it is a choice question, reply with ONLY the correct choice letter(s). If it is a short answer, reply with ONLY the answer text. Reply with nothing else."})

        logger.info("Qwen test call: model=%s, base_url=%s, has_image=%s", self.model, self.BASE_URL, image_bytes is not None)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": content}],
            )
            result = (response.choices[0].message.content or "").strip()
            logger.info("Qwen test call successful: %s", result[:50] + "..." if len(result) > 50 else result)
            return result
        except Exception as e:
            logger.error("Qwen test call failed: %s", str(e), exc_info=True)
            raise


class DashScopeProvider(QwenProvider):
    BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    DEFAULT_MODEL = "qwen3.6-plus"


class MoonshotProvider(QwenProvider):
    BASE_URL = "https://api.moonshot.cn/v1"
    DEFAULT_MODEL = "kimi-k2.5"

    def __init__(self, api_key: str, model: str = None):
        from openai import OpenAI
        # Moonshot API base url and auth requires standard OpenAI setup without modelscope inference
        self.client = OpenAI(base_url=self.BASE_URL, api_key=api_key)
        self.model = model or self.DEFAULT_MODEL


_PROVIDERS = {
    "google": GeminiProvider,
    "qwen": QwenProvider,
    "dashscope": DashScopeProvider,
    "moonshot": MoonshotProvider,
}


def create_provider(provider_name: str, api_key: str) -> Optional[AIProvider]:
    if not api_key:
        return None
    cls = _PROVIDERS.get(provider_name)
    if cls is None:
        return None
    return cls(api_key=api_key)
