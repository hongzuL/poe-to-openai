import contextvars
import logging
import os
import secrets
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

_REQ_ID_VAR = contextvars.ContextVar("req_id", default="-")
_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
_BACKUP_COUNT = 5


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.req_id = _REQ_ID_VAR.get()
        return True


def set_current_request_id(req_id: Optional[str] = None) -> str:
    rid = (req_id or "").strip()
    if not rid or len(rid) > 64:
        rid = secrets.token_hex(4)
    _REQ_ID_VAR.set(rid)
    return rid


def get_current_request_id() -> str:
    return _REQ_ID_VAR.get()


def configure_logging(log_file_path: Optional[str] = None) -> None:
    log_level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, log_level_name, logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # 避免在 Gunicorn/Uvicorn worker 中重复添加 StreamHandler（Gunicorn 已接管 stdout/stderr）
    if not any(isinstance(h, RotatingFileHandler) for h in root_logger.handlers):
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] [pid:%(process)d] [%(req_id)s] [%(name)s] %(message)s"
        )
        req_filter = RequestIdFilter()

        target_path = Path(log_file_path or "log/app.log")
        target_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            str(target_path),
            maxBytes=_MAX_BYTES,
            backupCount=_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(req_filter)
        root_logger.addHandler(file_handler)
