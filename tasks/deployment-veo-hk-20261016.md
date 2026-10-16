# ArcReel 服务器部署记录（2026-10-16）

## 后续发布的 AppleDouble 故障与修复边界

- 后续发布 `20261016-bc55b115` 的模板扫描遇到 `._*.md`，UTF-8 解码在字节 `0xa3` 失败；远端已确认文件头 `00051607`，属于 AppleDouble 元数据。主代理将该单个文件移到 release 内 `metadata-quarantine` 后，服务恢复 active。以下早先发布记录保留，不代表该后续版本的状态。
- 本地 `lib/prompts/prompt_templates/engine.py` 仅在模板扫描时忽略文件名以 `._` 开头的 sidecar；普通模板仍严格按 UTF-8 解码，不能用忽略编码错误掩盖真实内容损坏。此代码修复尚未部署到并发发布目录。
- macOS 打包时设置 `COPYFILE_DISABLE=1`，并显式排除已有 `._*` 与 `__MACOSX`；例如 BSD tar 使用 `COPYFILE_DISABLE=1 tar --no-mac-metadata --exclude='._*' --exclude='__MACOSX' -czf <归档> <发布文件>`。环境变量防止生成新元数据，排除规则处理磁盘已有 sidecar，两者不能相互替代。
- 上传前检查归档成员，解包后检查模板目录的额外文件；只比对 Git 跟踪文件哈希不能发现多出来的元数据。切换服务前仍需以运行账户加载模板并完成启动检查，服务 active 不等于完整媒体制作验收。

## 发布结果

- 目标：`ai-hk`（上次记录中的 veo-hk，`43.154.247.11`）。`arcreel.service` 于北京时间 18:43:19 启动，`/opt/arcreel/current` 指向 `/opt/arcreel/releases/20261016-1367bf6b`。
- 发布 Git 提交：已推送的 `1367bf6b05a2e710821a2ef62673b422f9913649`。实际发布标识另带 `+preserved-character-hotfix`：线上独有的 `lib/prompts/prompt_templates/templates/partials/asset/sheet/guard/character.md` 原文予以保留，SHA-256 为 `046b31f08da2eecd9c17c085ec7cbe362bf3ddfef20f8c1523e6d2832d1e3c42`。
- 从旧目录 `/opt/arcreel/releases/20261015-9ad6b64d-pacingfix` 复制发布目录，应用当前提交的 23 个新增/修改文件。新目录与 Git HEAD 的 3910 个跟踪文件逐一核对，只有上述预期热修不相同。上次未提交的 pacing 修复及草稿相关服务端代码已包含在当前 Git HEAD，服务器旧目录中的对应字节也已与 HEAD 一致。
- 只操作 ArcReel 软链、`/etc/arcreel/arcreel.env` 中 `ARCREEL_PROFILE_DIR` 与 `PATH` 的旧发布路径，以及 `arcreel.service`；没有修改 nginx、网关服务或其配置和数据。

## 检查与验收

- 切换前活跃任务和 Agent 会话均为 0，SQLite `integrity_check=ok`。停服后生成完整数据、环境文件、systemd 单元归档 `/opt/arcreel/backups/20261016-1367bf6b/data-env-service.tar.gz`，870855759 字节、权限 `0600`，SHA-256 为 `c81200ca9db5f4589e399c912ee0cd7610126637ac676a570276360be12bb99a`。归档完整可读取；从归档提取的数据库 `integrity_check=ok`、任务 280 条。Unix socket 不可归档，tar 跳过了 6 个临时 socket。
- 新版本以 `arcreel` 用户导入 `server.app` 与改动模块成功。启动后进程 PID 1140885 的 `cwd` 指向新发布目录；ArcReel、网关和 nginx 均为 active。live DB `integrity_check=ok`，Alembic 为 `a9c3e5d17b24`，任务为 256 succeeded、23 failed、1 cancelled；启动 invocation 日志 72 行中无 ERROR/Traceback。
- 应用回环 `/health` 与首页、nginx 回环首页、公网 `http://43.154.247.11/health` 与首页均为 200；三个首页与发布目录 `frontend/dist/index.html` 哈希一致，公网抽验 3 个 JS 资源返回 200 且哈希一致。
- 使用 ArcReel 已保存的有效凭据向公网网关 `/v1/chat/completions` 发出最小真实文本请求，HTTP 200、模型 `elysium-chat`、文本 `OK`。未输出密钥。此验收只证明文本链路，不证明图片、视频或完整创作流程。
- 验收后出现 7 个新图片任务：5 running、2 queued，入队于 10:47:15 UTC，均在本次启动之后；没有中断或回滚这些任务。再次停服或回滚前必须重新检查任务与会话状态。

## 本地测试边界

- 相关测试 248 passed；类型修正后的草稿流程定向复测 54 passed。`ruff check`、`ruff format --check`、`basedpyright --warnings`（0 错误）、8 条 import-linter 契约和 deptry 均通过。
- 全量 pytest 为 16406 passed、62 failed、2 skipped。失败集中于 60 个媒体工具/图像后端事件循环同步 I/O 护栏及 2 个分集规划提示词期望；按失败节点对纯 Git `9ad6b64d` 基线复跑，19 failed、43 passed。后 43 项相对该纯 Git 基线新增，但相关 runtime/media 业务文件在切换前线上目录已逐字等于目标提交，故并非本次发布新增的运行代码。完整后端闸门没有通过，不应将此结果描述为通过；本次放行以当前线上行为和新增两处源码的定向验证为界。

## 回滚

受当前版本与任务/会话状态保护的代码回滚脚本位于 `/opt/arcreel/backups/20261016-1367bf6b/rollback.py`，权限 `0600`、语法检查通过、未实际执行。旧发布目录保留。脚本只切回旧代码并保留 live 数据；灾难恢复归档不可直接覆盖上线后新增数据。确认没有活跃任务或会话后才可运行：

```bash
ssh ai-hk 'sudo -n python3 /opt/arcreel/backups/20261016-1367bf6b/rollback.py'
```
