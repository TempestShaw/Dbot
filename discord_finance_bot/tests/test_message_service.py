import unittest

from config import Config
from services.message_service import MessageService


class TestMessageService(unittest.TestCase):
    """Basic tests asserting JSON payload shape for n8n integration."""

    def test_json_shape(self):
        cfg = Config(discord_token="", channel_id=None, selected_stocks=["AAPL", "MSFT"])  # type: ignore
        svc = MessageService(cfg)
        payload = svc.generate_daily_summary_json()
        self.assertIn("macro", payload)
        self.assertIn("stocks", payload)
        self.assertIn("sectors", payload)


if __name__ == "__main__":
    unittest.main()