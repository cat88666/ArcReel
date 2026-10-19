# DramaOS X Stage 01：最小技术方案

## 目标与边界

输入一部本地、已获分析授权的 MP4，输出可追溯的镜头时间线、每镜关键帧、音轨、版本化 JSON 和静态 HTML。Stage 01 只证明拆解工程可行；不代表学会导演能力，也不进入 Stage 02–06、训练、自动成片或生产部署。用户完成最终人工验收。

## 只读审计结论

| 结论 | 代码证据 | 适用边界 |
|---|---|---|
| ArcReel 已有本地媒体探测与逐帧时间戳 | `lib/infra/media_probe.py:148-197,227-273` | 通过随包 FFmpeg 读取本地文件，不依赖 ffprobe |
| ArcReel 已有镜头切点、黑屏、卡帧检测 | `lib/video_review/signals.py:165-207` | 阈值 `SCENE_THRESHOLD=0.4` 偏向审阅提示；已知硬切样本漏检 1/2 个切点，不满足 AC-2 |
| ArcReel 已有抽帧，但现有联系表限制最多 24 帧 | `lib/video_review/contact_sheet.py:179-221` | Stage 01 需每镜独立关键帧，不能直接拿联系表替代 |
| 既有视频审阅绑定项目版本 | `server/media_tools/video_review.py:156-193` | 不适合作为任意授权 MP4 的 CLI 入口 |
| 现有网关没有视频理解接口 | 网关 `internal/provider/comfyui/executor.go:40,256-272` | H3 是生成模型，不能当作视频分析模型；本阶段不改网关 |

## 方案

1. 在 `scripts/dramaos_stage01.py` 新建独立入口，只接受扩展名 `.mp4`、容器家族含 `mp4`、且存在视频流的本地文件和明确的 `--rights-confirmed` 标记。输入最长 120 秒；相邻帧时间戳间隔偏离中位数超过 1% 时拒绝，以免切镜器估算帧号与真实帧号错位。输出目录必须与输入分离。
2. 复用 `probe_media`、`probe_video_frame_times`。已知硬切样本证明既有 `detect_signals` 会漏检，Stage 01 在独立依赖组中使用 PySceneDetect `ContentDetector`。直接以它的帧索引 `[start_frame,end_frame)` 定界，用 `frame_times` 反推秒数，避免毫秒取整偏移。每镜选中点的原始、未缩放帧作为证据。检测算法参数、运行版本和输入 SHA-256 写入结果。
3. 用 `local_file_input` 和已有 FFmpeg 提取各镜头关键帧与 16 kHz 单声道音轨；不跨模块调用私有抽帧函数，不使用网络输入。音轨独立归零，原视频与音轨起点差如无法可靠读取则标记未校准，不能声称对白与视频帧级对齐。音轨不存在时记录 `unavailable`。
4. 本机有 `mlx_whisper` CLI 时，可显式传入已落盘的本地模型目录进行 ASR；绝不自动下载。未提供可用模型时记录 `unavailable`；不得把音轨存在推断为对白文本。视觉/叙事标签同理，Stage 01 默认 `unavailable`，预留版本化字段，不伪造推断。
5. 输出 `result.json`、`frames/`、`audio.wav`（有音轨时）、`report.html`、`run.json`。`schema.json` 对结构和数值边界做机器校验；路径为输出目录相对路径，避免暴露本机绝对路径。
6. CLI 不接入平台数据库、任务队列、GPU，也不改现有模型或部署配置。失败保留具体错误并以非零退出码结束。

## 验收标准

- AC-1：输入非本地 MP4、未确认授权、缺失或不可解析时，拒绝分析且不访问网络。
- AC-2：已知切点合成视频的切点误差不超过 2 帧；镜头时间线有序、正时长、覆盖视频且不越界。
- AC-3：每个已输出镜头有真实关键帧与时间范围；音轨状态、对白状态、视觉标签状态各有明确来源或 `unavailable`。
- AC-4：JSON 符合 `schema.json`，文件引用存在；`report.html` 仅使用同目录相对路径资源，离线打开可浏览。
- AC-5：记录输入哈希、依赖/算法版本、耗时、子进程观察到的峰值 RSS（统一换算为字节）与错误；不触碰生产配置或数据库。
- AC-6：一部经许可核实的真实短剧完成解析，并由用户抽样检查切点、对白和画面标签。缺样本或模型时标记未验收，不调整标准。

## 设计取舍

最初试用 ArcReel 已有 FFmpeg 检测时，红→绿→蓝的 30 fps 合成视频只识别出 2 秒切点，漏掉 1 秒切点；PySceneDetect 0.7.2 的 `ContentDetector` 对同一样本给出 `[0,30),[30,60),[60,90)`。因此新增仅供 Stage 01 使用的 `dramaos` 依赖组，不改生产检测链。软转场仍可能漏检，本阶段只对硬切建立误差证据。现有网关没有视频理解服务，因此不接入 H3。首轮只做一个已知切点短片和一部现有短片的快速验证；完整质量判断留给用户。

## 依据

- [PySceneDetect Python API 与版本提示](https://www.scenedetect.com/api/)、[BSD-3-Clause 许可证](https://github.com/Breakthrough/PySceneDetect/blob/main/LICENSE)：作为独立 `dramaos` 依赖组使用，不进入生产默认依赖。
- [FFmpeg 法律信息](https://www.ffmpeg.org/legal.html)：具体二进制可能启用 GPL 组件，交付仅调用既有工具，不再分发二进制。
- [WhisperX 代码许可证](https://github.com/m-bain/whisperX/blob/main/LICENSE)：代码许可证不能代替模型权重授权；本阶段不自动下载。
- [Qwen3-VL-2B-Instruct 模型卡](https://huggingface.co/Qwen/Qwen3-VL-2B-Instruct)：候选视觉模型，当前未部署/未验证，不将其描述为已有能力。
