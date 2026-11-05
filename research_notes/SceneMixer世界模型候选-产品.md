# SceneMixer「世界模型」的开源产品候选（2026-11-06）

## 对照边界

SceneMixer 的 `#world` 页面描述的是先固定场景空间、家具和人物位置，再在该空间布置多个机位，让正反打和过肩镜头共享空间约束。页面展示的是产品说明；没有 SceneMixer 的服务端源码或生成中间产物，不能从页面证明其底层用了可复用的真实 3D 重建算法。选型时须区分：①有坐标和相机的 3D 灰盒／预演；②用参考图维持外观一致性；③自动生成可转动的带纹理 360° 场景；④从小说到整集的视频流水线和 C 端商业平台。

| 候选 | 一手证据与接近之处 | 与 SceneMixer 目标的差距 |
| --- | --- | --- |
| [CozyClay](https://github.com/NomaDamas/CozyClay) | [README](https://github.com/NomaDamas/CozyClay/blob/main/README.md)及[场景](https://github.com/NomaDamas/CozyClay/blob/main/src/domains/stage.js)、[镜头取景](https://github.com/NomaDamas/CozyClay/blob/main/src/shot-frame.js)、[导出](https://github.com/NomaDamas/CozyClay/blob/main/src/commands/export.js)源码：在共享 3D 场景里搭布景、摆角色、排摄像机和切镜；导出首尾帧、灰盒视频、相机参数、深度/法线通道，作为视频模型的参考。2026-10-28 发布 [v3.2.1](https://github.com/NomaDamas/CozyClay/releases/tag/v3.2.1)；[AGPL-3.0-or-later](https://github.com/NomaDamas/CozyClay/blob/main/LICENSE)。 | **最接近「先搭景，再开机」的开源交互工具**，但场景需要搭建或由 Agent 操作；灰盒参考不等于自动生成带纹理、可环视的 360° 房间。它不是小说拆集、角色连续性、完整成片与账户收费平台；视频模型最终是否遵守空间约束仍须用实际模型测试。 |
| [AI Video Production Editor](https://github.com/LudwigKienle/ai-video-production-editor) | [README](https://github.com/LudwigKienle/ai-video-production-editor/blob/main/README.md)有剧本→导演→分镜→生成→剪辑→交付和 3D 预演；[SceneMap3DView](https://github.com/LudwigKienle/ai-video-production-editor/blob/main/src/components/SceneMap3DView.tsx)把平面元素 1:1 映射成 3D 预制件、人物和相机视锥；[setdesign/sceneBuilder](https://github.com/LudwigKienle/ai-video-production-editor/blob/main/src/setdesign/sceneBuilder.ts)共用交互场景与相机帧捕获；[GPL-3.0](https://github.com/LudwigKienle/ai-video-production-editor/blob/main/LICENSE)，2026-10-28 发布 [v3.2.0](https://github.com/LudwigKienle/ai-video-production-editor/releases/tag/v3.2.0)。 | 创作链覆盖较广，但主要是本地 Electron 工作站。3D 场景使用预制件、代理人和可导入模型；README 的参考图转 3D 依赖外部模型。没有证据表明可自动从小说建立准确的 360° 场景并保证 AI 视频跨镜头完全一致；没有现成 C 端用户计费体系。 |
| [AI Movie Studio 2](https://github.com/Heroesjouney/AIMovieStudiov2) | [README](https://github.com/Heroesjouney/AIMovieStudiov2/blob/main/README.md)与[3D 预演前端](https://github.com/Heroesjouney/AIMovieStudiov2/tree/main/frontend/src/components/previs)显示共享 3D 舞台、代理角色、相机移动与运动参考视频；含剧本导入、分镜、生成和时间线导出；[AGPL-3.0](https://github.com/Heroesjouney/AIMovieStudiov2/blob/main/LICENSE)。 | README 明说 3D 预演仍属实验／开发中。连续性主要靠参考图和提示词；3D 代理镜头与最终视频之间没有几何一致性保证。浏览器工作站以本地项目为主，没有现成会员、积分与支付。 |

## 判断

【事实】CozyClay 提供最直接的同一 3D 场景多机位控制；AI Video Production Editor 提供更长的创作链和 3D 场景地图。【推断】如果要给现有短剧平台补一个「可编辑场景 + 相机规划」模块，先验证 CozyClay 的场景与镜头数据格式和导出参考素材，比套用另一整个影视工作站更有针对性。上述仓库均没有公开证据证明完整复刻 SceneMixer 所宣传的「小说→自动建世界→同空间多镜头→整集成片→C 端收费」闭环。

已在 Orca 浏览器打开 CozyClay 的[官方在线 Studio](https://cozyclay.org/app/)，看到新建项目、Stage、Camera、Motion 与时间线控件；未创建项目、未运行本地代码或模型生成，也未验证 SceneMixer 的服务端实现。README 与源码的能力声明仍需实际成片验收。
