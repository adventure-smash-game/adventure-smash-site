# Site do Adventure Smash — adventuresmash.online

Páginas estáticas do jogo (privacidade, termos, exclusão de conta, suporte) nas três
línguas, geradas por `tools/build_site.py`, e a página do APK de teste. Sem framework nem
dependência: HTML + `style.css` (base escura, dourado, acento); `logo.svg` é o `icon.svg`
do repositório do jogo.

URLs que o app aponta (`AppEnv`, `project.godot [adventure] links/*`):

- https://adventuresmash.online/privacidade
- https://adventuresmash.online/termos
- https://adventuresmash.online/excluir-conta
- https://adventuresmash.online/suporte

## Três línguas (gerado por `tools/build_site.py`)

As páginas `.html` são **geradas**: editar uma à mão se perde na próxima montagem.

| Onde | O que é |
|---|---|
| `templates/page.html` | o esqueleto: cabeçalho, menu, rodapé, seletor de idioma, `hreflang` |
| `i18n/site.csv` | o cromo que se repete (menu, título da aba, descrição), no formato `keys,pt_BR,en,es` do jogo |
| `content/<língua>/<página>.html` | o miolo de `<main>`, um arquivo por língua: onde a prosa se escreve e se revisa |

```sh
python tools/build_site.py           # escreve as 5 páginas (index, privacidade, termos, excluir-conta, suporte) nas 3 línguas
python tools/build_site.py --check   # falha se o disco divergir do molde ou se página gerada estiver fora do git
```

- Português na raiz, inglês em `/en/`, espanhol em `/es/`, com o mesmo nome de arquivo
  nas três: quem carrega a língua é a pasta, então os links relativos e as URLs do app não
  mudam.
- Texto legal fica em HTML (revisão linha a linha no diff); no CSV só o que se repete.

## Hospedagem

GitHub Pages do repo `adventure-smash-game/adventure-smash-site`, branch `main` `/`;
`CNAME` `adventuresmash.online`; DNS do apex (Hostinger) nos IPs 185.199.108-111.153. As
rotas sem `.html` funcionam no Pages. Sem CI: o `--check` é cobrado pela skill `commits` da
raiz.

## APK de teste (`apk.html` + `apk.json`)

Gerados por `adventure-smash/tools/publish_apk.ps1`, que o `tools/deploy_server.ps1 -Apk`
chama quando a casca muda (ou avulso; `-PageOnly` regenera a página do JSON); o script
commita e pusha só esses dois. Não
edite à mão: o template está no `.ps1`. O APK mora no VPS, não aqui; o link é público, sem
senha, desde 2026-09-06 (decisão do dono, `server/docs/SECURITY.md` D18). `APK_USER` e
`APK_PASSWORD` do `.env` do VPS só protegem o `/update/`. Página `noindex`, fora do menu.

## Regras

- A data no topo de `privacidade.html` é a mesma do `Consent.VERSION`
  (`src/app/consent.gd` do jogo, hoje "2026-08-27"): mudou a política, muda nos dois
  lugares e o app pede o aceite de novo.
- Sem rastreadores, analytics ou fonte externa.
- O português prevalece nos textos legais; inglês e espanhol levam a linha de cortesia.
  Mudou a política, muda nas três e a data anda junto.
- Página nova: entrada em `PAGES` do `build_site.py`, título em `i18n/site.csv` e um
  arquivo de conteúdo em cada língua (o `--check` cobra).
- No commit, `git status --short` dos arquivos da frente tem de sair vazio (en/ e es/ já
  ficaram de fora uma vez).
