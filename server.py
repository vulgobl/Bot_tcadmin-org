import os
import subprocess
import threading
from datetime import datetime
from fastapi import FastAPI, Header, HTTPException
# pylint: disable=invalid-name
app = FastAPI()

is_running = False
current_proc: subprocess.Popen | None = None
WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN", "")
LOG_FILE = os.getenv("ON_DEMAND_LOG", "bot_on_demand.log")


@app.get("/")
def health():
    return {"ok": True, "service": "tcadmin-bot", "running": is_running}


@app.post("/run")
def run_anti_lag(x_webhook_token: str = Header(default="")):
    global is_running
    if WEBHOOK_TOKEN and x_webhook_token != WEBHOOK_TOKEN:
        raise HTTPException(status_code=401, detail="invalid token")

    global is_running, current_proc
    if is_running and current_proc and current_proc.poll() is None:
        return {"ok": True, "status": "already_running"}

    # prepara log file
    log_fp = open(LOG_FILE, "a", buffering=1)
    log_fp.write(f"\n===== START {datetime.utcnow().isoformat()}Z =====\n")
    log_fp.flush()

    env = os.environ.copy()
    cmd = ["timeout", "120s", "python3", "anti_lag_bot.py"]
    current_proc = subprocess.Popen(
        cmd,
        stdout=log_fp,
        stderr=subprocess.STDOUT,
        cwd=os.getcwd(),
        env=env,
        text=True,
    )

    is_running = True

    def _wait_and_release():
        global is_running, current_proc
        code = current_proc.wait()
        log_fp.write(f"===== EXIT code={code} {datetime.utcnow().isoformat()}Z =====\n")
        try:
            log_fp.flush()
            log_fp.close()
        except Exception:
            pass
        is_running = False
        current_proc = None

    threading.Thread(target=_wait_and_release, daemon=True).start()

    return {"ok": True, "status": "started", "pid": current_proc.pid}


