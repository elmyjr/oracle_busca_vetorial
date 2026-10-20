import logging
from pathlib import Path
from typing import Annotated

import oracledb
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, StringConstraints

from app.busca import buscar_filmes

logger = logging.getLogger(__name__)

class BuscaRequest(BaseModel):
    pergunta: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1),
    ]


class FilmeResultado(BaseModel):
    titulo: str
    sinopse: str
    distancia: float


class BuscaResponse(BaseModel):
    pergunta: str
    resultados: list[FilmeResultado]


app = FastAPI(
    title="Busca Semântica de Filmes",
    description="Pesquisa de filmes utilizando embeddings e Oracle Vector Search.",
    version="1.0.0",
)

CAMINHO_HTML = Path(__file__).parent / "static" / "index.html"


@app.get("/", include_in_schema=False)
def pagina_inicial():
    return FileResponse(CAMINHO_HTML)

@app.post("/search", response_model=BuscaResponse)
def pesquisar(dados: BuscaRequest) -> BuscaResponse:
    try:
        resultados = buscar_filmes(
            pergunta=dados.pergunta,
            limite=3,
        )

    except requests.exceptions.RequestException as erro:
        logger.exception("Falha ao consultar o serviço Ollama.")

        raise HTTPException(
            status_code=503,
            detail=(
                "Serviço de embeddings indisponível. "
                "Verifique a URL do Ollama e se o modelo "
                "bge-m3 está disponível."
            ),
        ) from erro
    # Quando o container oracle para, o Podman tira o nome oracle do DNS da rede do compose. 
    # A conexão falha antes de chegar ao banco, já na tradução do nome para endereço.
    except (oracledb.Error, OSError) as erro:
        logger.exception("Falha ao consultar o banco Oracle.")

        raise HTTPException(
            status_code=503,
            detail=(
                "Banco de dados indisponível. "
                "Verifique a conexão com o Oracle e se o banco "
                "está pronto para receber consultas."
            ),
        ) from erro

    return BuscaResponse(
        pergunta=dados.pergunta,
        resultados=resultados, # type: ignore
    )