# Busca semântica de filmes com Oracle AI Database 26ai

Grupo 3 — MBA em Engenharia de Dados, PUC Minas.

Você descreve o filme que quer ver, em linguagem natural, e a aplicação devolve os 3 filmes mais próximos em significado, com a distância de cada um. A base tem 400 filmes, cada um com sinopse, gênero, direção, elenco, clima e recepção.

| Peça | Escolha |
|---|---|
| Banco | Oracle AI Database 26ai Free (`docker.io/gvenzl/oracle-free:23-slim`), PDB `FREEPDB1` |
| Embeddings | Ollama com o modelo `bge-m3` (1024 dimensões) |
| Coluna do vetor | `VECTOR(1024, FLOAT32)` |
| Métrica | distância cosseno (`VECTOR_DISTANCE ... COSINE`), busca exata, top-3 |
| Aplicação | Python, `python-oracledb` (modo thin) e FastAPI, com uma página HTML |

## Estrutura

```
app/        aplicação Python
  main.py       API (POST /search) e página inicial
  busca.py      busca top-3 e avaliação com gabarito
  vetores.py    carga a partir dos vetores pré-calculados
  carga.py      carga ao vivo (gera os vetores no Ollama)
  static/       página HTML
data/
  filmes.json     os 400 filmes
  vetores.json    os mesmos filmes com os vetores já calculados pelo bge-m3
  perguntas.json  9 perguntas com resposta esperada + 1 fora da base
sql/
  01-create-table.sql  cria a tabela; roda sozinho na primeira subida
  03-search.sql        consultas didáticas: filmes parecidos e comparação com LIKE
docs/
  avaliacao.txt  resultado da avaliação (7/9 no top-3), pergunta a pergunta
compose.yaml    os três serviços: oracle, ollama e app
Containerfile   receita da imagem da aplicação
.env.example    senhas da demonstração (copiar para .env)
```

## Requisitos

