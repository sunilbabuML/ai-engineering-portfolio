import json
import logging
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
LOG_DIR = ROOT / "logs"
LOG_FILE = LOG_DIR / "agent_audit.jsonl"


class AgentAuditLogger:
    """Write structured banking audit events without account details."""

    def __init__(self, log_file: Path = LOG_FILE):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(
            f"banking.audit.{self.log_file.resolve()}"
        )
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        if not self.logger.handlers:
            handler = logging.FileHandler(
                self.log_file,
                encoding="utf-8",
            )
            handler.setFormatter(logging.Formatter("%(message)s"))
            self.logger.addHandler(handler)

    def log_tool_execution(self, tool_name: str, status: str) -> dict:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "banking_tool_execution",
            "tool_name": tool_name,
            "status": status,
        }

        self.logger.info(json.dumps(event))
        return event

    def close(self):
        """Release file handles so Windows can safely delete log files."""
        for handler in self.logger.handlers[:]:
            handler.flush()
            handler.close()
            self.logger.removeHandler(handler)
