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
- [x] 网关增加 `elysium-grok`，保留现有三个公开模型并隔离 OpenClaw 管理员令牌。
- [x] 运行网关相关测试，发布网关并实测普通文本、工具回合和流式响应。
- [x] 在 ArcReel 设置里将现有 Agent 供应商的模型切换到 `elysium-grok`，验证新会话。
- [x] 核对原有三个模型和服务状态，记录回顾与验收边界。

### 回顾

网关新增 `openclaw` 渠道，公开模型 `elysium-grok` 指向本机 `openclaw/arcreel`（实际底层模型 `xai/grok-4.7-build-fast`）。OpenClaw 令牌在 HK 的 `openclaw.key` 中，由 gateway 用户以 0600 权限读取；没有写入仓库或 ArcReel 代码。为避开 OpenClaw 保留工具名，仅此渠道对 ArcReel 客户端工具名做双向映射，并将上游流式错误转换为 Anthropic 错误事件。

`go test ./...`、临时假上游完整工具回合探针和 `git diff --check` 通过；网关按 `--binary-only` 发布，备份在 `/opt/llm-modes-gateway/backups/20261018-161923`。生产设置页当前仅 `elysium` 为生效 Agent 供应商，默认及四个高级档位均为 `elysium-grok`。真实新会话输出 `ARCREEL_GROK_OK`，随后 `Bash(pwd)` 工具调用、结果回传和最终回答成功；网关日志对应流式 `stop → tool_calls → stop` 均为 200。现有 `elysium-chat`、`elysium-image`、`elysium-video` 路由仍在；未运行新的图片或视频生成。已有视频任务 `video_16b25cbe6883200cf4100a29c4a1d254` 持续查询上游得到 502，保持原状，未作为此次接入验收成功项。

# OpenClaw 网页登录 AI 服务失败

- [x] 在用户指定的 OpenClaw 会话复现错误，记录时间及页面请求/响应。
- [x] 只读核对 HK OpenClaw 的模型认证状态、服务日志与相关调用链，确定根因。
- [x] 确认无需重登或改动 ArcReel 路由；记录可行的会话处理方式和验证边界。

## 回顾

2026-10-18 16:35:41，`arcreel-director` 的 `xai/grok-4.7` 请求收到上游 HTTP 403，响应为内容拒绝；OpenClaw 2026.10.4 将该 403 归类为 `auth`，显示“Couldn't sign in to the AI service”并使认证配置进入冷却。此前同一模型在 16:33:17 与 16:34:42 返回 HTTP 200；`models status --agent arcreel-director --check` 显示 xAI OAuth 凭据存在、无缺失路由或不可用配置，凭据状态为即将到期（约 21:01），因此这次报错不能证明登录失效。当前会话包含被上游拒绝的内容，建议另开会话并使用合规素材；不更换模型、不重登、不重发原请求。日志另有多次 HTTP 426 Grok CLI 版本提示，属于独立现象，未作为这次 403 的原因。未改线上配置、进程或 ArcReel 代码；独立 CLI 模型探针未成功，故没有声称修复后真实推理通过。

# 修复 OpenClaw 将内容拒绝误判为认证失败

- [x] 找到 xAI 403 响应到 OpenClaw 错误分类、认证冷却和 UI 文案的实际代码路径。
- [x] 用安装包真实分类函数先复现误判，再实施严格匹配的最小补丁并验证边界。
- [x] 在 HK 发布补丁，验证分类、服务和页面；记录独立模型调用的验收限制。

## 回顾

OpenClaw 2026.10.4 的通用分类把未识别的 403 归为 `auth`。已在 HK 安装包 `dist/extensions/xai/index.js` 的 xAI 专用 hook 中，仅对状态 403 且错误正文精确等于本次上游内容拒绝文案的情况返回 `format`。生产文件的原版备份位于 `/var/lib/openclaw/hotfixes/20261018-xai-refusal/index.js.before`；原版 SHA-256 为 `b3def85c2a7ce097db076a24b817eeed00af718b9799967aacee245dffe05008`，补丁版为 `8edab5979a56ed6d5b0f3763379991c18aa79204fa516a9203bce1b950921f4e`。补丁为安装产物热修，后续 npm 更新可能覆盖。

