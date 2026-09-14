"""Provision the local WordPress environment from scratch (idempotent).

Downloads portable PHP 8.3 (NTS x64), WP-CLI, WordPress core and the SQLite
Database Integration plugin; writes php.ini, wp-content/db.php, wp-config.php;
installs the site with credentials from .env (created if missing).

Usage:  python scripts/setup.py [--force-core]
"""
import hashlib, json, os, re, secrets, shutil, subprocess, sys, urllib.request, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS, TMP, WP = (os.path.join(ROOT, d) for d in ("tools", ".tmp", "wordpress"))
PHP_MAJOR = "8.3"
PHP_EXE = os.path.join(TOOLS, "php", "php.exe")
WPCLI = os.path.join(TOOLS, "wp-cli.phar")
PORT = "8080"

def log(m): print(f"[setup] {m}", flush=True)

def download(url, dst):
    if os.path.exists(dst): return dst
    log(f"download {url}")
    urllib.request.urlretrieve(url, dst); return dst

def env_file():
    p = os.path.join(ROOT, ".env"); env = {}
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1); env[k] = v
    changed = False
    for k, v in {"WP_URL": f"http://localhost:{PORT}", "WP_PORT": PORT, "WP_ADMIN_USER": "admin",
                 "WP_ADMIN_PASSWORD": secrets.token_urlsafe(12), "WP_ADMIN_EMAIL": "admin@example.com"}.items():
        if k not in env: env[k] = v; changed = True
    if changed:
        open(p, "w", encoding="utf-8").write("".join(f"{k}={v}\n" for k, v in env.items()))
    return env

def install_php():
    if os.path.exists(PHP_EXE): return
    rel = json.load(urllib.request.urlopen("https://windows.php.net/downloads/releases/releases.json"))
    build = rel[PHP_MAJOR][f"nts-vs16-x64" if PHP_MAJOR in ("8.1", "8.2", "8.3") else "nts-vs17-x64"]
    z = download("https://windows.php.net/downloads/releases/" + build["zip"]["path"], os.path.join(TMP, "php.zip"))
    if hashlib.sha256(open(z, "rb").read()).hexdigest() != build["zip"]["sha256"]:
        sys.exit("PHP zip checksum mismatch")
    zipfile.ZipFile(z).extractall(os.path.join(TOOLS, "php"))
    ini = os.path.join(TOOLS, "php", "php.ini")
    s = open(ini + "-development", encoding="utf-8", errors="ignore").read()
    s = s.replace(';extension_dir = "ext"', 'extension_dir = "ext"')
    for ext in ["curl", "mbstring", "openssl", "pdo_sqlite", "sqlite3", "gd", "zip", "intl", "exif", "fileinfo", "pdo_mysql", "mysqli"]:
        s = re.sub(r"^;extension=%s\s*$" % ext, "extension=%s" % ext, s, flags=re.M)
    for k, v in {"memory_limit": "512M", "upload_max_filesize": "64M", "post_max_size": "64M", "max_execution_time": "300"}.items():
        s = re.sub(r"^%s = .*$" % k, f"{k} = {v}", s, flags=re.M)
    s = re.sub(r"^;?date.timezone =.*$", "date.timezone = Europe/Moscow", s, flags=re.M)
    open(ini, "w", encoding="utf-8").write(s)
    log(f"PHP installed: {PHP_EXE}")

def wp(*args, check=True):
    return subprocess.run([PHP_EXE, "-d", "memory_limit=512M", WPCLI, *args], cwd=WP, check=check, text=True)

