# SceneMixer 一比一复刻：开源项目全面对比

> **广域检索后修订：**本报告基于较窄的候选池，开头「影策第一」仅作为当时的暂定判断。新增发现的 Go/MIT [连镜](https://github.com/zaylora/video-canvas)和 Java/MIT [NovaNova Studio](https://github.com/Swayingleaves/novanova-studio)都具备短剧、3D 导演台与支付相关源码，必须进入第一梯队。当前复评与搜索范围见[广域候选复评](SceneMixer广域候选复评.md)；以下旧排名不再单独作为最终选型依据。

核查日期：2026-11-06。目标是复刻 [SceneMixer 大陆站](https://scenemixer.cn/) 的**整站用户旅程**，不是只做短剧生成器或 `#world` 展示。以下比较公开页面、官方说明和公开源码；没有运行候选的付费生成、支付回调和并发用户验收。详细基线见[整站功能清单](../research_notes/SceneMixer一比一复刻功能基线.md)，项目源码证据见[候选审计](../research_notes/SceneMixer一比一候选源码审计.md)及[全球补查](../research_notes/SceneMixer一比一全球补查.md)。

## 结论先行

**严格按「开源且可自建商业 C 端」选一个项目：影策 Open AI Canvas 第一。**它是已核查单仓库里最接近的起点：Go 业务后端、React 创作端，公开源码包含短剧从小说到成片、3D 预演、用户后台、积分和支付。其 [MIT 许可](https://github.com/ddcat-ai/open-ai-canvas/blob/main/LICENSE)允许商业改造。但它不是一比一成品：完整世界引擎[仍标为下个版本内测](https://github.com/ddcat-ai/open-ai-canvas/blob/main/README.md)，预演台到短剧视频的自动空间约束未被证实，SceneMixer 式会员方案、四入口、样片与获客页面仍需逐项补齐。

**只按创作功能相似度：DramaClaw 第一，但不符合本题的商业开源条件。**它有[短剧流水线与 Director World](https://github.com/dramaclaw/dramaclaw)，公开服务端含 360 场景/空间契约；完整 3D 导演台仍在 closed beta。[官方许可说明](https://github.com/dramaclaw/dramaclaw/blob/main/docs/en/license.md)明确社区版是 source available，不能作为第三方托管 SaaS，公开仓库不含企业版的多租户和计费。因此不能称为可直接复刻 SceneMixer 商业站的开源底座。

## 逐项对比

表中「有」指公开实现或官方功能说明，**不代表本轮完成实测**；「部分」指相邻功能存在但不足以等同 SceneMixer；「未核到」只表示公开证据不足。SceneMixer 列依据[首页](https://scenemixer.cn/)、[样片项目](https://scenemixer.cn/showcase/815/episode/2470)、[帮助中心](https://scenemixer.cn/help/)、[会员](https://scenemixer.cn/membership)、[定价](https://scenemixer.cn/pricing/)。

| 一比一验收项 | SceneMixer 目标 | 影策 MIT / Go | DramaClaw ELv2 / Python | AID Studio MIT / Java | PRINTFILM MIT / Python | ArcReel 现有仓库 |
| --- | --- | --- | --- | --- | --- | --- |
| 输入到分集 | 小说、剧本、一句想法自动拆集 | 有小说拆集；一句想法需验收 | 有小说/剧本到分集 | 有 | 有 | 有，偏创作者工作流 |
| 四入口 | 上传剧本、AI 创作、商品照广告、参考视频复刻进入同一项目 | 有短剧与电商 Agent；统一项目模型、视频复刻入口未核 | 有剧集、广告/商品视频能力；同一四入口未核 | 部分，偏短剧 | 部分，偏漫剧 | 部分，偏故事/剧本 |
| 角色/场景/道具 | 设定图、上传替换、跨集/跨项目复用、音色及状态变体 | 有素材与短剧资产；细节需验收 | 有共享资产库、声音/变体 | 有资产流程 | 有资产流程 | 有资产及项目流程 |
| 共享 3D 片场 | 同场景 360°、空间布局、人物/道具位置 | 有 3D 预演台；完整世界引擎内测 | Director World 公开源码最接近；完整导演台内测 | 未核到 | 未核到 | 未核到 |
| 多机位连续性 | 同片场全景、过肩、反打、特写，并约束生成视频 | 预演支持机位；自动跨镜头生成链未证实 | 空间契约与取景源码；完整成片链实测未做 | 参考图一致性，不等同 | 参考图一致性，不等同 | 参考图/提示词一致性，不等同 |
| 分镜与逐段生成 | 每集镜头脚本、模型档位、对白视频、任务状态 | 有短剧逐段视频/任务 | 有流水线与画布 | 有 | 有 | 有 |
| 逐段精修 | 改画面、台词、裁剪、单段重出、历史版本 | 部分：画布精修及版本；细节需实测 | 画布与流水线双轨、版本 | 部分 | 部分 | 有逐分镜重出与编辑 |
| 成片交付 | 合成、配乐、字幕/SRT、分享、下载 | 有成片与画布精剪；逐项验收 | 有 MP4、字幕/SRT 等 | 有导出 | 有合成 | 有成片/时间线；分享站不足 |
| 多人 C 端 | 手机/网页注册、个人项目、资产库、任务中心、公开样片 | 有用户端、后台、资产/任务；[体验站](https://yingce.tv/)可见工作区 | 社区版主要单机创作；企业多租户闭源 | 有用户端和后台 | 有前台/后台 | 工作台有登录，但非成熟多租户 |
| 获客与内容页 | 官网、作品展示、指南、帮助、定价、SEO 页面 | 创作端有；SceneMixer 式营销/样片体系未核到 | 创作者产品页；C 端获客体系未核到 | 部分 | 部分 | 文档站有；C 端营销体系待建 |
| 账户积分 | 按字数/图片/视频秒数计价、提交前报价、冻结/交付/失败退款 | 有定价/账务/充值源码；具体规则需适配 | CE 用量计费未开放，EE 管理 | 有积分冻结/结算 | 有账务与预留 | 供应商成本账本；无用户钱包 |
| 充值与支付 | 积分包、支付宝/微信、订单 | [充值商品和支付插件](https://github.com/ddcat-ai/open-ai-canvas/blob/main/docs/content/docs/overview/features.mdx) | CE 端到端支付未核到；EE 计费闭源 | 有充值/支付 | 有支付 | 无 |
| 会员权益 | 月/季/年包、赠点、项目数/并发/存储配额、升级与到期 | 周期会员及 SceneMixer 式权益规则未验收 | CE 未公开 | [会员议题仍在规划](https://github.com/shijue-aid/aid-studio/issues/3) | 未核到完整周期会员 | 无 |
| 推荐与客服 | 推荐码、邀请、AI 帮助、反馈和订单支持 | [推广中心](https://github.com/ddcat-ai/open-ai-canvas/blob/main/docs/content/docs/overview/features.mdx)有源码/文档；客服流程待验收 | 部分 | 部分 | 未核到完整链 | 部分 |

影策的相关源码入口：[短剧编排](https://github.com/ddcat-ai/open-ai-canvas/blob/main/backend/internal/app/drama_orchestrator.go)、[成片导出](https://github.com/ddcat-ai/open-ai-canvas/blob/main/backend/internal/app/drama_export.go)、[3D 预演](https://github.com/ddcat-ai/open-ai-canvas/tree/main/web/src/components/canvas/previs)、[支付](https://github.com/ddcat-ai/open-ai-canvas/blob/main/backend/internal/app/payment.go)。DramaClaw 的关键证据为 [Director World](https://github.com/dramaclaw/dramaclaw/tree/main/src/novelvideo/director_world)、[功能边界](https://github.com/dramaclaw/dramaclaw/blob/main/docs/en/concepts/features.md)、[许可证原文](https://github.com/dramaclaw/dramaclaw/blob/main/LICENSES/Elastic-2.0.txt)。其他候选的源码链接逐项列在[候选审计](../research_notes/SceneMixer一比一候选源码审计.md)。

## 排名与取舍

1. **影策：最接近可合法商业改造的完整开源底座。** Go 后端降低了重做账户、任务、支付与编排的起步量，但其 Agent 运行时还涉及 Node，[官方仓库约定](https://github.com/ddcat-ai/open-ai-canvas/blob/main/AGENTS.md)并非「纯 Go 项目」。现有 3D 预演台与 SceneMixer 所述的自动搭景/多机位视频约束之间仍有核心研发任务。
2. **DramaClaw：纯功能参考第一。** 在空间世界与创作链上比影策更接近。社区版的托管许可和缺失的企业商业模块使其无法作为题目要求的开源 SaaS 答案；只有拿到另行授权并验收企业版，排名才可能改变。
3. **AID Studio / PRINTFILM：商业与短剧流程可借鉴，世界能力差距大。** 若世界片场是必须项，它们的复刻工作量不能仅按页面和支付完成度估算。
4. **ArcReel 当前库：保留既有创作能力有价值，但并非一比一复刻的最近开源起点。** 还需建设共享 3D 片场、真正多租户、用户钱包/支付/会员，以及整站获客流程。现有 Python 栈本身不是决定排名的唯一原因。

[全球补查](../research_notes/SceneMixer一比一全球补查.md)还核查了 Go 的 M-duanju、灵果短剧、MediaGo Drama，以及海外 EvoLinkAI AIDrama Studio、本地 3D 工具；前者缺世界域或商用功能，后者缺多人收费整站。VOZEB-PRO 看似接近但公开仓库未见应用源码，且商业许可受限，不能按开源底座排序。

## 以影策复刻时必须补齐的交付件

1. **世界到视频的闭环**：从场景图/剧本自动建立可复用的场景坐标、人物/物件位置与机位；把场景与镜头约束传到视频生成请求。用同一房间的正反打、过肩和跨集复用实片验收，而不是只看 3D 预演截图。
2. **SceneMixer 创作流程**：统一四入口到项目/分集结构；补齐跨项目资产和音色、镜头版本、单段修改与重算、字幕/SRT、分享与素材下载的差异。每项以用户操作和产物验收。
3. **会员与账务规则**：实现月/季/年购买及升级/到期、赠点与额度；按每次任务实际模型/时长报价，冻结、核销与失败退款需在并发与重复回调下保持一致。现有充值插件只覆盖部分规则。
4. **C 端与增长**：做访客首页、样片项目、公开分享、指南/帮助/定价、免费试用、推荐邀请及登录后支持入口；移动端和 SEO 单独验收。
5. **生产与模型质量**：完成多用户隔离、注册/密钥/存储/支付的安全配置，实测目标模型的对白、角色一致性、画幅、画质、成本和服务稳定性。[影策 README](https://github.com/ddcat-ai/open-ai-canvas/blob/main/README.md)对公网多人部署给出了明确配置边界。网页展示不能证明 SceneMixer 自研了「物理视频基础模型」；复刻应先验证用户可见的同片场连续性。

**选型决定**：如果要求拿到代码就已经一比一交付，当前没有可推荐的项目；如果要选一个开源仓库作为一比一复刻的开发起点，选影策，最先验证世界到视频闭环和会员账务。若要求直接使用功能最像的现成产品，需要先与 DramaClaw 权利方确认商业授权和企业版交付范围。