发布前 `node --check` 通过；用实际 xAI hook 加核心分类器验证：该 403 为 `format`，普通 `403 Forbidden` 和 `401 Unauthorized` 仍为 `auth`。`format` 按 OpenClaw 现有策略不写认证配置冷却。重启后 `openclaw-hk.service` 为 active，公开 `/openclaw/` 返回 200，Orca 页面恢复“已连接”。未重发原会话内容。独立无害模型调用在 30 秒内超时，日志见独立的上游 HTTP 426；因此仅确认了错误分类和服务恢复，未确认 Grok 推理链路恢复。

# 2026-10-19 修复 HK 服务器 IP 根路径 404

- [x] 复现 `https://43.154.247.11/` 返回 404，并确认 `/openclaw` 仍有独立路由。
- [x] 核对线上 Nginx 路由、ArcReel 服务与预期入口，确定最小修复：HTTPS `location /` 显式返回 404，HTTP 同路径代理到 ArcReel。
- [x] 备份受影响配置，修复 HTTPS 根路径和 `/login`，`nginx -t` 通过并热重载。
- [x] 从本机验证公网根路径、登录页、静态资源、`/openclaw/` 与 `/healthz`，均返回 200。

## 回顾

根因是 ai-hk 的 `/etc/nginx/snippets/openclaw-https.conf` 显式让 HTTPS 根路径返回 404，而 HTTP 根路径代理 ArcReel。已将 HTTPS 根路径及 `/login` 与 HTTP 的 ArcReel 规则对齐；原始配置备份为 `/etc/nginx/snippets/openclaw-https.conf.bak-20261019-root-404`。公网 TLS 校验、首页、登录页、两项静态资源、OpenClaw 和健康检查均通过；Nginx 与 ArcReel 服务为 active。IP 证书当前有效，2026-10-24 到期，需确保续期正常。
# 2026-10-19 从本机一键部署 ArcReel 到 ai-hk

- [x] 核对 ai-hk 的发布目录、systemd 服务、构建依赖及持久数据边界。
- [x] 编写单命令部署脚本：本机构建、上传、远端准备、立即中断任务、切换、健康检查。
- [x] 验证脚本语法、打包清单、Node 24 前端构建及服务器临时目录中的 `uv sync`；不执行真实切换。

## 回顾

新增 `scripts/deploy_ai_hk.sh`，从本机工作树发布到 ai-hk。上传清单为 1181 个文件、约 35 MB，不含 `.env` 或项目数据；Node 24 前端类型检查和构建通过，服务器临时目录上传与生产依赖安装通过。两段 Bash 语法及 `git diff --check` 通过，临时目录已清理；线上服务仍 active，`current` 未切换，公网 HTTPS 首页仍为 200。脚本切换时强制中断任务，仅备份 SQLite 数据库和旧版本指针；项目文件保留在独立数据目录，失败自动恢复旧代码指针并重启服务，不自动回滚数据迁移。
# 2026-10-19 E1S01 旁白与 E1S02 双画面只读定位

- [x] 核对页面中 S01/S02 的分镜、视频提示词与发声序列。
- [x] 对照实际生成请求、参考输入、原始图像和视频，定位异常首次出现的位置。
- [x] 沿 ArcReel → 网关 → 模型调用链判断责任边界，记录证据与无法确认之处。

## 回顾

S01 的脚本 `utterances=[]`，ArcReel 实际视频提示词无台词。所用 `openai-video` 通道不下发 `generate_audio` 开关，H3 视频本身有声；线上 MP4 原文件已带 AAC 音轨，与版本文件哈希一致，排除 ArcReel 后期加旁白。网关 H3 编译代码对无对白输入应加入 `No dialogue, no narration...`，但未保留该任务提交给 ComfyUI 的最终 graph，因此不能做字节级确认；旁白更可能是模型未遵守约束。

