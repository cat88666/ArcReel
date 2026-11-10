# ArcReel 服务器部署记录

部署完成：2026-10-12。目标：`veo-hk`（`43.154.247.11`）。访问地址：<http://43.154.247.11/>。登录使用本地的账号密码，默认用户名为 `admin`；凭证未写入本记录。

## 当前版本与范围

- 代码版本：`276450af62077b0423b07b8e0f400b8eb21c555d`。
- 发布目录：`/opt/arcreel/releases/20261012-192238-276450af`，`/opt/arcreel/current` 已切换到此目录。
- 服务：`arcreel.service`，监听 `127.0.0.1:1241`，沿用现有 nginx 入口。
- 数据根：`/var/lib/arcreel`。覆盖本地完整数据库（25 张表）、项目、媒体、用户记忆、配置及运行数据；不是与旧服务器数据合并。
- 环境文件：`/etc/arcreel/arcreel.env`，发布目录 `.env` 指向此文件。本地 `.env` 的 `AUTH_PASSWORD`、`CLAUDE_CODE_MAX_CONTEXT_TOKENS` 均已核对实际服务进程值一致。
- 服务器路径、HOME、SDK 目录及认证 token secret 按服务器环境设置。旧服务器的 `CLAUDE_CODE_MAX_OUTPUT_TOKENS=8192` 和 `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` 未保留，已验证新进程中不存在。
- 项目专用 SDK 历史复制了 11 个 JSONL。数据库会话 `project_key`、结构化 `cwd` 元数据和 SDK 目录键仅在部署副本中转换为服务器路径；历史正文和工具调用原文未改写。
- 未修改应用源码，未部署或重启网关服务。

## 旧部署备份

备份目录：`/opt/arcreel/backups/20261012-192238-276450af/`。

`previous-deployment.tar.gz` 包含旧发布目录、完整数据根、旧环境文件、systemd 服务文件和 nginx 主配置。归档大小为 680160179 字节，SHA256：

```text
2603b27c598212fc3ebe964ad5d62cc5ff61557537d1222f05a93093f53ee6bd
```

备份解包后的 SQLite `integrity_check` 为 `ok`，核对旧任务 150 条、旧会话 26 条。备份目录权限为 `0700`，归档为 `0600`。

切换前的原数据目录另完整保留在 `/var/lib/arcreel.previous-20261012-192238-276450af`，旧发布目录 `/opt/arcreel/releases/20260929-192508-7d97661c` 也保留。

## 验证结果

- 本地 Node 24.21.0、项目 pnpm 10.33.2：类型检查和生产构建通过。
- 服务器依据 `uv.lock` 安装依赖成功，FastAPI、Claude Agent SDK、市场核心包导入通过。
- 相同 systemd 保护条件下，Agent 所需 bwrap 沙箱探针通过。
- 最终快照逐文件校验通过：198 个文件。数据库全部表的记录数均保留，六类配置表的完整内容指纹与本地快照完全一致。
- 数据库 `integrity_check` 通过，Alembic 启动检查和 Agent profile 物化通过，后者错误数为 0。
- 登录成功；未认证项目访问返回 401；当前项目 `proj-d33835ca` 的会话列表及事件历史可读取。
- 54 个媒体及源文件哈希与本地一致，13 个页面静态资源可访问。
- 公网首页与本地构建文件哈希一致；公网 `/health` 和认证状态接口返回 200。
- ArcReel 和网关服务均为 active。

验证记录存放于备份目录的 `verification.json`、`incoming-manifest.json` 和 `manifest.json`。部署验证未额外触发模型或媒体生成，不能将健康及数据验证视为所有生成供应商的端到端测试。

## 本地状态

本地最后一个视频任务在 19:32:20 成功落盘，全部排队及运行任务清空，服务正常退出后才制作快照。本地服务保持停止；后续在服务器继续工作，避免两份数据独立写入产生分叉。

## 回滚

仅在需要恢复旧服务器内容时运行。脚本会检查当前发布版本，并在存在排队或运行任务时拒绝回滚。脚本保留被替换的新数据，不删除它；恢复旧数据、旧环境文件、旧服务文件及旧发布链接后检查健康状态。

```bash
ssh veo-hk 'sudo -n python3 /opt/arcreel/backups/20261012-192238-276450af/rollback.py'
```

回滚脚本已保存并通过语法检查，未实际执行回滚。
