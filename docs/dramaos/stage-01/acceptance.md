# Stage 01 验收清单

| AC | 当前状态 | 证据与人工步骤 |
|---|---|---|
| AC-1 本地授权 MP4 门控 | 工程门控通过，授权法律事实待用户确认 | `--rights-confirmed` 缺失时拒绝且不建输出目录；输入经 `local_file_input` 限定本地 file 协议；用户确认真实素材权利。 |
| AC-2 已知切点与时间线 | 合成硬切样本通过 | 30 fps 已知切点 30、60 帧，实际 30、60；用户可检查 `synthetic/result.json`。真实样本切点需人工抽样。 |
| AC-3 每镜证据与可用性 | 工程路径通过 | `real-sample/result.json` 的 8 镜各有关联 JPEG；音轨存在，ASR/视觉/叙事标为 `unavailable`。 |
| AC-4 数据协议与离线报告 | 快速验证通过 | CLI 已做 JSON Schema 与相对文件引用校验；打开 `real-sample/report.html` 检查画面。 |
| AC-5 版本、运行资源、生产隔离 | 本机证据通过 | `result.json` 记录输入 SHA-256、PySceneDetect/FFmpeg 版本及阈值；`run.json` 记录耗时与 RSS。本阶段未改生产配置或数据库。 |
| AC-6 真实样本内容质量 | 未验收 | 用户确认素材授权，抽查 8 个镜头边界和关键帧；提供许可明确的本地 ASR 模型后再检查对白；视觉/叙事标签仍需后续能力。 |

## 给用户的手动验收

1. 打开 [真实样本报告](../../../tasks/artifacts/dramaos-stage01/real-sample/report.html)，逐镜检查边界和关键帧与源片一致。
2. 如需新素材，按 [运行说明](README.md) 输入一部 30–120 秒、已授权的本地 MP4，检查 `result.json`、`run.json`、音轨和报告。
3. 如需对白，准备已授权的本地 `mlx_whisper` 模型目录并通过 `--asr-model` 运行；检查转写与源音频，注意音画起点尚未校准。

当前不建议进入 Stage 02：视频结构化拆解的硬切工程路径已可运行，但真实样本切点质量、对白和视觉语义尚未验收，不能据此推断已获得学习导演规律的能力。
