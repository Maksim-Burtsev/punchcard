#!/usr/bin/env python3
"""Extract corpus books (books/NN-slug.pdf|epub) into plain-text chunks.

Output: books/.text/NN-slug/01.txt, 02.txt, ... — chunks of ~150-250KB cut
at paragraph boundaries. books/ is gitignored; extracted text never ships.

Requires: pdftotext (brew install poppler). EPUB handled with stdlib.
Idempotent: books with an existing non-empty .text dir are skipped.
"""
import html
import html.parser
import re
import subprocess
import sys
import zipfile
from pathlib import Path

BOOKS = Path(__file__).resolve().parent.parent / "books"
OUT = BOOKS / ".text"
MIN_CHUNK, MAX_CHUNK = 150_000, 250_000


class _Text(html.parser.HTMLParser):
    SKIP = {"script", "style"}
    BREAK = {"p", "div", "br", "h1", "h2", "h3", "h4", "li", "tr", "blockquote"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self._skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._skip += 1
        elif tag in self.BREAK:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self._skip:
            self._skip -= 1
        elif tag in self.BREAK:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


def epub_text(path: Path) -> str:
    z = zipfile.ZipFile(path)
    container = z.read("META-INF/container.xml").decode("utf-8", "ignore")
    opf_path = re.search(r'full-path="([^"]+)"', container).group(1)
    opf = z.read(opf_path).decode("utf-8", "ignore")
    opf_dir = str(Path(opf_path).parent)
    manifest = {}
    for m in re.finditer(r"<item\b[^>]*>", opf):
        tag = m.group(0)
        i, h = re.search(r'id="([^"]+)"', tag), re.search(r'href="([^"]+)"', tag)
        if i and h:
            manifest[i.group(1)] = h.group(1)
    spine = re.findall(r'<itemref[^>]*idref="([^"]+)"', opf)
    chunks = []
    for idref in spine:
        href = manifest.get(idref)
        if not href or not href.endswith((".html", ".xhtml", ".htm")):
            continue
        name = href if opf_dir in ("", ".") else f"{opf_dir}/{href}"
        try:
            raw = z.read(name).decode("utf-8", "ignore")
        except KeyError:
            continue
        p = _Text()
        p.feed(raw)
        chunks.append(html.unescape("".join(p.parts)))
    return "\n\n".join(chunks)


def pdf_text(path: Path) -> str:
    r = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", str(path), "-"],
                       capture_output=True, timeout=300)
    return r.stdout.decode("utf-8", "ignore")


def clean(text: str) -> str:
    text = text.replace("\f", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    return re.sub(r"\n{4,}", "\n\n\n", text)


def chunk(text: str):
    while text:
        if len(text) <= MAX_CHUNK:
            yield text
            return
        cut = text.rfind("\n\n", MIN_CHUNK, MAX_CHUNK)
        if cut == -1:
            cut = MAX_CHUNK
        yield text[:cut]
        text = text[cut:]


def main():
    failures = []
    for book in sorted(BOOKS.iterdir()):
        if book.suffix.lower() not in (".pdf", ".epub"):
            continue
        dest = OUT / book.stem
        if dest.exists() and any(dest.iterdir()):
            print(f"{book.stem}: already extracted, skip")
            continue
        try:
            text = clean(pdf_text(book) if book.suffix.lower() == ".pdf" else epub_text(book))
        except Exception as e:
            failures.append(f"{book.name}: {e}")
            continue
        if len(text) < 100_000:
            failures.append(f"{book.name}: only {len(text)} chars extracted")
            continue
        dest.mkdir(parents=True, exist_ok=True)
        n = 0
        for n, part in enumerate(chunk(text), 1):
            (dest / f"{n:02d}.txt").write_text(part, encoding="utf-8")
        print(f"{book.stem}: {len(text) / 1e6:.1f}MB text, {n} chunks")
    if failures:
        print("\nFAILURES:\n" + "\n".join(failures))
        sys.exit(1)


if __name__ == "__main__":
    main()
