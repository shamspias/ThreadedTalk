import logging
from collections import deque


class InMemoryLogHandler(logging.Handler):
    def __init__(self, max_bytes: int = 10 * 1024 * 1024, *args, **kwargs):
        """
        max_bytes: Maximum total size (in bytes) for stored logs.
        """
        super().__init__(*args, **kwargs)
        self.max_bytes = max_bytes
        self.logs = deque()
        self.current_size = 0

    def emit(self, record):
        try:
            msg = self.format(record)
            msg_bytes = len(msg.encode("utf-8"))
            self.logs.append(msg)
            self.current_size += msg_bytes
            # Remove oldest logs until current_size is within the allowed maximum
            while self.current_size > self.max_bytes and self.logs:
                old_msg = self.logs.popleft()
                self.current_size -= len(old_msg.encode("utf-8"))
        except Exception:
            self.handleError(record)

    def get_logs(self, offset: int = 0, limit: int = None):
        logs_list = list(self.logs)
        if limit is None:
            return logs_list[offset:]
        return logs_list[offset:offset + limit]


# Instantiate a global handler to be used across the application.
in_memory_handler = InMemoryLogHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
in_memory_handler.setFormatter(formatter)
in_memory_handler.setLevel(logging.DEBUG)
