# 服务器部署准备与阻塞（2026-10-14）

## 状态

尚未切换线上服务。目标服务器为 `veo-hk`，线上仍为 `/opt/arcreel/releases/20261012-192238-276450af`。

已将当前提交 `55930508f7944fd8aefb88d3aac6312c77bc94ec` 构建上传到 `/opt/arcreel/releases/20261014-55930508`，服务器依赖安装及关键模块导入通过。线上数据和环境文件未修改，未停服，尚未执行升级前备份。

发布包本地与远端 SHA-256 均为 `68e2d66bc0e923fe739a21b6a8aa723617424cd73edf697286efd389a66a62c5`。

## 检查结果

- 前端使用 Node 24、pnpm 10.33.2：锁定依赖安装、生产构建、typecheck、lint、knip 通过。
- 后端完整测试：16,453 passed、2 skipped、1 failed，耗时 1,232 秒。
- 失败用例：`tests/unit/lib/backends/image_backends/test_openai_image_backend.py::TestOpenAIImageBackend::test_provider_bad_request_is_not_reported_as_retryable[True]`。
- Python 3.12 下该模块复测：26 passed、1 failed，同一用例失败。护栏捕获 `openai.py:201` 图片编辑上传路径在事件循环线程执行 `io.BufferedReader.read`。护栏不按耗时判定，不能归因为高负载。业务文件与旧版无差异；新增护栏揭露既有 SDK/httpx multipart 同步读取路径。
- 子包在 Python 3.12 下 686 项全部通过。Python 3.14 首轮 1 项深层 JSON 解析失败，因此以目标服务器 Python 3.12 复测为准。
- 前端首轮并行测试多项失败；单进程复测最终因 `Error: Worker exited unexpectedly` 中断，没有完整通过结果，不宣称前端测试通过。

## 待决定

已询问用户：先修复后部署，还是明确接受已知问题、保持当前源码部署。项目 AGENTS.md 要求相关测试通过，目前不满足；收到选择前不切换。

## 后续操作准备

本地及远端 `/tmp/arcreel-remote-20261014.py` 提供 `prepare` / `switch` 操作，prepare 已执行，不能重复创建同名发布目录。switch 会检查活跃任务，停服备份数据根、环境和服务文件，更新版本路径并切换软链，启动后检查健康。

预定备份位置：`/opt/arcreel/backups/20261014-55930508`，当前尚未创建。回滚脚本 `/tmp/arcreel-rollback-20261014.py` 已准备；仅在实际切换和备份后适用，未执行。

验证脚本 `/tmp/arcreel-verify-20261014.py` 检查版本、进程路径、SQLite 完整性、Alembic 版本、nginx 页面与静态资源以及启动日志。迁移预期到 `a9c3e5d17b24`；还需确认项目迁移无失败，不能仅以 `/health` 判定成功。

本地日志：`/tmp/arcreel-tests-20261014.log`、`/tmp/arcreel-backend-retest-20261014.log`、`/tmp/arcreel-market-tests-20261014.log`、`/tmp/arcreel-frontend-20261014.log`、`/tmp/arcreel-frontend-tests-serial-20261014.log`。
