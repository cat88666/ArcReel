# 暂只支持角色对白（隐藏说书与 TTS，提示词不产出旁白）

- [x] drama script_plan 提示词：novel / screenplay 两个 utterances_rule 只产出角色台词；叙述改为画面或角色内心独白；口播下界文案去掉「画外音」
- [x] 新建项目向导：隐藏「旁白/解说」创作类型与「旁白交付方式」区块（交付方式保持默认后期配音）
- [x] 更新 CreateProjectModal 单测与 create-project e2e 脚本，跑前端与提示词相关测试
- [x] 不改后端准入与工作流；现有 E1S07 由整集重做或手工拆分解决（需部署后生效）

## 回顾

提示词单测 349 passed；CreateProjectModal 与 NarrationDeliveryFields 单测 27 passed；tsc、eslint、knip、audit_tests 通过。e2e 本机缺 Playwright 浏览器未能运行，create-project 截图基线（第一步卡片由 3 张变 2 张、第二步无旁白区块）需在有浏览器的环境重录。未部署。

# 页面标题缩短

- [x] 在 Orca 当前标签页确认实际标题及运行时覆盖位置。
- [x] 将浏览器占位标题和运行时标题改为「Agent」。
- [x] 运行前端检查并构建（全量测试 3 项并行超时，单独重跑 52/52 通过；Node 24 生产构建通过）。
- [x] 完成 Python 3.12 后端检查，保留线上热修及数据后发布本地最新代码。
- [x] 核对线上产物与服务状态；页面操作由用户手动验证。

## 回顾

前端生产构建通过；`pnpm check` 的全量 Vitest 有 3 项并行超时，相关 3 个测试文件单独重跑 52/52 通过。Python 3.12 后端全量 pytest 16842 passed、2 skipped。已部署到 `/opt/arcreel/releases/20261017-b623d8af-agent-title`，停服快照与回滚资料在 `/opt/arcreel/backups/20261017-b623d8af-agent-title`。服务、HTTP 和数据库检查通过；3 个外部视频任务恢复轮询、12 个排队任务保留。用户自行验收页面与业务流程。

# Elysium 媒体模型市场参考价

- [x] 核对项目页面、实际上游模型及 ArcReel 计费单位和倍率。
- [x] 查证同类 API 当前公开报价，确定参考单价。
- [x] 在 Orca 页面填写图片、视频模型价格并保存。
- [x] 返回项目确认价格已覆盖缺价项，记录结果和限制。

## Elysium 价格回顾

`elysium-image` 关联手动条目 Qwen Image 2.1，基础价 US$0.015/张，供应商倍率 2 后为 US$0.03/张。`elysium-video` 关联 MiniMax H3，模型倍率 0.5 抵消供应商倍率 2；在原目录 768p ¥0.50/秒、2k ¥0.80/秒之外补了 720p ¥0.50/秒，覆盖 OpenAI 视频端点默认计量的 720p。补档后该模型价格转为用户覆盖，不再随官方目录自动更新。项目页预估变为视频 CN¥156.00 + 分镜 US$1.23，预估缺价项从 82 降到 0；历史已落库费用为空的 24 次调用仍显示未计价，已花保持 CN¥127.00。

# Codex 默认使用 Orca 内置浏览器

- [x] 排查环境：Orca 1.4.229 运行中、`orca` CLI 可控内置浏览器；Codex 0.163.0 由 Orca 以 `CODEX_HOME=~/.codex` 启动。
- [x] 定位 Chrome 来源：`agent-browser` 技能（仓库 `.agents/skills`）启动 Chrome for Testing；Codex `chrome@openai-bundled` 插件驱动真实 Google Chrome；`BROWSER` 未设置时链接走系统默认浏览器。
- [x] 备份 `~/.codex/config.toml`（`config.toml.bak-orca-browser-20261017`）。
- [x] 关闭 Codex Chrome 插件与 node_repl 的 chrome 后端。
- [x] 在 Codex 中禁用仓库内的 agent-browser 技能（只改 Codex 配置，不动仓库）。
- [x] Codex shell 的 `BROWSER` 指向 Orca 标签页（Orca 不可用时回退到 `open`）。
- [x] 补一条 developer_instructions，指向官方 orca-cli 技能（只作补充）。
- [x] 用 `codex exec` 实测：打开网页、snapshot、点击/输入、截图、复用会话、确认没有新的 Chrome 进程。

## Orca 浏览器回顾

