# Perguntas de teste

As 10 perguntas do gabarito (`data/perguntas.json`), prontas para copiar e colar na página de busca (http://localhost:8001). Cada uma traz o filme esperado e o top-3 da avaliação, com a distância cosseno: menor é mais parecido.

Na demonstração ao vivo, a ordem sugerida é **P6, P1, P7 e P10**.

Os números vêm da avaliação de 18/10. Rodando no compose, podem variar na quarta casa decimal.

---

## P1 · enredo · sem palavras em comum

```text
Um zelador mecânico, último habitante de um mundo coberto de sujeira, se apaixona por uma visitante
```

- **Esperado:** WALL·E
- **Resultado:** acertou, em 1º
- **Top-3:** WALL·E (0,4900) · Intocáveis (0,5015) · Interestelar (0,5020)

## P2 · enredo · sem palavras em comum

```text
Carteiro isolado após um acidente aéreo, tendo um objeto esportivo como único amigo
```

- **Esperado:** Náufrago
- **Resultado:** errou
- **Top-3:** Apertem os Cintos… o Piloto Sumiu! (0,4767) · Up: Altas Aventuras (0,5102) · O Fabuloso Destino de Amélie Poulain (0,5223)
- **Provável motivo:** o “acidente aéreo” puxou filmes de avião, e a sinopse do Náufrago diz “empresa de entregas”, não “carteiro”.

## P3 · enredo · sem palavras em comum

```text
Homem percebe que cada momento da própria rotina é filmado em segredo para uma plateia de milhões
```

- **Esperado:** O Show de Truman: O Show da Vida
- **Resultado:** errou
- **Top-3:** Matrix (0,5014) · Click (0,5178) · Ghost: Do Outro Lado da Vida (0,5288)
- **Provável motivo:** vieram filmes de temas vizinhos, de realidade e rotina controladas de fora.

## P4 · enredo · sem palavras em comum

```text
Repórter que fala de chuva e sol, aprisionado numa única data do calendário, que reinicia sempre que acorda
```

- **Esperado:** Feitiço do Tempo
- **Resultado:** acertou, em 1º
- **Top-3:** Feitiço do Tempo (0,4645) · O Dia Depois de Amanhã (0,4881) · Diário de uma Paixão (0,4965)

## P5 · inglês · sem palavras em comum

```text
A poor family cons its way into working for a rich household, until a secret hidden in the house surfaces on a rainy night
```

- **Esperado:** Parasita
- **Resultado:** acertou, em 1º, com a pergunta em inglês e a base em português
- **Top-3:** Parasita (0,4676) · Encanto (0,4743) · Pequena Miss Sunshine (0,4755)

## P6 · enredo · com palavras em comum

```text
Filme sobre um homem que se apaixona por uma inteligência artificial
```

- **Esperado:** Ela
- **Resultado:** acertou, em 2º
- **Top-3:** Ex Machina: Instinto Artificial (0,3703) · Ela (0,3996) · Matrix (0,4077)

## P7 · ator · com palavras em comum

```text
Quero ver um filme com a Fernanda Montenegro
```

- **Esperado:** Central do Brasil, O Auto da Compadecida ou Ainda Estou Aqui
- **Resultado:** acertou, em 1º
- **Top-3:** Central do Brasil (0,4682) · Encontro de Amor (0,4953) · O Diabo Veste Prada (0,4975)

## P8 · ocasião · com palavras em comum

```text
O que assistir com as crianças na noite de Natal?
```

- **Esperado:** Esqueceram de Mim
- **Resultado:** acertou, em 3º
- **Top-3:** Gremlins (0,4872) · Matilda (0,4892) · Esqueceram de Mim (0,4944)

## P9 · recepção · com palavras em comum

```text
Um filme que foi mal nos cinemas, mas depois virou cult
```

- **Esperado:** qualquer um dos 14 filmes listados em `data/perguntas.json`
- **Resultado:** acertou, em 3º
- **Top-3:** As Patricinhas de Beverly Hills (0,4754) · Os Bons Companheiros (0,4937) · A Felicidade Não se Compra (0,5096)

## P10 · fora da base

```text
Como declarar o imposto de renda?
```

- **Esperado:** nenhum filme; a pergunta não tem relação com a base
- **Resultado:** a busca devolve 3 filmes mesmo assim, porque o top-k sempre devolve k. A pista é a distância do 1º lugar, maior que a das outras perguntas.
- **Top-3:** Jerry Maguire: A Grande Virada (0,5868) · Uma Verdade Inconveniente (0,5982) · Spotlight: Segredos Revelados (0,6052)

---

## Resumo

| Medida | Resultado |
|---|---|
| Acerto no top-3 | 7 de 9 |
| Sem palavras em comum com o texto | 3 de 5 |
| Com palavras em comum | 4 de 4 |
| Distância do 1º lugar, fora da base | 0,5868 |
| Distância do 1º lugar, média das outras 9 | 0,4668 |

Para repetir a avaliação completa no compose:

```powershell
podman compose exec app python -m app.busca
```
