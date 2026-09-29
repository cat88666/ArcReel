from __future__ import annotations

import io
import json
from dataclasses import dataclass, field
from typing import Any
from urllib import request

import pytest

from scripts import configure_elysium_gateway as gateway_config


@dataclass
class _Provider:
    id: int
    display_name: str
    discovery_format: str
    base_url: str
    api_key: str


@dataclass
class _AgentCredential:
    id: int
    preset_id: str
    display_name: str
    base_url: str
    api_key: str
    model: str | None
    haiku_model: str | None
    sonnet_model: str | None
    opus_model: str | None
    subagent_model: str | None
    is_active: bool = False


@dataclass
class _State:
    providers: list[_Provider] = field(default_factory=list)
    models: dict[int, list[dict[str, Any]]] = field(default_factory=dict)
    settings: dict[str, str] = field(default_factory=dict)
    agent_credentials: list[_AgentCredential] = field(default_factory=list)
    commits: int = 0


class _Session:
    def __init__(self, state: _State):
        self.state = state

    async def commit(self) -> None:
        self.state.commits += 1


class _SessionContext:
    def __init__(self, state: _State):
        self.session = _Session(state)

    async def __aenter__(self) -> _Session:
        return self.session

    async def __aexit__(self, *_args: object) -> None:
        return None


class _SessionFactory:
    def __init__(self, state: _State):
        self.state = state

    def __call__(self) -> _SessionContext:
        return _SessionContext(self.state)


class _ProviderRepo:
    def __init__(self, session: _Session):
        self.state = session.state

    async def list_providers(self) -> list[_Provider]:
        return self.state.providers

    async def create_provider(self, **values: Any) -> _Provider:
        models = values.pop("models")
        provider = _Provider(id=1, **values)
        self.state.providers.append(provider)
        self.state.models[provider.id] = models
        return provider

    async def update_provider(self, provider_id: int, **values: Any) -> _Provider:
        provider = self.state.providers[0]
        assert provider.id == provider_id
        for key, value in values.items():
            setattr(provider, key, value)
        return provider

    async def replace_models(self, provider_id: int, models: list[dict[str, Any]]) -> None:
        self.state.models[provider_id] = models


class _AgentCredentialRepo:
    def __init__(self, session: _Session):
        self.state = session.state

    async def list_for_user(self) -> list[_AgentCredential]:
        return self.state.agent_credentials

    async def create(self, **values: Any) -> _AgentCredential:
        credential = _AgentCredential(id=1, **values)
        self.state.agent_credentials.append(credential)
        return credential

    async def update(self, credential_id: int, **values: Any) -> _AgentCredential:
        credential = self.state.agent_credentials[0]
        assert credential.id == credential_id
        for key, value in values.items():
            setattr(credential, key, value)
        return credential

    async def set_active(self, credential_id: int) -> None:
        for credential in self.state.agent_credentials:
            credential.is_active = credential.id == credential_id


class _ConfigService:
    def __init__(self, session: _Session):
        self.state = session.state

    async def set_setting(self, key: str, value: str) -> None:
        self.state.settings[key] = value


class _Response(io.BytesIO):
    def __init__(self, payload: object, status: int = 200):
        super().__init__(json.dumps(payload).encode())
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.close()


def test_validate_gateway_requires_all_shipped_models() -> None:
    calls: list[str] = []

    def urlopen(target: str | request.Request, **_kwargs: Any) -> _Response:
        url = target.full_url if isinstance(target, request.Request) else target
        calls.append(url)
        if url.endswith("/health"):
            return _Response({"status": "ok"})
        return _Response({"data": [{"id": model["model_id"]} for model in gateway_config.MODEL_DEFINITIONS]})

    assert gateway_config.validate_gateway("secret", urlopen=urlopen) == [
        "elysium-chat",
        "elysium-image",
        "elysium-video",
    ]
    assert calls == [
        "http://43.154.247.11/health",
        "http://43.154.247.11/v1/models",
    ]


def test_validate_gateway_rejects_incomplete_catalog() -> None:
    def urlopen(target: str | request.Request, **_kwargs: Any) -> _Response:
        url = target.full_url if isinstance(target, request.Request) else target
        if url.endswith("/health"):
            return _Response({"status": "ok"})
        return _Response({"data": [{"id": "elysium-chat"}]})

    with pytest.raises(RuntimeError, match="elysium-image, elysium-video"):
        gateway_config.validate_gateway("secret", urlopen=urlopen)


def test_model_definitions_are_independent() -> None:
    first = gateway_config.model_definitions()
    first[0]["display_name"] = "changed"

    assert gateway_config.model_definitions()[0]["display_name"] == "Elysium Chat"
    assert json.loads(gateway_config.model_definitions()[2]["supported_durations"]) == list(range(1, 16))


def test_default_settings_cover_every_supported_model_bucket() -> None:
    settings = gateway_config.default_settings(7)

    assert settings == {
        "default_text_backend": "custom-7/elysium-chat",
        "text_backend_simple": "custom-7/elysium-chat",
        "text_backend_complex": "custom-7/elysium-chat",
        "default_image_backend": "custom-7/elysium-image",
        "default_image_backend_t2i": "custom-7/elysium-image",
        "default_image_backend_i2i": "custom-7/elysium-image",
        "default_video_backend": "custom-7/elysium-video",
        "default_video_backend_i2v": "custom-7/elysium-video",
        "default_video_backend_r2v": "custom-7/elysium-video",
        "default_audio_backend": "",
        "video_generate_audio": "true",
    }


@pytest.mark.asyncio
async def test_apply_configuration_is_idempotent(monkeypatch: pytest.MonkeyPatch) -> None:
    state = _State()
    monkeypatch.setattr(gateway_config, "async_session_factory", _SessionFactory(state))
    monkeypatch.setattr(gateway_config, "CustomProviderRepository", _ProviderRepo)
    monkeypatch.setattr(gateway_config, "AgentCredentialRepository", _AgentCredentialRepo)
    monkeypatch.setattr(gateway_config, "ConfigService", _ConfigService)

    assert await gateway_config.apply_configuration("first-key") == (1, True, 1)
    assert await gateway_config.apply_configuration("replacement-key") == (1, False, 1)

    assert len(state.providers) == 1
    assert state.providers[0].api_key == "replacement-key"
    assert [model["model_id"] for model in state.models[1]] == [
        "elysium-chat",
        "elysium-image",
        "elysium-video",
    ]
    assert state.settings["default_video_backend_r2v"] == "custom-1/elysium-video"
    assert len(state.agent_credentials) == 1
    agent_credential = state.agent_credentials[0]
    assert agent_credential.api_key == "replacement-key"
    assert agent_credential.is_active is True
    assert {
        agent_credential.model,
        agent_credential.haiku_model,
        agent_credential.sonnet_model,
        agent_credential.opus_model,
        agent_credential.subagent_model,
    } == {"elysium-chat"}
    assert state.commits == 2
