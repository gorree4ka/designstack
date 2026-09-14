"""PreToolUse hook for Bash: block WP-CLI calls that Git Bash or cmd.exe would silently corrupt.
Reads the hook JSON from stdin, exits 2 (blocking feedback) with the reason on stderr.

Two classes, both seen on 2026-09-10/11:
1. Git Bash rewrites arguments that start with "/" (or values like --x=/...) into Windows paths:
   `wp rewrite structure '/%postname%/'` stored /C:/Program Files/Git/%postname%/.
   Allowed with MSYS_NO_PATHCONV=1.
2. tools/wp.cmd runs through cmd.exe, which reads > < | & ^ inside arguments as redirects and pipes:
   `wp.cmd eval '...$wpdb->$t...'` created a stray file `$t}` in the repo root.
"""
import json, os, re, shlex, sys

SEPARATORS = {"|", "||", "&&", ";", "&", "(", ")"}
REDIRECTS = {">", ">>", "<", "<<", ">&", "<&", "&>", ">|"}
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
CMD_METACHARS = set("<>|&^")


def tokens_of(command):
    lexer = shlex.shlex(command.replace("\n", " ; "), posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    return list(lexer)


def segments(tokens):
    seg = []
    for tok in tokens:
        if tok in SEPARATORS:
            if seg:
                yield seg
            seg = []
        else:
            seg.append(tok)
    if seg:
        yield seg


def check(command):
    """Return a reason string if the command must be blocked, else None."""
    try:
        toks = tokens_of(command)
    except ValueError:
        return None  # unbalanced quotes or heredoc: do not guess
    names_wp = "wp-cli.phar" in command or "wp.cmd" in command
    exported = re.search(r"\bexport\s+MSYS_NO_PATHCONV=1\b", command) is not None
    for seg in segments(toks):
        i = 0
        env = set()
        while i < len(seg) and ASSIGNMENT.match(seg[i]):
            env.add(seg[i])
            i += 1
        if i >= len(seg):
            continue
        word = seg[i]
        base = os.path.basename(word).lower()
        if base in ("wp", "wp.cmd"):
            args = seg[i + 1:]
        elif base in ("php", "php.exe") and i + 1 < len(seg) and os.path.basename(seg[i + 1]).lower() == "wp-cli.phar":
            args = seg[i + 2:]
        elif word.startswith("$") and names_wp:
            args = seg[i + 1:]  # e.g. WP="php.exe wp-cli.phar" && $WP rewrite structure ...
        else:
            continue
        real_args = [a for k, a in enumerate(args) if a not in REDIRECTS and not (k and args[k - 1] in REDIRECTS)]
        if base == "wp.cmd":
            bad = [a for a in real_args if CMD_METACHARS & set(a)]
            if bad:
                return (f"WP-CLI через tools/wp.cmd идёт через cmd.exe, и символы {''.join(sorted(CMD_METACHARS))} "
                        f"в аргументе {bad[0][:60]!r} станут перенаправлением или конвейером. "
                        "Положи PHP в файл в scratchpad и вызови `wp eval-file <путь C:/...>`, "
                        "или запусти tools/php/php.exe tools/wp-cli.phar напрямую.")
        if "MSYS_NO_PATHCONV=1" in env or exported:
            continue
        bad = [a for a in real_args if a.startswith("/") or re.match(r"^-{0,2}[\w-]+=/", a)]
        if bad:
            return (f"Git Bash превратит аргумент WP-CLI {bad[0][:60]!r} в путь Windows "
                    "(так /%postname%/ стал /C:/Program Files/Git/%postname%/). "
                    "Добавь MSYS_NO_PATHCONV=1 перед командой, передай путь как C:/..., "
                    "или выполни команду из Python, как scripts/setup.py.")
    return None


if __name__ == "__main__":
    data = json.load(sys.stdin)
    if data.get("tool_name") != "Bash":
        sys.exit(0)
    reason = check((data.get("tool_input") or {}).get("command", ""))
    if reason:
        sys.stderr.reconfigure(encoding="utf-8")  # Windows Python defaults to cp1251; the harness reads UTF-8
        print(f"Заблокировано хуком wpcli-guard: {reason}", file=sys.stderr)
        sys.exit(2)
    sys.exit(0)
