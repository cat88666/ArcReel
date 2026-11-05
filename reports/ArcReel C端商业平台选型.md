# 不套模板，在 ArcReel 上原地补出商业外壳

> **2026-11-06 复核提示：**下文是此前围绕 ArcReel 商业外壳的方案，不能作为「SceneMixer 整站唯一最优替代」结论。后续广域检索又发现[连镜](https://github.com/zaylora/video-canvas)、[NovaNova Studio](https://github.com/Swayingleaves/novanova-studio)、[Toonflow](https://github.com/HBAI-Ltd/Toonflow-app)等强候选，影策不再被视为唯一领先的开源底座。DramaClaw 的公开功能覆盖仍很接近，但其 Elastic 2.0 许可限制面向第三方的托管服务。当前比较和搜索边界见[广域候选复评](SceneMixer广域候选复评.md)；下文的「唯一最优」及工作量估算均未据此重新评估。

结论：开源世界里没有哪个现成项目能直接给出“SceneMixer 级”的 C 端体验。唯一最优方案是一条组合路线：**在 ArcReel 本体上按 ADR 0021 预留的缝隙做原地多租户，把积分账本接到已有的 `lib/billing/ledger.py` 记账括号上，支付走一层薄的 PaymentProvider 适配器（默认 Creem，备选 Stripe 或 Paddle），营销站另建一个独立的 Astro 静态站做 i18n 和 SEO**。改造后的 ArcReel fork 按 AGPL 公开源码，并保留 “Powered by ArcReel”。这个结论有三层依据。第一，SceneMixer 自己就不是模板产品，而是自研的 Vite + React SPA，营销页由 Python 脚本生成静态页 ([sitemap.xml](https://scenemixer.com/sitemap.xml))，和 ArcReel 现有的 React 19 + Vite 前端同一路数。第二，ArcReel 已经具备 SceneMixer 创作控制台的内核，以及按调用精确计价的账本，缺的只是商业外壳。第三，ShipAny、MkSaaS 这类付费模板的许可证禁止公开源码，与 AGPL 的修改版开源义务正面冲突，而且它们自带一套 TypeScript 用户和积分体系，没法在 Python 侧原子地拦住视频任务，最后会变成两套用户系统并存。【推断】整体路线置信度约 **75%**，支付渠道的默认选择置信度约 **55%**。后者取决于你有没有海外主体，以及 MoR 能否通过 AI 视频产品的审核，这两点目前都没有核实。【推断】总工作量约 **22–34 人日**（一名资深全栈），下文给出可以直接交给 Codex 的分阶段方案。

## SceneMixer 是自研 SPA，可抄的是它的商业闭环，不是它的代码

【事实】SceneMixer 由悉尼注册的 Sincosphere Holdings Pty Ltd 运营 ([legal](https://scenemixer.com/legal/))，域名 2026-04-07 注册（本地 whois）。线上 HTML 只引用 Vite 分块产物（`/assets/index-*.js`、`react-*.js`、`router-*.js`），没有 `_next/`，HTML 注释里出现 `vite.config.ts`、`localize-shell.py`、`gen-static-pages.build_lang_home` 等中文开发注释 ([scenemixer.com/create](https://scenemixer.com/create))。主 JS 包里 `shipany`、`mksaas`、`supabase`、`clerk`、`better-auth` 都出现 **0 次** ([bundle](https://scenemixer.com/assets/index-EBCBr7vR.js))。sitemap 有 **11,928 个 URL**，注释写明由 `scripts/gen-static-pages.py` 生成，每条带 hreflang 组 ([sitemap.xml](https://scenemixer.com/sitemap.xml))。robots.txt 主动放行 GPTBot、ClaudeBot、PerplexityBot，并写明“被 ChatGPT/Claude/Perplexity 引用是获客渠道” ([robots.txt](https://scenemixer.com/robots.txt))。【推断】所以“找一个和 SceneMixer 一样的模板”这个前提不成立。真正要复刻的是它的商业闭环：多语言程序化 SEO，注册赠点加首部剧免费额度，按秒计价且提交前报价，运行中预冻结，会员订阅加积分包，OTP 和 Google、Apple 登录，推荐联盟，以及按会员等级区分的并发数、水印和上传权限。

【事实】定价页（更新于 2026-11-04）显示：会员 Pro $7.99/月 700 点，到 Max $199.99/月 25,000 点，共 5 档；积分包从 100 点 $1.49 到 100,000+15,000 点 $899.49，共 6 档；视频按秒计费，Wan 3.0 480P 每秒 10 点起；注册赠 **50 点**；支付方面，“scenemixer.com 透過 Stripe 以美元刷卡；scenemixer.cn 支援支付寶與微信支付” ([pricing](https://scenemixer.com/zh-hant/pricing/))。响应头的 `permissions-policy` 同时放行了 `checkout.airwallex.com` 和 `js.stripe.com`（curl -D）。开发者门户显示 “{n} on hold for running jobs”，证实它有运行中预冻结机制。**笔记冲突一**：Product Hunt 页面写的是 “500 free credits” ([Product Hunt](https://www.producthunt.com/posts/1240376))，与定价页的 50 点不一致。这里以带日期、标明“取自网站即时设置”的定价页为准，Product Hunt 的数字视为旧数据或活动价。**笔记冲突二**：两份笔记对主包里 wechat 的计数分别是 22 次和 6 次，差别来自 grep 模式不同（`wechat` 与 `WeChat Pay/wechatPay`），不影响结论。hreflang 记为 16 条还是 17 条，差别只在是否算上 x-default。【事实】Product Hunt 只有 2 票 ([Product Hunt](https://www.producthunt.com/posts/1240376))。【推断】它是上线约半年、主要靠 SEO 和 GEO 获客的早期产品，说明这套打法一个小团队能做出来，不需要大平台底座。

## ArcReel 已有创作内核和成本账本，缺的是用户、钱包和支付

【事实】ArcReel 的 API 已覆盖 SceneMixer 控制台需要的全部创作动作：项目 CRUD，`generate/{storyboard|video}/{segment_id}` 和 `generate/character|scene|prop|product`（返回 task_id，由 GenerationWorker 异步执行，`server/routers/generate.py:185-198`），edit-timeline 的 `final-cut` 合成（`server/routers/edit_timelines.py:378,415`），提交前报价 `GET /projects/{p}/cost-estimate`（`server/routers/cost_estimation.py:30`），SSE 推送（`server/routers/project_events.py:48`），以及挂在 `/mcp` 的远程 MCP（`server/app.py:827`）。计量层的 `api_calls` 表按调用记录 `cost_amount`、currency、task_id、user_id（`lib/db/models/api_call.py:13-60`）。`lib/billing/ledger.py` 的记账括号在调用开始时写 pending 行，成功时结算，失败或取消时零费用结算；resume 路径以 `WHERE status='pending'` 作幂等守卫（`lib/billing/ledger.py:11-12,235,268-292`）；启动时 `settle_interrupted_calls` 会收口孤儿 pending 行（`lib/billing/ledger.py:340`）。【推断】积分系统里最难做对的部分是“终态恰好结算一次”，而 ArcReel 已经在 USD 成本这一层做对了。

【事实】ArcReel 实际上是单用户系统。`_payload_to_user` 无论收到 JWT 还是 API Key，都返回 `CurrentUserInfo(id=DEFAULT_USER_ID, sub=sub, role="admin")`（`server/auth.py:440-445`）。ADR 0021 写明“开源版预埋多用户数据模型与 `_scope_query` 缝隙，但不实装多租户……商业版通过 migration 扩字段 + 子类覆盖 `_scope_query`”，并点名原生 SQL 的 `claim_next` 是需要单独覆盖的特例（`docs/adr/0021-multi-user-preembed-scope-query.md:5-12`）。缝隙本身在 `lib/db/repositories/base.py:17`，`claim_next` 在 `lib/db/repositories/task_repo.py:470`。`GET /projects` 不按用户过滤（`server/routers/projects.py:574-580`）。媒体文件经 `public_router` 的 `/files/{project_name}/{path}` 无鉴权暴露（`server/routers/files.py:302`）。数据库可通过 `DATABASE_URL` 切到 Postgres（`lib/db/engine.py:56-61`）。用 `gh search issues` 查上游，没有任何多租户相关工作。【推断】这意味着无论最后选哪个外壳，都绕不开 ArcReel 侧的多租户改造或实例隔离。这也是“模板 1–2 周就能接上”这类估算普遍偏低的根本原因。

### 原地多租户胜过一用户一容器

【推断，决策】选择原地多租户，否决一用户一容器。一用户一容器的好处是不用改 ArcReel 代码，但代价很具体：每个容器都带 Agent 的 bwrap 沙箱，需要 `seccomp:unconfined` 和 `NET_ADMIN`（`deploy/docker-compose.yml`）。C 端免费用户动辄几千个，这样按人起实例，资源和编排成本不可接受。外壳还得自己维护“用户 → 实例 URL + arc- Key”的映射、跨实例计费和产物代理。原地多租户的改动面很清楚，ADR 已经预留了接口，只要改认证映射、覆盖 `_scope_query` 和 `claim_next`、给项目加归属校验、给媒体加签名。为了“最少改动”，项目隔离不搬目录。保留单一 `projects/` 数据根，新增 `project_owners` 归属表，由服务端生成带用户前缀的项目名，再给所有带 `{project_name}` 的路由加一个 `require_project_access` 依赖。这样 `api_calls.project_name`、任务表和文件路由里以项目名为键的大量既有代码都不用动。【未验证】目前不清楚 `ProjectManager` 有多少处全局单例式调用，按用户拆 data_root 的成本因此未知，这也是推迟目录隔离的原因。

## AGPL 让付费模板路线自相矛盾，开源 fork 反而是最省事的合规姿势

【事实】ArcReel 采用 AGPL-3.0（`LICENSE:1`）。NOTICE 依第 7(b) 条要求，修改版的 UI 必须在 about、legal 或页脚保留 “Powered by ArcReel — https://github.com/ArcReel/ArcReel” 和仓库链接（`NOTICE:1-20`），目前这行文字在 `frontend/src/components/pages/settings/AboutSection.tsx:193`。【事实】ShipAny 的许可证禁止 “Redistribute the source code publicly” 和 “Remove ShipAny attribution” ([LICENSE（fork）](https://github.com/wujiabao77/shipany-template-one))。MkSaaS 禁止脱离终端产品单独再分发组件 ([fork LICENSE](https://github.com/omegacc91/mksaas))。两者官方仓库都是私有的（gh api 返回 404）。【推断】这里的矛盾是结构性的。只要把模板代码与 ArcReel 代码合在一个仓库里，或者为了接入而修改 ArcReel，就同时背上两份互斥的义务：AGPL 要求向网络用户公开修改后的源码，模板许可证禁止公开模板源码。唯一能共存的形态是模板作为独立进程，只通过 HTTP 调用 ArcReel。但 ArcReel 本身仍要做多租户改造并公开这部分修改，用户在控制台看到的 ArcReel 界面也仍须显示 “Powered by ArcReel”。【未验证】外壳通过网络 API 调用 ArcReel 时，外壳本身是否构成衍生作品，需要法务判断，几份笔记都没有给出法律意见。

【推断，决策】把合规当成设计约束，而不是事后补救。ArcReel fork 从第一天起就在 GitHub 公开，控制台页脚放 “Powered by ArcReel” 和 “源码” 链接，变更按第 7(c) 条标注。商业护城河放在运营、内容、定价和获客上，SceneMixer 的护城河也是 SEO 规模和内容，不是代码。营销站作为独立的静态站点，不含 ArcReel 代码，可以不开源。支付密钥、价目倍率这类经营数据放在环境变量和数据库里，不进仓库。这样就不需要任何闭源模板。

## 只有三条路线值得认真考虑

【事实】排除项及原因：waoowaoo 自 v0.5.0-beta.1 起改为 ELv2，“may not provide the software to third parties as a hosted or managed service” ([LICENSE](https://github.com/waooAI/waoowaoo/blob/main/LICENSE))；huobao-drama 是 CC BY-NC-SA，禁止商用 ([README](https://github.com/chatfire-AI/huobao-drama))；Toonflow 是 MIT，但“业务页面与 API 没有独立登录鉴权” ([README](https://github.com/HBAI-Ltd/Toonflow-app))；FastMovieAI 是 Apache-2.0，带支付宝/微信和会员，但只有 434 star、2026-02-19 之后没有提交、没找到 Stripe、demo 无法访问 ([GitHub](https://github.com/xhadmincn/FastMovieAI))；Open SaaS 的积分只是 User 表上的 `credits Int @default(3)` 单字段 ([schema.prisma](https://github.com/wasp-lang/open-saas/blob/main/template/app/schema.prisma))；Velobase Harness 有积分冻结，但 2026-04 才创建，只有 619 star ([repo](https://github.com/velobase/velobase-harness))；Dify 和 FastGPT 的许可证禁止多租户运营 ([Dify LICENSE](https://github.com/langgenius/dify/blob/main/LICENSE)、[FastGPT LICENSE](https://github.com/labring/FastGPT/blob/main/LICENSE))；Lago 的实时钱包余额只在付费授权里提供 ([Lago wallet](https://getlago.com/docs/guide/wallet-and-prepaid-credits))；Autumn 和 Flowglad 的 GitHub 仓库在 2026-11-05 返回 404。剩下值得考虑的只有三条。

| 维度 | ① 组合路线（唯一推荐） | ② ShipAny Two 外壳 + ArcReel 后端 | ③ BuildingAI 外壳 + ArcReel 控制台 |
|---|---|---|---|
| 构成 | ArcReel 原地多租户 + 自建积分账本 + Creem/Stripe 适配器 + Astro 营销站 | 付费 Next.js 16 模板，新增 `arcreel` AI provider | Apache-2.0 的 NestJS + Nuxt 商业壳，写扩展跳转 ArcReel |
| 接近 SceneMixer 的程度 | 高：自有 React SPA + 静态 SEO 站，与 SceneMixer 同构 | 中：落地页、控制台齐全，但是两个应用、两个域 | 中低：Vue 与 React 两套 UI |
| 成熟度证据 | ArcReel 6,155 star，v0.35.0（2026-11-01）；账本已在生产路径上 | 有付费用户但没有公开源码；`todo: get cost credits from settings` ([镜像](https://github.com/chifenglovekele/shipany-template-two-dev)) | 1,928 star，2026-10-30 仍有推送，有 demo ([GitHub](https://github.com/BidingCC/BuildingAI)) |
| 商业化能力 | 要自建，但可以直接挂在已有账本上 | 积分预扣 + 失败退还、Stripe/Creem/PayPal、en/zh | 原生支付宝/微信/Stripe、会员、充值订单 |
| 许可证风险 | 低（fork 开源） | 高（与 AGPL 冲突） | 低（Apache-2.0） |
| 实际接入成本【推断】 | 22–34 人日，单一技术栈 | 同样要做 ArcReel 多租户，外加双用户体系桥接，长期双栈维护 | SSO 桥接 + 积分 API + 长任务预扣，扩展 SDK 能否承载外部 SPA【未验证】 |
| 适用条件 | 默认选择 | 团队只会 Next.js，并且愿意接受法务风险 | 首要市场是中国大陆，必须立刻有微信/支付宝 |

**笔记冲突三，工作量**：模板笔记估计 ShipAny 接入只要 1–2 周，组合笔记估计两条路线前期都要 19–29 人日，模板路线另外还有长期双栈成本。这里采纳后者。1–2 周的估算只算了“新增一个 provider”，没有算 ArcReel 的单用户现实（`server/auth.py:440-445`），也没有算视频任务必须在 Python 侧原子拦截。ShipAny 的积分在 Next.js 的数据库里，GenerationWorker 入队前看不到余额。【推断】组合路线 19–29 人日的估算同样没有包含多租户，补上 3–5 人日，得到 22–34 人日。

## 交给 Codex 的执行方案

【推断，决策】下面每个阶段都是一个可以独立合并的 PR，以“验收”一栏为完成标准。文件路径都已在本地仓库核实。标【未验证】的函数位置需要 Codex 先读代码确认，再动手。

### 数据表（Alembic 迁移，放在 `alembic/versions/`）

| 表 | 关键字段 | 说明 |
|---|---|---|
| `users`（扩字段） | `email UNIQUE`、`google_sub UNIQUE`、`apple_sub`、`display_name`、`plan`、`plan_expires_at`、`referrer_id`、`created_at` | 现有表只有 id、username、role、is_active（`lib/db/models/user.py:10-16`） |
| `email_otps` | `email`、`code_hash`、`expires_at`、`attempts` | 6 位验证码，10 分钟有效，最多 5 次尝试 |
| `project_owners` | `project_name PK`、`user_id`、`created_at` | 项目归属，不搬目录 |
| `credit_accounts` | `user_id PK`、`balance BIGINT CHECK(balance>=0)`、`reserved BIGINT` | 余额缓存 |
| `credit_entries` | `id`、`user_id`、`kind`（grant_purchase / grant_subscription / grant_promo / reserve / capture / release / refund / expire / adjust）、`amount`（有符号）、`idempotency_key UNIQUE`、`ref_type`、`ref_id`、`bucket_id`、`expires_at` | 只追加的流水 |
| `credit_buckets` | `id`、`user_id`、`source`（subscription / pack / promo）、`remaining`、`expires_at` | 订阅积分在当期结束时过期，优先消耗最先过期的桶 |
| `payment_orders` | `order_no`、`user_id`、`provider`、`sku`、`amount_minor`、`currency`、`status`、`provider_ref` | 订单 |
| `webhook_events` | `provider`、`event_id`、`UNIQUE(provider,event_id)`、`payload`、`processed_at` | webhook 去重 |
| `subscriptions` | `user_id`、`provider`、`plan`、`period_end`、`status` | 订阅 |

### 积分冻结、结算、退还流程

【推断】做法借鉴 new-api 已经在生产中验证过的两个模式：一是用条件更新做原子预扣，`UPDATE users SET quota = quota - ? WHERE id = ? AND quota >= ?`，只有 `RowsAffected == 1` 才算成功 ([quota_reserve.go](https://github.com/QuantumNous/new-api/blob/main/model/quota_reserve.go))；二是“终态由状态 CAS 的赢家统一收尾，恰好一次” ([task_polling.go](https://github.com/QuantumNous/new-api/blob/main/service/task_polling.go))。new-api 本身是 AGPL，这里只借设计，不拷代码。

**冻结（入队时）**：在 `lib/generation/generation_queue.py:396` 的 `enqueue_task` 写入任务之前，调用新的 `lib/billing/credits.py: reserve(user_id, task_id, est_points)`。预估值复用 `cost_estimation` 的价目逻辑，按模型的最大单段时长取上限，再换算成积分。同一事务里先做条件扣减（`balance -= est`，`reserved += est`），再写一条 `reserve` 流水，`idempotency_key=f"reserve:{task_id}"`。余额不足时返回 402，带上 `required` 和 `balance`，前端据此弹出充值框。同一入口还要检查会员并发上限，即该用户 running 状态的任务数，超出时返回 429 “Concurrency limit reached”。

**结算（任务终态）**：在任务翻到终态的那一处（候选位置是 `lib/db/repositories/task_repo.py` 里把状态写成终态的方法，以及 `lib/generation/task_terminal_events.py:57` 的 `emit_task_terminal_events`，需要 Codex 确认真正的 CAS 位置【未验证】）调用 `settle(task_id)`。实际积分 = Σ `api_calls.cost_amount where task_id=?`，按 `ceil(cost_usd × POINTS_PER_USD × margin)` 换算。写一条 `capture`（实际值）和一条 `release`（`est - actual`），key 为 `settle:{task_id}`，保证重复调用是空操作。失败或取消时 ArcReel 账本本来就计零费用（`lib/billing/ledger.py:235,277-292`），所以 capture 为 0，全额 release。实际值大于预估值时，只扣到 est 封顶。超出部分记一条 `adjust` 负项，允许少量负余额，余额为负时拦住新任务。

**崩溃兜底**：在 `settle_interrupted_calls`（`lib/billing/ledger.py:340`）之后，追加一次“没有存活任务的 reserve 全额 release”。

**Agent 回合**：`record_agent_turn` 不经过 pending 中间态（`lib/billing/ledger.py:302`），采用先扣后记：`/sessions/send`（`server/routers/assistant.py:153`）要求余额至少有一个最低门槛（比如 5 点），回合结束后按实际费用记一条 `capture`。

**积分定价锚点**：参照 SceneMixer 的 100 点 $1.49、Pro 700 点 $7.99，设 1 点约等于 $0.011 零售价，`POINTS_PER_USD` 和 `margin` 放进 `config/pricing.json`，后端和营销站读同一份配置。

### 分阶段任务

| 阶段 | 改动（具体到文件和接口） | 人日【推断】 | 验收 |
|---|---|---|---|
| P0 合规基线 | 公开 fork；在控制台全局页脚组件加 “Powered by ArcReel” 和源码链接（保留 `AboutSection.tsx:193`）；在 `NOTICE` 末尾追加修改说明 | 0.5 | 任何登录后的页面都能看到署名和源码链接 |
| P1 多租户 | `server/auth.py:440` 的 `_payload_to_user` 改为从 `sub` 和 API Key 的 user_id 解析出真实用户，`role` 读库；`lib/db/repositories/base.py:17` 的 `_scope_query` 按 `current_user` 过滤（用 contextvar 注入）；`task_repo.py:470` 的 `claim_next` 原生 SQL 不按用户过滤（worker 是全局的），但要把 user_id 带进任务上下文；新增 `require_project_access` 依赖，挂到所有 `{project_name}` 路由；`GET /projects`（`projects.py:574`）按 `project_owners` 过滤；`POST /projects` 由服务端生成 `u{uid}-{slug}`；`files.py:302` 的公开媒体改为 HMAC 签名 URL（`?exp=&sig=`，复用 `create_download_token` 的思路） | 4–6 | A 用户无法列出、读取或下载 B 用户的项目和媒体（直接访问返回 403/404）；未签名的媒体 URL 返回 403 |
| P2 认证 | `server/routers/auth_public.py`：`POST /auth/otp/send`、`POST /auth/otp/verify`（首次验证即自动注册，与 SceneMixer 一致）；Google OIDC 用 Authlib 实现 `/auth/google/login|callback`；Apple 推迟到 P8；注册时发 50 点 `grant_promo`；`?ref=` 写入 `referrer_id`；保留管理员口令登录，供运营使用 | 3–5 | 新邮箱收到验证码后可以登录，账户里有 50 点；Google 首登会建号，再登不会重复建号 |
| P3 积分账本 | 新建 `lib/billing/credits.py`（reserve / settle / grant / adjust）、`lib/db/models/credit.py`、对应的 repository；挂接点见上一节；`GET /me/credits`、`GET /me/credits/entries` | 5–7 | 提交一个视频任务后冻结额等于预估值；成功后余额 = 初始 − 实际；失败或取消后余额恢复原值；同一 task 的 settle 调两次，流水不变；kill worker 再重启后，冻结被释放 |
| P4 支付 | `lib/payments/base.py` 定义 `PaymentProvider`，提供 `create_checkout(sku,user)->url` 和 `parse_webhook(req)->list[GrantEvent]`；先实现 `creem.py`，再实现 `stripe.py`；`POST /billing/checkout`、`POST /billing/webhook/{provider}`（先按 `webhook_events` 去重，再写 `grant_purchase` 或 `grant_subscription`，订阅积分按 `period_end` 建桶）；退款或拒付时写负 `adjust` | 3–5 | 沙箱支付完成后，余额只增加一次（重放同一个 webhook 不会重复入账）；退款后余额相应减少 |
| P5 控制台商业 UI | `frontend/src/` 下新增 `/pricing`、`/billing` 页面（余额、流水、积分包、会员）；每个生成按钮在确认前显示点数（读 `cost-estimate`）；402 时弹充值框；免费账号的 final-cut 在 `lib/final_cut/ffmpeg_render.py` 加 AI 角标水印；角色照片和音色上传限会员使用；控制台 i18n 在现有 i18next 上补 zh-TW 和 ja（`lib/i18n/` 服务端同步补） | 3–5 | 免费用户导出的成片带水印，会员没有；所有付费动作提交前都能看到价格 |
| P6 营销站 | 新建独立仓库或 `marketing/` 目录（不含 ArcReel 代码），用 Astro 静态生成：英文在根路径，加 `/zh-hant/`、`/ja/` 前缀，每页带 hreflang 和 x-default；首页、定价（读 `config/pricing.json`）、10–20 个关键词落地页（novel-to-video、ai-short-drama-generator 等）、示例剧集、FAQ、legal、privacy、terms；生成 sitemap.xml；robots 放行 AI 爬虫，只禁 `/api/`；部署到 Cloudflare Pages，`/app/*` 反代到 ArcReel | 3–5 | 每个语言的页面在 Google Rich Results 和 hreflang 校验中都没有错误；定价页数字与后端配置一致 |
| P7 部署 | `DATABASE_URL` 切到 Postgres（`lib/db/engine.py:56`），跑 Alembic；`deploy/docker-compose.yml` 增加 postgres；前面挂 Cloudflare；新增每日对账脚本 `scripts/reconcile_credits.py`（Σ流水 = balance + reserved，订单 = grant）；部署到 HK 并跑一次冒烟 | 2–3 | 在线上完成一遍“注册 → 赠点 → 生成一段视频 → 成片 → 充值 → 余额”的冒烟；对账脚本差额为 0 |
| P8（按需） | Apple 登录、联盟分佣（佣金表 + 延迟可提现 + 退款追回）、大陆站（支付宝/微信官方商户，需要大陆主体和备案） | — | 等前面的核心闭环跑出真实付费后再启动 |

### 支付渠道决策

【事实】Creem 支持卡、Apple Pay、Google Pay、**Alipay（Global，仅一次性支付）** 和 **Alipay HK**，不支持微信支付 ([Creem payment methods](https://docs.creem.io/merchant-of-record/finance/payment-methods))，可以提现到支付宝 ([Creem payouts](https://docs.creem.io/merchant-of-record/finance/payouts))。Paddle 的费率是 5% + 50¢，作为 MoR 承担全球报税；它的微信支付只面向中国大陆的桌面端客户，支付宝要申请开通，并且只对人民币定价的商品展示 ([Paddle pricing](https://www.paddle.com/pricing)、[Paddle WeChat Pay](https://developer.paddle.com/concepts/payment-methods/wechat-pay)、[Paddle Alipay](https://developer.paddle.com/concepts/payment-methods/alipay))。Polar 支持向香港和台湾提现，不支持中国大陆，也没有列出支付宝或微信 ([Polar countries](https://polar.sh/docs/merchant-of-record/supported-countries))。Stripe 的 credit grants 是开票时的抵扣，不是可以预冻结的实时余额 ([Stripe billing credits](https://docs.stripe.com/billing/subscriptions/usage-based/billing-credits))，所以无论用哪家支付，余额都必须由 ArcReel 自己的账本持有。Lemon Squeezy 正在并入 Stripe Managed Payments ([LS 2026 update](https://www.lemonsqueezy.com/blog/2026-update))，新项目不应该再接。

【推断，决策】如果没有海外公司主体，默认选 **Creem**：它是 MoR，替你承担销售税；Alipay HK 覆盖香港买家；可以提现到支付宝，方便大陆创始人收款；名义费率最低。代价是支付宝只能用于积分包，订阅只能刷卡。如果已有香港或澳洲主体（SceneMixer 就是澳洲主体 + Stripe），改用 **Stripe 直连**，税务自理。**Paddle** 作为被拒审时的备选。三家都放在 `PaymentProvider` 接口后面，切换只需要改配置。【未验证】SceneMixer 用的 Airwallex 在这几份笔记里没有调研费率、支持的支付方式和 AI 产品审核政策，不纳入第一期。台湾本地的街口支付、LINE Pay、超商付款也都没有找到 MoR 支持。【未验证，最大上线风险】各家 MoR 对 AI 生成视频产品的审核政策都没有取到，第一周就应该同时向 Creem 和 Paddle 提交审核申请。

## Conclusion

这次选型最反直觉的发现是：SceneMixer 级的 C 端体验，瓶颈不在 UI 模板，而在“谁持有余额”和“谁对网络用户负 AGPL 义务”这两个归属问题上。模板把余额放在 Node 应用里，账本却必须在能拦住 GenerationWorker 的 Python 侧。模板的许可证要求闭源，ArcReel 的许可证要求开源。两个矛盾都指向同一个答案：商业外壳长在 ArcReel 里面，并公开源码。护城河交给 SceneMixer 已经证明有效的东西，也就是上万页的多语言程序化 SEO、对 AI 爬虫的开放姿态和清晰的按秒定价，这些都在不受 AGPL 约束的营销站和运营数据里。

往后看，这条路线的风险不在工程上，而在两件外部事务：一是 MoR 是否接受 AI 视频产品，二是外壳通过 API 调用 ArcReel 时的法律边界。所以 P0 和支付审核申请应该与 P1 同时启动。另外，如果上游 ArcReel 将来自己做了多租户，原地改造的 fork 会面临合并冲突。建议把 P1 的 `_scope_query` 覆盖和认证映射按 ADR 0021 的接口写成可以回馈上游的形态，最好直接提给上游，把“维护一个 fork”变成“共享一份多租户能力”。
