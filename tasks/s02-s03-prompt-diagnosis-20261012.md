# S02、S03 动作描述被朗读：责任层定位

## 结论

当前项目 `proj-d33835ca` 的 E1S02、E1S03 均命中网关 H3 提示词适配器的无对白透传分支。ArcReel 没有把动作解析为对白；网关把合法的无对白场景跳过适配，导致模型收到原始 YAML，缺少已在 S01 生效的动作非朗读边界。

责任位置：`/Users/mac/ai/llm-modes-gateway/internal/provider/comfyui/workflow/video.go:225` 的 `h3ScenePrompt`，第 250 行条件含 `len(scene.Dialogue) == 0`，第 251 行直接 `return prompt, nil`。调用位置为同文件第 93 行。

## 当前版本与真实任务证据

2026-10-12 只读查询本地项目脚本、版本文件、ArcReel SQLite、线上网关 SQLite，并通过 HK 的 ComfyUI 隧道读取对应 `/history/{remote_id}`。三个当前视频均为 v1，均为成功任务。

| 镜头 | ArcReel task | Gateway task | ComfyUI remote_id |
|---|---|---|---|
| E1S01 | fdc71ee7039a4069a09af3dfa0c56806 | video_62b832821cf55f26df3185bb0c45a9fb | 804f468c-5eba-4f50-b51d-967b067fcc97 |
| E1S02 | 77d2a3a2347248feb5d034d1515c8def | video_c83c4739c6c5ddfd79f585fafb6dd253 | 218cb4bc-2ef9-4c87-a745-8e2d4a5f2310 |
| E1S03 | 4a9ea9e58079436985e1be2ccaff9638 | video_e2a29d5afddb5a9e1b01acdc4b681735 | beed9f1e-8f4b-46ff-ab81-eba61efdf71a |

ComfyUI 节点 `n105_104`（`MiniMaxH3ImageToVideo`）的实际输入：

- S01 已转换为 `integrated_multimodal_description`，动作前有 `Visual actions only (not spoken)`；唯一台词为 `<d>[Chinese] 龙哥，你别走。今天陪陪我好吗？</d>`，并有 `No narration, no additional speech`。
- S02 原样收到 `Action: '@[龙哥]抬手用食指轻按门铃…'`、`Camera_Motion`、`Ambiance_Audio`、`Avoid`。没有 `Dialogue`，也没有上述边界约束。
- S03 原样收到 `Action: '@[龙哥]与@[阿秀]隔着满桌菜肴相视而坐…'` 及相同类型的字段，同样没有 `Dialogue` 或边界约束。

S02 模型实际 prompt SHA-256：`478f02396c7426a3f7cf97dafa23352f97b950a3ea789fd12468a228e32c42d0`。
S03 模型实际 prompt SHA-256：`26eb6d8de0b852c0be7d4a569f1e0e49ad2f383c808bac71bad062c7a07179a8`。
两者均与 ArcReel 当前版本保存的请求 prompt 哈希一致，验证了逐字透传。

线上二进制当前 SHA-256 为 `0f2f3b3d72481d0341d91c1cf76e66a20d83492f488aaaf3b376b38e36eb9aa7`，PID `3764223`。与网关工作记录的 18:51 部署一致；此次任务晚于部署。S01 的实际原生格式转换也证明当前链路存在适配，不能归因于整套适配未部署。

## ArcReel 解析与旁白交付

针对真实 `scripts/episode_1.json` 执行只读解析与提示词渲染：

- E1S01：`character_speech`，有角色对白，输出 `Dialogue`。
- E1S02、E1S03：`narrator_voiceover`，无角色对白；动作保持在 `Action`，旁白独立交付，不进入视频提示词。
- 三个镜头均未报告发声结构解析问题。

代码位置：`lib/prompts/prompt_utils.py:216` 为分镜视频渲染入口；第 346 行转换发声条目，第 445 行跳过非 `dialogue` 条目。`lib/speech/narration_delivery.py:33` 提取独立旁白。该行为符合 ADR 0089。

## 声音语义与验证边界

S02、S03 的视频生成不应朗读动作，也不应代读独立旁白。但当前脚本仍配置了环境音：S02 门铃、锅铲及电视声；S03 碗筷、谈笑及汤锅声。因此现有配置不是完全静音。若要求绝对静音，需要另行明确输出策略；此诊断没有修改任何音效或旁白内容。

已经确认实际生产请求命中错误适配分支，定位到网关的无对白处理遗漏。没有重新生成或转写视频，也没有单变量媒体实验，故不声称仅修复分支就能保证模型完全不产生人声。没有修改业务代码、服务、项目内容或任务队列。

建议后续修复方向：为合法的无对白场景补齐 H3 适配，明确动作仅供画面、无对白/无旁白，按产品要求处理环境音；避免删除整个音轨来掩盖解析边界问题。修复后分别验证有对白 S01 与无对白 S02、S03。
