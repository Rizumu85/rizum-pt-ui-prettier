"""Look up Painter's own translations.

Two uses, both part of the Painter Languages standard in
``docs/integration.md``:

    python tools/painter_translations.py ActionEditor Viewer3D
        Which languages translate these Qt object names. A plugin that finds
        a Painter widget by such a name breaks in those languages.

    python tools/painter_translations.py --find "Free rotation"
        Painter's wording for a piece of its English text in every language,
        so plugin catalogs use Painter's terms.

Painter's install folder is taken from ``--painter`` or ``PAINTER_DIR``.
"""

from __future__ import annotations

import argparse
import os
import struct
import sys
from pathlib import Path


LANGUAGES = ("de", "es", "fr", "it", "ja", "ko", "pt", "zh")
DEFAULT_INSTALL = Path(r"C:/Program Files/Adobe/Adobe Substance 3D Painter")
_MESSAGES_SECTION = 0x69
_END, _TRANSLATION, _OBSOLETE, _SOURCE, _CONTEXT, _COMMENT = 1, 3, 5, 6, 7, 8


def read_messages(path: Path) -> list[dict]:
    """Messages of a Qt ``.qm`` file as ``{context, source, translation}``."""
    data = path.read_bytes()
    position = 16
    messages = []
    while position < len(data):
        section = data[position]
        (length,) = struct.unpack(">I", data[position + 1:position + 5])
        block = data[position + 5:position + 5 + length]
        position += 5 + length
        if section != _MESSAGES_SECTION:
            continue
        offset = 0
        message = {}
        while offset < len(block):
            tag = block[offset]
            offset += 1
            if tag == _END:
                messages.append(message)
                message = {}
                continue
            if tag == _OBSOLETE:
                offset += 4
                continue
            (size,) = struct.unpack(">I", block[offset:offset + 4])
            offset += 4
            if size == 0xFFFFFFFF:
                size = 0
            raw = block[offset:offset + size]
            offset += size
            if tag == _TRANSLATION:
                message.setdefault("translation", raw.decode("utf-16-be", "replace"))
            elif tag == _SOURCE:
                message["source"] = raw.decode("utf-8", "replace")
            elif tag == _CONTEXT:
                message["context"] = raw.decode("utf-8", "replace")
            elif tag != _COMMENT:
                raise ValueError(f"{path.name}: unknown message tag {tag}")
    return messages


def lookup(directory: Path, texts: list[str]) -> dict:
    """``{(source, context): {language: translation}}`` for the given sources."""
    wanted = {text.casefold() for text in texts}
    found = {}
    for language in LANGUAGES:
        for message in read_messages(directory / f"translation_{language}.qm"):
            source = message.get("source", "")
            if source.casefold() in wanted:
                key = (source, message.get("context", ""))
                found.setdefault(key, {})[language] = message.get("translation", "")
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("texts", nargs="+", help="object names, or English texts with --find")
    parser.add_argument("--find", action="store_true", help="print every translation of the texts")
    parser.add_argument("--painter", default=os.environ.get("PAINTER_DIR", str(DEFAULT_INSTALL)))
    arguments = parser.parse_args()
    directory = Path(arguments.painter) / "resources" / "translation"
    if not directory.is_dir():
        parser.error(f"no translations in {directory}; pass --painter <install folder>")
    sys.stdout.reconfigure(encoding="utf-8")

    found = lookup(directory, arguments.texts)
    if arguments.find:
        for (source, context), translations in sorted(found.items()):
            print(f"{source}  [{context}]")
            for language, translation in translations.items():
                print(f"    {language}: {translation}")
        return 0

    for text in arguments.texts:
        rows = [
            (context, {language: value for language, value in translations.items() if value and value != source})
            for (source, context), translations in sorted(found.items())
            if source.casefold() == text.casefold()
        ]
        rows = [(context, changed) for context, changed in rows if changed]
        if not rows:
            print(f"{text}: not translated in any language")
            continue
        print(f"{text}: translatable; only a problem where the context is the widget's parent class")
        for context, changed in rows:
            print(f"    [{context}] " + ", ".join(f"{language}={value}" for language, value in changed.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
