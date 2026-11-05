# SceneMixer 全产品开源候选核查（2026-11-06）

浏览器核对：大陆站[首页](https://scenemixer.cn/)展示剧本到整集成片、片段重生成和场景世界多机位；[公开样片](https://scenemixer.cn/showcase/815/episode/2470)展示资产库、逐段脚本、时间线、成片播放与下载；[会员页](https://scenemixer.cn/membership)展示并发、项目数、存储和月度积分权益；[定价页](https://scenemixer.cn/pricing/)展示视频按秒积分、积分包和支付宝/微信支付。样片和公开页面可核查产品界面，不能证明实际支付回调、视频模型质量或场景世界的服务端实现。

## 对照范围

用户要求的是整个 [SceneMixer 大陆站](https://scenemixer.cn/)：小说/剧本到分集分镜、素材与视频生成、成片下载；`#world` 所描述的同场景 360° 片场与多机位空间一致性；C 端首页/样片/项目/资产库；账号、免费额度、积分、会员及支付。页面列出 MiniMax、Wan、Kling、Seedance 等驱动模型，但网页不能证实其内部是否自研物理视频模型或具体采用何种 3D 实现。把普通角色参考图一致性视为 `#world` 的替代，会高估候选。

下表只列公开证据最强的单仓/同组织产品，`✓` 表示仓库提供对应实现或官方文档，`部分` 表示范围不足或未验收，`—` 表示未核到；这些符号不代表生产验收。

| 候选 | 剧本到视频成片 | 3D/世界与机位 | C 端用户/页面 | 计费支付 | 许可与决定性缺口 |
| --- | --- | --- | --- | --- | --- |
| [DramaClaw](https://github.com/dramaclaw/dramaclaw/blob/main/README.md) | ✓ 小说/剧集、资产、分镜、视频、合成、18 类画布节点 | ✓ [Director World 源码](https://github.com/dramaclaw/dramaclaw/tree/main/src/novelvideo/director_world)有 scene-360、空间约束、场景构建；README 的 3D director stage 仍标为 closed beta | 部分：创作者工作台，非公开 C 端站点 | 部分：前端有积分和订阅结账组件，未核到完整公开支付运营链；[官方许可说明](https://github.com/dramaclaw/dramaclaw/blob/main/docs/en/license.md)称企业版才含 billing | [Elastic License 2.0](https://github.com/dramaclaw/dramaclaw/blob/main/LICENSES/Elastic-2.0.txt)第 2 条禁止将软件作为托管/管理服务向第三方提供。功能层最接近，但不满足拟运营 C 端 SaaS 的许可边界；也不是 OSI 意义的开源许可。 |
| [影策 Open AI Canvas](https://github.com/ddcat-ai/open-ai-canvas/blob/main/README.md) | ✓ 小说改编、拆集、视频和成片 | 部分：已有 3D 预演节点；README 把「影策世界引擎」标为**下个版本、内测中**，不能按已发布能力计算 | ✓ 创作首页、画布、用户和后台 | ✓ 积分与支付插件/充值 | [MIT](https://github.com/ddcat-ai/open-ai-canvas/blob/main/LICENSE)；README 明示快速开发中，未经安全配置不要直接作为公网多人服务。完整世界引擎与运营稳定性仍待验收。 |
| [AID Studio](https://github.com/shijue-aid/aid-studio/blob/main/README.md) | ✓ 项目、剧本、分镜、视频、配音、成片导出 | — 未核到同场景 3D 世界和机位求解实现 | ✓ 用户端、管理后台 | ✓ 充值套餐、冻结结算、支付宝/微信；[会员订阅仍在规划](https://github.com/shijue-aid/aid-studio/issues/3) | [MIT](https://github.com/shijue-aid/aid-studio/blob/main/LICENSE)；更接近商业平台，缺 SceneMixer `#world` 的关键差异能力。 |
| [PRINTFILM](https://github.com/yi1108/printfilm/blob/main/README.md) | ✓ 漫剧分集、分镜、图片/视频、合成下载 | — 按 README 使用参考图、前镜图片维持风格，未核到同空间 3D 世界 | 部分：工作台与管理端，营销站未核到 | ✓ [用量钱包、预留冻结、支付宝/微信及可选 Stripe](https://github.com/yi1108/printfilm/blob/main/docs/BILLING.md)；会员订阅未核到 | [MIT](https://github.com/yi1108/printfilm/blob/main/LICENSE)；v0.2.0，创作与计费已有源码，但世界能力和完整 C 端体验不足。 |
| [AI Video Production Editor](https://github.com/LudwigKienle/ai-video-production-editor/blob/main/README.md) | ✓ 剧本、分镜、生成、剪辑、导出 | 部分：3D 预演、场景地图与镜头参考 | — 本地 Electron 工作站 | 部分：README 说 hosted billing 需要自建 Supabase/Stripe；不是现成 C 端结算服务 | [GPL-3.0](https://github.com/LudwigKienle/ai-video-production-editor/blob/main/LICENSE)，侧重专业桌面制作。 |

## 判断

【事实】DramaClaw 的公开源码最接近 SceneMixer 创作链加世界/多机位能力，且有 `director_world` 的服务端实现和测试；其许可证明确挡住将软件本身提供为用户可访问的托管服务。影策与 AID Studio 提供更多运营组件，其中影策的世界引擎仍标为内测、AID 未核到世界引擎。PRINTFILM 的计费与视频流程较全，但也没有同空间世界实现。

【推断】如果同时要求这四域都在**一个可合法运营的成熟开源产品**中交付，当前检索没有找到已被公开证据证实的单一候选。按功能最接近的是 DramaClaw，按可商用托管的现成商业底座是 AID Studio/影策/PRINTFILM 这类 MIT 项目；这不是「四者都已满足」的结论。把 DramaClaw 的 Elastic 许可当作开源许可，或把影策内测截图当成发布能力，都会误导上线判断。

未部署候选，未用真实小说、视频模型、支付沙箱或并发用户验收。README 的功能说明、源码存在与可运营表现须分别核查。
