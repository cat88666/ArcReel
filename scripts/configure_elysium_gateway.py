"""Configure ArcReel to use the shared Elysium gateway.

The public gateway contract lives in this file so a fresh checkout can recreate
the provider and model defaults.  The API key is deliberately read from stdin:
provider secrets must never be committed, passed on the command line, or kept in
the parent process environment.
"""

from __future__ import annotations

import argparse
import asyncio
import copy
import json
import sys
from collections.abc import Callable
from typing import Any
from urllib import error, request

from lib.config.service import ConfigService
from lib.db import close_db
from lib.db.engine import async_session_factory
from lib.db.repositories.agent_credential_repo import AgentCredentialRepository
from lib.db.repositories.custom_provider_repo import CustomProviderRepository

GATEWAY_BASE_URL = "http://43.154.247.11"
PROVIDER_DISPLAY_NAME = "Elysium Gateway"
AGENT_CREDENTIAL_DISPLAY_NAME = "Elysium Agent (Qwen3.8)"
AGENT_MODEL = "elysium-chat"

MODEL_DEFINITIONS: tuple[dict[str, Any], ...] = (
    {
        "model_id": "elysium-chat",
        "display_name": "Elysium Chat",
        "endpoint": "openai-chat",
        "is_default": True,
        "is_enabled": True,
    },
    {
        "model_id": "elysium-image",
        "display_name": "Elysium Image",
        "endpoint": "openai-images",
        "is_default": True,
        "is_enabled": True,
    },
    {
        "model_id": "elysium-video",
        "display_name": "Elysium Video",
        "endpoint": "openai-video",
        "is_default": True,
        "is_enabled": True,
        "supported_durations": list(range(1, 16)),
        "resolution": "720p",
    },
)


def model_definitions() -> list[dict[str, Any]]:
    """Return independent model dictionaries suitable for repository writes."""
    models = copy.deepcopy(MODEL_DEFINITIONS)
    for model in models:
        durations = model.get("supported_durations")
        if durations is not None:
            model["supported_durations"] = json.dumps(durations)
    return models


def default_settings(provider_id: int) -> dict[str, str]:
    """Return every gateway-backed global model selection."""
    prefix = f"custom-{provider_id}"
    chat = f"{prefix}/elysium-chat"
    image = f"{prefix}/elysium-image"
    video = f"{prefix}/elysium-video"
    return {
        "default_text_backend": chat,
        "text_backend_simple": chat,
        "text_backend_complex": chat,
        "default_image_backend": image,
        "default_image_backend_t2i": image,
        "default_image_backend_i2i": image,
        "default_video_backend": video,
        "default_video_backend_i2v": video,
        "default_video_backend_r2v": video,
        "default_audio_backend": "",
        "video_generate_audio": "true",
    }


def validate_gateway(
    api_key: str,
    *,
    urlopen: Callable[..., Any] = request.urlopen,
) -> list[str]:
    """Verify the remote gateway contract without making a paid generation call."""
    try:
        with urlopen(f"{GATEWAY_BASE_URL}/health", timeout=10) as response:
            if response.status != 200:
                raise RuntimeError(f"gateway health returned HTTP {response.status}")
        models_request = request.Request(
            f"{GATEWAY_BASE_URL}/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        with urlopen(models_request, timeout=10) as response:
            payload = json.load(response)
    except (error.HTTPError, error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"gateway validation failed: {exc}") from exc

    available = sorted(item.get("id", "") for item in payload.get("data", []))
    required = {model["model_id"] for model in MODEL_DEFINITIONS}
    missing = sorted(required - set(available))
    if missing:
        raise RuntimeError(f"gateway is missing required models: {', '.join(missing)}")
    return available


async def apply_configuration(api_key: str) -> tuple[int, bool, int]:
    """Create or reconcile the provider, Agent credential, and global defaults."""
    async with async_session_factory() as session:
        provider_repo = CustomProviderRepository(session)
        agent_repo = AgentCredentialRepository(session)
        config_service = ConfigService(session)
        providers = await provider_repo.list_providers()
        matches = [
            provider
            for provider in providers
            if provider.display_name == PROVIDER_DISPLAY_NAME or provider.base_url.rstrip("/") == GATEWAY_BASE_URL
        ]
        if len(matches) > 1:
            raise RuntimeError("multiple Elysium gateway providers exist; resolve duplicates first")

        created = not matches
        if created:
            provider = await provider_repo.create_provider(
                display_name=PROVIDER_DISPLAY_NAME,
                discovery_format="openai",
                base_url=GATEWAY_BASE_URL,
                api_key=api_key,
                models=model_definitions(),
            )
        else:
            provider = matches[0]
            await provider_repo.update_provider(
                provider.id,
                display_name=PROVIDER_DISPLAY_NAME,
                discovery_format="openai",
                base_url=GATEWAY_BASE_URL,
                api_key=api_key,
            )
            await provider_repo.replace_models(provider.id, model_definitions())

        for key, value in default_settings(provider.id).items():
            await config_service.set_setting(key, value)

        agent_credentials = await agent_repo.list_for_user()
        agent_matches = [
            credential
            for credential in agent_credentials
            if credential.display_name == AGENT_CREDENTIAL_DISPLAY_NAME
            or credential.base_url.rstrip("/") == GATEWAY_BASE_URL
        ]
        if len(agent_matches) > 1:
            raise RuntimeError("multiple Elysium Agent credentials exist; resolve duplicates first")
        agent_values = {
            "preset_id": "__custom__",
            "display_name": AGENT_CREDENTIAL_DISPLAY_NAME,
            "base_url": GATEWAY_BASE_URL,
            "api_key": api_key,
            "model": AGENT_MODEL,
            "haiku_model": AGENT_MODEL,
            "sonnet_model": AGENT_MODEL,
            "opus_model": AGENT_MODEL,
            "subagent_model": AGENT_MODEL,
        }
        if agent_matches:
            agent_credential = await agent_repo.update(agent_matches[0].id, **agent_values)
            if agent_credential is None:
                raise RuntimeError("Elysium Agent credential disappeared during reconciliation")
        else:
            agent_credential = await agent_repo.create(**agent_values)
        await agent_repo.set_active(agent_credential.id)
        await session.commit()
        return provider.id, created, agent_credential.id


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--api-key-stdin",
        action="store_true",
        help="read the gateway API key from stdin",
    )
    return parser.parse_args()


async def _run() -> int:
    args = _parse_args()
    if not args.api_key_stdin:
        print("error: --api-key-stdin is required", file=sys.stderr)
        return 2
    api_key = sys.stdin.readline().strip()
    if not api_key:
        print("error: gateway API key is empty", file=sys.stderr)
        return 2

    available = validate_gateway(api_key)
    provider_id, created, agent_credential_id = await apply_configuration(api_key)
    action = "created" if created else "updated"
    print(f"Elysium gateway {action}: custom-{provider_id}")
    print(f"Gateway: {GATEWAY_BASE_URL}")
    print(f"Models: {', '.join(available)}")
    print(f"Active Agent credential: {agent_credential_id} ({AGENT_MODEL})")
    print("Restart ArcReel if it was already running.")
    return 0


def main() -> int:
    try:
        return asyncio.run(_run())
    finally:
        asyncio.run(close_db())


if __name__ == "__main__":
    raise SystemExit(main())
