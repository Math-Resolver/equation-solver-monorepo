import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import APIRouter, HTTPException
from api.v1.learning.schemas.learn_action_request import LearnActionRequest
from api.v1.learning.schemas.learn_action_response import LearnActionResponse
from api.v1.learning.schemas.learn_request import LearnRequest
from api.v1.learning.schemas.learning_response import LearnResponse, TopicItem, TopicsResponse

router = APIRouter(prefix="/learning", tags=["learning"])

@router.get("/topics", response_model=TopicsResponse)
def get_learning_topics() -> TopicsResponse:
    topics = [TopicItem(id=item, label=_build_user_friendly_label(item)) for item in TOPICS]
    return TopicsResponse(topics=topics)


@router.post("/learn", response_model=LearnResponse)
def learn_math_topic(payload: LearnRequest) -> LearnResponse:
    ai_content = _call_ai_math_teacher(topic=payload.topic, level=payload.level)
    return LearnResponse(
        topic=payload.topic,
        level=payload.level,
        contexto_breve=ai_content["contexto_breve"],
        explicacao=ai_content["explicacao"],
        exemplo=ai_content["exemplo"],
        next_actions=["sair", "outro_exemplo"],
    )


@router.post("/learn/action", response_model=LearnActionResponse)
def handle_learning_action(payload: LearnActionRequest) -> LearnActionResponse:
    if payload.action == "sair":
        return LearnActionResponse(
            topic=payload.topic,
            level=payload.level,
            action="sair",
            status="encerrado",
            mensagem="Sessao encerrada. Voce pode escolher outro assunto quando quiser.",
            exemplo=None,
            next_actions=["reiniciar"],
        )

    new_example = _call_ai_new_example(
        topic=payload.topic,
        level=payload.level,
        previous_examples=payload.previous_examples,
    )
    return LearnActionResponse(
        topic=payload.topic,
        level=payload.level,
        action="outro_exemplo",
        status="continuar",
        mensagem="Aqui esta um novo exemplo para o mesmo assunto.",
        exemplo=new_example,
        next_actions=["sair", "outro_exemplo"],
    )

TOPICS = [
    "equacoes-primeiro-grau",
    "equacoes-segundo-grau",
    "sistemas-lineares",
    "fracoes",
    "potenciacao",
    "radiciacao",
    "regra-de-tres",
    "porcentagem",
    "funcao-afim",
    "funcao-quadratica",
    "geometria-plana",
    "trigonometria-basica",
]


def _build_user_friendly_label(topic: str) -> str:
    return topic.replace("-", " ").title()


def _call_ai_math_teacher(topic: str, level: str) -> dict[str, str]:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY nao configurada no ambiente.",
        )

    system_prompt = (
        "Voce e um professor de matematica didatico para estudantes brasileiros. "
        "Sempre responda em JSON valido com as chaves exatas: "
        "contexto_breve, explicacao, exemplo. "
        "contexto_breve deve ter no maximo 2 frases. "
        "explicacao deve ensinar passo a passo de forma simples. "
        "exemplo deve trazer um exemplo resolvido."
    )

    user_prompt = (
        f"Assunto: {topic}. Nivel: {level}. "
        "Gere a resposta no formato JSON solicitado."
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.4,
        "response_format": {"type": "json_object"},
    }

    req = Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(req, timeout=30) as response:
            body = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Falha ao chamar a IA: HTTP {exc.code}",
        ) from exc
    except URLError as exc:
        raise HTTPException(
            status_code=502,
            detail="Falha de rede ao chamar a IA.",
        ) from exc

    content = body.get("choices", [{}])[0].get("message", {}).get("content")
    if not content:
        raise HTTPException(
            status_code=502,
            detail="Resposta da IA sem conteudo.",
        )

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=502,
            detail="Resposta da IA nao veio em JSON valido.",
        ) from exc

    required_fields = ["contexto_breve", "explicacao", "exemplo"]
    if not all(field in parsed for field in required_fields):
        raise HTTPException(
            status_code=502,
            detail="Resposta da IA incompleta.",
        )

    return {
        "contexto_breve": str(parsed["contexto_breve"]),
        "explicacao": str(parsed["explicacao"]),
        "exemplo": str(parsed["exemplo"]),
    }


def _call_ai_new_example(topic: str, level: str, previous_examples: list[str]) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY nao configurada no ambiente.",
        )

    system_prompt = (
        "Voce e um professor de matematica didatico para estudantes brasileiros. "
        "Responda apenas em JSON valido com a chave exata: exemplo. "
        "Gere um exemplo novo, resolvido passo a passo, diferente dos exemplos anteriores."
    )

    previous_examples_text = "\n".join(previous_examples) if previous_examples else "nenhum"
    user_prompt = (
        f"Assunto: {topic}. Nivel: {level}. "
        f"Exemplos anteriores para evitar repeticao: {previous_examples_text}."
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
    }

    req = Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(req, timeout=30) as response:
            body = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Falha ao chamar a IA: HTTP {exc.code}",
        ) from exc
    except URLError as exc:
        raise HTTPException(
            status_code=502,
            detail="Falha de rede ao chamar a IA.",
        ) from exc

    content = body.get("choices", [{}])[0].get("message", {}).get("content")
    if not content:
        raise HTTPException(
            status_code=502,
            detail="Resposta da IA sem conteudo.",
        )

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=502,
            detail="Resposta da IA nao veio em JSON valido.",
        ) from exc

    example = parsed.get("exemplo")
    if not example:
        raise HTTPException(
            status_code=502,
            detail="Resposta da IA sem exemplo.",
        )

    return str(example)