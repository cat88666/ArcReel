# 服务器部署记录（2026-10-14）

## 状态

已部署到 `veo-hk`，2026-10-14 21:43（北京时间）恢复服务。线上版本为 `/opt/arcreel/releases/20261014-55930508`，systemd 为 active。

当前提交 `55930508f7944fd8aefb88d3aac6312c77bc94ec` 已生效。旧版目录保留，数据根、环境和服务单元已备份；环境中的版本路径已同步更新。

验证：实际进程 cwd、Agent profile 指向新版；SQLite integrity_check=ok，Alembic 已到 `a9c3e5d17b24`；应用首页、nginx 首页和登录页均返回 200，JS 资源哈希与发布目录一致，启动日志无 ERROR/Traceback。nginx `/health` 是独立端点，应用健康同时通过 `127.0.0.1:1241/health` 验证。

快速重启影响：1 个正在执行的图片任务被恢复逻辑标记为 `restart_lost_image`，6 个依赖图片任务级联失败；记录未删除，未擅自重试。队列已恢复执行，尚未验证这些任务最终完成。

发布包本地与远端 SHA-256 均为 `68e2d66bc0e923fe739a21b6a8aa723617424cd73edf697286efd389a66a62c5`。

## 检查结果

- 前端使用 Node 24、pnpm 10.33.2：锁定依赖安装、生产构建、typecheck、lint、knip 通过。
- 后端完整测试：16,453 passed、2 skipped、1 failed，耗时 1,232 秒。
- 失败用例：`tests/unit/lib/backends/image_backends/test_openai_image_backend.py::TestOpenAIImageBackend::test_provider_bad_request_is_not_reported_as_retryable[True]`。
- Python 3.12 下该模块复测：26 passed、1 failed，同一用例失败。护栏捕获 `openai.py:201` 图片编辑上传路径在事件循环线程执行 `io.BufferedReader.read`。护栏不按耗时判定，不能归因为高负载。业务文件与旧版无差异；新增护栏揭露既有 SDK/httpx multipart 同步读取路径。
- 子包在 Python 3.12 下 686 项全部通过。Python 3.14 首轮 1 项深层 JSON 解析失败，因此以目标服务器 Python 3.12 复测为准。
- 前端首轮并行测试多项失败；单进程复测最终因 `Error: Worker exited unexpectedly` 中断，没有完整通过结果，不宣称前端测试通过。

## 部署授权

用户已在获知上述测试结果后明确要求「执行 部署」，按当前源码继续，不修复应用代码。切换前检测到新一批排队和运行中的生成任务，采用优雅停机等待运行任务完成，保留排队任务到新版继续。

临时 systemd runtime drop-in 将 `TimeoutStopSec=infinity`、`KillMode=mixed`，避免强杀生成任务和子进程；切换脚本在启动新版前移除该临时配置。两条到 1241 的入口长连接阻碍 lifespan 关停，已定向断开，随后日志确认开始停止 GenerationWorker。

用户随后要求「快速部署，服务已经停了好久了」，因此结束无限等待，终止旧进程，完成停服备份并立即切换。未完成任务记录和检查点保留。临时 drop-in 已移除，服务参数恢复 `TimeoutStopSec=120`、`KillMode=control-group`。

## 后续操作准备

本地及远端 `/tmp/arcreel-remote-20261014.py` 提供 `prepare` / `switch` 操作，prepare 已执行，不能重复创建同名发布目录。switch 会检查活跃任务，停服备份数据根、环境和服务文件，更新版本路径并切换软链，启动后检查健康。

备份位置：`/opt/arcreel/backups/20261014-55930508/data-env-service.tar.gz`，约 195 MiB，权限 0600，已完整解压读取校验归档。旧版路径记录在同目录 `previous-release`。回滚脚本已保存为该目录 `rollback.py`，会拒绝在活跃任务存在时执行，未实际回滚。

验证脚本 `/tmp/arcreel-verify-20261014.py` 已执行，版本、进程路径、SQLite 完整性、Alembic 版本、nginx 页面与静态资源检查通过。启动期间没有项目迁移失败日志；该日志在存在迁移或失败项时输出，不能仅以 `/health` 判定成功。

本地日志：`/tmp/arcreel-tests-20261014.log`、`/tmp/arcreel-backend-retest-20261014.log`、`/tmp/arcreel-market-tests-20261014.log`、`/tmp/arcreel-frontend-20261014.log`、`/tmp/arcreel-frontend-tests-serial-20261014.log`。
