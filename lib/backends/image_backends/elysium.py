"""Elysium Gateway 图片协议适配器。"""

from __future__ import annotations

from lib.backends.image_backends.base import ImageGenerationRequest
from lib.backends.image_backends.openai import OpenAIImageBackend, _resolve_openai_params

_MAX_REFERENCE_IMAGES = 10


class ElysiumImageBackend(OpenAIImageBackend):
    """使用 OpenAI SDK 传输 Elysium 网关的窄图片契约。"""

    @property
    def max_reference_images(self) -> int:
        return _MAX_REFERENCE_IMAGES

    def _build_create_kwargs(self, request: ImageGenerationRequest) -> dict:
        kwargs = {
            "model": self._model,
            "prompt": request.prompt,
            "n": 1,
            "size": _resolve_openai_params(request.image_size, request.aspect_ratio)["size"],
        }
        if request.seed is not None:
            kwargs["seed"] = request.seed
        return kwargs

    def _build_edit_kwargs(self, request: ImageGenerationRequest, image_files: list) -> dict:
        return {
            "model": self._model,
            "image": image_files,
            "prompt": request.prompt,
            "size": _resolve_openai_params(request.image_size, request.aspect_ratio)["size"],
        }

    def _result_quality(self, request: ImageGenerationRequest) -> None:
        return None
