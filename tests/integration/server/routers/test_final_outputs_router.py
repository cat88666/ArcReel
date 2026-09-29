from fastapi import FastAPI
from fastapi.testclient import TestClient

import lib.project.project_manager as project_manager_module
from server.auth import CurrentUserInfo, get_current_user
from server.error_handlers import register_error_handlers
from server.routers import final_outputs
from tests.auth_deps import AUTH_DEPENDENCIES


def _client(monkeypatch, tmp_path):
    manager = project_manager_module.ProjectManager(tmp_path)
    manager.create_project("demo")
    manager.create_project_metadata("demo", "Demo", "Anime", "drama")
    monkeypatch.setattr(final_outputs, "get_project_manager", lambda: manager)

    app = FastAPI()
    register_error_handlers(app)
    app.dependency_overrides[get_current_user] = lambda: CurrentUserInfo(
        id="default",
        sub="testuser",
        role="admin",
    )
    app.include_router(final_outputs.router, prefix="/api/v1", dependencies=AUTH_DEPENDENCIES)
    app.include_router(final_outputs.self_auth_router, prefix="/api/v1")
    return TestClient(app), manager.get_project_path("demo")


def test_lists_only_safe_mp4_outputs(tmp_path, monkeypatch):
    client, project_dir = _client(monkeypatch, tmp_path)
    output_dir = project_dir / "output"
    (output_dir / "第1集_final.mp4").write_bytes(b"video")
    (output_dir / "notes.txt").write_text("ignore", encoding="utf-8")
    (output_dir / ".hidden.mp4").write_bytes(b"ignore")

    response = client.get("/api/v1/projects/demo/final-outputs")

    assert response.status_code == 200
    assert response.json() == {
        "outputs": [{"name": "第1集_final.mp4", "size": 5}],
    }


def test_creates_token_for_existing_output(tmp_path, monkeypatch):
    client, project_dir = _client(monkeypatch, tmp_path)
    output_dir = project_dir / "output"
    (output_dir / "episode.mp4").write_bytes(b"video")
    calls = []
    monkeypatch.setattr(
        final_outputs,
        "create_download_token",
        lambda username, project_name: calls.append((username, project_name)) or "signed",
    )

    response = client.post("/api/v1/projects/demo/final-outputs/episode.mp4/token")

    assert response.status_code == 200
    assert response.json() == {"download_token": "signed", "expires_in": 300}
    assert calls == [("testuser", "demo")]


def test_rejects_token_for_missing_or_non_mp4_output(tmp_path, monkeypatch):
    client, project_dir = _client(monkeypatch, tmp_path)
    output_dir = project_dir / "output"
    (output_dir / "notes.txt").write_text("not a video", encoding="utf-8")

    missing = client.post("/api/v1/projects/demo/final-outputs/missing.mp4/token")
    wrong_type = client.post("/api/v1/projects/demo/final-outputs/notes.txt/token")

    assert missing.status_code == 404
    assert wrong_type.status_code == 404


def test_previews_with_ranges_and_downloads_as_attachment(tmp_path, monkeypatch):
    client, project_dir = _client(monkeypatch, tmp_path)
    output_dir = project_dir / "output"
    (output_dir / "episode.mp4").write_bytes(b"0123456789")
    monkeypatch.setattr(final_outputs, "verify_download_token", lambda token, project: {})

    preview = client.get(
        "/api/v1/projects/demo/final-outputs/episode.mp4?download_token=signed",
        headers={"Range": "bytes=2-5"},
    )
    download = client.get(
        "/api/v1/projects/demo/final-outputs/episode.mp4?download_token=signed&download=true",
    )

    assert preview.status_code == 206
    assert preview.content == b"2345"
    assert preview.headers["content-range"] == "bytes 2-5/10"
    assert preview.headers["content-disposition"].startswith("inline;")
    assert download.status_code == 200
    assert download.headers["content-disposition"].startswith("attachment;")
