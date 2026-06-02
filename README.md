Para rodar o Backend For Frontend, instale as dependencias do projeto e entre no diretorio `src/presentation.application`.

```bash
pip install -r ../../requirements.txt
python -m uvicorn main:app --reload
```

Documentacao OpenAPI: `http://127.0.0.1:8000/docs`

Para rodar todos os testes unitarios, execute o comando abaixo no diretorio `tests/mobile_bff/domain`:

```bash
python -m unittest discover -v
```

## Endpoint de conversation

`POST /v1/conversation`

Body:

```json
{
	"topic": "Logarithm"
}
```

Resposta:

```json
{
	"message": "A logarithm tells which exponent produces a value.",
	"example": "log2(8) = 3 because 2^3 = 8."
}
```

Autenticacao:
- Requer header `Authorization: Bearer <jwt>`

Cache e integracao:
- O backend consulta Redis antes de chamar o Gemini
- Se o Redis falhar, o fluxo continua via Gemini
- Respostas bem-sucedidas do Gemini sao salvas no cache por TTL

Variaveis de ambiente:
- `REDIS_URL`: URL de conexao do Redis
- `CONVERSATION_CACHE_TTL_SECONDS`: TTL do cache em segundos. Default: `3600`
- `GEMINI_API_KEY`: chave da Gemini Developer API
- `GEMINI_MODEL`: modelo Gemini. Default: `gemini-2.0-flash`
- `GEMINI_TIMEOUT_SECONDS`: timeout da chamada ao Gemini. Default: `10`