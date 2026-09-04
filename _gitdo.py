import subprocess


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "").strip() + "\n" + (p.stderr or "").strip()


rc, out = run(["git", "add", "-A"])
print("ADD_RC", rc)
rc, out = run(["git", "commit", "-m", "feat: auto setup conda/miniforge env via setup.bat, fix requirements GBK decode, fix UI flicker"])
print("COMMIT_RC", rc)
print(out[:400])
rc, out = run(["git", "push", "origin", "main"])
print("PUSH_RC", rc)
print(out[:400])
rc, out = run(["git", "log", "--oneline", "-2"])
print("LOG_RC", rc)
print(out[:300])
