"""Preview and download completed videos written to the project output directory."""

from __future__ import annotations

import asyncio
from pathlib import Path

import jwt as pyjwt
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from lib.infra.path_safety import try_safe_join
from lib.project.project_manager import get_project_manager
from server.auth import (
    DOWNLOAD_TOKEN_EXPIRY_SECONDS,
    CurrentUser,
    create_download_token,
    verify_download_token,
)
from server.i18n import Translator

router = APIRouter()
self_auth_router = APIRouter()


def _output_dir(project_name: str) -> Path | None:
    project_dir = get_project_manager().get_project_path(project_name)
    return try_safe_join(project_dir, "output")


def _output_file(project_name: str, filename: str) -> Path | None:
    if Path(filename).suffix.lower() != ".mp4":
        return None
    output_dir = _output_dir(project_name)
    if output_dir is None:
        return None
    return try_safe_join(output_dir, filename, require_file=True)


@router.get("/projects/{project_name}/final-outputs")
async def list_final_outputs(project_name: str):
    def _sync() -> list[dict[str, int | str]]:
        output_dir = _output_dir(project_name)
        if output_dir is None or not output_dir.is_dir():
            return []

        outputs: list[dict[str, int | str]] = []
        for entry in output_dir.iterdir():
            if entry.name.startswith(".") or entry.suffix.lower() != ".mp4":
                continue
            file_path = try_safe_join(output_dir, entry.name, require_file=True)
            if file_path is None:
                continue
            outputs.append({"name": entry.name, "size": file_path.stat().st_size})
        return sorted(outputs, key=lambda item: str(item["name"]).casefold())

    return {"outputs": await asyncio.to_thread(_sync)}


@router.post("/projects/{project_name}/final-outputs/{filename}/token")
async def create_final_output_token(
    project_name: str,
    filename: str,
    current_user: CurrentUser,
    _t: Translator,
):
    file_path = await asyncio.to_thread(_output_file, project_name, filename)
    if file_path is None:
        raise HTTPException(status_code=404, detail=_t("file_not_found", path=filename))
    return {
        "download_token": create_download_token(current_user.sub, project_name),
        "expires_in": DOWNLOAD_TOKEN_EXPIRY_SECONDS,
    }


@self_auth_router.get("/projects/{project_name}/final-outputs/{filename}")
async def serve_final_output(
    project_name: str,
    filename: str,
    _t: Translator,
    download_token: str = Query(...),
    download: bool = Query(False),
):
    try:
        verify_download_token(download_token, project_name)
    except pyjwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail=_t("download_expired")) from exc
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=_t("download_token_mismatch")) from exc
    except pyjwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail=_t("download_token_invalid")) from exc

    file_path = await asyncio.to_thread(_output_file, project_name, filename)
    if file_path is None:
        raise HTTPException(status_code=404, detail=_t("file_not_found", path=filename))
    return FileResponse(
        file_path,
        media_type="video/mp4",
        filename=filename,
        content_disposition_type="attachment" if download else "inline",
    )


__all__ = ["router", "self_auth_router"]
