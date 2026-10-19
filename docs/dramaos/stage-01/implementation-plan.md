# DramaOS X Stage 01 实施计划

- 类型：调研验证与独立实验代码。
- 调研来源：`architecture.md` 的只读审计结论；不修改现有生产调用链。
- 人工决策：真实样本的分析授权由用户确认；机器无法从文件本身证明授权。完整内容质量由用户验收。

## 步骤

1. `scripts/dramaos_stage01.py` — 新增本地 CLI：参数与输入约束、ArcReel 媒体探测复用、PySceneDetect 帧索引切点、镜头关键帧与音轨提取、可选本地 `mlx_whisper` ASR、结果与运行记录、静态 HTML。对应 AC-1 至 AC-5。
2. `pyproject.toml`、`uv.lock`、`.github/dependabot.yml` — 新增隔离的 `dramaos` 依赖组并锁定 `scenedetect-headless==0.7.2`；生产默认依赖不变。对应 AC-2/5。
3. `docs/dramaos/stage-01/schema.json` — 新增版本化 JSON Schema，规定媒体、镜头、证据、可用性、运行来源。对应 AC-3/4。
4. `docs/dramaos/stage-01/dependency-audit.md` — 记录既有 FFmpeg 与可选 ASR/VLM 的版本、许可证和未验证项。对应 AC-5。
5. `docs/dramaos/stage-01/README.md`、`test-results.md`、`cost-report.md`、`unresolved-risks.md`、`acceptance.md` — 记录运行方法、有限运行的真实结果、成本、缺口及人工验收。对应 AC-2 至 AC-6。
6. `tests/unit/scripts/test_dramaos_stage01.py` — 只覆盖授权门控与帧边界转换；JSON 结构由一次合成媒体运行校验，不增加完整媒体矩阵。对应 AC-1/2/4。
7. `tasks/todo.md` — 跟踪完成状态与回顾。对应全部 AC。

## 快速验证

- 静态：`uv run python -m py_compile scripts/dramaos_stage01.py`、`git diff --check`。
- 定向用例：`uv run --group dramaos pytest tests/unit/scripts/test_dramaos_stage01.py`；按用户要求不进行大量媒体测试。推送前再执行 `uv run python scripts/gate.py --changed`。
- 合成：用既有 FFmpeg 构造已知切点 MP4，运行一次 CLI 并核对 ±2 帧；用 `jsonschema` 校验 `result.json`，检查全部证据路径。
- 真实：仅在样本权利明确时，对一部现有短片运行一次 CLI；人工质量未验收如实留空。

## 审核循环

方案先交 Claude Code 只读审核；按问题改方案再实施。代码由 Codex 与 Claude Code 审核，最多三轮，严重问题修复后再交付。

## 验证结果

已运行定向单元用例、静态检查、一次已知硬切合成样本和一次现有 60.47 秒样本；详见 `test-results.md`。完整内容质量由用户人工验收。
