# 历史 Agent 报错归因

核查时间：2026-10-12。项目：`proj-5c68fa87`。下文时间均为北京时间。只读检查了数据库、实际日志、配置和调用链；未修改源码或运行配置，未重启服务，未发送新的生成请求。

结论：这些错误来自不同层。旧 502 属于网关或其上游调用失败；今天有两项明确的 Agent 工具调用错误、一项已定位的并发版本冲突，以及尚未能区分网关与模型责任的自动压缩失败。现有证据不支持通过修改项目源码解决，也不支持把所有错误归咎于单一模型或网关。

## 两个会话

| 会话 | 当前状态 | 核实结果 |
| --- | --- | --- |
| `538373c9-2473-4f82-8c9c-422960c206e5` | error | 工具调用出错后继续运行，最终因自动压缩失败终止 |
| `b96106ab-c92c-4ae1-8236-dc5abf3332ad` | completed | 生成提示词时遇到剧本版本变化，后续重试任务成功 |

来源：`projects/arcreel.db`，只读连接；`agent_sessions`、`agent_session_event_log`、`tasks` 表。

## 分项判断

| 错误 | 证据与责任判断 | 处理方向 |
| --- | --- | --- |
| `Unknown skill: normalize-drama-script` | 第一会话 seq 7/8：Agent 调用了 `Skill`，但该对象实际位于 `.claude/agents/normalize-drama-script.md`，是子智能体；源文件与项目安装副本均存在。是 Agent 选择错调用方式，不是缺安装。 | 正确委派子智能体；单次记录证明调用错误，不能单凭它评价模型整体能力。 |
| `episode_id: Extra inputs are not permitted` | 第一会话 seq 16/19：给 `get_video_capabilities` 传入 `episode_id`。工具明确使用 `NoArguments`，随后 seq 31 改为 `{}`。 | Agent 按工具 schema 调用；无需修改项目校验。 |
| `script changed: expected ... actual ...` | 18:45:27 开始基于 18 条正式剧本生成提示词；18:45:48 `script-review/confirm` 成功，将正式剧本替换为 17 条；18:47:06 上游返回 HTTP 200，保存时 hash 不同而拒写。 | 是生成期间确认了另一版剧本，触发防覆盖保护，不是网关或模型请求失败。先确认内容，再生成提示词，期间避免再次改写正式剧本。 |
| `Prompt is too long`，压缩时超过 `32000 output token maximum` | 第一会话 seq 37：SDK 报压缩调用输出达到限制，实际 API 模型为 `elysium-chat`。 | 是上下文压缩路径失败；需要区分模型未及时完成摘要、网关输出/停止事件转换异常和预算设置，不应直接提高限制。 |
| `automatic compaction failed: summarization produced empty response` | 第一会话 seq 46：终止原因 `prompt_too_long`，SDK 记录压缩没有得到可用摘要。 | 目前缺少对应网关原始请求/响应，不能判定是模型原始空输出还是网关转换后变空。 |
| `generate_script_plan` 的 `502 upstream_error` | 用户贴出的原文与 10 月 9 日任务记录一致。当天日志包含多次重试；10 月 12 日两次规划任务均成功。 | 属于当时远端服务调用失败，不是这两个新会话当前终止原因。仅凭 502 无法进一步划分网关自身与其上游责任。 |

版本冲突证据：`projects/logs/arcreel.log:5905`、`:5922`、`:5923`、`:5959`、`:5971`。第二会话失败任务为 `7c293a8acc744b62aa0b2cf14c513480`，重试任务 `1a17fb42d74f4b5b9541eeeec4ef6714` 于 18:49:31 成功。这里仅确认该任务成功，不代表完整视频流程已经验收。

旧 502 证据：`projects/logs/arcreel.log.2026-10-09:613`、`:621`；例如任务 `13a129a98de34456ad4f4615ba67742d`，10 月 9 日 23:25:35–23:26:55。历史任务把错误存成 `generation_refused` / `fix_input`，但底层原文是 HTTP 502；该标签不能证明内容被模型拒绝，也不能据此要求修改小说内容。

今天规划成功任务：`bdd4ebc0ebb242fda9ea78912c3de621`，18:42:32 完成；`b6004884310542a29f258f2fd8d5c909`，18:45:27 完成。不能将此前 502 解读成该模型今天完全无法规划。

## 配置核对

- 当前创作 Agent：`elysium-chat`，Anthropic 兼容入口 `http://43.154.247.11`。
- 当前项目简单、复杂文本档及默认文本后端：`custom-1/elysium-chat`，OpenAI 兼容入口 `http://43.154.247.11/v1`；模型端点 `openai-chat`。
- `generate_script_plan` 使用 `TextTaskType.SCRIPT`，属于复杂文本档，不直接采用创作 Agent 凭证的模型设置。参见 `server/text_generation.py:932`、`lib/backends/text_backends/base.py:237`、`lib/config/resolver.py:1633`、ADR 0051。
- 项目 `.env` 明确设置 `CLAUDE_CODE_MAX_CONTEXT_TOKENS=65536`；该文件未显式设置 `CLAUDE_CODE_MAX_OUTPUT_TOKENS`。未读取常驻进程的完整环境，不能把文件配置视为进程生效证明，也不能把缺少输出变量视为根因。
- 当前模型配置不是旧的 `claude-opus-5-5`；本次错误中 SDK 明确记录实际发送的是 `elysium-chat`，因此不能套用旧会话模型名未更新的历史解释。

## 未确认项与下一步

最需要继续核验的是自动压缩，而不是旧 502。需取第一会话 18:43:50 前及 18:49:11 前压缩请求的网关记录，对照原始上游响应与返回给 SDK 的响应：模型、输入长度、输出预算、文本与推理 token 分布、停止原因、流式结束事件、请求 ID。日志必须脱敏。

如果上游有非空摘要、网关转换后为空，责任在网关适配；如果上游本身耗尽输出预算仍无摘要，需进一步对照模型和预算；如果请求预算或上下文配置与模型能力不符，则调整相应配置。现有应用日志无法完成这个区分，因此本报告不将其中任一假设标记为已证实。

本次采用历史失败记录与代码合同交叉验证，未重放有副作用的生成请求，也未验证任何修复。已有 `tasks/todo.md` 中旧诊断记录仅用来找线索，不把历史对照实验当作本次实测结果。
