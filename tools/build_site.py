#!/usr/bin/env python3
"""Monta o site nas tres linguas do jogo (pt-BR, ingles, espanhol).

O jogo fala tres linguas desde 2026-09-02 (adventure-smash/docs/i18n.md); o
site era o unico lugar onde o jogador so encontrava portugues — inclusive a
politica de privacidade que a Play exige e que a app abre de dentro do jogo.

Como funciona, em uma frase: **o cromo vem do CSV, a prosa vem do HTML**.

  templates/page.html        o esqueleto (cabecalho, nav, rodape, seletor)
  i18n/site.csv              o que se repete em toda pagina: rotulo do menu,
                             titulo da aba, descricao. Formato keys,pt_BR,en,es
                             — o mesmo de assets/i18n no jogo, e a coluna e
                             achada pelo NOME, nunca pela posicao.
  content/<lingua>/<pag>.html   o miolo de <main>, um arquivo por lingua

Por que a prosa NAO vai no CSV: politica de privacidade e termos sao textos
longos, com lista e link no meio. Numa celula de CSV viram uma linha unica de
3 mil caracteres, impossivel de revisar em diff — e revisar texto legal linha
a linha e exatamente o que se quer poder fazer. No CSV fica o que repete e
por isso precisa ser consistente; no HTML fica o que se le.

Saida (o nome do arquivo e o MESMO nas tres linguas — quem carrega a lingua e
a PASTA, entao todo link relativo do conteudo funciona sem traducao, e as
URLs que o app ja publica em project.godot nao mudam):

  /index.html  /privacidade.html  ...     pt-BR (raiz, sem prefixo)
  /en/index.html  /en/privacidade.html    ingles
  /es/index.html  /es/privacidade.html    espanhol

Cada pagina sai com <html lang>, canonical, hreflang cruzado das tres mais
x-default (aponta para o portugues) e o seletor de idioma no rodape, com cada
lingua escrita NA PROPRIA LINGUA (endonimo nao se traduz, como em
src/app/i18n.gd).

FORA daqui, de proposito: apk.html e apk.json, gerados por
adventure-smash/tools/publish_apk.ps1 a cada deploy verde. Mexer neles aqui
brigaria com aquele script na proxima publicacao.

Sem dependencia externa. Exit 0 = ok, 1 = achados, 2 = uso.

Uso (da raiz do repositorio do site):
  python tools/build_site.py            # escreve as paginas
  python tools/build_site.py --check    # so confere que o que esta no disco
                                        # e o que o molde geraria (para CI)
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Ordem do seletor, e a mesma de I18n.SUPPORTED no jogo. A chave e a lingua
# como o CSV a nomeia; o resto e como a WEB a nomeia.
LOCALES = [
    # (coluna do CSV, pasta de saida, <html lang>, endonimo)
    ("pt_BR", "", "pt-BR", "Português"),
    ("en", "en", "en", "English"),
    ("es", "es", "es", "Español"),
]

# (arquivo, chave do titulo, chave da descricao ou "")
PAGES = [
    ("index", "site.title.index", "site.desc.index"),
    ("privacidade", "site.title.privacy", ""),
    ("termos", "site.title.terms", ""),
    ("excluir-conta", "site.title.delete", ""),
    ("suporte", "site.title.support", ""),
]

# Menu e rodape: a ordem e a mesma das paginas de servico.
NAV = [
    ("privacidade", "site.nav.privacy"),
    ("termos", "site.nav.terms"),
    ("excluir-conta", "site.nav.delete"),
    ("suporte", "site.nav.support"),
]

SITE_URL = "https://adventuresmash.online"


def read_csv(path: Path) -> dict:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    out = {}
    for row in rows:
        key = (row.get("keys") or "").strip()
        if key:
            out[key] = {loc: (row.get(loc) or "").strip() for loc, _, _, _ in LOCALES}
    return out


def escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def url_of(folder: str, page: str) -> str:
    """URL publica, sem .html: e a forma que o app publica em project.godot
    (links/privacy = /privacidade) e a que o GitHub Pages serve sozinho."""
    prefix = "/" + folder + "/" if folder else "/"
    return SITE_URL + (prefix if page == "index" else prefix + page)


def href_of(folder: str, page: str) -> str:
    prefix = "/" + folder + "/" if folder else "/"
    return prefix if page == "index" else prefix + page + ".html"


def render(template: str, chrome: dict, locale: str, folder: str, lang_tag: str, page: str,
           title_key: str, desc_key: str, main: str) -> str:
    def text(key: str) -> str:
        return chrome.get(key, {}).get(locale, "")

    nav = "\n".join(
        '    <a href="%s.html">%s</a>' % (target, escape(text(key))) for target, key in NAV
    )
    footer = "\n".join(
        '  <a href="%s.html">%s</a>%s'
        % (target, escape(text(key)), " ·" if i < len(NAV) - 1 else "")
        for i, (target, key) in enumerate(NAV)
    )
    # Cada lingua no seletor se escreve na propria lingua; a atual sai marcada
    # e sem link, senao o jogador clica no que ja esta lendo.
    langs = []
    for other_locale, other_folder, _, endonym in LOCALES:
        if other_locale == locale:
            langs.append("<b>%s</b>" % escape(endonym))
        else:
            langs.append('<a href="%s">%s</a>' % (href_of(other_folder, page), escape(endonym)))
    langs_html = "%s: %s" % (escape(text("site.langs.label")), " · ".join(langs))

    alternates = []
    for other_locale, other_folder, other_tag, _ in LOCALES:
        alternates.append(
            '<link rel="alternate" hreflang="%s" href="%s">'
            % (other_tag, url_of(other_folder, page))
        )
    # x-default = portugues: e a lingua em que o jogo e escrito e a versao que
    # prevalece nos textos legais.
    alternates.append('<link rel="alternate" hreflang="x-default" href="%s">' % url_of("", page))

    description = ""
    if desc_key:
        description = '<meta name="description" content="%s">\n' % escape(text(desc_key))

    out = template
    out = out.replace("{{lang_tag}}", lang_tag)
    out = out.replace("{{title}}", escape(text(title_key)))
    out = out.replace("{{description}}", description)
    out = out.replace("{{canonical}}", url_of(folder, page))
    out = out.replace("{{alternates}}", "\n".join(alternates) + "\n")
    out = out.replace("{{home}}", href_of(folder, "index"))
    out = out.replace("{{nav}}", nav)
    out = out.replace("{{main}}", main.rstrip("\n"))
    out = out.replace("{{footer}}", footer)
    out = out.replace("{{langs}}", langs_html)
    return out


def build(root: Path, check_only: bool) -> list:
    findings = []
    template = (root / "templates" / "page.html").read_text(encoding="utf-8")
    chrome = read_csv(root / "i18n" / "site.csv")

    for key in [k for _, k, _ in PAGES] + [k for _, k in NAV] + ["site.langs.label"]:
        for locale, _, _, _ in LOCALES:
            if not chrome.get(key, {}).get(locale):
                findings.append("i18n/site.csv: %s sem texto em %s" % (key, locale))

    for locale, folder, lang_tag, _ in LOCALES:
        for page, title_key, desc_key in PAGES:
            source = root / "content" / (folder or "pt-BR") / (page + ".html")
            if not source.is_file():
                findings.append("conteudo ausente: %s" % source.relative_to(root).as_posix())
                continue
            main = source.read_text(encoding="utf-8")
            html = render(
                template, chrome, locale, folder, lang_tag, page, title_key, desc_key, main
            )
            target = root / folder / (page + ".html") if folder else root / (page + ".html")
            rel = target.relative_to(root).as_posix()
            if check_only:
                current = target.read_text(encoding="utf-8") if target.is_file() else ""
                if current != html:
                    findings.append("desatualizado: %s (rode tools/build_site.py)" % rel)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(html, encoding="utf-8", newline="\n")
            print("[site] %s" % rel)
    return findings


def main(argv: list) -> int:
    parser = argparse.ArgumentParser(description="monta o site nas tres linguas")
    parser.add_argument("--check", action="store_true", help="so confere, nao escreve")
    parser.add_argument("--root", default=str(ROOT))
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()

    findings = build(root, args.check)
    for line in findings:
        print("[site] %s" % line)
    if findings:
        print("[site] %d achado(s)" % len(findings))
        return 1
    print("[site] %d paginas x %d linguas" % (len(PAGES), len(LOCALES)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
