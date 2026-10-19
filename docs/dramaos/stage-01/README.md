# Stage 01 运行说明

此实验只读取一部已获分析授权的本地 MP4，输出镜头结构化数据和离线报告。要求 Python 3.12+，ArcReel 的 `uv` 环境，以及独立 `dramaos` 依赖组。不会接入网关、生产数据库或 GPU。

```bash
uv sync --group dramaos
uv run --group dramaos python scripts/dramaos_stage01.py \
  /absolute/path/to/authorized.mp4 \
  /absolute/path/to/new-output-directory \
  --rights-confirmed
```

输出目录必须尚不存在，视频最长 120 秒；相邻帧时间戳间隔偏离中位数超过 1% 时会被拒绝（包括部分时间基较粗的恒定帧率文件）。`--rights-confirmed` 是操作者的授权声明，程序无法自动证明版权。目录内含 `result.json`、`run.json`、`report.html`、`frames/`，有音轨时还含 `audio.wav`。浏览器直接打开 `report.html` 即可离线查看；JSON 格式见 [schema.json](schema.json)。输出保留原画面和音轨，请按原素材权限管理。

如已有本地 `mlx_whisper` CLI 和**已落盘**模型目录，可以加 `--asr-model /absolute/path/to/model`。CLI 不提供默认模型、不自动下载权重。ASR 输出时间以 `audio.wav` 的零点计，源视频与音轨起点偏移目前未校准；未给模型或运行失败时 `dialogue.status=unavailable`。视觉与叙事标签本阶段始终为 `unavailable`。

当前证据样例位于 `tasks/artifacts/dramaos-stage01/`。`synthetic/` 是 30 fps、1 秒与 2 秒硬切样本的结果；`real-sample/` 来自另一仓库现有的 60.47 秒成片，仅留在本机并被 `.gitignore` 排除。完整内容质量由用户人工验收。报告中的切点是算法候选，不能视为导演意图真值。

方案、三轮审核与验收分别见 [architecture.md](architecture.md)、[review-log.md](review-log.md)、[acceptance.md](acceptance.md)。
