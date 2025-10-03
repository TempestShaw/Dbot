class FutuRepo:
    """Futu API repository (placeholder).

    Designed to encapsulate Futu API interactions. Implementations can be
    added later without affecting service layer consumers.
    """

    def __init__(self, config):
        self.config = config

    # Example placeholder method
    def fetch_realtime_quote(self, symbol: str):
        """Fetch realtime quote from Futu (to be implemented)."""
        return {"symbol": symbol, "last": None}