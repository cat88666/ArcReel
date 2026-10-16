# 服务器部署记录（2026-10-15）

## 结果

- 目标：`veo-hk`（`43.154.247.11`）。`arcreel.service` 于北京时间 21:36:01 启动，`/opt/arcreel/current` 指向 `/opt/arcreel/releases/20261015-9ad6b64d-pacingfix`。
- 发布标识：`9ad6b64d679a719e16844cea4831512e77acd643+pacingfix+preserved-character-hotfix`。源码基线为本地 `main` 提交 `9ad6b64d`，另含未提交的单引用提示词片段修复、对应测试断言更新，以及保留的线上角色参考图提示词热修。不能把这个发布视为纯 Git 提交构建。
- 仅切换 ArcReel 发布软链、ArcReel 环境文件中的两处旧发布路径，并重启 `arcreel.service`。没有操作 nginx 或 `llm-modes-gateway.service`。
- 备份：`/opt/arcreel/backups/20261015-9ad6b64d-pacingfix/data-env-service.tar.gz`，802601988 字节、`0600`，SHA-256 `fcbaeab27f71bbb59a222ae5dd939e32e2e0ec26a552b70b118914a1c361f2ea`。包含停服后的完整 `/var/lib/arcreel`、原环境文件和 systemd 单元，共 1150 项；归档已完整读取校验。旧发布目录保留。

## 版本差异与验证

- `9ad6b64d` 相对上次部署记录中的 `55930508` 修改了 10 个提示词模板文件及文档记录；前端源码、依赖锁和数据库迁移没有变化。旧发布目录实际已含其中多数新模板文案，故版本戳不能代表旧目录的所有源码字节。
- 新提交增加的 `pacing/screenplay.md` 是 `shared/pacing/drama` 的唯一引用者，触发已有模板单测。发布前将原文内联到 screenplay 变体并删除无人引用的共享片段，渲染语义不变。小说画外音、小说节奏、视觉提示词的三条旧断言按新文案更新。相关测试：`116 passed`、2 warnings；`git diff --check` 通过。未跑完整后端/前端测试，未做完整媒体生成验收。
- 用本地目标源码生成 3909 个文件的 SHA-256 清单；线上新发布目录 3908 个文件逐一匹配。唯一例外 `lib/prompts/prompt_templates/templates/partials/asset/sheet/guard/character.md` 是旧线上独有的角色参考图热修：要求参考图只提供面部和体型，服装、发型、饰品以角色 description 为准，并忽略水印/Logo/文字。新目录保留原文，旧/新哈希均为 `046b31f08da2eecd9c17c085ec7cbe362bf3ddfef20f8c1523e6d2832d1e3c42`；本地 Git HEAD 哈希为 `5088a037a2d135db17ea4f8c577640e152eedd3d0b8ccd6fae223697b0620785`。
- 新发布目录的 `uv sync --locked --no-dev --no-install-project --python /usr/bin/python3.12` 与 FastAPI、Claude Agent SDK、市场核心包导入通过。进程 PID 753494 的 `cwd` 指向新发布目录。
- 应用 `/health`、应用首页、nginx 首页、公网首页均为 200。应用和 nginx 返回的首页与新发布目录 `frontend/dist/index.html` 字节一致；抽验 3 个 JS 资产哈希一致。
- SQLite `integrity_check=ok`，Alembic 为 `a9c3e5d17b24`。任务仍为 248 succeeded、20 failed、1 cancelled；切换前后均无 queued/pending/running 任务及运行中的 Agent 会话。启动日志无 ERROR/Traceback，Agent profile 物化 `errors=0`、`failed_projects=0`。
- 使用 ArcReel 已保存的 `elysium-chat` 接入配置发出最小真实文本请求，网关 Anthropic 兼容 `/v1/messages` 返回 HTTP 200、模型 `elysium-chat`、文本 `OK`。没有输出或改动密钥。ArcReel、网关与 nginx 验收时均为 active。

## 停服与回滚

21:33:29 开始优雅停服；两条网页长连接使 Uvicorn 等到 systemd 的 120 秒停止上限。其后停服备份和切换完成，21:36:01 新服务启动。停服时没有活跃生成任务，任务状态未变。

代码回滚脚本保存于 `/opt/arcreel/backups/20261015-9ad6b64d-pacingfix/rollback.py`，权限 `0600`，语法检查通过，未实际执行。它要求当前版本匹配、无活跃任务/会话，仅切回旧代码并保留当前数据，启动后检查健康；归档用于灾难恢复，不能直接覆盖上线后新增的数据。需要回滚时先评估运行中任务及上线后数据，再执行：

```bash
ssh veo-hk 'sudo -n python3 /opt/arcreel/backups/20261015-9ad6b64d-pacingfix/rollback.py'
```

真实文本请求只验证网关文本链路，不证明图片、视频或完整创作流程可用。
