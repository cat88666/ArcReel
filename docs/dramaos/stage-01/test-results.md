# Stage 01 快速验证结果

日期：2026-10-19。范围：一个 3 秒已知硬切合成视频、一个项目现有 60.47 秒成片；没有扩大成测试矩阵。环境：macOS arm64，ArcReel `codex/dramaos-stage01`，随包 FFmpeg 7.1，PySceneDetect 0.7.2。

| 项目 | 观察结果 | 判定 |
|---|---|---|
| 原有 ArcReel `detect_signals` | 红→绿→蓝合成视频只识别 2 秒切点，漏掉 1 秒切点 | 不满足 AC-2；已改用独立 PySceneDetect |
| 已知切点合成视频 | 源 30 fps、90 帧，预期 `[0,30),[30,60),[60,90)`，实际完全一致；误差 0 帧 | AC-2 的这一硬切样本通过 |
| 合成结果结构 | `synthetic/result.json` 由 CLI 使用 `schema.json` 校验通过；3 张关键帧真实存在；无音轨时明确 `unavailable` | AC-3/4 基础路径通过 |
| 现有成片 | 60.466667 秒，输出 8 镜、8 张不同关键帧与 `audio.wav`，`report.html` 和 `run.json` 均存在，运行状态 `completed` | AC-3/4 工程路径通过；切点质量待人工抽样 |
| 对白与视觉 | 未提供已授权的本地 ASR 权重，`dialogue.status=unavailable`；视觉与叙事均 `unavailable` | AC-6 的语义/对白部分未验收 |
| 定向单元用例 | `tests/unit/scripts/test_dramaos_stage01.py` 5 passed；有一条既有 SQLite 反射 warning | 通过；未做完整测试集 |
| 审核后边界复核 | 单帧时长从视频流时长取值；帧间隔偏差超过 1% 会被拒绝；屏蔽 `scenedetect` 导入后脚本模块仍可加载；两份本地结果再次通过 Schema 校验 | 已修复默认 CI 收集、末帧时长及切点错位风险；量化较粗的恒定帧率可能被保守拒绝 |
| 静态检查 | `ruff check`、`ruff format --check`、`basedpyright` 对新增脚本通过；`py_compile` 与 `git diff --check` 通过 | 通过 |

证据：`tasks/artifacts/dramaos-stage01/synthetic/`、本机 `real-sample/`；合成视频保存在 `tasks/artifacts/dramaos-stage01/known-cuts.mp4`。真实样本来源是 `llm-modes-gateway/tasks/artifacts/openclaw-acceptance-20261016/final-accepted-candidate.mp4`，源 SHA-256 为 `4bafabdd595297a4f064fb868517eaf85f552c6d98fd4f18162e08e9806954b1`。`real-sample/` 已从版本控制排除；本次仅根据它是用户现有项目产物进行本地分析，对外再分发权利仍需用户判断。

局限：真实样本 8 个切点的漏检/误检尚未逐镜人工核对；没有完成对白或画面模型质量验证，也没有性能压力测试。合成样本只覆盖两次硬切，不证明软转场召回率。
