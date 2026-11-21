# faladelecorredor.com.br

Site do FALA DELE CORREDOR (Jorge Henrique). HTML estático gerado por `build.py`.

## Atualizar
1. Edite `data.json` (números, cupons, promoções, provas, marcos), `strava.json` (últimos treinos) ou crie um post em `content/diario/AAAA-MM-DD-slug.md`.
2. Rode `python3 build.py` (precisa de `pip install markdown`). O site sai em `dist/`.
3. Faça commit de tudo, incluindo `dist/`. A Vercel publica `dist/` sem build.

Promoções e cupons com `until`/`codeUntil` somem sozinhos depois da data (horário de Brasília).
