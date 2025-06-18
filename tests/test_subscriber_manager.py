import unittest
from unittest.mock import AsyncMock, patch
import importlib
import sys

# Provide fake DB connection before importing the module
class FakeCursor:
    def execute(self, *args, **kwargs):
        pass
    def fetchall(self):
        return []
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        pass

class FakeConn:
    def cursor(self):
        return FakeCursor()
    def commit(self):
        pass

with patch('psycopg2.connect', return_value=FakeConn()):
    if 'bot.subscriber_manager' in sys.modules:
        importlib.reload(sys.modules['bot.subscriber_manager'])
    else:
        import bot.subscriber_manager
from bot.subscriber_manager import SubscriberManager

class TestSubscriberManager(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        class TestManager(SubscriberManager):
            def __init__(self):
                self.conn = FakeConn()
        self.manager = TestManager()

    async def test_add_subscriber_invite(self):
        with patch('bot.subscriber_manager.Bot') as MockBot:
            mock_bot = MockBot.return_value
            mock_bot.export_chat_invite_link = AsyncMock(return_value='link')
            mock_bot.send_message = AsyncMock()
            with patch('bot.subscriber_manager.PLANS', {'trial': {'name': 'Trial', 'duration_days': 1}}), \
                 patch('bot.subscriber_manager.CHANNELS', {'main': '@channel'}):
                result = await self.manager.add_subscriber(user_id=1, plan_name='Trial')
                self.assertTrue(result)
                mock_bot.export_chat_invite_link.assert_called_with(chat_id='@channel')
                mock_bot.send_message.assert_called_with(chat_id=1, text='Join @channel: link')

if __name__ == '__main__':
    unittest.main()
