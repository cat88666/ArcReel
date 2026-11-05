# SceneMixer 一比一复刻：全球候选补查

核查日期：2026-11-06。任务是找**比 DramaClaw／影策更接近 SceneMixer 整站**的可复用单一项目，重点补查英文和 Go 候选。比较四域：①小说／剧本到成片，②同一 3D 片场的空间、多机位与跨镜头约束，③多人 C 端创作和作品页面，④会员、积分及支付。这里的「3D 风格视频」「场景参考图」「手写镜头角度」不算第二域。

## 检索办法

- 英文组合：`AI short drama generator 3D scene camera billing SaaS`、`novel to video director world 3D multi camera payment`、`AI film production platform 3D previs credits billing`、`short drama 3D payment`、`micro drama multi-camera credits`；用 GitHub 搜索限定 Go 和 README，包括 `AI short drama language:Go`、`drama video language:Go`、`3D previs short drama`。
- 先用搜索发现仓库，再看**仓库自己的** README、源码树、许可证文件和商业功能说明；聚合站只用来找线索，不作功能证据。未运行这些应用，未测试真实生成、支付、并发或许可证合规部署。

## 补查候选

| 候选 | 创作链／页面／商业 | 世界能力与决定性缺口 | 与 DramaClaw／影策相比 |
| --- | --- | --- | --- |
| [EvoLinkAI AIDrama Studio](https://github.com/EvoLinkAI/ai-short-drama/blob/main/README.md) | Next.js/TypeScript，多用户注册、小说拆解、分镜、视频、Remotion 剪辑；[计费源码](https://github.com/EvoLinkAI/ai-short-drama/tree/main/src/lib/billing)含账本、预留清理及测试 | 源码树中的 `WorldContextModal` 属创作上下文，未核到同片场 3D 舞台、物理空间布局或多机位求解；README 也未证明会员支付闭环。**许可文档冲突**：README 写 MIT，仓库实际 [LICENSE](https://github.com/EvoLinkAI/ai-short-drama/blob/main/LICENSE) 是 Apache-2.0，使用前应以许可文件核实并请维护者澄清。 | 创作与国际化较强，但第二域差距大，不能取代两位领先候选。 |
| [Dralo Studio](https://github.com/lnblfkj-del/Dralo-Studio/blob/main/README.md) | Apache-2.0，本地 Python/React 工作台；剧本、资产、画布、视频、多轨剪辑 | 有 Three.js／React Three Fiber 3D 导演台，但 README 明确是本地单机配置、默认只监听 127.0.0.1；未核到多人站点、会员积分支付或已验收的自动跨镜头视频一致性。 | 功能组合靠近，但缺整站商业域且非云端 C 端。 |
| [AI Video Production Editor](https://github.com/LudwigKienle/ai-video-production-editor/blob/main/README.md) | 开源本地 Electron 制作工具，脚本到导出；有 3D previs、场景布局、相机预演 | 官方 README 将 hosted billing/BYOK proxy 列为**可选且需自建**；不是现成多人 SaaS。 | 世界预演较强，商业产品差距大。 |
| [M-duanju](https://github.com/startopenapi-glitch/M-duanju/blob/main/README.md) | Go/Gin + React；四阶段剧本、定妆、分镜视频、成片；积分预占／结算、微信支付结构、分成后台；[Apache-2.0](https://github.com/startopenapi-glitch/M-duanju/blob/main/LICENSE) | README 自称学习／二次开发参考实现，支付默认 mock；未核到同空间 3D 世界／机位模块，也未证实产品级 C 端页面。 | Go 商业基础候选，缺 SceneMixer 最独特的世界域。 |
| [灵果短剧 LingGuo-Drama](https://github.com/LingGuoAI/LingGuo-Drama/blob/main/README.md) | Go/Gin + Vue 管理工作台；剧本、分镜、视频合成 | README 的公开功能清单没有 3D 片场、多机位、积分会员支付或 C 端营销站。README 末尾写 MIT，但仓库根目录检查未见独立 LICENSE 文件，需要再核许可。 | Go 创作后台，整站复刻缺口比影策大。 |
| [MediaGo Drama](https://github.com/mediago-dev/mediago-drama/blob/main/README.md) | Apache-2.0、Go 本地 Agent 工作台，小说、分镜、资产与生成；有 Electron 客户端 | [官方商业功能说明](https://github.com/mediago-dev/mediago-drama/blob/main/COMMERCIAL_FEATURES.md)明确账户、商城、托管、支付、退款等商业服务**不在开源仓库中**；场景四视图提示词不能证明同片场 3D 世界。 | Go 桌面创作工具，不是整站 SaaS 底座。 |
| [NovelVids](https://github.com/Anning01/novelvids/blob/main/README.en.md) | Python、MIT，有公开 demo、故事到分镜视频和成片 | 未核到同片场 3D 世界模块和公开积分／会员支付源码。 | 创作流程完整，第二与第四域不足。 |
| [Sogni Worlds Kit](https://github.com/Sogni-AI/sogni-worlds-kit/blob/main/README.md) | 可制作交互式电影世界，第三方 Sogni 账号有[付费渲染方案](https://github.com/Sogni-AI/sogni-worlds-kit/blob/main/docs/costs-and-plans.md) | 交互地点和片段视频与 SceneMixer 的「剧本分集、共享片场多机位短剧」不是同一工作流；付费方案属于 Sogni 服务，不是仓库内可复用的 C 端支付。 | 不能替代整站。 |
| [OpenMontage](https://github.com/calesthio/OpenMontage) | Agent 视频制作流程，含 3D/Three.js 路线和[本地只读 backlot](https://github.com/calesthio/OpenMontage/blob/main/backlot/README.md) | 公开 backlot 是本地制作观察页面，未核到 SceneMixer 式会员／积分／支付和多人项目站点。 | 创作引擎线索，不是完整 C 端平台。 |

## 补查结论

这轮新候选没有出现可证实同时覆盖四域、且比 **DramaClaw 的公开功能覆盖**或**影策的可商用单仓基础**更接近的项目。Go 限定下，`M-duanju`、灵果和 MediaGo 均在世界能力或商业 C 端方面落后于[影策的短剧＋3D 预演＋支付源码](https://github.com/ddcat-ai/open-ai-canvas/blob/main/README.md)。这只是本轮检索范围内的比较，不能推出全球所有项目均不存在；公开 README 和源码也不足以证明生产质量、视频物理一致性或支付上线可用。
