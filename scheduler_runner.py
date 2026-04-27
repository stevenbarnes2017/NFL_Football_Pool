import time
from wsgi import app

# Importing app triggers scheduler startup when DISABLE_APSCHEDULER is not "1"
print("[SCHEDULER] STARTED scheduler_runner.py", flush=True)
if __name__ == "__main__":
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        pass
