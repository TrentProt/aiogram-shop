import pytest
from unittest.mock import patch, AsyncMock, Mock

def test_setting():
    with patch.dict('os.environ', {
        'APP_CONFIG__API__KEY': 'test_bot_token',
        'APP_CONFIG__DB__URL': 'sqlite+aiosqlite:///test.db',
        'APP_CONFIG__DB__ECHO': 'True',
        'APP_CONFIG__ADMINS__TG_IDS': '[]'
    }):
        from app.core.config import Settings

        settings = Settings()

        assert settings.api.key == 'test_bot_token'
        assert str(settings.db.url) == 'sqlite+aiosqlite:///test.db'
        assert settings.db.echo is True
        assert settings.admins.tg_ids == []


@pytest.mark.asyncio
async def test_check_admin_new_user():
    from app.utils.utils import check_admin
    from app.core.models import Role

    mock_message = AsyncMock()
    mock_message.from_user.id = 123456
    mock_message.from_user.username = "test_user"

    mock_session = AsyncMock()

    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None

    mock_session.execute.return_value = mock_result

    with patch('app.utils.utils.settings') as mock_settings:
        mock_settings.admins.tg_ids = [123456]

        result = await check_admin(mock_message, mock_session)

        mock_session.execute.assert_called_once()
        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()

        added_user = mock_session.add.call_args[0][0]
        assert added_user.telegram_id == 123456
        assert added_user.role == Role.admin
        assert added_user.username == "test_user"
        assert result is True


@pytest.mark.asyncio
async def test_view_empty_cart(mock_message, mock_session):
    from app.handlers.cart import get_cart

    mock_session.execute.return_value.all.return_value = []

    await get_cart(mock_message, mock_session)

    mock_message.answer.assert_called_once_with('Ваша корзина пуста')