class StatusService:
    """Collects status messages and notifies listeners."""

    def __init__(self) -> None:
        self.messages = []
        self._listeners = []

    def add_listener(self, listener):
        """Register a callback to receive messages."""
        self._listeners.append(listener)

    def add_message(self, message: str) -> None:
        """Store ``message`` and notify listeners."""
        self.messages.append(message)
        for cb in list(self._listeners):
            try:
                cb(message)
            except Exception:
                pass
