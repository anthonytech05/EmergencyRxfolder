class BaseSMSBackend:
    """Interface every SMS backend (Termii, Twilio, console) must implement."""

    def send(self, to: str, message: str) -> bool:
        raise NotImplementedError
