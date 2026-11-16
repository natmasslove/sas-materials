"""Convert raw/Материалы/NN_*.md -> docs/session-NN.html + docs/index.html.

Run: python tools/build.py   (needs: pip install markdown)
"""
import html
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "raw" / "Материалы"
OUT = ROOT / "docs"
SITE = "Solution Architecture School"

PAGE = """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<nav>{nav}</nav>
<main>
{body}
</main>
<nav>{nav}</nav>
{script}
</body>
</html>
"""

MERMAID = """<script type="module">
import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11.4.0/dist/mermaid.esm.min.mjs";
const dark = matchMedia("(prefers-color-scheme: dark)").matches;
mermaid.initialize({ startOnLoad: true, theme: dark ? "dark" : "default" });
</script>"""


def link(href, text):
    return f'<a href="{href}">{html.escape(text)}</a>'


def convert(text):
    body = markdown.markdown(text, extensions=["tables", "fenced_code"])
    # Mermaid reads textContent, so escaped HTML entities are fine.
    body = re.sub(
        r'<pre><code class="language-mermaid">(.*?)</code></pre>',
        r'<pre class="mermaid">\1</pre>',
        body,
        flags=re.S,
    )
    # Wide tables scroll inside their own box on small screens.
    return body.replace("<table>", '<div class="table"><table>').replace(
        "</table>", "</table></div>"
    )


def main():
    OUT.mkdir(exist_ok=True)
    pages = []
    for src in sorted(SRC.glob("[0-9][0-9]_*.md")):
        text = src.read_text(encoding="utf-8")
        title = re.search(r"^# (.+)$", text, re.M).group(1)
        pages.append((f"session-{src.name[:2]}.html", title, text))

    for i, (name, title, text) in enumerate(pages):
        nav = [link("index.html", "← Все сессии")]
        if i > 0:
            nav.append(link(pages[i - 1][0], "‹ Назад"))
        if i < len(pages) - 1:
            nav.append(link(pages[i + 1][0], "Дальше ›"))
        (OUT / name).write_text(
            PAGE.format(
                title=html.escape(f"{title} — {SITE}"),
                nav=" ".join(nav),
                body=convert(text),
                script=MERMAID if "```mermaid" in text else "",
            ),
            encoding="utf-8",
        )

    items = "\n".join(f"<li>{link(n, t)}</li>" for n, t, _ in pages)
    (OUT / "index.html").write_text(
        PAGE.format(
            title=SITE,
            nav="",
            body=f'<h1>{SITE}</h1>\n<ul class="toc">\n{items}\n</ul>',
            script="",
        ),
        encoding="utf-8",
    )
    (OUT / ".nojekyll").touch()
    print(f"Built {len(pages)} pages -> {OUT}")


if __name__ == "__main__":
    main()
