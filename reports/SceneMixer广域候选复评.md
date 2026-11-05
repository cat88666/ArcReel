# SceneMixer 整站复刻：广域开源候选复评

核查时间：2026-11-06。此前报告只深审少数熟悉项目，样本范围不足；本报告重新从仓库搜索和第一方资料发现候选。目标仍是 [SceneMixer 大陆站](https://scenemixer.cn/) 的整套用户旅程：小说/剧本到分集、资产、共享场景/多机位、逐段视频、成片；访客页面、账号、会员、积分、支付及运营。目标基线见[功能清单](../research_notes/SceneMixer一比一复刻功能基线.md)。

## 搜索边界

主检索用 10 组中英文 GitHub Repository Search 式，前排样本共 **260 个去重仓库**；另一轮国际检索用 8 组式得 **149 个去重样本**、列出 22 个宽松相关项目；中文/Go 检索记录 **24 个去重制作候选**。这些样本有交集，不相加；也没有遍历每组全部命中。查询式、命中数和初筛名单分别见[主检索记录](../research_notes/SceneMixer广域检索-主检索记录.md)、[国际检索](../research_notes/SceneMixer广域检索-国际.md)、[中文与 Go 检索](../research_notes/SceneMixer广域检索-中文Go.md)。GitHub 搜索 API 随后遇到速率限制，已用网页搜索补查，但仍不声称覆盖整个互联网。

**修正：此前将影策称为唯一最接近的开源底座，依据不充分。**新发现的连镜、NovaNova Studio、Toonflow、TapCanvas 等都应进入主比较。真正需要分清的是：目录有 3D 代码，是否已经接进短剧视频流水线；目录有钱包代码，是否包含可自建的支付订单与回调；网站展示功能，是否在开源仓库中。

## 第一梯队：同表对照

「有」只表示第一方文档或源码有对应模块，不等于本轮运行验收。**所有候选均未证实可一比一交付 SceneMixer 所展示的自动共享片场、跨镜头视频空间一致性。**

| 项目 | 短剧到整集 | 3D/共享片场 | 用户/运营页面 | 积分与自建支付 | 开源/商用边界 | 当前判断 |
| --- | --- | --- | --- | --- | --- | --- |
| [影策 Open AI Canvas](https://github.com/ddcat-ai/open-ai-canvas) | 小说拆集、资产、逐段视频、合成、画布精修 | 画布内有 3D 预演；完整世界引擎仍为下版本内测，自动进入短剧链未证实 | 创作端、用户、后台、资产任务；[体验站](https://yingce.tv/)实际打开 | 充值商品、支付插件、账务；SceneMixer 式周期会员未验收 | [MIT](https://github.com/ddcat-ai/open-ai-canvas/blob/main/LICENSE)；Go 业务后端 + React，Agent 另用 Node | **仍是可商用整站起点的领先候选，但不再称唯一** |
| [连镜 video-canvas](https://github.com/zaylora/video-canvas) | 小说/剧本拆集、分镜视频、[Go 服务端整集合成](https://github.com/zaylora/video-canvas/blob/master/backend/internal/pkg/videoframe/compose.go)及成片页 | 普通画布有 3D 导演台、多机位、导出参考媒体；[短剧工作区目前明确过滤导演台](https://github.com/zaylora/video-canvas/blob/master/web/src/pages/drama/workspace/assets-area.tsx) | 多人账号、工作台、后台、资产；[公开体验站](https://canvas.vbing.site/)可见落地/登录页 | [微信](https://github.com/zaylora/video-canvas/blob/master/backend/internal/payment/wechat/wechat.go)、[支付宝](https://github.com/zaylora/video-canvas/blob/master/backend/internal/payment/alipay/alipay.go)等支付适配器及冻结/退款；会员未核到 | [MIT](https://github.com/zaylora/video-canvas/blob/master/LICENSE)；Go 业务后端 + React，Agent 用 TypeScript；版本 0.6.x | **与影策并列 Go 强候选**；短剧与导演台的断点是关键缺口 |
| [NovaNova Studio](https://github.com/Swayingleaves/novanova-studio) | [漫剧工作流](https://github.com/Swayingleaves/novanova-studio/blob/master/docs/zh-cn/using-studio/comic-drama.mdx)描述剧本、角色/场景/道具、逐镜、时间线和 MP4 | 有[3D 导演台源码](https://github.com/Swayingleaves/novanova-studio/tree/master/web/src/app/%28user%29/canvas/director-desk)，手工输出参考媒体；未证实自动世界到视频，作者称合入时未做浏览器人工验收 | 用户/运营后台及创作工作台 | [支付后端源码](https://github.com/Swayingleaves/novanova-studio/tree/master/server/src/main/java/com/novanovastudio/payment)含微信/支付宝；会员未核到 | [MIT](https://github.com/Swayingleaves/novanova-studio/blob/master/LICENSE)；Java/Spring Boot + Next.js | **功能粗覆盖进入第一梯队**；需真实部署验证 3D、支付与成片 |
| [Toonflow](https://github.com/HBAI-Ltd/Toonflow-app) | 剧本、角色、场景、镜头视频与画布 | [3D 导演台源码](https://github.com/HBAI-Ltd/Toonflow-app/tree/master/packages/nodes/director3dNode/src)真实存在；自动跨镜头约束未证实 | 公开多租户账号与钱包代码，但[当前发布入口仍显示开发中](https://github.com/HBAI-Ltd/Toonflow-app/blob/master/apps/web/src/components/settings/panels/multiTenant/developmentNotice.vue) | SQL 钱包预占/结算有源码；[微信/支付宝充值代理 Toonflow 官方云](https://github.com/HBAI-Ltd/Toonflow-app/blob/master/apps/server/src/utils/channel/toonflow.ts)，自建支付闭环未公开 | [MIT](https://github.com/HBAI-Ltd/Toonflow-app/blob/master/LICENSE) | **创作和导演台强**；自建商业站尚有核心断点 |
| [TapCanvas 社区版](https://github.com/anymouschina/TapCanvas) | 一键成片 Agent、章节/画布双视图、字幕编辑 | 已集成 3D DirectorDesk 输出参考媒体；自动世界约束未证实 | 有项目、画布、团队/分享 | README 明确社区版**不提供在线支付和短信验证码**，商业版是另一产品 | 根项目 MIT；内置 `apps/new-api` 保留 AGPL-3.0，须按组件许可处理 | **创作/空间强**，运营闭环须自建 |
| [DramaClaw CE](https://github.com/dramaclaw/dramaclaw) | 小说到成片流水线与画布 | [Director World](https://github.com/dramaclaw/dramaclaw/tree/main/src/novelvideo/director_world)含 360 场景与空间契约，完整 3D 导演台内测 | CE 主要单机创作；多租户和计费属于未公开企业版 | CE 无可确认的自建 C 端商业闭环 | [Elastic 2.0](https://github.com/dramaclaw/dramaclaw/blob/main/LICENSES/Elastic-2.0.txt)限制第三方托管，官方明确非 OSI 开源 | **功能相似度强，但不能按社区版许可证运营整站** |

连镜的 [README](https://github.com/zaylora/video-canvas)和[源码审计](../research_notes/SceneMixer广域检索-中文Go.md)证明前表中的 Go 短剧、支付、合成模块不是只有文案；同时短剧页面明确未接导演台。Toonflow 的自建支付边界由[充值路由](https://github.com/HBAI-Ltd/Toonflow-app/blob/master/apps/server/src/routes/channel/wallet/pay.ts)、[渠道实现](https://github.com/HBAI-Ltd/Toonflow-app/blob/master/apps/server/src/utils/channel/toonflow.ts)和[多租户交接说明](https://github.com/HBAI-Ltd/Toonflow-app/blob/master/.agent/multiTenantContext.md)共同支持。影策的[3D 预演源码](https://github.com/ddcat-ai/open-ai-canvas/tree/main/web/src/components/canvas/previs)及[世界引擎阶段](https://github.com/ddcat-ai/open-ai-canvas/blob/main/README.md)需分开读。

## 其他相关项目及排除理由

这些项目并非「不存在」，而是本轮公开证据不足以使其超过第一梯队：

- [Huohuo Drama](https://github.com/appolloqin/huohuo-drama)：小说到成片和多渠道支付描述很全；未核到共享 3D 片场，仓库未见可确认的 LICENSE 文件。
- [AID Studio](https://github.com/shijue-aid/aid-studio)、[PRINTFILM](https://github.com/yi1108/printfilm)、[EvoLinkAI AIDrama Studio](https://github.com/EvoLinkAI/ai-short-drama)、[Jellyfish](https://github.com/Forget-C/Jellyfish)：各有短剧链或账务/支付，公开证据未核到同片场 3D 世界链。
- [Kinema](https://github.com/chillzhuang/Kinema)、[Reveric](https://github.com/looplj/reveric)、[Film Engine](https://github.com/mannyhenri/film-engine)、[AI Video Production Editor](https://github.com/LudwigKienle/ai-video-production-editor)、[Dralo Studio](https://github.com/lnblfkj-del/Dralo-Studio)：创作及 3D 预演强，但主要是本地/桌面工具，现成多用户收费整站不足。
- [LocalMiniDrama](https://github.com/xuanyustudio/LocalMiniDrama)：本地短剧工作台，无多人商业模块或共享 3D 场景证据。
- [BigBanana AI Director](https://github.com/shuyu-labs/BigBanana-AI-Director)：后续版本仅发布 Docker 镜像，源码不同步；当前许可证为 CC BY-NC-SA，不能作为可直接商业复刻的开源底座。
- [VideoForge](https://github.com/miao-x1/VideoForge)：有短剧、导演台、余额，但正式支付需另接，未见明确 LICENSE。
- [VOZEB-PRO](https://github.com/csyqlz/VOZEB-PRO)：产品宣传覆盖多域，公开仓库未见所述应用源码，BUSL-1.1 商业 SaaS 需授权。

其余宽松筛出的项目名称和原始搜索记录都保留在上述研究笔记中，避免把「没进前六」误写成「没找到」。

## 当前选型判断与下一步验收

**不再称某个项目是已被充分证明的唯一第一名。**若以已公开的 Go 业务后端、自建积分支付、短剧整集及合法商用为硬条件，**影策和连镜是双领先候选**。影策的优势是公开项目文档和可访问体验站显示更完整的短剧/画布产品；连镜的优势是 3D 导演台、Go 整集合成和支付适配器已经明确在同仓库。两者都缺少经证实的 SceneMixer 式自动世界到视频闭环。NovaNova 作为 Java/MIT 的第一梯队候选应一起验证，不能因语言被跳过。Toonflow 与 TapCanvas 更适合借鉴导演台/创作链，自建商业闭环尚有明确缺口。

若要从双领先中真正选一个，最小而有区分度的验收是：同一短剧项目导入一段剧本 → 建角色与房间 → 排正反打、过肩 3 个机位 → 导出参考帧并逐镜生成 → 合成一集 → 用测试支付完成充值和失败退款 → 在另一用户下验证项目与账单隔离。重点记录 3D 场景是否进入生成请求、生成视频是否保持同一房间的空间关系。没有这个实测，任何「一比一」比例或绝对第一都只是 README 排名。