S02 的 720×1280 原始分镜 PNG 已有上下两块独立画面，视频仅以它为首帧，MP4 首帧延续相同边界。上一分镜参考图是单幅；S02 图像请求向 Qwen Image 2.1 提供五张独立参考图，提示词分别要求鞋在画面上沿、清洁者的手在下方，未要求分屏。网关工作流只返回单张模型产物，没有图像拼接逻辑。诱因是空间描述和多参考图，错误构图在图像模型产出时形成；单次样本无法量化提示词与模型各自的贡献。本轮未修改代码、生产配置和素材，也未重生成。
# 2026-10-19 S01/S02 网关日志补充定位

- [x] 通过生成时间、ArcReel task ID 与网关 TID 关联视频和图像请求。
- [x] 核对 H3 提示词编译代码路径、Qwen 参考图上传和 GPU 工作流提交日志；记录未保存最终 graph 的限制。
- [x] 用日志证据修正 S01/S02 的归因与剩余不确定性；不修复、不重生成。

## 回顾

S01 成功任务 `video_de6ab466ffd3e73e67f38b2f48be4213`、TID `tid_67a4993eb42a2fd196a195d7a418a6c8`：15:45:41 提交、1 张参考图，15:47:45 上游完成。提交前 6 次 503 未产出该成片。ArcReel 原始 prompt 以 `Action:` 开头且无 Dialogue；按线上网关 H3 编译路径，必追加 `No dialogue, no narration, no intelligible speech...`。网关 journal/DB 没有最终 graph，无法做字节级核对；旁白更符合 H3 违背语音约束。

S02 图片 TID `tid_c1b410416928b49ba24d49a8b66d7d3e`：15:36:40 `/v1/images/edits` 成功、5 张参考图；Nginx access 对应该 TID 的 5 次 `/image1/upload/image`、1 次 `/image1/prompt`，轮询单个 GPU history ID `652d140c-9b4c-4cd8-9f93-1c58d1967011`。S02 视频任务 `video_a1c7155e54059c3d5bcd5054ba5212b8` 15:47:49 提交、1 张参考图，15:49:45 完成。GPU `/history` 和 `/view` 当前返回 502，无法取最终 graph 或原图哈希；已有日志和产物表明双画面源于单次 Qwen 图像生成，而非网关多次拼接。本轮未修改生产配置、代码或素材，也未重生成。
# 2026-10-19 DramaOS X Stage 01：视频结构化拆解实验

- [x] 同步两个仓库，保留 ArcReel 本地分叉历史和网关既有未提交改动。
- [x] 只读审计两仓库现有能力、依赖、模型与授权样本，记录可核查证据。
- [x] 写 Stage 01 研究结论、最小方案和验收边界；请 Claude Code 审核。
- [x] 按审核意见修改方案并实现独立 CLI、版本化 JSON 与静态报告。
- [x] 做有限的合成切点与现有样本快速验证，记录结果、成本及未验证项。
- [x] Codex 与 Claude Code 继续审核实现，最多三轮；修复确认的问题。
- [x] 交付 Stage 01 文档、代码、运行说明与人工验收清单。

## 回顾

网关同步到 `6ab0db8`，保留原有工作树改动和备份 stash；ArcReel 同步到 `7ff8001b`，旧本地分叉历史保存在 `codex/pre-sync-20261019`，Stage 01 在 `codex/dramaos-stage01` 实现。方案经 Claude Code 首轮审核后实施；Claude 第二、三轮及 Codex 复审指出的 CI 可选依赖、素材误提交、Schema 错误记录、末帧时长、VFR 切点错位等问题均已修正。最终 Codex 复审未发现阻断项；三轮 Claude 审核上限已用完。

快速验证：5 个定向用例通过；ruff、basedpyright、依赖审计、约定审计、语法编译与 `git diff --check` 通过。最终代码重跑 3 秒合成硬切样本（3 镜，边界 0/30/60/90）和 60.47 秒本地既有产物（8 镜），两份结果通过 JSON Schema。真实样本的抽帧与音轨仅留本机并由 `.gitignore` 排除；未进行完整测试矩阵、真实内容质量或 ASR/视觉模型验收，交由用户按 `docs/dramaos/stage-01/acceptance.md` 手动完成。未部署生产。

