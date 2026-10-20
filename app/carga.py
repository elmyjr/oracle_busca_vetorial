
import array
import json
import time

from app.database import conectar
from app.embeddings import DIMENSAO, gerar_embedding


def ler_json(caminho: str) -> list[dict]:

    with open(caminho, encoding="utf-8") as arquivo:
        return json.load(arquivo)

def montar_texto(filme: dict) -> str:
    titulo = filme["titulo"]
    titulo_original = filme["titulo_original"]
    ano = filme["ano"]
    sinopse = filme["sinopse"]
    genero: list[str] = filme["genero"]
    direcao: list[str] = filme["direcao"]
    elenco: list[str] = filme["elenco" ]
    clima: list[str] = filme["clima"]
    recepcao = filme["recepcao"]

    texto = []
    texto.append(f"Título: {titulo}")
    texto.append(f"Título original: {titulo_original}")
    texto.append(f"Ano: {ano}")
    texto.append(f"Sinopse: {sinopse}")
    texto.append(f"Gênero: {', '.join(genero)}")
    texto.append(f"Direção: {', '.join(direcao)}")
    texto.append(f"Elenco: {', '.join(elenco)}")
    texto.append(f"Clima: {', '.join(clima)}")
    texto.append(f"Recepção: {recepcao}")

    return "\n".join(texto)


def gravar( caminho: str , limite: int | None = None) -> int:
    filmes = ler_json(caminho)[:limite]

    sql_insert = """
    INSERT INTO kb_docs (titulo, texto, embedding)
    VALUES (:titulo, :texto, :embedding)
    """
    with conectar() as conexao, conexao.cursor() as cur:
        # DELETE e os INSERTS estão na mesma transação, 
        # então uma falha no meio faz rollback e a base anterior volta inteira
        # TRUNCATE é DDL, faz commit implícito e deixaria a tabela vazia
        cur.execute("DELETE FROM kb_docs")
        for posicao, filme in enumerate(filmes, start=1):
            titulo = filme.get("titulo")
            print(f"Gravando filme: {titulo} | {posicao} de {len(filmes)}")
            texto = montar_texto(filme)
            embedding = gerar_embedding(texto)
            if len(embedding) != DIMENSAO:
                raise ValueError(
                    f"Dimensão do embedding incorreta. Esperado: {DIMENSAO}, Obtido: {len(embedding)}"
                )
            cur.execute(sql_insert, {"titulo": titulo, "texto": texto, "embedding": array.array("f", embedding)})
        conexao.commit()
    return len(filmes)

if __name__ == "__main__":
    inicio = time.perf_counter()
    total = gravar("data/filmes.json")
    duracao = time.perf_counter() - inicio
    print(f"Total de filmes gravados: {total}, em {duracao:.2f} s")

