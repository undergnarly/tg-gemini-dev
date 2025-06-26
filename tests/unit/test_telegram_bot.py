import pytest
from unittest.mock import AsyncMock, patch
from services.telegram_bot.main import start, handle_message
import httpx

# A more realistic mock for the telegram library objects
class MockMessage:
    def __init__(self, text):
        self.text = text
        self.chat_id = 12345
        self.from_user = AsyncMock()
        self.from_user.id = 54321
        # The bot replies using this method, so we mock it
        self.reply_text = AsyncMock()

class MockUpdate:
    def __init__(self, text):
        self.message = MockMessage(text)

@pytest.mark.asyncio
@patch('httpx.AsyncClient.post')
async def test_handle_message_success(mock_post):
    """
    Tests that the bot correctly handles an incoming message
    and calls the API gateway.
    """
    # Arrange
    # Create a more realistic response that doesn't crash .raise_for_status()
    mock_request = httpx.Request("POST", "http://test_url")
    mock_post.return_value = httpx.Response(202, json={"task_id": "123"}, request=mock_request)
    
    update = MockUpdate(text="Hello, bot!")
    context = AsyncMock()

    # Act
    await handle_message(update, context)

    # Assert
    # Check that the bot replied correctly
    update.message.reply_text.assert_called_once_with("✅ Task received! The AI crew is on it. I'll get back to you with the result.")

    # Check if the API was called correctly
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "http://api_gateway:8000/tasks/"
    assert kwargs['json']['text'] == "Hello, bot!"

@pytest.mark.asyncio
@patch('httpx.AsyncClient.post')
async def test_handle_message_api_error(mock_post):
    """
    Tests that the bot sends an error message if the API gateway is down.
    """
    # Arrange
    mock_post.side_effect = httpx.ConnectError("Connection refused")
    
    update = MockUpdate(text="A message that will fail.")
    context = AsyncMock()

    # Act
    await handle_message(update, context)

    # Assert
    # Check that the bot sent an error message
    update.message.reply_text.assert_called_once_with("❌ An error occurred: Could not connect to the API gateway. Please try again later.")

@pytest.mark.asyncio
async def test_start_command():
    """
    Tests the /start command handler.
    """
    # Arrange
    update = MockUpdate(text="/start")
    context = AsyncMock()

    # Act
    await start(update, context)

    # Assert
    update.message.reply_text.assert_called_once_with("Welcome! I am your autonomous development assistant. Send me a task.")