# DramaOS Stage 01 文档入口改写

- [x] 核对现有结果、验收边界和样例文件是否还在当前工作区。
- [x] 重写入口页，先解释用途和当前进度，再给操作命令。
- [x] 修正验收页中失效的样例链接和无法执行的人工步骤。
- [x] 复核事实、相对链接与 Markdown 差异，记录回顾。

## 回顾

入口页现先说明本地切镜实验的用途、已验证结果与未验收能力，再给运行命令。验收页不再链接当前工作区缺失的 `real-sample/`，改用存在的合成样本报告，并明确真实短剧须另行确认授权和人工核对。仅修改文档；链接检查通过，`git diff --check` 通过。

# 打通 ArcReel 参考生视频 + 角色声音（2026-10-19）

- [x] 线上新建自定义端点 `ce-1`（定义见 `tasks/artifacts/elysium-ref2v/elysium-h3-ref2v.json`），`elysium-video` 由 `openai-video` 改绑 `ce-1`；首帧（分镜模式）与参考图/音频（参考模式）同端点。回滚：把该模型端点改回 `openai-video`。
- [x] 用 ArcReel 实际渲染的参考模式提示词 + 线上角色图 + 合成日语声音样本直连网关试生成 1 条（8 秒，约 4 分钟）：单画面无分屏；两段人声顺序与台词一致，音高与对应声音样本吻合（男 102Hz/样本 84Hz，女 234Hz/样本 237Hz），无额外旁白。产物：`tasks/artifacts/elysium-ref2v/ref2v-test.mp4`。
- [ ] 角色声音样本须由用户提供有权使用的日语声音；现有项目为分镜模式且角色均无参考音频，需新建参考生视频项目。
# 分镜模式下角色声音与视频生成链路核对

- [x] 核对小说项目的分镜视频请求实际携带的首帧、角色图和角色声音。
- [x] 核对当前网关 H3 工作流能否同时接受分镜首帧和角色声音参考。
- [x] 只读核对线上端点切换状态及对现有分镜项目的影响。
- [x] 给出保留分镜模式的可执行结论、证据与未验证边界。

## 回顾

目标项目仍是分镜模式；ArcReel 生成视频时只提交分镜图首帧和提示词，角色声音样本不随请求传输。线上 `elysium-video` 已绑定 `ce-1`，但该项目四名角色均未保存声音样本。网关 H3 的精确首帧路线与角色图/音频参考路线互斥，二者同传被拒；端点能力声明不能改变该模型/工作流限制。保留分镜模式时，应分别处理分镜图质量和视频音频，不能把参考生视频的单次成功视为现有小说项目验收。本轮只读，没有生成、改代码或改生产。
# 分镜图分屏：仅修改提示词模板的计划

- [x] 核对结构化和纯文本分镜图是否共用最终 `storyboard/image` 模板，并确认宫格模板独立。
- [x] 在最终分镜图模板声明单一连续镜头；参考图只作外观、场景和连续性依据，不作为分格素材。
- [x] 在图片提示词写作指引要求单个时刻与同一空间关系，避免把上下区域写成两个独立画面。
- [x] 复核模板幂等性及现有精确文本断言；相关单元测试 39 项通过。
- [ ] 在保留原素材的前提下，单独重生 S02 分镜图核对效果；若仍分屏，再修改该镜头已保存的画面描述。

回顾：本轮只改提示词模板及其精确输出断言；设置页是只读浏览器，模板需由本机脚本部署后在线查看。S02 已保存的镜头描述和原图未改动，实际出图效果仍待单独重生验证。

## 2026-10-19 分镜图重生后仍异常：线上核对

- [x] 对照线上 S01、S02 当前图片及版本，区分实际重生的镜头。
- [x] 核对 S02 v2 的最终提示词和参考图声明，确认新模板已经生效。
- [ ] 根据用户指出的具体异常确定目标镜头，再处理已保存的分镜描述或参考图使用方式。

