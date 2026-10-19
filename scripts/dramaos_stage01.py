"""把一部已授权的本地 MP4 拆成可追溯的镜头数据。"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import html
import importlib.metadata
import json
import platform
import shutil
import subprocess
import sys
import time
from itertools import pairwise
from pathlib import Path
from statistics import median
from typing import Any

try:
    import resource
except ImportError:  # Windows 没有 resource；分析结果仍可写出。
    resource = None

from jsonschema import ValidationError, validate

from lib.infra.ffmpeg import ffmpeg_executable, ffmpeg_status, local_file_input
from lib.infra.media_probe import MediaProbe, probe_media, probe_video_frame_times

SCHEMA_VERSION = "1.0"
MAX_DURATION_SECONDS = 120.0
SCHEMA_PATH = Path(__file__).resolve().parents[1] / "docs/dramaos/stage-01/schema.json"


def aligned_shots(
    frame_times: tuple[float, ...], cuts: list[int], duration: float
) -> list[tuple[int, int, float, float]]:
    """用切点帧索引建立连续镜头，秒数取自源视频逐帧时间戳。"""
    if any(cut <= 0 or cut >= len(frame_times) for cut in cuts):
        raise ValueError("切点超出视频帧范围")
    if duration <= frame_times[-1]:
        raise ValueError("视频流终点不晚于最后一帧")
    boundaries = sorted({0, *cuts, len(frame_times)})
    return [
        (
            start,
            end,
            frame_times[start],
            frame_times[end] if end < len(frame_times) else duration,
        )
        for start, end in pairwise(boundaries)
    ]


def require_constant_frame_rate(frame_times: tuple[float, ...]) -> None:
    """拒绝帧时距明显变化的输入，避免切镜器估算帧号与真实帧号错位。"""
    if len(frame_times) < 3:
        return
    intervals = [end - start for start, end in pairwise(frame_times)]
    typical = median(intervals)
    # ACT: 1% 容差只覆盖恒定帧率；要支持 VFR，需把切点时间映射回真实帧序。
    if typical <= 0 or any(abs(interval - typical) > typical * 0.01 for interval in intervals):
        raise ValueError("暂不支持可变帧率视频：切点帧号可能与真实帧序不一致")


def run_ffmpeg(args: list[str], *, timeout: int = 180) -> None:
    """运行受时间限制的本地 FFmpeg，并把失败原因交给 CLI。"""
    result = subprocess.run(args, capture_output=True, timeout=timeout, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode(errors="replace")[-1200:])


def extract_keyframes(video: Path, output: Path, indices: list[int]) -> list[str]:
    """一次解码精确提取每镜的一帧，不缩放原始画面。"""
    frames_dir = output / "frames"
    frames_dir.mkdir()
    expression = "+".join(f"eq(n\\,{index})" for index in indices)
    run_ffmpeg(
        [
            ffmpeg_executable(),
            "-hide_banner",
            "-nostdin",
            "-v",
            "error",
            *local_file_input(video),
            "-map",
            "0:v:0",
            "-vf",
            f"select='{expression}'",
            "-fps_mode",
            "passthrough",
            "-q:v",
            "2",
            str(frames_dir / "shot_%04d.jpg"),
        ]
    )
    paths = [f"frames/shot_{number:04d}.jpg" for number in range(1, len(indices) + 1)]
    if any(not (output / path).is_file() for path in paths):
        raise RuntimeError("关键帧数量与镜头数不符")
    return paths


def extract_audio(video: Path, output: Path) -> str:
    """将首条音轨独立归零并导出为 16 kHz 单声道 WAV。"""
    path = output / "audio.wav"
    run_ffmpeg(
        [
            ffmpeg_executable(),
            "-hide_banner",
            "-nostdin",
            "-v",
            "error",
            *local_file_input(video),
            "-map",
            "0:a:0",
            "-vn",
            "-af",
            "asetpts=PTS-STARTPTS",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "pcm_s16le",
            str(path),
        ]
    )
    return path.name


def transcribe(audio: Path, output: Path, model: Path) -> dict[str, Any]:
    """仅使用显式指定的本地 mlx_whisper 模型；失败时由调用方记为不可用。"""
    executable = shutil.which("mlx_whisper")
    if executable is None or not model.is_dir():
        raise RuntimeError("本地 mlx_whisper 或模型目录不可用")
    result = subprocess.run(
        [
            executable,
            str(audio),
            "--model",
            str(model),
            "--output-dir",
            str(output),
            "--output-name",
            "transcript",
            "--output-format",
            "json",
        ],
        capture_output=True,
        timeout=180,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode(errors="replace")[-500:])
    raw = json.loads((output / "transcript.json").read_text(encoding="utf-8"))
    segments = [
        {
            "start_seconds": float(item["start"]),
            "end_seconds": float(item["end"]),
            "text": str(item["text"]),
            "evidence": audio.name,
            "confidence": None,
        }
        for item in raw["segments"]
    ]
    return {
        "status": "available",
        "engine": "mlx_whisper",
        "model": model.name,
        "timeline": "audio_zero",
        "segments": segments,
    }


def write_report(output: Path, result: dict[str, Any]) -> None:
    """生成不依赖脚本、网络或绝对路径的离线镜头报告。"""
    rows = []
    for shot in result["shots"]:
        frame = shot["keyframe"]
        rows.append(
            f"<section><h2>{shot['id']} · {shot['start_seconds']:.3f}–{shot['end_seconds']:.3f}s</h2>"
            f'<img src="{html.escape(frame["path"], quote=True)}" alt="{shot["id"]} 关键帧">'
            f"<p>帧 {shot['start_frame']}–{shot['end_frame'] - 1}；画面语义：unavailable；叙事作用：unavailable</p></section>"
        )
    title = html.escape(result["source"]["filename"])
    content = (
        '<!doctype html><html lang="zh-CN"><meta charset="utf-8">'
        f"<title>Stage 01 · {title}</title>"
        "<style>body{font:16px system-ui;max-width:900px;margin:2rem auto;padding:0 1rem}"
        "section{border-top:1px solid #ccc;padding:1rem 0}img{max-width:100%;max-height:600px}"
        "small{color:#555}</style>"
        f"<h1>Stage 01 · {title}</h1><p>镜头数：{len(rows)}；对白状态：{result['dialogue']['status']}</p>"
        "<small>切点为算法候选；画面与叙事标签未经过模型识别。</small>" + "".join(rows) + "</html>"
    )
    (output / "report.html").write_text(content, encoding="utf-8")


async def inspect(video: Path) -> tuple[MediaProbe, tuple[float, ...], list[int]]:
    """复用 ArcReel 媒体探测，以独立切镜头器得到帧索引。"""
    probe = await probe_media(video)
    if "mp4" not in probe.container_formats or probe.first_stream("video") is None:
        raise ValueError("输入不是含视频流的 MP4")
    if probe.duration_seconds is None or probe.duration_seconds > MAX_DURATION_SECONDS:
        raise ValueError("视频时长不可用或超过 120 秒")
    times = await probe_video_frame_times(video)
    if not times:
        raise ValueError("没有可读取的视频帧")
    require_constant_frame_rate(times)
    try:
        from scenedetect import ContentDetector, detect
    except ImportError as exc:
        raise RuntimeError("缺少 Stage 01 依赖；请先运行 uv sync --group dramaos") from exc
    scenes = await asyncio.to_thread(detect, str(video), ContentDetector(threshold=27.0))
    cuts = [start.frame_num for start, _ in scenes[1:]]
    return probe, times, cuts


def validate_result(output: Path, data: dict[str, Any]) -> None:
    """校验结构及其指向的实际证据文件。"""
    validate(data, json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))
    references = [shot["keyframe"]["path"] for shot in data["shots"]]
    if data["audio"]["status"] == "available":
        references.append(data["audio"]["path"])
    references.append(data["report"])
    if any(not (output / name).is_file() for name in references):
        raise ValueError("JSON 中有不存在的证据路径")


def analyze(video: Path, output: Path, asr_model: Path | None) -> dict[str, Any]:
    """顺序完成只读分析和文件导出，输出可独立复核的 JSON。"""
    digest = hashlib.sha256()
    with video.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    probe, times, cuts = asyncio.run(inspect(video))
    video_stream = probe.first_stream("video")
    if video_stream is None or video_stream.duration_seconds is None:
        raise ValueError("视频流时长不可用")
    ranges = aligned_shots(times, cuts, video_stream.duration_seconds)
    indices = [(start + end - 1) // 2 for start, end, _, _ in ranges]
    frames = extract_keyframes(video, output, indices)
    shots = [
        {
            "id": f"shot_{number:04d}",
            "start_frame": start,
            "end_frame": end,
            "start_seconds": round(start_time, 6),
            "end_seconds": round(end_time, 6),
            "keyframe": {
                "path": frames[number - 1],
                "frame_index": indices[number - 1],
                "time_seconds": round(times[indices[number - 1]], 6),
            },
            "visual": {"status": "unavailable"},
            "narrative": {"status": "unavailable"},
        }
        for number, (start, end, start_time, end_time) in enumerate(ranges, 1)
    ]
    audio: dict[str, Any] = {"status": "unavailable", "reason": "源视频没有音轨"}
    dialogue: dict[str, Any] = {"status": "unavailable", "reason": "源视频没有音轨"}
    if probe.first_stream("audio") is not None:
        dialogue = {"status": "unavailable", "reason": "未提供本地 ASR 模型"}
        audio = {
            "status": "available",
            "path": extract_audio(video, output),
            "sample_rate": 16000,
            "timeline": "audio_zero",
            "video_offset_seconds": None,
        }
        if asr_model is not None:
            try:
                dialogue = transcribe(output / audio["path"], output, asr_model)
            except (OSError, ValueError, KeyError, RuntimeError, subprocess.TimeoutExpired) as exc:
                dialogue = {"status": "unavailable", "reason": f"ASR 未完成：{exc}"}
    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "source": {
            "filename": video.name,
            "sha256": digest.hexdigest(),
            "size_bytes": video.stat().st_size,
            "duration_seconds": round(ranges[-1][3], 6),
            "container_formats": sorted(probe.container_formats),
            "streams": [
                {
                    "kind": stream.kind,
                    "codec": stream.codec,
                    "duration_seconds": stream.duration_seconds,
                    "packet_count": stream.packet_count,
                }
                for stream in probe.streams
            ],
        },
        "detector": {
            "name": "pyscenedetect_content",
            "threshold": 27.0,
            "version": importlib.metadata.version("scenedetect-headless"),
            "ffmpeg_version": ffmpeg_status().version,
        },
        "shots": shots,
        "audio": audio,
        "dialogue": dialogue,
        "report": "report.html",
        "run": "run.json",
    }
    write_report(output, result)
    validate_result(output, result)
    (output / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main() -> int:
    """执行一次 Stage 01 分析并留下可定位的运行状态。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path, help="已授权的本地 MP4")
    parser.add_argument("output", type=Path, help="新建的输出目录")
    parser.add_argument("--rights-confirmed", action="store_true", help="确认拥有本地视频的分析权利")
    parser.add_argument("--asr-model", type=Path, help="已落盘的本地 mlx_whisper 模型目录")
    args = parser.parse_args()
    video = args.video.resolve()
    output = args.output.resolve()
    if not args.rights_confirmed:
        parser.error("必须明确提供 --rights-confirmed")
    if video.suffix.lower() != ".mp4" or not video.is_file():
        parser.error("输入必须是本地 MP4 文件，输出必须是另一个新目录")
    if output.exists():
        parser.error("输出目录已存在")
    output.mkdir(parents=True)
    started = time.perf_counter()
    run: dict[str, Any] = {"status": "failed", "error": None}
    try:
        result = analyze(video, output, args.asr_model.resolve() if args.asr_model else None)
        run["status"] = "completed"
        print(f"{output / 'result.json'} · {len(result['shots'])} shots")
        return 0
    except (OSError, ValueError, RuntimeError, ValidationError, subprocess.TimeoutExpired) as exc:
        run["error"] = str(exc)
        print(f"Stage 01 失败：{exc}", file=sys.stderr)
        return 1
    finally:
        rss = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss if resource is not None else None
        run.update(
            {
                "elapsed_seconds": round(time.perf_counter() - started, 3),
                "peak_child_rss_bytes": (rss if sys.platform == "darwin" else rss * 1024) if rss is not None else None,
                "peak_child_rss_scope": "maximum_single_child_process",
                "platform": platform.platform(),
            }
        )
        (output / "run.json").write_text(json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