两次 `codex exec` 实测，提示词都没提 Orca：Codex 自己加载 orca-cli，全程用 `orca tab create/goto/snapshot/fill/click/screenshot`；Python `webbrowser.open` 经 `BROWSER` 在 Orca 里开了标签页；新标签页沿用 Default profile 的登录态；测试前后没有新增 Chrome 或 Chrome for Testing 进程。会话记录显示，改动后 `agent-browser` 和 `chrome:control-chrome` 两个技能已不在 Codex 的技能列表里。第一次测试时 Codex 把用户已有的标签页导航走了，已恢复原 URL，并在 developer_instructions 里要求新页面用 `orca tab create`。还没覆盖的入口：Codex 桌面版的 `open-local-url-in-target-preference`、直接执行 `open <url>`、项目自带的 Playwright 测试，以及 Orca 尚未提供的原生路由（stablyai/orca#28177 仍未关闭）。

# 项目语言模型切换至 Grok 4.7 Fast

- [x] 核对线上项目设置、Grok 供应商及现有网关模型。
- [x] 核对 xAI 官方的 Grok 4.7 Fast API 可用性。
- [ ] 待具备 ArcReel 可调用的 Fast 接入后，切换全部项目的三个文本模型字段并逐项验证。

## 回顾

线上 Grok 供应商未配置密钥，模型列表没有 Grok 4.7 Fast；现有 Elysium 网关只提供 chat、image、video 三个模型。xAI 官方文档说明 Grok 4.7 Fast 不开放公共 xAI API。本次未修改项目配置，以免把运行中的项目切换到不可调用的模型。

# Grok 4.7 Fast 独立接入与项目切换

- [x] 验证 OpenClaw 订阅代理上的 Fast 模型可调用，并确认 ArcReel 现有 Grok 后端的认证限制。
- [x] 用户否定独立 OpenClaw 网关方案后，取消设备登录并撤销新增服务、账号和安装文件。
- [ ] 确认用户希望采用的 ArcReel Grok 供应商接入方式与实际可调用的目标模型。
- [ ] 在可调用性验证通过后，切换全局与所有项目文本模型配置并逐项验收。

## 回顾

本机 OpenClaw Fast 模型调用返回 OK；ArcReel 内置 Grok 后端仅接受 xAI API Key。独立 OAuth 网关方案被用户否定，已取消设备登录并撤销服务器上新增的服务、账号和安装文件。用户新建的密钥为 Cursor 类型，公共 xAI API 返回密钥不正确；控制台的 Grok Inference 类型要求先添加支付方式并预充值，且公共 API 不提供 4.7 Fast。线上项目仍未修改。

# OpenClaw 迁移到 HK（仅同步配置）

- [x] 核对最新版、当前配置、HK 入口与依赖；备份本机配置和 HK 现状。
- [x] 在 HK 安装最新版 OpenClaw，迁移配置并适配 Linux 路径、插件和认证。
- [x] 验证 HK Gateway 和网页版访问；实测 xAI Fast 调用并记录上游额度限制。
- [x] 停用本机 OpenClaw Gateway/桌面端；保留本机数据备份供用户手动验收后再决定清理。

## 回顾

HK 安装 OpenClaw 2026.10.4，仅同步配置、工作区和插件代码，不迁移历史会话与 SQLite 状态。HTTP `/openclaw` 可直达并自动跳转 HTTPS；Orca 页面显示已连接。HK Gateway 与 Telegram 运行正常，证书续期演练通过；本机桌面端和网关已停用。xAI OAuth 已登录，Grok 4.7 Fast 调用返回上游 402（Grok Build 使用余额耗尽），故模型推理尚未通过验收。安装证书工具时系统自动重启 ArcReel，E1S20 分镜任务因此失败；用户要求直接部署，未自动重试该任务。本机备份保留，待用户手动测试后再清理。

## 本机彻底卸载（用户已手动验收）

- [x] 复核 HK 网页入口、Gateway、配置、工作区与 Telegram 状态。
- [x] 停止本机残留进程；用户明确要求不留备份，终止归档并清点既有备份。
- [x] 移除本机应用、用户数据、缓存和 OpenClaw 备份，并检查安装残留。
- [x] 复核 HK 入口和服务，记录卸载结果。

### 卸载回顾

