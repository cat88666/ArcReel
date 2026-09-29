"""TXT/MD 文本解码：4 层策略。

1. BOM 优先（UTF-8-SIG / UTF-16 LE/BE）
2. 严格 UTF-8
3. charset-normalizer 概率检测（chaos < 0.5）
4. gb18030 + errors='replace' 兜底（>5% 乱码判定失败）
"""

import logging
import re
from pathlib import Path

import charset_normalizer

from .base import ExtractedText
from .errors import SourceDecodeError

logger = logging.getLogger(__name__)

_REPLACE_THRESHOLD = 0.05
_RTF_HEADER_RE = re.compile(r"^\ufeff?\s*\{\\rtf\d")
_RTF_DESTINATIONS = {
    "colortbl",
    "expandedcolortbl",
    "filetbl",
    "fonttbl",
    "header",
    "headerf",
    "headerl",
    "headerr",
    "footer",
    "footerf",
    "footerl",
    "footerr",
    "info",
    "listtable",
    "listoverridetable",
    "object",
    "pict",
    "stylesheet",
}


def decode_rtf(text: str) -> str | None:
    """Return plain text for RTF content, or ``None`` when *text* is not RTF."""
    if not _RTF_HEADER_RE.match(text):
        return None

    # Each group inherits Unicode fallback width and destination visibility.
    # ``skip`` counts the ANSI fallback characters following a ``\\uN`` escape.
    state = [1, False, 0]  # uc_skip, hidden, skip
    stack: list[list[int | bool]] = []
    output: list[str] = []
    encoding = "cp1252"
    index = 0

    def append(value: str) -> None:
        if state[1]:
            return
        if state[2]:
            skipped = min(int(state[2]), len(value))
            state[2] = int(state[2]) - skipped
            value = value[skipped:]
        if value:
            output.append(value)

    while index < len(text):
        char = text[index]
        if char == "{":
            stack.append(state.copy())
            index += 1
            continue
        if char == "}":
            if stack:
                state = stack.pop()
            index += 1
            continue
        if char in "\r\n":
            index += 1
            continue
        if char != "\\":
            append(char)
            index += 1
            continue

        index += 1
        if index >= len(text):
            break
        symbol = text[index]
        if symbol in "\\{}":
            append(symbol)
            index += 1
            continue
        if symbol == "*":
            state[1] = True
            index += 1
            continue
        if symbol == "'":
            raw = bytearray()
            while index + 2 < len(text) and text[index] == "'":
                try:
                    raw.append(int(text[index + 1 : index + 3], 16))
                except ValueError:
                    break
                index += 3
                if index + 1 < len(text) and text[index : index + 2] == "\\'":
                    index += 1
            if raw:
                try:
                    append(raw.decode(encoding))
                except (LookupError, UnicodeDecodeError):
                    append(raw.decode("cp1252", errors="replace"))
            continue
        if not symbol.isalpha():
            if symbol == "~":
                append("\u00a0")
            elif symbol == "_":
                append("\u2011")
            index += 1
            continue

        word_start = index
        while index < len(text) and text[index].isalpha():
            index += 1
        word = text[word_start:index]
        number: int | None = None
        number_start = index
        if index < len(text) and text[index] in "+-":
            index += 1
        digit_start = index
        while index < len(text) and text[index].isdigit():
            index += 1
        if index > digit_start:
            number = int(text[number_start:index])
        if index < len(text) and text[index] == " ":
            index += 1

        if word in _RTF_DESTINATIONS:
            state[1] = True
        elif word == "uc" and number is not None:
            state[0] = max(0, number)
        elif word == "u" and number is not None:
            codepoint = number if number >= 0 else number + 65536
            if not state[1]:
                output.append(chr(codepoint))
            state[2] = int(state[0])
        elif word == "ansicpg" and number is not None:
            encoding = "utf-8" if number == 65001 else f"cp{number}"
        elif word in {"par", "line"}:
            append("\n")
        elif word == "tab":
            append("\t")

    return "".join(output).strip()


def _decoded_text(text: str, encoding: str) -> tuple[str, str]:
    rtf_text = decode_rtf(text)
    if rtf_text is not None:
        return rtf_text, "rtf"
    return text, encoding


def decode_txt(raw: bytes) -> tuple[str, str]:
    if raw.startswith(b"\xef\xbb\xbf"):
        return _decoded_text(raw[3:].decode("utf-8"), "utf-8-sig")
    if raw.startswith(b"\xff\xfe"):
        return _decoded_text(raw[2:].decode("utf-16-le"), "utf-16-le")
    if raw.startswith(b"\xfe\xff"):
        return _decoded_text(raw[2:].decode("utf-16-be"), "utf-16-be")

    try:
        return _decoded_text(raw.decode("utf-8"), "utf-8")
    except UnicodeDecodeError:
        pass

    best = charset_normalizer.from_bytes(raw).best()
    detected_enc: str | None = None
    if best is not None and best.chaos < 0.5 and best.encoding:
        detected_enc = best.encoding
        try:
            return _decoded_text(raw.decode(best.encoding), best.encoding)
        except (UnicodeDecodeError, LookupError):
            pass

    decoded = raw.decode("gb18030", errors="replace")
    replace_ratio = decoded.count("\ufffd") / len(decoded) if decoded else 0.0
    if replace_ratio > _REPLACE_THRESHOLD:
        raise SourceDecodeError(
            filename="<bytes>",
            tried_encodings=["utf-8", detected_enc, "gb18030"],
        )
    if "\ufffd" in decoded:
        logger.warning(
            "gb18030 fallback with %d replacements (ratio=%.4f)",
            decoded.count("\ufffd"),
            replace_ratio,
        )
        return _decoded_text(decoded, "gb18030-lossy")
    return _decoded_text(decoded, "gb18030")


class TxtExtractor:
    def extract(self, path: Path) -> ExtractedText:
        raw = path.read_bytes()
        try:
            text, enc = decode_txt(raw)
        except SourceDecodeError as exc:
            raise SourceDecodeError(filename=path.name, tried_encodings=exc.tried_encodings) from exc
        return ExtractedText(text=text, used_encoding=enc, chapter_count=0)
