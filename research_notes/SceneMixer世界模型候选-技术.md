# SceneMixer「世界模型」开源技术候选（2026-11-06）

## 对照范围

[SceneMixer 大陆站的 `#world` 段落](https://scenemixer.cn/#world)公开描述「先搭景，再开机」：同一场戏的 360° 片场、家具和角色位置、多机位、跨镜头复用。该网页是产品展示，**不能据此确认 SceneMixer 内部使用了真实 3D 重建、哪一种世界模型或哪一种机位解算器**。以下只比较可核实的开源实现，不把研究演示当成可运营产品。

## 最接近产品交互的开源工具

| 项目 | 源码证据与许可 | 与目标的关系和缺口 |
| --- | --- | --- |
| [CozyClay](https://github.com/NomaDamas/CozyClay) | [README](https://github.com/NomaDamas/CozyClay/blob/main/README.md)有 `npx cozyclay` 本地启动、摆放布景与人物、分镜时间线、多机位、镜头轨迹、碰撞与脚滑检查；可导出首尾帧、灰盒参考视频、深度、法线和 OTIO。仓库有 [CI](https://github.com/NomaDamas/CozyClay/blob/main/.github/workflows/ci.yml)、[v3.2.1 发布](https://github.com/NomaDamas/CozyClay/releases/tag/v3.2.1)，[AGPL-3.0-or-later](https://github.com/NomaDamas/CozyClay/blob/main/LICENSING.md)。 | 最贴近「同一片场多机位拍摄」的可运行交互工具。高质量成片需把导出参考交给外部视频模型；仓库没有小说拆集、全剧角色资产、C 端用户/支付。改造后网络用户访问会触发其 AGPL 源码提供义务。 |
| [Topview 3D Builder](https://github.com/topviewai/topview-3d-builder) | [README](https://github.com/topviewai/topview-3d-builder/blob/main/README.md)说明自然语言搭 3D 场景、摆角色和机位、多机位渲染、动作与镜头轨迹；内置 4 个角色、121 个姿势和几何道具，有本地编辑器及 CLI。[Apache-2.0 源码许可证](https://github.com/topviewai/topview-3d-builder/blob/main/LICENSE)，内置资产 CC BY 4.0。 | 场景和机位可本地编辑/渲染，示例中的最终 AI 视频标为由 Topview.ai 生成；公开仓库未呈现可独立运营的视频模型服务、剧集编排或 C 端收费体系。未查到正式 GitHub release。 |

两个仓库都有实质源码和运行入口，不能归类为仅有截图的概念项目。它们控制的是**拍摄前的空间布局和参考素材**；输出视频能否严格保持每个家具、角色和视线位置，仍取决于后续视频模型与素材接口，README 演示不能代替跨镜头、跨集验收。

## 模型与研究管线

| 项目 | 已公开能力 | 商业平台边界 |
| --- | --- | --- |
| [NVIDIA GEN3C](https://github.com/nv-tlabs/GEN3C) | [README](https://github.com/nv-tlabs/GEN3C/blob/main/README.md)提供单图/视频输入、任意相机轨迹 GUI 和多视角推理；代码 Apache-2.0，模型权重另受 NVIDIA Open Model License 约束。 | 是 3D 一致性视频推理模型，不包含可复用片场资产、角色/剧集/支付平台；官方仅在 H100/A100 测试，卸载后最大显存约 43 GB，部署成本高。商用须分别核对代码、权重与依赖许可。 |
| [4DSynth](https://github.com/QZepHyr/4DSynth) | [README](https://github.com/QZepHyr/4DSynth/blob/main/README.md)描述文本/布局/室内图到动态 3D 场景、角色运动规划、相机轨迹求解和 MP4；自身代码 BSD-3-Clause。 | 更接近「自动搭景+求机位」的研究管线，但需 Linux NVIDIA GPU、多个 Conda 环境和约 25 GB 模型文件；[外部依赖](https://github.com/QZepHyr/4DSynth/blob/main/EXTERNAL_DEPENDENCIES.md)和权重各有许可，且没有创作 SaaS。不能仅凭自身 BSD 许可认定整个流水线可商用。 |
| [WorldCrafter](https://github.com/TencentARC/WorldCrafter) | [README](https://github.com/TencentARC/WorldCrafter/blob/main/README.md)公开相机可查询的 3D 感知记忆及交互演示。 | [许可证](https://github.com/TencentARC/WorldCrafter/blob/main/LICENSE.txt)明确限定学术用途、禁止商业或生产用途，不能作为目标商业平台的模型底座。 |

[NAVER InSpace](https://github.com/naver/inspace)虽能从 360° 全景生成完整房间和分离的家具网格，恰好贴近「量好房间」，但其 [README 的许可说明](https://github.com/naver/inspace/blob/main/README.md)明确表示运行所需依赖限定非商业研究，因此也不能直接列入商业推荐。

## 可执行判断

若目标是先验证 SceneMixer `#world` 的核心体验，优先以 CozyClay 或 Topview 3D Builder 做**同一场景四机位、角色与窗/桌固定、镜头间空间关系可复查**的独立样例。通过后再核视频模型能否忠实使用这些参考素材，并与短剧平台的剧集/计费流程集成。当前没有证据表明上述单个项目已交付 SceneMixer 所述「小说到多集成片 + 世界搭景 + C 端商业化」完整闭环；已打开 CozyClay 官方在线 Studio，未在本机运行候选或生成付费视频。
