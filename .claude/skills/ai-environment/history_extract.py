"""Выжимка из истории работы с агентом: реплики пользователя, сводки сжатий, счётчики.

Файл сессии Claude Code — это JSONL на сотни мегабайт (272 МБ за пять дней работы над
DesignStack). Целиком он в контекст не помещается и не нужен: сигнал — в том, что говорил
пользователь, в сводках сжатия контекста и в том, какие инструменты и навыки шли в ход.

    python .claude/skills/ai-environment/history_extract.py <папка-проекта-в-~/.claude/projects>
    python .claude/skills/ai-environment/history_extract.py c--Projects-DesignSite --out .tmp/history

Кладёт рядом файлы `users_N.txt` и `summaries_N.txt` кусками примерно по 130 тысяч знаков —
такой кусок читает один субагент. Больше двух-трёх субагентов одновременно не запускать:
упрёшься в лимит сессии.
"""
import argparse
import collections
import json
import os
import pathlib
import re
import sys

p = argparse.ArgumentParser()
p.add_argument("project", help="имя папки проекта в ~/.claude/projects")
p.add_argument("--out", default=".tmp/history", help="куда класть выжимку")
p.add_argument("--chunk", type=int, default=130000, help="знаков в одном куске")
a = p.parse_args()

src_dir = pathlib.Path(os.path.expanduser("~")) / ".claude" / "projects" / a.project

if not src_dir.is_dir():
    print("нет такой папки:", src_dir)
    sys.exit(1)

out_dir = pathlib.Path(a.out)
out_dir.mkdir(parents=True, exist_ok=True)

users, summaries = [], []
tools, skills = collections.Counter(), collections.Counter()
NOISE = re.compile(r"<(system-reminder|local-command|command-message|ide_|task-notification)")

for src in sorted(src_dir.glob("*.jsonl")):
    with open(src, encoding="utf-8") as f:
        for line in f:
            try:
                o = json.loads(line)
            except ValueError:
                continue

            if o.get("isSidechain"):
                continue

            kind = o.get("type")
            msg = o.get("message") or {}
            content = msg.get("content")
            stamp = (o.get("timestamp") or "")[:16].replace("T", " ")

            if kind == "user":
                texts = [content] if isinstance(content, str) else [
                    b.get("text", "") for b in (content or [])
                    if isinstance(b, dict) and b.get("type") == "text"
                ]

                for text in texts:
                    text = text.strip()

                    if not text or NOISE.match(text):
                        continue

                    if text.startswith("This session is being continued"):
                        summaries.append((stamp, text))
                    else:
                        users.append((stamp, text))

            elif kind == "assistant" and isinstance(content, list):
                for b in content:
                    if isinstance(b, dict) and b.get("type") == "tool_use":
                        tools[str(b.get("name"))] += 1

                        if b.get("name") == "Skill":
                            skills[str((b.get("input") or {}).get("skill"))] += 1


def dump(rows, prefix):
    """Пишет куски примерно равного размера и возвращает, сколько файлов вышло."""
    part, size, files = [], 0, 0

    def flush():
        nonlocal part, size, files

        if not part:
            return

        files += 1
        path = out_dir / ("%s_%d.txt" % (prefix, files))
        path.write_text("\n\n".join(part), encoding="utf-8")
        print("  ", path, len(part), "записей")
        part, size = [], 0

    for stamp, text in rows:
        block = "[%s] %s" % (stamp, text)

        if part and size + len(block) > a.chunk:
            flush()

        part.append(block)
        size += len(block)

    flush()

    return files


print("реплик пользователя:", len(users), "· сводок сжатия:", len(summaries))
dump(users, "users")
dump(summaries, "summaries")
print("инструменты:", tools.most_common(12))
print("навыки:", dict(skills))