- Podman com `podman compose` funcionando (`podman compose version` responde) ou Docker Desktop.
- Máquina virtual do Podman com pelo menos 6 GB de memória; 8 GB é o ideal. Veja [Memória da máquina virtual](#memória-da-máquina-virtual).
- Uns 10 GB livres em disco.
- Internet só na preparação. Na aula, nada precisa ser baixado.

**Use a mesma ferramenta na preparação e na aula.** O Podman e o Docker guardam imagens e volumes em lugares separados: o que foi baixado com um não aparece no outro. Os comandos abaixo usam `podman`; com Docker, troque `podman compose` por `docker compose`.

## 1. Preparação (antes da aula, com internet)

Clone o repositório (ou baixe o ZIP em Code > Download ZIP e extraia) e abra o terminal na pasta do projeto:

```powershell
copy .env.example .env               # no Mac/Linux: cp .env.example .env
podman compose pull oracle ollama    # baixa as imagens do Oracle e do Ollama
podman compose build                 # constrói a imagem da aplicação
podman compose up -d                 # sobe tudo
```

Na primeira vez, o `up` leva de 1 a 3 minutos: o comando só termina depois que o Oracle passa no healthcheck. Na mesma subida, o Oracle cria o usuário `app_embedding` e roda o `sql/01-create-table.sql`.

Depois, baixe o modelo e carregue a base:

```powershell
podman compose exec ollama ollama pull bge-m3            # 1,2 GB
podman compose exec app python -m app.vetores importar   # esperado: 400 filmes, em segundos
```

Abra http://localhost:8000 e faça uma busca. Para conferir a qualidade:

```powershell
podman compose exec app python -m app.busca
```

O esperado é `Acerto@3 geral: 7/9` e a distância da pergunta fora da base (cerca de 0,587) bem acima da média das outras (cerca de 0,467).

Por fim, desligue **sem** apagar nada:

```powershell
podman compose down
```

O banco carregado e o modelo ficam nos volumes e estarão lá na aula.

## 2. Na aula

```powershell
podman compose up -d
```

Uns 5 minutos antes de apresentar, faça uma busca qualquer na página. Ela carrega o bge-m3 na memória: a primeira busca leva de 6 a 23 segundos; as seguintes são bem mais rápidas. O compose já define `OLLAMA_KEEP_ALIVE=1h`, então o modelo fica carregado por 1 hora.

Buscas para a demonstração:

| Pergunta | Esperado |
|---|---|
| Filme sobre um homem que se apaixona por uma inteligência artificial | Ex Machina e Ela no top-3 |
| Um zelador mecânico, último habitante de um mundo coberto de sujeira, se apaixona por uma visitante | WALL·E em 1º, sem nenhuma palavra em comum com a sinopse |
| Quero ver um filme com a Fernanda Montenegro | Central do Brasil em 1º |
| Como declarar o imposto de renda? | Fora da base: algum filme volta, mas com distância bem maior |

Para mostrar o SQL, conecte o VS Code ou o SQL Developer em `localhost:1521/FREEPDB1`, usuário `app_embedding`, senha do `APP_USER_PASSWORD` no `.env`, e rode o `sql/03-search.sql` como script (F5).

No fim: `podman compose down`. **Nunca use `down -v` na aula**: o `-v` apaga o banco e o modelo.

## Como funciona

- **Três serviços, encontrados pelo nome.** Dentro da rede do compose, a aplicação fala com `oracle:1521/FREEPDB1` e com `http://ollama:11434`. Os endereços vêm de variáveis de ambiente (`DB_USER`, `DB_PASSWORD`, `DB_DSN`, `OLLAMA_URL`), então o mesmo código roda fora do compose com `localhost`.
- **Ordem de subida.** O Oracle leva dezenas de segundos para abrir depois que o container inicia. O `depends_on` com `condition: service_healthy` faz a aplicação esperar o healthcheck do Oracle passar. Além disso, a aplicação abre a conexão a cada busca: se o Oracle cair depois, a busca responde 503 com uma mensagem clara e volta a funcionar quando ele voltar, sem reiniciar nada.
- **Vetores pré-calculados.** Gerar os 400 vetores no Ollama levou 881 s num desktop; num notebook, só com o processador, levaria mais. Por isso os vetores dos filmes vêm prontos em `data/vetores.json`. São os mesmos que deram 7/9 na avaliação. A pergunta continua indo ao Ollama ao vivo.
- **Proteção contra troca de modelo.** O `vetores.json` guarda o nome do modelo que gerou os vetores, e a carga recusa o arquivo se o modelo configurado for outro. Sem isso, a troca seria silenciosa: se o novo modelo também gerasse 1024 números, nem o INSERT nem o `VECTOR_DISTANCE` dariam erro.
- **Carga ao vivo (alternativa).** `podman compose exec app python -m app.carga` gera os vetores de novo a partir do `filmes.json`. Demora: 15 minutos ou mais. DELETE e inserts ficam numa transação só: se falhar no meio, a base anterior volta inteira.

## Memória da máquina virtual

No Windows e no Mac, os containers rodam numa máquina virtual. Ela precisa de uns 6 GB: o Oracle Free usa até 2 GB, o Ollama com o bge-m3 perto de 2 GB, e o sistema da VM o resto.

Para ver quanto a VM tem, em bytes (8000000000 é cerca de 8 GB):

```powershell
podman info --format "{{.Host.MemTotal}}"
```

### Windows

O Podman usa o WSL 2 por padrão, e quem define a memória é o próprio WSL: por padrão, metade da RAM do computador. Num notebook de 16 GB, isso dá 8 GB, e não é preciso mudar nada.

Se o valor estiver abaixo de 6 GB, crie ou edite o arquivo `C:\Users\<seu usuário>\.wslconfig`:

```ini
[wsl2]
memory=8GB
```

Depois reinicie o WSL e a máquina do Podman:

```powershell
wsl --shutdown
podman machine start
```

O Docker Desktop no Windows também usa o WSL 2 e segue o mesmo arquivo.

### Mac

A máquina do Podman no Mac começa com 2 GB, o que não basta. Para aumentar:

```bash
podman machine stop
podman machine set --memory 8192 --cpus 4
podman machine start
```

Se o `set` for recusado, ajuste em Podman Desktop > Settings > Resources. Outra opção é recriar a máquina com `podman machine rm` e `podman machine init --memory 8192 --cpus 4`, mas isso apaga as imagens e os volumes que estavam nela.

## Problemas comuns

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| `dependency failed to start: container ...-oracle-1 exited (1)` | Falta o `.env`, e a senha chega em branco | Ver `podman compose logs oracle`; criar o `.env`; `podman compose down -v` e `up -d` de novo (só na preparação, nunca na aula) |
| `address already in use` na 1521 ou na 8000 | Outro Oracle ou outra aplicação na mesma porta | Parar o outro container (`podman ps`, `podman stop <nome>`) |
| Página: "Serviço de embeddings indisponível…" | O bge-m3 não foi baixado | `podman compose exec ollama ollama pull bge-m3` |
| Página: "Banco de dados indisponível…" | O Oracle ainda está subindo ou parou | `podman compose ps`; `podman compose start oracle` e esperar 1 minuto |
| Página: "Não foi possível conectar à API." | O container `app` não está no ar | `podman compose ps`; `podman compose logs app` |
| Primeira busca demora de 6 a 23 s | O modelo está sendo carregado na memória | Normal; fazer a busca de aquecimento antes de apresentar |
| Erro de nome curto de imagem no Podman | O Podman não completa nomes como `gvenzl/oracle-free` | O compose já usa os nomes completos (`docker.io/...`); manter assim |