已删除本机 OpenClaw 应用、`~/.openclaw`、更新捕获、桌面状态与缓存、旧 Clawdbot/Clawdis 套接字、浏览器原生消息配置与专属扩展文件、钥匙串中两条 OpenClaw 记录、Shell PATH 注入、本机及废纸篓中的 OpenClaw 备份。无本机命令、启动项、监听端口或进程；HK 服务仍为 active，入口返回 200。用户的独立课程资料和 ArcReel 项目文件不属于 OpenClaw 安装，未触碰。

# Grok 4.7 Fast 仅承担 ArcReel 纯文本任务（直连 HK OpenClaw）

- [x] HK OpenClaw 启用本机 Chat Completions 接口，建立固定 Fast 模型且禁用工具的 `arcreel` Agent。
- [x] 实测普通文本、一次 JSON 输出及流式请求成功；确认附图输入目前未传达给模型，不能用于风格分析。
- [x] 按用户最新要求撤销 llm-modes-gateway 临时渠道与代码改动，网关健康检查通过。
- [x] 用户同意使用现有 OpenClaw 管理员 Bearer，并知悉 ArcReel 自定义供应商密钥存入数据库明文。
- [x] 配置 ArcReel 自定义供应商；普通文本和结构化输出均通过真实调用。
- [x] 将纯文本任务分配到复杂档，风格图分析留在简单档；相关后端和前端测试通过。
- [x] 为全局和六个项目配置复杂文本模型，保留自建模型承担视觉和媒体能力。
- [x] 等待运行中的视频任务完成后切换隔离发布目录，重启 ArcReel；验证线上实际路由与服务健康。

## 回顾

OpenClaw 本机接口以 `openclaw/arcreel` 调用 `xai/grok-4.7-build-fast` 返回 HTTP 200；ArcReel 已接入并实测文本调用。全局和六个项目的复杂文本模型已设置为 `custom-2/openclaw/arcreel`。隔离发布目录已切换，线上项目概述通过实际路由调用返回 `ARCREEL_ROUTE_OK`。等待中的视频任务已由新进程接续，关停超时恢复为原值。风格图分析仍走原有自建 `custom-1/elysium-chat`，该模型在当前目录中声明不支持图像输入，能力校验会拦截此任务；这属于本次切换前已有的配置限制，需另配支持看图的自建文本模型。
# ArcReel Agent 默认模型切换至 Grok 4.7 Fast

- [x] 核对线上 Agent 配置、模型标识及调用路径。
- [ ] 确定 Anthropic Messages 兼容接入方案，再切换生效供应商。
- [ ] 重新读取线上配置并执行 Agent 新会话验证。

## 回顾

线上 `Grok4.7` Agent 供应商未生效，配置地址为 `http://127.0.0.1:18789/v1`，默认模型与四个档位均留空。页面连接测试请求 `/v1/v1/messages` 返回 404；HK OpenClaw 的 `/v1/messages` 也返回 404，而 `/v1/chat/completions` 存在。当前 OpenClaw 入口无法直接供 Claude Agent SDK 使用，故保留 `elysium` 生效，避免新 Agent 会话故障。需先确定兼容方案并进行真实新会话验收。

## 方案评估

- [x] 对比现有网关适配与 ArcReel 内部新增适配。
- [x] 核对 OpenClaw 官方 Chat Completions 工具调用协议。
- [x] 列出切换前必须验证的实际工具回合和流式路径。

现有 `llm-modes-gateway` 已具备 Anthropic Messages 到 OpenAI Chat Completions 的请求、工具及流式响应转换。若坚持让内嵌 Agent 使用 Grok 4.7，复用该网关并加独立 OpenClaw 渠道的改动量最小；在 ArcReel 内重写转换会增加重复代码和 SDK 兼容风险。现有网关测试未覆盖完整工具回合，且 OpenClaw HTTP 端点本身运行 Agent，故仍需真实验证工具调用、工具结果、流式和新会话后才可切换。此前用户要求撤销临时网关渠道，实施前应确认这一限制是否仍适用。

## elysium-grok 接入与 Agent 切换（用户已同意复用现有网关）

- [x] 盘点两个生产服务、运行中会话、网关配置和密钥边界。
- [ ] 网关增加 `elysium-grok`，保留现有三个公开模型并隔离 OpenClaw 管理员令牌。
- [ ] 运行网关相关测试，发布网关并实测普通文本、工具回合和流式响应。
- [ ] 在 ArcReel 设置里将现有 Agent 供应商的模型切换到 `elysium-grok`，验证新会话。
- [ ] 核对原有三个模型和服务状态，记录回顾与验收边界。

