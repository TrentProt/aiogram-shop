import pytest
import asyncio
from unittest.mock import AsyncMock, Mock
from aiogram.types import Message, User
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_message():
    message = Mock(spec=Message)
    message.from_user = Mock(spec=User)
    message.from_user.id = 123456
    message.from_user.first_name = "TestUser"
    message.from_user.username = "testuser"
    message.text = "/start"
    message.answer = AsyncMock()
    message.reply = AsyncMock()
    return message


@pytest.fixture
def mock_session():
    session = AsyncMock(spec=AsyncSession)

    mock_result = AsyncMock()
    mock_result.scalars = Mock(return_value=mock_result)
    mock_result.scalar_one_or_none = AsyncMock()
    mock_result.scalar = AsyncMock()
    mock_result.all = Mock(return_value=[])
    mock_result.first = Mock(return_value=None)

    session.execute = AsyncMock(return_value=mock_result)
    session.commit = AsyncMock()
    session.add = Mock()
    session.scalar = AsyncMock()

    return session