回顾：线上 S01 仍只有 15:35 生成的 v1；22:52 新增的是 S02 v2。S02 新图仍上下分屏，最终提示词含单画面约束，但已保存的 Scene 仍有“画面上沿/画面下方”，并包含上一分镜图作为图5。先对齐用户所指的镜头和症状，避免误改 S01。

## 2026-10-19 分镜重测

- [x] 按上一轮实际失败的 S02 上下分屏复测；记录旧图 v2 与最终提示词。
- [x] 仅重写 S02 的 Scene，五张参考图和模型配置不变，生成 v3 并与 v2 对比。
- [x] 在页面大图确认 v3 是单一连续画面，且 v1/v2 仍保留在版本记录中。

回顾：v2 的“画面上沿/画面下方”表述和图5 上一分镜输入共同存在；v3 仅重写 Scene 后，上下分屏消失。23:19 的网关请求仍使用 elysium-image/image1 和 5 张参考图，HTTP 200。此单次对照支持已保存 Scene 是关键诱因，但不能排除模型生成的随机性。S02 视频仍显示“比当前内容旧”，未在本轮重生。

## 2026-10-19 模板自动约束复测

- [x] 恢复 S02 原始 Scene，确认其仍含“画面上沿/画面下方”；保留五张参考图。
- [x] 仅修改全局 `storyboard/image` 模板，并更新对应精确文本断言。
- [x] 相关测试 87 项通过，一键脚本已部署，并在设置页对应的线上渲染结果中核对新模板。
- [x] 使用原始 Scene 测试 S02：v4 仍有横向接缝；v5 连续画面，但此前采用先部署后测试的顺序，故再做独立直接出图。
- [x] 将本机模板渲染出的提示词与原始 S02 的五张参考图直接送到图像模型，检查实际生成图。
- [x] 直接出图通过后，只运行一次最终部署并核对线上模板。

回顾：上一轮手动改 S02 的 Scene 生成 v3，不满足“模板自动改”的验收标准。本轮以原始 Scene 为固定输入重新测试。
实测补记：v4 虽然模板约束位于 Scene 后，仍出现 S01 人物画面与鞋的拼接。继续查多图输入形式与仅靠模板自动改写旧 Scene 的可行性；不能以这轮通过验收。
流程修正：v5 已在部署后出图，画面连续且未复制 S01 人物，但测试顺序不符合用户要求。后续先用本机模板直接调用同一图像模型，成功后再部署。
独立直测：原始 Scene、五张参考图、`custom-1/elysium-image`，本机模板生成的提示词 SHA-256 为 `3168942f8b1590df46b2353ec2a0f2c6423e6ca478ae517d7f88636ef379ddb8`；出图是单一连续画面，无横向接缝。随后只运行一次 `scripts/deploy_ai_hk.sh`，切换到 `/opt/arcreel/releases/20261019T160339Z-de8b0d38-73428`，公网 HTTPS 检查通过。独立直测只输出临时图片，未写入项目分镜版本。
用户随后再次明确要求执行部署，脚本切换到 `/opt/arcreel/releases/20261019T161249Z-de8b0d38-75330`，公网 HTTPS 检查通过。
# 2026-10-20 提交并推送当前改动

- [x] 核对远端 main、当前 diff 与提交范围；保留本地媒体测试产物。
- [x] 运行 push 前受影响域闸门并检查 diff。
- [x] 按仓库规范创建短分支、提交并推送，核对远端分支。

## 回顾

首次完整闸门发现 7 条集成测试仍断言旧的分镜图提示词格式；更新断言后，相关 67 项通过。重跑 `uv run python scripts/gate.py --changed`：backend、tests、conventions 域全部通过，后端 16848 passed、2 skipped。`bash -n scripts/deploy_ai_hk.sh` 和 `git diff --check` 通过。提交范围不含本地 `tasks/artifacts/elysium-ref2v/` 的媒体测试产物。
