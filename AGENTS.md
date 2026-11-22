# Voyaura 工程协作规则

- 本开发副本位于本任务目录，基线 cbdab47，分支 codex/xiaoxi-evidence-agent；不得修改桌面原仓库、其他任务、真实用户数据。
- 保留 Vue 3 / FastAPI / SQLAlchemy / PostgreSQL / Redis / MinIO 架构。SQLite 仅为明确标示的本地单机验证配置，不替代生产数据库。
- 小曦使用显式状态机、白名单工具、独立约束验证和持久化调用事件。未知信息必须保持未知，不得将本地样例、模型文本或测试替身标记为在线事实。
- 密钥仅来自环境或本地忽略文件，不提交密钥及立项书中的个人资料。默认外部服务关闭；开启付费模型调用必须由使用者明确配置并在界面授权。
- 正式行程／故事写入需服务端确认，绑定用户、内容摘要、有效期，具备幂等及并发保护。私人记忆读取和对外传输分别授权。禁止实现自主购买、公开发布或自动删除。
- 认证必须约束原有 username 参数，禁止仅靠客户端传入用户名授权。单机访问令牌模式须如实说明不等于多租户生产账号体系。
- Codex 完成的工作只记为 Codex；CodeArts 证据目录只能由实际使用 CodeArts 的开发者填充。
- 变更必须有针对性的真实测试。pytest 测试中的 Provider 替身必须命名清楚，并与在线集成结果分开。
- 协作边界：后端工作流负责人仅编辑新的 agent 模块、agent migration 和对应测试；基础安全负责人编辑 auth、config、database、main、原有 routers、CI 与启动脚本；主负责人编辑 web、总体文档及交付验证。交叉变更需先沟通。

## 验证命令

在 api：`python -m pytest -q`、`python -m ruff check app tests`、`python -m alembic upgrade head`。
在 web：`npm ci`、`npm run test`、`npm run build`、`npm audit --omit=dev`。
启动／端到端与数据库迁移验证命令在 RUNBOOK.md 随实现更新。所有命令结果记录于 PROGRESS.md 与 docs/delivery/TEST_REPORT.md。
