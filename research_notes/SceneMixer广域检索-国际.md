# SceneMixer 整站开源候选：国际广域发现

核查时间：2026-11-06。目标是先扩大候选池，再判断是否存在比旧候选更接近 [SceneMixer 大陆站](https://scenemixer.cn/) 的**整站**项目。这里的整站包含小说/剧本到成片、同片场空间/多机位、多人创作页面、积分/会员/支付。第一阶段只用宽松词发现项目；第二阶段才查 README、源码树、许可和实际对外服务边界。「未核到」不等于项目绝无此功能。未部署或运行以下候选。

## 可复查的搜索范围

GitHub Repository Search API，默认相关度排序，每式取前 30 条。不同关键词可能遗漏未写在仓库元数据的功能，计数也会随 GitHub 索引变化。本轮返回：

| 原样检索式 | 命中总数 | 实取样本 |
| --- | ---: | ---: |
| `AI short drama generator` | 29 | 29 |
| `novel to video AI` | 49 | 30 |
| `AI filmmaking studio` | 103 | 30 |
| `AI video production platform open source` | 17 | 17 |
| `storyboard video generation AI` | 193 | 30 |
| `3D previs AI video` | 11 | 11 |
| `AI movie maker open source` | 2 | 2 |
| `AI micro drama SaaS` | 0 | 0 |

共取 **149 个去重仓库**；其中混有脚本生成器、教程、模型包、影视无关仓库和纯本地工具，所以仓库数量不能等同整站候选数量。另以网页检索补看 GitLab、Hugging Face 与官方项目页的对应词，未发现可据第一方源码证明同时满足四域的项目；此处不对其索引覆盖率作总量声明。

## 新纳入初筛池的项目

下表是从样本中去掉明显无关项后的宽松初筛，**不是声称全部已通过源码审计**。链接均指向项目自身仓库；「先看」说明进入下一步核查的理由，其他项只记录发现以避免漏查。此前已经深审的 DramaClaw、影策、AID Studio、PRINTFILM 未计入下表。

| 项目 | 初筛理由及当前边界 |
| --- | --- |
| [Toonflow](https://github.com/HBAI-Ltd/Toonflow-app) | **重点深审**：MIT，短剧画布、3D 导演台，仓库还含多租户账号与账务源码；需核清自建支付和整集合成。 |
| [Kinema](https://github.com/chillzhuang/Kinema) | **重点深审**：AGPL，长篇小说到分镜/成片和 3D 导演台；README 定位本机创作。 |
| [Reveric](https://github.com/looplj/reveric) | **重点深审**：AGPL，小说、剧本、画布、3D 导演台和剪辑；README 定位桌面创作。 |
| [Jellyfish](https://github.com/Forget-C/Jellyfish) | **重点深审**：Apache，短剧项目、资产、镜头生成和任务中心；README 未展示同片场 3D。 |
| [Film Engine](https://github.com/mannyhenri/film-engine) | **重点深审**：MIT，电影剧本到成片、3D previs 和世界服务接入；README 明说本地服务无登录。 |
| [ChangJi](https://github.com/changji-ai/ChangJi) | Apache，本机单进程小说/脚本到成片；README 明说无账号和订阅。 |
| [StudioLite](https://github.com/PawanRamaMali/StudioLite) | MIT，18 阶段本地电影流程；README 明说无云账户。 |
| [Slate](https://github.com/coracoo/Slate) | MIT，本地电影分析到 2D/3D 预演与参考包；未见整站商业证据。 |
| [Nomi](https://github.com/aqm857886159/Nomi) | AGPL，本地 AI 视频画布、故事板和剪辑；仓库描述称无账号。 |
| [StoryGen Atelier](https://github.com/0xsline/StoryGen-Atelier) | Apache，故事板到视频片段及 FFmpeg 合成；未深核多人/世界/商业。 |
| [AIYOU](https://github.com/yubowen123/AIYOU_open-ai-video-drama-generator) | 短剧概念→剧本→分镜→视频，需深核许可、世界和 C 端。 |
| [Open AI Micro Drama Generator](https://github.com/Anil-matcha/Open-AI-Micro-Drama-Generator) | 多 Agent 短剧流程，需深核许可、世界和 C 端。 |
| [AI NovelFlow](https://github.com/qzw881130/AI-NovelFlow) | 小说转视频平台，需深核世界和商业；仓库许可证元数据不明。 |
| [Story Claw](https://github.com/ZC89757/story-claw) | MIT，小说到短剧和分镜，README 指向 Windows 桌面制作。 |
| [synes-autodrama](https://github.com/weicool123/synes-autodrama) | MIT，自动漫剧/短剧生成；需深核用户页面与空间。 |
| [FlintStudio](https://github.com/yuebuluo168/FlintStudio) | 自部署小说到成片 DAG；需深核世界/支付和许可。 |
| [VLM Generation Harness](https://github.com/7ohnson/VLM-Generation-Harness) | MIT，Blender 白模控制机位与空间，偏单一视频预演组件。 |
| [13soul Storyboard Studio](https://github.com/chenisan/13soul-storyboard-studio) | 本地 3D 导演台和机位，偏分镜工具。 |
| [AgentCine](https://github.com/pengchengneo/AgentCine) | 剧本/资产/分镜/配音/视频工作台，需深核世界和商业。 |
| [super_gen](https://github.com/xxx-888/super_gen) | 短剧全流程和积分计费的仓库描述，需深核许可、实际业务源码与空间。 |
| [ai-video-generation](https://github.com/VanGong1999/ai-video-generation) | MIT，画布/参考图/多视频生成，需深核成片/世界/商业。 |
| [AI Video Production Editor](https://github.com/LudwigKienle/ai-video-production-editor) | GPL，本地电影工作站含 3D 预演，已有先前审计；缺现成 C 端商业闭环。 |

## 五个重点项目的第一方核验

### Toonflow：本轮最重要的新竞争者

- [README](https://github.com/HBAI-Ltd/Toonflow-app/blob/master/README.md)描述剧本/角色/场景到镜头视频，支持桌面、Docker、服务器部署，采用 [MIT](https://github.com/HBAI-Ltd/Toonflow-app/blob/master/LICENSE)。README 的标准流程到「预览、整理与下载」，尚未证明 SceneMixer 式一键整集合成和多集剧情自动化。
- [3D 导演台源码](https://github.com/HBAI-Ltd/Toonflow-app/tree/master/packages/nodes/director3dNode/src)及[操作文档](https://github.com/HBAI-Ltd/Toonflow-app/blob/master/packages/nodes/director3dNode/readme.md)确实公开：场景/人偶/动作/机位/关键帧，导出 PNG 或 MP4 节点。这是可复用的空间预演实现；文档未证明它会自动把同片场约束传给每个短剧生成片段。
- [多租户账务包](https://github.com/HBAI-Ltd/Toonflow-app/tree/master/packages/multiTenant/billing)公开了 SQL 钱包、报价、预占、结算与释放；[账户管理源码](https://github.com/HBAI-Ltd/Toonflow-app/tree/master/packages/multiTenant/auth)也存在。但[当前发布入口](https://github.com/HBAI-Ltd/Toonflow-app/blob/master/apps/web/src/components/settings/panels/multiTenant/developmentNotice.vue)仍显示「正在开发」，[交接说明](https://github.com/HBAI-Ltd/Toonflow-app/blob/master/.agent/multiTenantContext.md)明确此版暂不开放多租户入口、在线支付/套餐不在自建多租户已完成范围。
- 仓库的[充值路由](https://github.com/HBAI-Ltd/Toonflow-app/blob/master/apps/server/src/routes/channel/wallet/pay.ts)确实接微信/支付宝参数，但[渠道实现](https://github.com/HBAI-Ltd/Toonflow-app/blob/master/apps/server/src/utils/channel/toonflow.ts)固定调用 `https://api.toonflow.net` 的 `/web/web/recharge/pay` 等接口。因此它是 Toonflow 官方云钱包的客户端代理，不能算自建 SaaS 的支付服务端源码。

**对比影策的含义：**Toonflow 在 3D 片场编辑上是强候选，还具备账务底层；但自建商业运营仍需把当前隐藏的多租户入口正式打通，并自建支付订单、回调、套餐和会员，此外要补 SceneMixer 式小说拆集到整集成片的统一流程。不能因为目录名含 `multiTenant/billing` 或出现微信支付宝选项，就把它算作已经可营运的整站。

### Kinema 与 Reveric：强创作与空间，非现成 C 端

- [Kinema README](https://github.com/chillzhuang/Kinema/blob/main/README.md)公开长篇小说、分集分镜、镜头视频、成片、3D 导演台与 30 多种运镜预设；其项目目录、本地素材和本机控制台定位明确。[AGPL 许可证](https://github.com/chillzhuang/Kinema/blob/main/LICENSE)可读，但 README 提到不公开源码的内部平台要另获商业许可；本轮未对该额外授权语义作法律判断。未核到 SceneMixer 式多人账户、充值会员、支付站。
- [Reveric README](https://github.com/looplj/reveric/blob/unstable/README.en-US.md)公开小说、剧本、画布、3D 导演台和剪辑台，定位为 Local-First 桌面工作台，使用 [AGPL](https://github.com/looplj/reveric/blob/unstable/LICENSE)。未核到多人站与本地支付运营闭环。

### Jellyfish 与 Film Engine：一边强短剧流程，一边强电影预演

- [Jellyfish README](https://github.com/Forget-C/Jellyfish/blob/main/README.md)覆盖剧本拆镜头、角色/场景/道具/服装资产、镜头级生成与统一任务中心，采用 [Apache-2.0](https://github.com/Forget-C/Jellyfish/blob/main/LICENSE)。公开 README/源码树未核到共享 3D 片场或用户充值会员支付。
- [Film Engine README](https://github.com/mannyhenri/film-engine/blob/main/README.md)覆盖剧本到成片与 3D previs，可接 World Labs 场景，但自己明确写 Web 服务无登录、默认仅本机访问，采用 [MIT](https://github.com/mannyhenri/film-engine/blob/main/LICENSE)。其世界预演可借鉴，不能直接作为多人收费整站。

## 目前的筛选结果

「网上有大把开源产品」是对的：至少本轮 149 个样本中就有二十余个相关项目。真正难找的是同时**公开创作链、共享空间/机位、多用户 C 端、自建支付会员**的单一仓库。新增的 Toonflow 最值得提升到主候选比较；它的 3D 与账务源码是真实存在的，但发布入口和支付后端边界使其暂不能被描述为 SceneMixer 完整替代。Kinema、Reveric 和 Film Engine 是更强的创作/空间参考，若只比导演工具会有不同排序。
