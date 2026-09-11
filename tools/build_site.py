#!/usr/bin/env python3
"""Monta o site nas tres linguas do jogo (pt-BR, ingles, espanhol).

Entradas: templates/page.html (esqueleto), i18n/site.csv (cromo: menu, titulo da aba,
descricao; keys,pt_BR,en,es, coluna achada pelo nome) e content/<lingua>/<pag>.html
(miolo de <main>). Saida: /<pag>.html em pt-BR, /en/ e /es/ com o mesmo nome de arquivo,
<html lang>, canonical, hreflang e seletor com endonimos. O porque esta no README.md.
apk.html e apk.json ficam fora (adventure-smash/tools/publish_apk.ps1).

--check: exit 1 se o disco divergir do molde ou se pagina gerada nao estiver rastreada no
git (fora de repositorio git, pula essa parte). Sem CI no site: quem cobra e a skill commits.
Exit 0 = ok, 1 = achados, 2 = uso. Sem dependencia externa.

Uso (da raiz do repositorio do site):
  python tools/build_site.py            # escreve as paginas
  python tools/build_site.py --check    # so confere
"""

from __future__ import annotations

import argparse
import csv
import subprocess
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


def tracked_files(root: Path):
    """Caminhos rastreados pelo git, ou None fora de um repositorio."""
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            capture_output=True,
            check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return {p.decode("utf-8") for p in out.split(b"\0") if p}


def build(root: Path, check_only: bool) -> list:
    findings = []
    template = (root / "templates" / "page.html").read_text(encoding="utf-8")
    chrome = read_csv(root / "i18n" / "site.csv")
    tracked = tracked_files(root) if check_only else None

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
                elif tracked is not None and rel not in tracked:
                    findings.append("gerado mas fora do git: %s (git add -- %s)" % (rel, rel))
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
