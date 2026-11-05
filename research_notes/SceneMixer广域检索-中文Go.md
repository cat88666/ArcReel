# SceneMixer 广域检索：中文与 Go 候选

核查日期：2026-11-06。目标是补齐此前只比较少数熟悉项目的遗漏，按 SceneMixer 整站四域（短剧到成片、同片场 3D 世界与多机位、C 端页面、积分会员支付）粗筛。本轮先宽松收集，再对有竞争力的仓库查第一方源码。未运行候选，也未验证真实模型效果或支付到账。

## 搜索范围和数量

使用 GitHub Repository Search（不是只检索已有候选）：`AI短剧` 返回 **1,028** 个仓库、`小说推文` 返回 **170** 个仓库、`短剧 language:Go` 返回 **28** 个仓库；还取了 `AI漫剧` 的首页结果。API 随后达到速率上限，`AI影视`、`AI视频创作平台`、`3D导演台`、`短剧 积分 支付` 等搜索式未拿到可计数结果，因此不能把前面三个总数相加，也不能声称遍历所有结果。另用 Web 搜索交叉检索 `site:github.com` / `site:gitee.com` 下的「短剧、3D 导演台、积分支付、Go」，查到 Gitee 的 [AID Studio 镜像](https://gitee.com/gzxx-2025/aid-studio/blob/master/README.md)和[模力方舟视频应用页](https://ai.gitee.com/appstore?fc=video)，没有将镜像重复计数。

在这些搜索结果的前 50／30 条及 Web 检索结果里，记录了以下 **24 个不同仓库**，排除了小说阅读、短剧播放/下载、纯 Skill、提示词集、Fork 镜像等不属于制作平台的结果。此处「元数据初筛」只依据仓库自己的简介，不代表源码功能已核实。

| 仓库 | 初筛原因与状态 |
| --- | --- |
| [连镜 video-canvas](https://github.com/zaylora/video-canvas) | **深审**：Go/React，短剧、3D 导演台、积分支付、整集合成 |
| [NovaNova Studio](https://github.com/Swayingleaves/novanova-studio) | **深审**：Java/React，短剧、3D 导演台、积分及支付 |
| [Huohuo Drama](https://github.com/appolloqin/huohuo-drama) | **深审**：Nuxt/Node，短剧 SaaS 与多渠道支付，世界域待核 |
| [LocalMiniDrama](https://github.com/xuanyustudio/LocalMiniDrama) | **深审**：本地端到端短剧工具 |
| [BigBanana AI Director](https://github.com/shuyu-labs/BigBanana-AI-Director) | **深审**：高人气短剧工作台，须核源码/授权 |
| [TapCanvas 社区版](https://github.com/anymouschina/TapCanvas) | **深审**：一键成片与 3D 导演台，但社区版支付边界需核 |
| [VideoForge](https://github.com/miao-x1/VideoForge) | **深审**：短剧、3D 导演台、余额；正式收款与许可需核 |
| [Toonflow-app](https://github.com/HBAI-Ltd/Toonflow-app) | 创作链/画布，商业及空间域待核；此前已有局部审计 |
| [CineGen-ShortDrama](https://github.com/UllrAI/CineGen-ShortDrama) | 元数据初筛：AI 漫剧/短剧导演系统 |
| [LumenX](https://github.com/alibaba/lumenx) | 元数据初筛：小说到动态视频，3D 与商业待核 |
| [AI Fusion Video](https://github.com/Stonewuu/ai-fusion-video) | 元数据初筛：Java Agent 短剧/视频平台 |
| [xiaomaque](https://github.com/mclwh/xiaomaque) | 元数据初筛：剧本生成与无限画布 |
| [ai-shotlive](https://github.com/sorker/ai-shotlive) | 元数据初筛：小说、剧本、视频与用户服务 |
| [Shortify-AI](https://github.com/ycbing/Shortify-AI) | 元数据初筛：AI 短剧创作 |
| [AI-Short-Drama-Studio](https://github.com/JerrIsTheBesta/AI-Short-Drama-Studio) | 元数据初筛：短剧制作工作台 |
| [Daydream-Factory](https://github.com/chuchushijingxi/Daydream-Factory) | 元数据初筛：Go，剧本资产、分集分镜、提示词 |
| [Go-Ai-Studio](https://github.com/yunper-wang/Go-Ai-Studio) | 元数据初筛：Go + React，短剧/视频内容生产工作台 |
| [dramaforge](https://github.com/1037134254/dramaforge) | 元数据初筛：Go，内部 AI 短剧工具 |
| [S-Drama](https://github.com/feirate/S-Drama) | 元数据初筛：Python 全栈短剧引擎 |
| [ai_story](https://github.com/xhongc/ai_story) | 元数据初筛：AI 视频/动漫/短剧生成 |
| [AI-Canvas-tauri](https://github.com/Tenney95/AI-Canvas-tauri) | 元数据初筛：桌面画布与短剧制作 |
| [reveric](https://github.com/looplj/reveric) | 元数据初筛：桌面小说/短剧工作台 |
| [MiaoMuse](https://github.com/15673312611/MiaoMuse) | 元数据初筛：Go 剧本生成，视频与商业待核 |
| [Wintercom/ai-short-drama](https://github.com/Wintercom/ai-short-drama) | 元数据初筛：Go，多 Agent 剧本到渲染 |

上表的 17 个「元数据初筛」项目只作为可追踪的候选池，不能据此给出最终排序。深审优先级按是否同时在简介/目录中出现创作、3D、多人商业三个独立域确定；因此连镜、NovaNova 排在前面，纯本地工具和剧本生成器排后面。

## 新增强候选的源码核对

### 连镜：Go 项目中此前遗漏的最强竞争者

[README](https://github.com/zaylora/video-canvas)自述 Go/Gin + React、多人账号、短剧工作室、3D 导演台、冻结/退款积分及支付。[后端 API 文档](https://github.com/zaylora/video-canvas/blob/master/backend/README.md)与当前源码可直接核到：小说/剧本导入、研读、拆集、角色场景道具、分镜片段、逐段视频；[整集合成 API](https://github.com/zaylora/video-canvas/blob/master/backend/README.md)以服务端 FFmpeg 拼接已采用片段，并记录成片过期状态；[前端成片页面](https://github.com/zaylora/video-canvas/blob/master/web/src/pages/drama/workspace/final-area.tsx)提供播放、重合成、MP4 下载。[微信 Native](https://github.com/zaylora/video-canvas/blob/master/backend/internal/payment/wechat/wechat.go)、[支付宝](https://github.com/zaylora/video-canvas/blob/master/backend/internal/payment/alipay/alipay.go)、易支付、虎皮椒适配器及对应测试真实存在；[许可证](https://github.com/zaylora/video-canvas/blob/master/LICENSE)为 MIT。

3D 导演台也有大量[前端源码](https://github.com/zaylora/video-canvas/tree/master/web/src/components/director)，可摆人台、道具、机位并导出参考图片/视频。但关键边界是[短剧画布菜单源码](https://github.com/zaylora/video-canvas/blob/master/web/src/pages/drama/workspace/assets-area.tsx)明确写「短剧一期不做 3D 预演」并过滤 `director` 节点；导演台存在于普通无限画布，**尚未接入短剧主流程**。空间约束主要见分镜提示词与参考素材，未核到 SceneMixer 式自动搭同一 360° 房间、共享坐标与跨镜头视频验证。全仓源码搜索未核到周期会员方案/权益实现。它应进入与影策并列的 Go 强候选，而不是因为 README 较短就被排除。

### NovaNova Studio：Java，但整站覆盖很强

[README](https://github.com/Swayingleaves/novanova-studio)描述小说、剧本、漫剧/短剧、画布与多用户；[漫剧工作流文档](https://github.com/Swayingleaves/novanova-studio/blob/master/docs/zh-cn/using-studio/comic-drama.mdx)列明共用剧本数据、角色/场景/道具资产、分镜拆分、视频/音频/文字时间轴、单镜头生成、多版本、成片 MP4 导出。仓库确有[3D 导演台代码](https://github.com/Swayingleaves/novanova-studio/tree/master/web/src/app/%28user%29/canvas/director-desk)、[积分购买/支付与微信/支付宝后端](https://github.com/Swayingleaves/novanova-studio/tree/master/server/src/main/java/com/novanovastudio/payment)，[MIT 许可](https://github.com/Swayingleaves/novanova-studio/blob/master/LICENSE)。

但[导演台 README](https://github.com/Swayingleaves/novanova-studio/blob/master/web/src/app/%28user%29/canvas/director-desk/README.md)说导演台在画布中手工排场、机位、动作并本地导出参考媒体；合入时单测与构建通过，**未做浏览器人工验收**。不能推断其能自动从剧本搭场景并将同一 3D 坐标约束短剧视频。未核到 SceneMixer 式周期会员方案。技术栈为 Java 21 / Spring Boot + Next.js，不符合用户优先 Go 的偏好，但在功能粗覆盖上应与影策、连镜同桌比较。

### Huohuo Drama：商业与创作强，世界与许可弱

[README](https://github.com/appolloqin/huohuo-drama)描述小说转短剧、双视频流水线、TTS、逐镜合成/整集导出，以及 Stripe、PayPal、PingPong、微信/支付宝和多用户积分；[支付与短剧源码目录](https://github.com/appolloqin/huohuo-drama/tree/main/workbench-server/src)存在。公开仓库的 GitHub 许可证元数据为空，根目录未见 LICENSE，故不能只凭 README 的「open-source」字样推定商业复用授权。`novel-worldbuilding` 是小说世界观文本，未核到共享 3D 片场/多机位。

### LocalMiniDrama 与 BigBanana：创作强，但不适合作为本题整站底座

[LocalMiniDrama 官方英文说明](https://github.com/xuanyustudio/LocalMiniDrama/blob/main/docs/en.md)具备从故事、角色、场景、分镜到视频合成的流程和跨项目素材库，MIT；官方明确是 Node/Express/SQLite 的本地 Electron 工具，**没有订阅或多人云端商业模块**，也未核到共享 3D 场景。

[BigBanana 官方 README](https://github.com/shuyu-labs/BigBanana-AI-Director)宣传从剧本到成片，但同页明确表示后续版本**只发布 Docker 镜像、不继续同步源码**，当前仓库主要是文档/历史参考；[许可证](https://github.com/shuyu-labs/BigBanana-AI-Director/blob/main/LICENSE)为 CC BY-NC-SA 4.0，商业用途需另获授权。因此不能按「可一比一商业复刻的开源代码」排名。

### TapCanvas 社区版与 VideoForge：强创作候选，但商业边界不同

[TapCanvas 社区版 README](https://github.com/anymouschina/TapCanvas/blob/main/README.md)有一键成片 Agent、画布、3D DirectorDesk 参考视频输出、视频复刻及字幕合成；同时明确说**社区版不提供短信验证码与在线支付**，在线商业版是独立产品。根项目 MIT，但其内置 `apps/new-api` 是 AGPL-3.0 衍生组件，需按目录分别看许可。它是强创作/空间候选，不是已经交付 SceneMixer 计费支付的开源整站。

[VideoForge README](https://github.com/miao-x1/VideoForge/blob/main/README.md)称有剧本到镜头视频、3D 导演台和余额充值；但同页说明正式微信/支付宝收款需要另接商户，仓库里只有开发测试充值。公开仓库未见 LICENSE，不能把其源码公开等同商用许可。当前仅 8 次提交，未做功能运行验收。

## 对旧结论的影响与边界

本轮直接推翻了「影策是唯一值得深审的 Go 单仓候选」这一隐含前提：**连镜必须进入最终比较**；Java 的 NovaNova Studio 也不能因语言偏好被遗漏。按现有源码，连镜的短剧链和支付比旧报告呈现得更完整，然而其 3D 导演台明确未集成短剧画布；影策的 3D 预演已经进入画布，但完整世界引擎仍内测。两者都不能宣称已实现 SceneMixer 的自动世界到成片闭环。公开 README、源码目录和单测不等于真实生成、支付与空间一致性验收；最终排名应把业务功能与可运营验证分别列出。
