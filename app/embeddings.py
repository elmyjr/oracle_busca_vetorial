import os

import requests

URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/embed")
MODELO = "bge-m3"
DIMENSAO = 1024


def gerar_embedding(texto: str) -> list[float]:
    resposta = requests.post(URL, json={"model": MODELO, "input": texto}, timeout=60)
    resposta.raise_for_status()
    dados = resposta.json()
    vetor = dados["embeddings"][0]
    tamanho_vetor = len(vetor)

    if tamanho_vetor != DIMENSAO:
        raise ValueError(
            "Dimensão do embedding incorreta. Esperado: " 
            f"{DIMENSAO}, Obtido: {tamanho_vetor}. Modelo utilizado: {MODELO}"
        )
    return vetor


if __name__ == "__main__":
    texto = "Exemplo de texto para gerar embedding."
    embedding = gerar_embedding(texto)
    print("Embedding gerado:", embedding[:3], "tamanho do vetor:", len(embedding))
