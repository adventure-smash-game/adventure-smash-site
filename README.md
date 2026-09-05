# Site do Adventure Smash — adventuresmash.online

Páginas estáticas exigidas pela fase F5 do plano do beta
(`adventure-smash/docs/beta_release.md`): política de privacidade, termos,
exclusão de conta e suporte, nas URLs que o app aponta (`AppEnv`,
`project.godot [adventure] links/*`):

- https://adventuresmash.online/privacidade
- https://adventuresmash.online/termos
- https://adventuresmash.online/excluir-conta
- https://adventuresmash.online/suporte

Sem framework e sem dependência: HTML + `style.css` (identidade do jogo: base
escura, dourado, acento). `logo.svg` é o `icon.svg` do repositório do jogo.

## Três línguas (as mesmas do jogo)

O site sai em português, inglês e espanhol, como o jogo
(`adventure-smash/docs/i18n.md`). **As páginas `.html` são GERADAS** por
`tools/build_site.py` — editar uma delas à mão se perde na próxima montagem:

| Onde | O que é |
|---|---|
| `templates/page.html` | o esqueleto: cabeçalho, menu, rodapé, seletor de idioma, `hreflang` |
| `i18n/site.csv` | o cromo que se repete em toda página (menu, título da aba, descrição), no formato `keys,pt_BR,en,es` do jogo |
| `content/<língua>/<página>.html` | o miolo de `<main>`, um arquivo por língua — é onde a prosa se escreve e se revisa |

```sh
python tools/build_site.py           # escreve as 5 páginas nas 3 línguas
python tools/build_site.py --check   # falha se o disco divergir do molde
```

Saída: português na raiz (adventuresmash.online/privacidade.html), inglês em `/en/`, espanhol em
`/es/`. **O nome do arquivo é o mesmo nas três**: quem carrega a língua é a
pasta, então todo link relativo do conteúdo funciona sem tradução e as URLs
que o app publica (`project.godot [adventure] links/*`) não mudam.

Texto longo (privacidade, termos) fica em HTML, não em célula de CSV: texto
legal se revisa linha a linha no diff, e uma célula de 3 mil caracteres não
se revisa. No CSV fica só o que repete — que é justamente o que precisa ser
consistente entre as páginas.

## Publicar (GitHub Pages, recomendado)

1. Repo: `github.com/adventure-smash-game/adventure-smash-site` (público —
   Pages gratuito exige público; organização própria para o usuário pessoal
   não aparecer).
2. Settings → Pages → Deploy from branch → `main` `/ (root)`.
3. O arquivo `CNAME` já aponta `adventuresmash.online`. Na Hostinger, o DNS
   do apex vai para os IPs do GitHub Pages (185.199.108-111.153) e `www` em
   CNAME para `<usuario>.github.io`.
4. As rotas sem `.html` (`/privacidade`) funcionam no Pages automaticamente.

Alternativa: hospedagem estática da própria Hostinger (subir os arquivos por
FTP/painel; garantir que `/privacidade` sirva `privacidade.html`).

## APK de teste (`apk.html` + `apk.json`)

Gerados por `adventure-smash/tools/publish_apk.ps1` (chamado no fim de todo
`tools/deploy_server.ps1` verde): o script commita e pusha só esses dois
arquivos — não os edite à mão (mudou o template? é no `.ps1`; `-PageOnly`
regenera a página do JSON). O APK **não** fica neste repo nem em release
pública: mora no VPS atrás de usuário/senha (`APK_USER`/`APK_PASSWORD` do
`.env` de lá, passados ao time por canal privado), e a página só aponta
para `https://<api>/apk/<arquivo>`. `noindex`, fora do menu. Segurança:
`server/docs/SECURITY.md` D18.

## Regras

- A data no topo de `privacidade.html` é a MESMA do `Consent.VERSION` do app
  (`src/app/consent.gd`). Mudou o texto da política → muda a versão nos dois
  lugares, e o app pede o aceite de novo.
- Nada de rastreadores, analytics ou fonte externa.
- O português é a versão que PREVALECE nos textos legais; inglês e espanhol
  levam a linha de cortesia apontando para ele. Mudou a política em português
  → muda nas três, e a data no topo anda junto.
- Página nova entra em `PAGES` do `build_site.py`, com título no
  `i18n/site.csv` e um arquivo de conteúdo em cada uma das três línguas — o
  `--check` reprova conteúdo faltando.
