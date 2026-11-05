# SceneMixer 整站复刻：2026 年 11 月 6 日调研总览

本页汇总当天对 [SceneMixer 大陆站](https://scenemixer.cn/) 的功能核查、开源候选检索和选型修订。目标是寻找**可用于复刻整个商业创作网站**的公开源码：短剧从输入到成片、同场景空间与多机位、C 端页面、用户账务和支付。阅读详细证据可从[整站功能基线](../research_notes/SceneMixer一比一复刻功能基线.md)与[广域候选复评](SceneMixer广域候选复评.md)开始。

## 当前结论

网上有大量相关项目。此前只围绕少数项目深审，就将影策称为「唯一第一名」，检索范围不足；该结论已撤回。广域检索后，**影策与连镜是 Go 业务后端、MIT 许可、自建短剧和支付能力均有公开源码的双领先候选**；Java/MIT 的 NovaNova Studio 也属于功能第一梯队。Toonflow、TapCanvas、DramaClaw 在创作或导演台方面很强，但公开版本分别存在自建商业闭环或许可边界。候选都没有经本轮证实可直接一比一交付 SceneMixer 展示的自动共享片场和跨镜头视频空间一致性。

这不是「全球没有现成产品」的断言。本轮没有运行候选的真实小说到成片、支付回调或跨用户并发；「有源码」「作者描述可用」与「生产验收通过」是三个不同状态。若需要选定唯一开发底座，应让影策、连镜和 NovaNova 跑同一份短剧、三机位、成片、充值退款与用户隔离脚本，再比较实际结果。

## SceneMixer 整站验收范围

| 域 | 公开页面所示的主要能力 | 证据边界 |
| --- | --- | --- |
| 获客与账户 | 首页、样片、指南、帮助、定价；手机号验证码、推荐码、邀请入口 | [首页](https://scenemixer.cn/)、[样片库](https://scenemixer.cn/drama/)、[帮助中心](https://scenemixer.cn/help/)可见；登录后的邀请流程未验收 |
| 创作与交付 | 小说/剧本、AI 创作、商品照片广告、参考视频复刻四入口；角色场景道具、分集分镜、逐段生成/重做、整集合成、字幕、分享下载 | [帮助中心](https://scenemixer.cn/help/)描述完整流程；[公开样片项目](https://scenemixer.cn/showcase/815/episode/2470)可见资产、分镜、视频及 10 段 93 秒时间轴，展示项目的编辑操作禁用 |
| 世界与视频 | 同一 360° 片场、人物/家具位置与多机位，跨镜头复用空间关系 | [首页世界段](https://scenemixer.cn/#world)是可见展示和产品主张；网页不能证明后台算法、自研物理视频基础模型或实际成片达到一致性 |
| 商业与运营 | 注册赠点、免费设定图与短预览；按字数/张数/视频秒数计费，提交前报价；任务冻结/退款；充值、月季年会员、并发/项目/存储权益、支付宝/微信 | [定价](https://scenemixer.cn/pricing/)、[会员](https://scenemixer.cn/membership)、[帮助中心](https://scenemixer.cn/help/)说明规则；未进行真实支付和账本验收 |

## 候选结论与关键证据

| 候选 | 已核到的公开能力 | 决定性边界 |
| --- | --- | --- |
| [影策 Open AI Canvas](https://github.com/ddcat-ai/open-ai-canvas) | Go/React；短剧流水线、用户工作区、画布 [3D 预演](https://github.com/ddcat-ai/open-ai-canvas/tree/main/web/src/components/canvas/previs)、积分和支付插件；MIT | [完整世界引擎仍为内测](https://github.com/ddcat-ai/open-ai-canvas/blob/main/README.md)，周期会员与世界到视频闭环待验收 |
| [连镜 video-canvas](https://github.com/zaylora/video-canvas) | Go/React；短剧整集、普通画布 3D 导演台、支付适配器和冻结/退款；MIT | [短剧页面当前过滤导演台](https://github.com/zaylora/video-canvas/blob/master/web/src/pages/drama/workspace/assets-area.tsx)，自动空间约束与会员待实现或验收 |
| [NovaNova Studio](https://github.com/Swayingleaves/novanova-studio) | Java/Next.js；短剧/漫剧制作、3D 导演台及支付宝/微信支付源码；MIT | 导演台手工导出参考媒体；尚未证明自动共享片场进入短剧视频生成，作者注明未做浏览器人工验收 |
| [Toonflow](https://github.com/HBAI-Ltd/Toonflow-app) | 3D 导演台、多租户账务与创作源码；MIT | [自建多租户入口仍显示开发中](https://github.com/HBAI-Ltd/Toonflow-app/blob/master/apps/web/src/components/settings/panels/multiTenant/developmentNotice.vue)，微信/支付宝充值代理官方云接口 |
| [TapCanvas](https://github.com/anymouschina/TapCanvas) | 一键成片、3D 导演台、画布与团队流程；根项目 MIT | README 明说社区版无在线支付，商业版是独立产品；内置网关保留自身 AGPL 许可 |
| [DramaClaw CE](https://github.com/dramaclaw/dramaclaw) | 小说到成片、Director World 360 场景/空间契约，创作功能相似度高 | [Elastic 2.0 禁止第三方托管](https://github.com/dramaclaw/dramaclaw/blob/main/LICENSES/Elastic-2.0.txt)，官方称多租户/计费在未公开企业版；不是可直接运营的开源 SaaS 底座 |

AID Studio、PRINTFILM、EvoLinkAI AIDrama Studio、Jellyfish 偏创作与计费；Kinema、Reveric、Film Engine、Dralo Studio 偏本地创作与 3D 预演。它们的单项能力值得借鉴，但本轮公开证据未使其超过前表对整站的覆盖。详见[广域候选复评](SceneMixer广域候选复评.md)，其中列出更多项目与具体排除理由。

## 检索覆盖与研究索引

主检索 10 组中英文 GitHub 查询取前排 **260 个去重仓库样本**；国际补查 8 组得 **149 个去重样本**，列 22 个宽松相关项目；中文与 Go 补查记录 24 个不同制作候选。这些集合重叠、只取前排，不能相加，也不能代表全网穷尽。GitHub API 后续触发限流，研究补用了项目原站与网页搜索。

- **最终比较：**[广域候选复评](SceneMixer广域候选复评.md)。此前较窄范围的[一比一对比](SceneMixer一比一复刻开源项目对比.md)和[ArcReel 商业平台旧报告](ArcReel%20C端商业平台选型.md)都加了修订提示，不再单独作为最终排名依据。
- **整站和源码证据：**[功能基线](../research_notes/SceneMixer一比一复刻功能基线.md)、[候选源码审计](../research_notes/SceneMixer一比一候选源码审计.md)、[全球初次补查](../research_notes/SceneMixer一比一全球补查.md)、[整站候选源码矩阵](../research_notes/SceneMixer全产品候选-源码矩阵.md)、[整站候选全球检索](../research_notes/SceneMixer全产品候选-全球检索.md)。
- **广域发现记录：**[主检索式和数量](../research_notes/SceneMixer广域检索-主检索记录.md)、[国际候选](../research_notes/SceneMixer广域检索-国际.md)、[中文与 Go 候选](../research_notes/SceneMixer广域检索-中文Go.md)。
- **世界能力专项：**[产品候选](../research_notes/SceneMixer世界模型候选-产品.md)、[技术候选](../research_notes/SceneMixer世界模型候选-技术.md)。这两份只回答空间/机位组件问题，不能代替整站比较。

## 唯一候选的验收门槛

同一份小说章节分别导入影策、连镜和 NovaNova，完成「拆集 → 角色与同一房间 → 全景、过肩、反打三个机位 → 逐段生成 → 整集合成」。检查 3D 场景及机位是否进入生成请求，成片中人物和房间几何是否跨镜头稳定。再用测试账户分别完成充值、失败退款、会员权益和跨用户项目/账单隔离。当前公开材料不足以替代这些实测，故暂不作「一比一已可用」或精确相似度百分比的结论。
