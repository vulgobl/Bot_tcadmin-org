import os
import subprocess
from fastapi import FastAPI, Header, HTTPException

app = FastAPI()

is_running = False
WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN", "")


@app.post("/run")
def run_anti_lag(x_webhook_token: str = Header(default="")):
    global is_running
    if WEBHOOK_TOKEN and x_webhook_token != WEBHOOK_TOKEN:
        raise HTTPException(status_code=401, detail="invalid token")

    if is_running:
        return {"ok": True, "status": "already_running"}

    is_running = True
    try:
        subprocess.Popen(
            ["timeout", "120s", "python3", "anti_lag_bot.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=os.getcwd(),
            env=os.environ.copy(),
            text=True,
        )
        return {"ok": True, "status": "started"}
    finally:
        is_running = False


