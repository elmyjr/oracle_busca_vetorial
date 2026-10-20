import array

from app.carga import ler_json
from app.database import conectar
from app.embeddings import gerar_embedding


def buscar_filmes(pergunta: str, limite: int = 3) -> list[dict]:
    vetor = gerar_embedding(pergunta)

    sql = """
        SELECT
            titulo,
            VECTOR_DISTANCE(embedding, :vetor, COSINE) AS distancia
        FROM kb_docs
        ORDER BY distancia
        FETCH FIRST :limite ROWS ONLY
    """

    with conectar() as conexao, conexao.cursor() as cur:
        cur.execute(
            sql,
            {
                "vetor": array.array("f", vetor),
                "limite": limite,
            },
        )

        return [
            {
                "titulo": titulo,
                "distancia": distancia,
            }
            for titulo, distancia in cur
        ]


def avaliar_busca(caminho: str, limite: int = 3) -> None:
    gabarito = ler_json(caminho)
    avaliacao = []

    for posicao, caso in enumerate(gabarito, start=1):
        pergunta = caso["pergunta"]
        esperados_set = set(caso["esperados"])
        sem_palavras = caso["sem_palavras_em_comum"]

        resultados = buscar_filmes(pergunta, limite)

        recuperados_set = {
            filme["titulo"] for filme in resultados
        }

        encontrados = esperados_set & recuperados_set
        faltantes = esperados_set - recuperados_set

        acerto = (
            bool(encontrados)
            if esperados_set
            else None
        )

        avaliacao.append({
            "pergunta": pergunta,
            "categoria": caso["categoria"],
            "sem_palavras": sem_palavras,
            "esperados": esperados_set,
            "encontrados": encontrados,
            "faltantes": faltantes,
            "resultados": resultados,
            "acerto": acerto,
            "distancia_top1": (
                resultados[0]["distancia"]
                if resultados
                else None
            ),
        })

        print(f"\n{'=' * 60}")
        print(f"PERGUNTA {posicao}/{len(gabarito)}")
        print(f"Categoria: {caso['categoria']}")
        print(f"Pergunta: {pergunta}")

        if esperados_set:
            print(f"Esperados: {sorted(esperados_set)}")
            print(
                f"Acerto@{limite}: "
                f"{'SIM' if acerto else 'NÃO'}"
            )
            print(f"Encontrados: {sorted(encontrados)}")
            print(f"Faltantes: {sorted(faltantes)}")
        else:
            print("Tipo: consulta fora da base")
            print(
                f"Distância do primeiro resultado: "
                f"{resultados[0]['distancia']:.4f}"
                if resultados
                else "Nenhum resultado retornado."
            )

        print(f"Top {limite}:")

        for filme in resultados:
            marca = (
                " [ESPERADO]"
                if filme["titulo"] in esperados_set
                else ""
            )
            print(
                f"  {filme['titulo']}"
                f" | Distância: {filme['distancia']:.4f}"
                f"{marca}"
            )

    # Separa os casos conforme o gabarito.
    positivas = [
        r for r in avaliacao if r["esperados"]
    ]

    sem_palavras = [
        r for r in positivas
        if r["sem_palavras"] is True
    ]

    com_palavras = [
        r for r in positivas
        if r["sem_palavras"] is False
    ]

    fora_base = [
        r for r in avaliacao if not r["esperados"]
    ]

    # Calcula as métricas a partir dos resultados armazenados.
    acertos_geral = sum(r["acerto"] for r in positivas)
    acertos_sem = sum(r["acerto"] for r in sem_palavras)
    acertos_com = sum(r["acerto"] for r in com_palavras)

    distancias_positivas = [
        r["distancia_top1"] for r in positivas
        if r["distancia_top1"] is not None
    ]

    distancias_fora = [
        r["distancia_top1"] for r in fora_base
        if r["distancia_top1"] is not None
    ]

    print(f"\n{'=' * 60}")
    print("RESUMO DA AVALIAÇÃO")

    print(
        f"Acerto@{limite} geral: "
        f"{acertos_geral}/{len(positivas)}"
    )
    print(
        f"  sem palavras em comum: "
        f"{acertos_sem}/{len(sem_palavras)}"
    )
    print(
        f"  com palavras em comum: "
        f"{acertos_com}/{len(com_palavras)}"
    )

    if distancias_fora and distancias_positivas:
        distancia_fora = sum(distancias_fora) / len(distancias_fora)
        media_positivas = (
            sum(distancias_positivas) / len(distancias_positivas)
        )

        print(
            f"Distância do 1º lugar — fora da base: "
            f"{distancia_fora:.4f} | "
            f"média das outras {len(distancias_positivas)}: "
            f"{media_positivas:.4f}"
        )


if __name__ == "__main__":
    avaliar_busca("data/perguntas.json", limite=3)