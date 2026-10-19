# DramaOS X Stage 01 依赖审计

审计范围：2026-10-19 在本机 macOS arm64 的 ArcReel 工作树及现有 Python 环境观察到的事实。版本记录的是**本次环境**，不是所有部署节点的保证；Stage 01 新增隔离的 `dramaos` 依赖组，不分发第三方二进制或模型权重。

| 组件 | 当前状态与版本证据 | 许可证与边界 |
|---|---|---|
| `imageio-ffmpeg` | `pyproject.toml` 要求 `>=0.6.0`，`uv.lock` 锁定 `0.6.0`；本仓 `.venv` 实装 `0.6.0`。当前 macOS arm64 wheel 的锁文件 SHA-256 为 `b1ae3173414b5fc5f538a726c4e48ea97edc0d2cdc11f103afee655c463fa742`。`lib/infra/ffmpeg.py` 固定取随包可执行文件。 | Python 包代码为 [BSD-2-Clause](https://github.com/imageio/imageio-ffmpeg/blob/main/LICENSE)；**不能**把包代码许可套用于内含的 FFmpeg 二进制。官方说明平台 wheel 携带可执行文件：[项目 README](https://github.com/imageio/imageio-ffmpeg#readme)。 |
| wheel 内 FFmpeg | 本机执行 `-version` 返回 `ffmpeg version 7.1`，Apple clang 13.1.6。构建配置包含 `--enable-gpl`、`--enable-libx264`、`--enable-libx265`，也包含 `--enable-libvmaf`、`--enable-libopus`、`--enable-libmp3lame` 等；未见 `--enable-nonfree`。此为本机 wheel 的观察值，其他平台 wheel 须逐个核对。 | [FFmpeg 官方法律说明](https://www.ffmpeg.org/legal.html)指出默认 LGPL 2.1-or-later，启用 GPL 部分时整体适用 GPL 2-or-later。当前构建明确启用了 GPL。Stage 01 仅调用仓库现有二进制；若将此 wheel 或产物作为软件包对外分发，应另行完成对应二进制、源码、版权声明和编译配置的合规审查。 |
| `scenedetect-headless` / PySceneDetect | `pyproject.toml` 的独立 `dramaos` 组精确固定 `==0.7.2`，`uv.lock` 锁定同版；本仓 `.venv` 实装 `0.7.2`。锁文件通用 wheel SHA-256 为 `583fd5dbc2418f027a1c17c3444d0bbd8cb630357e19705c4f68ae4c1aa51ef2`。Stage 01 使用 `ContentDetector(threshold=27.0)` 的帧索引切点，生产视频审阅链不使用该依赖。 | 上游 [v0.7.2 许可证](https://github.com/Breakthrough/PySceneDetect/blob/v0.7.2/LICENSE)为 BSD-3-Clause。合成红→绿→蓝 30 fps 样本已得到 `[0,30)、[30,60)、[60,90)`，只验证该硬切样本；不能据此宣称软转场或真实短剧检测准确。 |
| `jsonschema` | `pyproject.toml` 要求 `>=4.26.0`，`uv.lock` 与本仓 `.venv` 均为 `4.26.0`；用于校验版本化 `result.json`。 | 依现有仓库依赖使用；本阶段无新增包。运行时仍须实际执行 schema 校验，依赖已安装不等于输出已合格。 |
| `mlx-whisper`（可选 ASR） | 不在 `pyproject.toml` / `uv.lock`，本仓 `.venv` 未安装；本机另一 Conda 环境中 `mlx_whisper` CLI 为 `0.4.3`（MLX `0.31.2`）。CLI 是否能读取指定本地权重并在 Stage 01 成功转录，尚未验证。 | 上游示例代码为 [MIT](https://github.com/ml-explore/mlx-examples/blob/main/LICENSE)；[官方说明](https://github.com/ml-explore/mlx-examples/blob/main/whisper/README.md)显示模型参数可指向本地目录，也可指向 Hub 并自动下载。Stage 01 只允许显式指定已落盘本地目录，不能依赖默认模型或 Hub 标识；所选**模型权重**许可须按具体模型卡另行核实。未通过本地路径与运行验证时对白状态记 `unavailable`。 |
| WhisperX、Qwen3-VL-2B-Instruct | 均未纳入 Stage 01 的本仓依赖或验证流程；视觉标签默认 `unavailable`。 | WhisperX 代码为 [BSD-2-Clause](https://github.com/m-bain/whisperX/blob/main/LICENSE)；[Qwen3-VL-2B-Instruct 模型卡](https://huggingface.co/Qwen/Qwen3-VL-2B-Instruct)标注 Apache-2.0。以上只是候选信息，不构成模型权重、输出质量或生产可用性验证。 |

## 复核点

- 每次执行将实际 FFmpeg 版本、PySceneDetect 包版本及算法参数写入 `result.json` 的 `detector` 字段；`run.json` 记录状态、错误、耗时和子进程峰值内存。FFmpeg 构建配置仅为本次依赖审计的环境观察值，其他运行环境须单独复核。
- 有限运行已得到三镜合成样本的帧边界 `0/30/60/90`，以及一份时长 `60.4667` 秒的本地产物的 8 镜结果；该次未提供可用 ASR 模型，对白状态为 `unavailable`。后者只证明此输入可完成流程，不证明真实短剧授权、切点质量或对白质量。
- 不记录网关配置或密钥；Stage 01 不读取网关私有配置，不接入网关视频生成路由。
- 授权确认只针对输入素材的使用权限。第三方模型权重、所选编解码器、二进制再分发和生成报告的对外使用，仍需按具体交付方式分别核查。
