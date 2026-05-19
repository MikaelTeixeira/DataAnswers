import json
from urllib import error, parse, request

from app.config import settings


class AiGenerationError(Exception):
    pass


def generate_reply(prompt: str) -> str:
    if not settings.gemini_api_key:
        raise AiGenerationError("Configure GEMINI_API_KEY no arquivo .env para usar a geracao com IA.")

    model = parse.quote(settings.gemini_model, safe="")
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        f"?key={parse.quote(settings.gemini_api_key)}"
    )
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
        "generationConfig": {
            "temperature": 0.35,
            "maxOutputTokens": 350,
        },
    }

    body = json.dumps(payload).encode("utf-8")
    api_request = request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(api_request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise AiGenerationError(f"Erro da API de IA: {details}") from exc
    except error.URLError as exc:
        raise AiGenerationError("Nao foi possivel conectar na API de IA.") from exc

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError):
        raise AiGenerationError("A API de IA nao retornou uma mensagem valida.")
