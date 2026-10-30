# Gunicorn settings for the football-web container (loaded by the Dockerfile CMD).
#
# One process with a few threads: a slow request (or a slow page for one user)
# no longer blocks /health or everyone else, without doubling memory. Keep a
# single process: Prometheus metrics are per-process, and a second worker would
# split /metrics between them. Override any value with GUNICORN_CMD_ARGS.
import os

bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

worker_class = "gthread"
workers = 1
threads = 4

# A worker that doesn't check in for this long is restarted (was the 30s default).
timeout = 60
# Shorter than Kubernetes' default 30s terminationGracePeriodSeconds, so in-flight
# requests finish and gunicorn exits cleanly instead of being SIGKILLed (exit 137).
graceful_timeout = 20
keepalive = 5
