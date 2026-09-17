"""Возвращает исходные переносы строк тем строкам, которые не менялись.

    python scripts/fix_eol.py <путь от корня репозитория> [ещё пути]

Правки через Python на Windows молча переводят файл в CRLF целиком, и коммит показывает
переписанным весь файл вместо десяти изменённых строк. Скрипт выравнивает текущий файл
с версией из HEAD: совпавшие строки берутся из HEAD побайтно, новые пишутся с переносом,
который в этом файле преобладает.
"""
import difflib
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def raw_lines(data: bytes):
    """Строки вместе с их концами, как есть."""
    out, start = [], 0
    for i, b in enumerate(data):
        if b == 0x0A:
            out.append(data[start:i + 1])
            start = i + 1
    if start < len(data):
        out.append(data[start:])
    return out


def body(line: bytes) -> bytes:
    return line.rstrip(b"\r\n")


for rel in sys.argv[1:]:
    path = ROOT / rel
    head = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=ROOT, capture_output=True).stdout
    now = path.read_bytes()

    if not head:
        print(f"{rel}: в HEAD нет, пропуск")
        continue

    old_raw, new_raw = raw_lines(head), raw_lines(now)
    old_txt = [body(x) for x in old_raw]
    new_txt = [body(x) for x in new_raw]

    # Каким переносом писать новые строки: тем, что преобладает в исходном файле.
    crlf = sum(1 for x in old_raw if x.endswith(b"\r\n"))
    nl = b"\r\n" if crlf * 2 > len(old_raw) else b"\n"

    out = []
    sm = difflib.SequenceMatcher(None, old_txt, new_txt, autojunk=False)

    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            # Совпавшие строки берём из HEAD со всеми их концами.
            out.extend(old_raw[i1:i2])
        elif tag in ("insert", "replace"):
            for j in range(j1, j2):
                out.append(new_txt[j] + nl)

    result = b"".join(out)

    # Последняя строка файла: как было в исходнике, если содержимое совпало.
    if result != now:
        path.write_bytes(result)

    changed = sum(1 for t, *_ in sm.get_opcodes() if t != "equal")
    print(f"{rel}: блоков изменений {changed}, перенос новых строк {'CRLF' if nl == b'\r\n' else 'LF'}")
