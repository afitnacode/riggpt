"""Gunicorn config — filters noisy HTTP 200 access log lines for polling endpoints.

Usage: gunicorn --config gunicorn_conf.py app:app
"""
import gunicorn.glogging

# Endpoints that fire every few seconds and spam journald with 200s
_NOISY_PATHS = frozenset([
    '/api/status',
    '/api/ghost/status',
    '/api/discord/status',
    '/api/ctrl/status',
    '/api/log/stats',
])


class QuietAccessLogger(gunicorn.glogging.Logger):
    """Suppress 200 responses on high-frequency polling endpoints."""

    def access(self, resp, req, environ, request_time):
        # resp.status is a string like '200 OK' or an int depending on version
        status = str(getattr(resp, 'status', ''))
        if status.startswith('200'):
            path = environ.get('PATH_INFO', '')
            if path in _NOISY_PATHS:
                return  # swallow this line
        super().access(resp, req, environ, request_time)


# Gunicorn config variables
logger_class = QuietAccessLogger
