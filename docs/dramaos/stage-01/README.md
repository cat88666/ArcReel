# DramaOS Stage 01：本地视频切镜实验

这一步让电脑读取一段本地 MP4，找出画面切换的位置，并为每个镜头保存一张原视频画面。它会生成一份可在本机打开的报告，方便人检查切镜结果。**它还不能理解剧情、学习导演手法或自动制作短剧，也没有接入 ArcReel 生产服务。**

## 现在做到哪一步

| 已完成 | 还没有完成 |
|---|---|
| 3 秒合成视频有 2 处预设硬切；程序都找到了，帧位置正确。 | 尚未由人逐镜核对真实短剧中的漏切、误切和关键帧质量。 |
| 一段现有的 60.47 秒成片曾在本机跑通：输出 8 个镜头、8 张关键帧、音轨和离线报告。 | 这次工程试跑不等于已核实素材分析授权，也不证明 8 个切点正确。该报告和素材未纳入仓库。 |
| 可选接入本机已有的语音识别模型。 | 本次没有可用的本地模型，因此没有得到对白文字；画面与剧情标签也尚未接入模型。 |

**当前结论：**切镜程序的基本路径已跑通；真实短剧的内容质量还没有验收，暂不据此进入 Stage 02。可以先打开[合成样本报告](../../../tasks/artifacts/dramaos-stage01/synthetic/report.html)，看看报告长什么样。它只展示预设硬切的测试结果，不能代替真实短剧验收。

## 用自己的视频试一次

准备一部**已确认有权分析**的本地 MP4，时长不超过 120 秒。运行环境需要 Python 3.12+、ArcReel 的 `uv` 环境和 `dramaos` 依赖组。第二个路径填写一个**尚不存在**的输出目录。

```bash
uv sync --group dramaos
uv run --group dramaos python scripts/dramaos_stage01.py \
  /absolute/path/to/authorized.mp4 \
  /absolute/path/to/new-output-directory \
  --rights-confirmed
```

运行成功后，打开输出目录里的 `report.html`，对照原视频逐镜检查。`frames/` 是各镜头画面，`result.json` 是镜头时间线，`run.json` 是运行记录；原片有音轨时还会生成 `audio.wav`。输出保留原画面和声音，分享前仍需按素材权限判断。`--rights-confirmed` 只记录操作者的声明，程序无法替人核实授权。

如需尝试对白识别，可额外传入 `--asr-model /absolute/path/to/model`。这要求本机已有 `mlx_whisper` 命令和已下载、可合法使用的模型目录；程序不会自动下载模型。未提供模型或识别失败时，对白状态为 `unavailable`。识别出的时间从 `audio.wav` 开始计算，目前没有校准源视频与音轨的起点偏移，因此不能把它当作精确的画面时间。

## 限制与详细资料

- 程序根据画面变化提出切点候选；复杂转场或运动镜头可能漏检、误检。相邻帧时间间隔偏离中位数超过 1% 的视频会被拒绝，包括部分时间基较粗的恒定帧率文件。
- [验收清单](acceptance.md)：哪些结果已验证，真实素材还需要检查什么。
- [测试结果](test-results.md)和[未解决风险](unresolved-risks.md)：现有证据及其适用范围。
- [技术方案](architecture.md)、[数据格式](schema.json)、[实施计划](implementation-plan.md)、[依赖审计](dependency-audit.md)、[成本记录](cost-report.md)、[审核记录](review-log.md)：供开发和复核时查阅。
