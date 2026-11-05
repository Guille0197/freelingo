from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.auth import RegisterRequest, UserUpdateRequest
from app.services.llm_adapter import LLMAdapter


def test_profile_cannot_bypass_available_languages(monkeypatch):
    monkeypatch.setattr(settings, "AVAILABLE_TARGET_LANGUAGES", ["en-GB", "en-US"])
    for code in ("es-ES", "de-DE", "ja-JP"):
        with pytest.raises(ValidationError):
            UserUpdateRequest(target_language=code)
        with pytest.raises(ValidationError):
            RegisterRequest(
                username="learner",
                email="learner@example.com",
                password="ExamplePass1!",
                native_language="es",
                target_language=code,
            )
    assert UserUpdateRequest(target_language="en-US").target_language == "en-US"
    assert UserUpdateRequest(display_name="Learner").target_language is None


@pytest.mark.asyncio
async def test_openrouter_uses_chat_completions_and_configured_model(monkeypatch):
    monkeypatch.setattr(settings, "LLM_PROVIDER", "openrouter")
    monkeypatch.setattr(settings, "OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(settings, "OPENROUTER_MODEL", "test/model")
    monkeypatch.setattr(settings, "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    client = MagicMock()
    client.chat.completions.create = AsyncMock(
        return_value=SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="Hello!"))]
        )
    )
    with patch("app.services.llm_adapter.AsyncOpenAI", return_value=client) as factory:
        adapter = LLMAdapter()
    factory.assert_called_once_with(
        base_url="https://openrouter.ai/api/v1", api_key="test-key", max_retries=0
    )
    assert await adapter.chat([{"role": "user", "content": "Hi"}]) == "Hello!"
    assert client.chat.completions.create.call_args.kwargs["model"] == "test/model"
    client.responses.create.assert_not_called()


@pytest.mark.parametrize("key,model", [("", "test/model"), ("test-key", "")])
def test_openrouter_requires_configuration(monkeypatch, key, model):
    monkeypatch.setattr(settings, "LLM_PROVIDER", "openrouter")
    monkeypatch.setattr(settings, "OPENROUTER_API_KEY", key)
    monkeypatch.setattr(settings, "OPENROUTER_MODEL", model)
    with pytest.raises(ValueError, match="OpenRouter requires"):
        LLMAdapter()


@pytest.mark.asyncio
@pytest.mark.parametrize("user_count", [0, 1])
async def test_private_invite_only_bootstraps_empty_installation(monkeypatch, capsys, user_count):
    from app import create_private_invite

    monkeypatch.setattr(settings, "ALLOW_REGISTRATION", False)
    monkeypatch.setattr(settings, "FIRST_USER_IS_ADMIN", True)
    monkeypatch.setattr(settings, "APP_BASE_URL", "https://english.example.com")
    db = AsyncMock()
    db.scalar.return_value = user_count
    session = MagicMock()
    session.__aenter__ = AsyncMock(return_value=db)
    redis = AsyncMock()
    redis_context = MagicMock()
    redis_context.__aenter__ = AsyncMock(return_value=redis)
    with (
        patch.object(create_private_invite, "AsyncSessionLocal", return_value=session),
        patch.object(create_private_invite, "engine", dispose=AsyncMock()),
        patch.object(
            create_private_invite.Redis, "from_url", return_value=redis_context
        ) as factory,
    ):
        if user_count:
            with pytest.raises(SystemExit, match="Users already exist"):
                await create_private_invite.main()
            factory.assert_not_called()
        else:
            await create_private_invite.main()
            key, ttl, value = redis.setex.await_args.args
            assert key.startswith("invite:") and len(key) > 40
            assert ttl == 900 and value == "first-user"
            assert "https://english.example.com/register?invite=" in capsys.readouterr().out