def main():
    force = "--force-core" in sys.argv
    os.makedirs(TMP, exist_ok=True); os.makedirs(TOOLS, exist_ok=True)
    env = env_file()
    install_php()
    download("https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar", WPCLI)
    for f in ("wp.cmd", "php.cmd"):
        p = os.path.join(TOOLS, f)
        if not os.path.exists(p):
            body = r'"%~dp0php\php.exe" -d memory_limit=512M "%~dp0wp-cli.phar" %*' if f == "wp.cmd" else r'"%~dp0php\php.exe" %*'
            open(p, "w", newline="\r\n").write("@echo off\n" + body + "\n")
    if force or not os.path.exists(os.path.join(WP, "wp-load.php")):
        z = download("https://wordpress.org/latest.zip", os.path.join(TMP, "wordpress.zip"))
        zipfile.ZipFile(z).extractall(ROOT)  # extracts into ROOT/wordpress, keeps existing wp-content files
        log("WordPress core extracted")
    plug = os.path.join(WP, "wp-content", "plugins", "sqlite-database-integration")
    if not os.path.isdir(plug):
        z = download("https://downloads.wordpress.org/plugin/sqlite-database-integration.latest-stable.zip", os.path.join(TMP, "sqlite.zip"))
        zipfile.ZipFile(z).extractall(os.path.join(WP, "wp-content", "plugins"))
    dbphp = os.path.join(WP, "wp-content", "db.php")
    if not os.path.exists(dbphp):
        s = open(os.path.join(plug, "db.copy"), encoding="utf-8").read()
        s = s.replace("'{SQLITE_IMPLEMENTATION_FOLDER_PATH}'", "__DIR__ . '/plugins/sqlite-database-integration'")
        s = s.replace("{SQLITE_PLUGIN}", "sqlite-database-integration/load.php")
        open(dbphp, "w", encoding="utf-8").write(s)
    if not os.path.exists(os.path.join(WP, "wp-config.php")):
        extra = "\n".join([
            "define( 'WP_ENVIRONMENT_TYPE', 'local' );", "define( 'WP_DEBUG', true );", "define( 'WP_DEBUG_LOG', true );",
            "define( 'WP_DEBUG_DISPLAY', false );", "define( 'SCRIPT_DEBUG', true );", "define( 'FS_METHOD', 'direct' );",
            "define( 'DISALLOW_FILE_EDIT', true );", "define( 'AUTOMATIC_UPDATER_DISABLED', true );",
            "define( 'DB_DIR', __DIR__ . '/wp-content/database/' );", "define( 'DB_FILE', '.ht.sqlite' );"])
        subprocess.run([PHP_EXE, WPCLI, "config", "create", "--dbname=wordpress", "--dbuser=root", "--dbpass=root",
                        "--dbhost=127.0.0.1", "--skip-check", "--extra-php"], cwd=WP, input=extra, text=True, check=True)
    if wp("core", "is-installed", check=False).returncode != 0:
        wp("core", "install", f"--url={env['WP_URL']}", "--title=DesignStack", f"--admin_user={env['WP_ADMIN_USER']}",
           f"--admin_password={env['WP_ADMIN_PASSWORD']}", f"--admin_email={env['WP_ADMIN_EMAIL']}", "--skip-email")
        wp("language", "core", "install", "ru_RU", "--activate")
        wp("option", "update", "timezone_string", "Europe/Moscow")
        wp("rewrite", "structure", "/%postname%/", "--hard")
        wp("plugin", "delete", "hello", "akismet", check=False)
        wp("plugin", "activate", "sqlite-database-integration")
    # Git Bash rewrites arguments that start with "/" into Windows paths: a manual `wp rewrite structure '/%postname%/'`
    # from Git Bash on 2026-09-10 stored /C:/Program%20Files/Git/%postname%/. Check the stored value on every run and repair it.
    permalink = lambda: subprocess.run([PHP_EXE, WPCLI, "option", "get", "permalink_structure"], cwd=WP,
                                       text=True, capture_output=True).stdout.strip()
    if permalink() != "/%postname%/":
        log(f"permalink_structure is {permalink()!r}, resetting to /%postname%/")
        wp("rewrite", "structure", "/%postname%/", "--hard")
        if permalink() != "/%postname%/":
            sys.exit(f"permalink_structure is still {permalink()!r}")
    log(f"Done. Start: scripts/start.cmd   Admin: {env['WP_URL']}/wp-admin  (creds in .env)")

if __name__ == "__main__":
    main()
