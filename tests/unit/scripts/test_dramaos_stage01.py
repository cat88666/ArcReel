"""Stage 01 文件入口与帧边界的快速契约验证。"""

from __future__ import annotations

import sys

import pytest

from scripts.dramaos_stage01 import aligned_shots, main, require_constant_frame_rate


def test_cut_frames_cover_video_without_overlap() -> None:
    times = tuple(index / 30 for index in range(90))

    shots = aligned_shots(times, [30, 60], 3.0)

    assert [(start, end) for start, end, _, _ in shots] == [(0, 30), (30, 60), (60, 90)]
    assert [start for _, _, start, _ in shots] == [0.0, 1.0, 2.0]
    assert shots[-1][3] == pytest.approx(3.0)


def test_out_of_range_cut_is_rejected() -> None:
    with pytest.raises(ValueError, match="切点超出"):
        aligned_shots((0.0, 0.04), [2], 0.08)


def test_single_frame_uses_stream_duration() -> None:
    assert aligned_shots((0.0,), [], 1.0) == [(0, 1, 0.0, 1.0)]


def test_variable_frame_rate_is_rejected() -> None:
    with pytest.raises(ValueError, match="可变帧率"):
        require_constant_frame_rate((0.0, 1 / 30, 2 / 30, 4 / 30))


def test_rights_are_required_before_output_creation(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    video = tmp_path / "sample.mp4"
    video.write_bytes(b"not a video")
    output = tmp_path / "result"
    monkeypatch.setattr(sys, "argv", ["dramaos_stage01.py", str(video), str(output)])

    with pytest.raises(SystemExit, match="2"):
        main()

    assert not output.exists()
