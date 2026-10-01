import os
import sys
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

def run():
    # 1. Pull latest state from cloud
    try:
        subprocess.run(["git", "pull", "--rebase", "origin", "main"], capture_output=True, text=True, timeout=15)
    except Exception:
        pass

    # 2. Execute warmup tick
    python_exe = sys.executable
    subprocess.run([python_exe, "engine.py", "--tick"], timeout=30)

    # 3. If state.json was updated, push back to GitHub
    try:
        diff = subprocess.run(["git", "diff", "state.json"], capture_output=True, text=True, timeout=10)
        if diff.stdout.strip():
            subprocess.run(["git", "add", "state.json"], timeout=10)
            subprocess.run(["git", "commit", "-m", "chore: sync warmup tick [skip ci]"], timeout=10)
            subprocess.run(["git", "push", "origin", "main"], timeout=15)
    except Exception:
        pass

if __name__ == "__main__":
    run()
