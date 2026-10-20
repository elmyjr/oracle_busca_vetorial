import array
import json
import sys

import oracledb

from app.database import conectar
from app.embeddings import DIMENSAO, MODELO

oracledb.defaults.fetch_lobs = False


def exportar(caminho: str) -> int:
    sql = """
        SELECT titulo, texto, embedding
        FROM kb_docs
        ORDER BY id
    """

    filmes = []

    with conectar() as conexao, conexao.cursor() as cur:
        cur.execute(sql)

        filmes = [
            {
                "titulo": titulo,
                "texto": texto,
                "embedding": list(embedding),
            }
            for titulo, texto, embedding in cur
        ]

    dados = {
        "modelo": MODELO,
        "dimensao": DIMENSAO,
        "filmes": filmes,
    }

    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False)

    return len(filmes)


def importar(caminho: str) -> int:
    with open(caminho, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    if dados.get("modelo") != MODELO:
        raise ValueError(
            f"Modelo incompatível: arquivo={dados.get('modelo')!r}; "
            f"esperado={MODELO!r}."
        )

    filmes = dados["filmes"]

    linhas = [
        {
            "titulo": filme["titulo"],
            "texto": filme["texto"],
            "embedding": array.array("f", filme["embedding"]),
        }
        for filme in filmes
    ]

    sql = """
        INSERT INTO kb_docs (titulo, texto, embedding)
        VALUES (:titulo, :texto, :embedding)
    """

    with conectar() as conexao:
        try:
            with conexao.cursor() as cur:
                cur.execute("DELETE FROM kb_docs")
                cur.executemany(sql, linhas)

            conexao.commit()

        except Exception:
            conexao.rollback()
            raise

    return len(linhas)


if __name__ == "__main__":
    caminho = "data/vetores.json"

    match sys.argv[1:]:
        case ["exportar"]:
            total = exportar(caminho)
            print(f"Total de filmes exportados: {total}")

        case ["importar"]:
            total = importar(caminho)
            print(f"Total de filmes importados: {total}")

        case _:
            print("Uso:")
            print("  python -m app.vetores exportar")
            print("  python -m app.vetores importar")
            sys.exit(1)