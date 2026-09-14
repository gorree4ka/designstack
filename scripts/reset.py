"""Reset the local site: delete the SQLite DB and reinstall WordPress (keeps themes/plugins files).
Usage: python scripts/reset.py"""
import os, shutil, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db = os.path.join(ROOT, "wordpress", "wp-content", "database")
if os.path.isdir(db):
    shutil.rmtree(db); print("[reset] database removed")
subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "setup.py")], check=True)
