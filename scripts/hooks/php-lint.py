"""PostToolUse hook: run `php -l` on any .php file written/edited by Claude.
Reads the hook JSON from stdin, exits 2 (blocking feedback) on syntax error."""
import json, os, subprocess, sys

data = json.load(sys.stdin)
path = (data.get("tool_input") or {}).get("file_path", "")
if not path.lower().endswith(".php") or not os.path.isfile(path):
    sys.exit(0)
root = os.environ.get("CLAUDE_PROJECT_DIR", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
php = os.path.join(root, "tools", "php", "php.exe")
r = subprocess.run([php, "-l", path], capture_output=True, text=True)
if r.returncode != 0:
    print(f"PHP syntax error in {path}:\n{r.stdout}{r.stderr}", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
