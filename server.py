import os
import subprocess
import threading
from datetime import datetime
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import PlainTextResponse
# pylint: disable=invalid-name
app = FastAPI()

is_running = False
current_proc: subprocess.Popen | None = None
WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN", "")
LOG_FILE = os.getenv("ON_DEMAND_LOG", "bot_on_demand.log")


@app.get("/")
def health():
    return {"ok": True, "service": "tcadmin-bot", "running": is_running}


@app.get("/logs", response_class=PlainTextResponse)
def get_logs():
    if not os.path.exists(LOG_FILE):
        return "(no logs yet)\n"
    try:
        with open(LOG_FILE, "r") as fp:
            data = fp.readlines()
        return "".join(data[-400:])
    except Exception as e:
        return f"error reading logs: {e}\n"


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
    start_line = f"===== START {datetime.utcnow().isoformat()}Z =====\n"
    print(start_line.strip())
    log_fp.write("\n" + start_line)
    log_fp.flush()

    env = os.environ.copy()
    cmd = ["timeout", "300s", "python3", "anti_lag_bot.py"]  # 5 minutos
    current_proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=os.getcwd(),
        env=env,
        text=True,
        bufsize=1,
    )

    def _tee_output(proc, fp):
        for line in proc.stdout:
            try:
                print(line.rstrip())
                fp.write(line)
            except Exception:
                pass
        try:
            fp.flush()
        except Exception:
            pass

    is_running = True

    def _wait_and_release():
        global is_running, current_proc
        code = current_proc.wait()
        exit_line = f"===== EXIT code={code} {datetime.utcnow().isoformat()}Z =====\n"
        print(exit_line.strip())
        log_fp.write(exit_line)
        try:
            log_fp.flush()
            log_fp.close()
        except Exception:
            pass
        is_running = False
        current_proc = None

    threading.Thread(target=_tee_output, args=(current_proc, log_fp), daemon=True).start()
    threading.Thread(target=_wait_and_release, daemon=True).start()

    return {"ok": True, "status": "started", "pid": current_proc.pid}


