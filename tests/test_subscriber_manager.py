import unittest
from unittest.mock import AsyncMock, patch
import importlib
import sys
import os
import types

# Ensure the 'bot' package is importable
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

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
    async def execute(self, *args, **kwargs):
        pass

    async def fetch(self, *args, **kwargs):
        return []

    async def fetchval(self, *args, **kwargs):
        return 0

class FakeAcquire:
    async def __aenter__(self):
        return FakeConn()

    async def __aexit__(self, exc_type, exc, tb):
        pass

class FakePool:
    def acquire(self):
        return FakeAcquire()

async def fake_create_pool(*args, **kwargs):
    return FakePool()

# Provide dummy asyncpg module
sys.modules.setdefault('asyncpg', types.SimpleNamespace(create_pool=fake_create_pool))
sys.modules.setdefault('dotenv', types.SimpleNamespace(load_dotenv=lambda: None))
sys.modules.setdefault('telegram', types.SimpleNamespace(Bot=object))

with patch('asyncpg.create_pool', side_effect=fake_create_pool):
    if 'bot.subscriber_manager' in sys.modules:
        importlib.reload(sys.modules['bot.subscriber_manager'])
    else:
        import bot.subscriber_manager
from bot.subscriber_manager import SubscriberManager

class TestSubscriberManager(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        class TestManager(SubscriberManager):
            def __init__(self):
                self.pool = FakePool()
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

    async def test_record_and_get_users(self):
        users_data = [
            {'user_id': 1, 'language': 'en', 'status': 'never'},
            {'user_id': 2, 'language': 'en', 'status': 'active'},
            {'user_id': 3, 'language': 'fr', 'status': 'churned'},
            {'user_id': 4, 'language': None, 'status': 'active'},
            {'user_id': 5, 'language': 'es', 'status': 'never'},
            {'user_id': 6, 'language': None, 'status': 'churned'},
        ]

        class DummyConn(FakeConn):
            async def fetch(self, query, *args):
                lang = args[1] if len(args) >= 2 else None
                statuses = args[2] if len(args) >= 3 else None
                filtered = users_data
                if lang is not None:
                    # when lang is None the query should not filter
                    filtered = [u for u in filtered if u['language'] == lang]
                if statuses is not None:
                    filtered = [u for u in filtered if u['status'] in statuses]
                return [dict(user_id=u['user_id'], language=u['language'], status=u['status']) for u in filtered]

        class DummyAcquire:
            def __init__(self, conn):
                self.conn = conn
            async def __aenter__(self):
                return self.conn
            async def __aexit__(self, exc_type, exc, tb):
                pass

        self.manager.pool.acquire = lambda: DummyAcquire(DummyConn())

        en_active = await self.manager.get_users(language='en', statuses=['active'])
        self.assertEqual({u['user_id'] for u in en_active}, {2})

        all_users = await self.manager.get_users()
        self.assertEqual(len(all_users), 6)

        never = await self.manager.get_users(statuses=['never'])
        self.assertEqual({u['user_id'] for u in never}, {1,5})

        active_churn = await self.manager.get_users(statuses=['active','churned'])
        self.assertEqual({u['user_id'] for u in active_churn}, {2,3,4,6})

        none_lang = await self.manager.get_users(language=None)
        self.assertEqual(len(none_lang), 6)

    async def test_error_handling(self):
        class ErrorConn(FakeConn):
            async def execute(self, *a, **k):
                raise RuntimeError('db fail')
            async def fetch(self, *a, **k):
                raise RuntimeError('db fail')

        class DummyAcquire:
            def __init__(self, conn):
                self.conn = conn
            async def __aenter__(self):
                return self.conn
            async def __aexit__(self, exc_type, exc, tb):
                pass

        self.manager.pool.acquire = lambda: DummyAcquire(ErrorConn())

        with self.assertRaises(RuntimeError):
            await self.manager.record_user(1, 'en')

        with self.assertRaises(RuntimeError):
            await self.manager.get_users(language='en')

if __name__ == '__main__':
    unittest.main()
