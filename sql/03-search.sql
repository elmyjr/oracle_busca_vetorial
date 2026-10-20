-- =====================================================================
-- 03-search.sql — Consultas de similaridade e comparação com LIKE
-- Projeto: busca vetorial de filmes (Grupo 3, MBA PUC Minas)
--
-- Como rodar: conectado como app_embedding em FREEPDB1, executar como
-- script (F5 no SQL Developer ou "Run Script" no VS Code), para que os
-- comandos VARIABLE, EXEC e PROMPT funcionem.
--
-- Este script não gera embedding nenhum. A busca por pergunta livre
-- precisa do Ollama para transformar o texto em vetor e por isso fica
-- no Python (app/busca.py). Aqui só se usam vetores que já estão na
-- tabela: o banco calcula as distâncias e ordena.
-- =====================================================================


-- ---------------------------------------------------------------------
-- 1. Conferência rápida da base
-- ---------------------------------------------------------------------
PROMPT === 1. Conferência da base ===

-- Esperado: 400 filmes, todos com 1024 dimensões e norma próxima de 1
-- (o Ollama devolve os vetores do bge-m3 já normalizados; o resíduo na
-- sétima casa vem da precisão do FLOAT32).
SELECT COUNT(*)                                 AS filmes,
       MIN(VECTOR_DIMENSION_COUNT(embedding))   AS dim_min,
       MAX(VECTOR_DIMENSION_COUNT(embedding))   AS dim_max,
       ROUND(MIN(VECTOR_NORM(embedding)), 6)    AS norma_min,
       ROUND(MAX(VECTOR_NORM(embedding)), 6)    AS norma_max
FROM   kb_docs;


-- ---------------------------------------------------------------------
-- 2. Filmes parecidos com um filme da base (recomendação por conteúdo)
-- ---------------------------------------------------------------------
-- O vetor de referência é o do próprio filme, já gravado na coluna.
-- Por isso esta consulta não chama o Ollama: é SQL puro.
-- O título vai por bind, como no Python. Para outro filme, troque só a
-- linha do EXEC. Se o título não existir, a subconsulta não devolve
-- linha e o resultado vem vazio.
PROMPT === 2. Filmes parecidos com um filme da base ===

VARIABLE titulo VARCHAR2(200)
EXEC :titulo := 'Interestelar';

SELECT titulo,
       ROUND(dist, 4) AS distancia
FROM  (SELECT d.titulo,
              VECTOR_DISTANCE(d.embedding, r.embedding, COSINE) AS dist
       FROM   kb_docs d
              CROSS JOIN (SELECT embedding
                          FROM   kb_docs
                          WHERE  titulo = :titulo) r
       -- O próprio filme sai da lista; sem este filtro ele ocuparia
       -- uma das três posições (veja o exercício 2b).
       WHERE  d.titulo <> :titulo)
-- Ordena pela distância sem arredondar, para não empatar na 4ª casa.
ORDER  BY dist
FETCH FIRST 3 ROWS ONLY;


-- 2b. Exercício: responda antes de rodar. Sem o filtro do próprio
-- filme, em que posição ele aparece e com que distância?
PROMPT === 2b. Exercício: sem excluir o próprio filme ===

SELECT d.titulo,
       ROUND(VECTOR_DISTANCE(d.embedding, r.embedding, COSINE), 4) AS distancia
FROM   kb_docs d
       CROSS JOIN (SELECT embedding FROM kb_docs WHERE titulo = :titulo) r
ORDER  BY VECTOR_DISTANCE(d.embedding, r.embedding, COSINE)
FETCH FIRST 3 ROWS ONLY;


-- 2c. Os três MENOS parecidos, para mostrar a escala da distância:
-- compare com os valores do item 2.
PROMPT === 2c. Os três filmes menos parecidos ===

SELECT d.titulo,
       ROUND(VECTOR_DISTANCE(d.embedding, r.embedding, COSINE), 4) AS distancia
FROM   kb_docs d
       CROSS JOIN (SELECT embedding FROM kb_docs WHERE titulo = :titulo) r
ORDER  BY VECTOR_DISTANCE(d.embedding, r.embedding, COSINE) DESC
FETCH FIRST 3 ROWS ONLY;


-- ---------------------------------------------------------------------
-- 3. Comparação com LIKE (busca por palavra)
-- ---------------------------------------------------------------------
-- O LIKE procura a sequência exata de caracteres no texto: diferencia
-- maiúsculas e acentos, acha pedaços de palavras e não tem noção de
-- relevância, então não existe "top-3".
-- Os termos abaixo são constantes escritas por nós, não entrada de
-- usuário; por isso aparecem como literais. A pergunta do usuário, no
-- Python, vai sempre por bind.
PROMPT === 3a. Quantos filmes cada termo encontra ===

-- Contagens esperadas na base atual de 400 filmes:
--   Fernanda Montenegro      3  (os três certos, mas sem ordem)
--   Christopher Nolan        6
--   Tom Hanks               11
--   inteligência artificial  5
--   Natal                   12  (inclui "Natalie" Portman e Wood)
--   virou cult              15
--   cult                    38  (inclui "cultura", "cultural" e "cultivar")
--   zelador                  2  (nenhum é o WALL·E)
--   carteiro                 0  (o Náufrago diz "empresa de entregas")
WITH termos (ordem, termo) AS (
    SELECT 1, 'Fernanda Montenegro'     FROM dual UNION ALL
    SELECT 2, 'Christopher Nolan'       FROM dual UNION ALL
    SELECT 3, 'Tom Hanks'               FROM dual UNION ALL
    SELECT 4, 'inteligência artificial' FROM dual UNION ALL
    SELECT 5, 'Natal'                   FROM dual UNION ALL
    SELECT 6, 'virou cult'              FROM dual UNION ALL
    SELECT 7, 'cult'                    FROM dual UNION ALL
    SELECT 8, 'zelador'                 FROM dual UNION ALL
    SELECT 9, 'carteiro'                FROM dual
)
SELECT t.termo,
       COUNT(d.id) AS filmes
FROM   termos t
       LEFT JOIN kb_docs d
              ON d.texto LIKE '%' || t.termo || '%'
GROUP  BY t.ordem, t.termo
ORDER  BY t.ordem;


-- 3b. Detalhe de um termo. A ordem é alfabética porque o LIKE não sabe
-- qual filme é mais relevante. Troque o termo no EXEC para ver outro.
--   'zelador' → O Iluminado e Karatê Kid: a palavra certa no filme
--               errado. A pergunta 1 descreve o WALL·E sem usar
--               "robô", e a busca vetorial acha o filme pelo sentido.
--   'Natal'   → 12 filmes, três deles só por causa do nome "Natalie".
PROMPT === 3b. Filmes encontrados por um termo ===

VARIABLE termo VARCHAR2(200)
EXEC :termo := 'zelador';

SELECT titulo
FROM   kb_docs
WHERE  texto LIKE '%' || :termo || '%'
ORDER  BY titulo;
