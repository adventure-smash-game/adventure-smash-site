# Site do Adventure Smash — adventuresmash.online

Páginas estáticas exigidas pela fase F5 do plano do beta
(`adventure-smash/docs/beta_release.md`): política de privacidade, termos,
exclusão de conta e suporte, nas URLs que o app aponta (`AppEnv`,
`project.godot [adventure] links/*`):

- https://adventuresmash.online/privacidade
- https://adventuresmash.online/termos
- https://adventuresmash.online/excluir-conta
- https://adventuresmash.online/suporte

Sem framework, sem build: HTML + `style.css` (identidade do jogo: base
escura, dourado, acento). `logo.svg` é o `icon.svg` do repositório do jogo.

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

## Regras

- A data no topo de `privacidade.html` é a MESMA do `Consent.VERSION` do app
  (`src/app/consent.gd`). Mudou o texto da política → muda a versão nos dois
  lugares, e o app pede o aceite de novo.
- Conteúdo em português; nada de rastreadores, analytics ou fonte externa.
