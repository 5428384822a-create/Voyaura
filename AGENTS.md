# Voyaura 工程协作规则

- 本开发副本位于本任务目录，原始基线 cbdab47；Agent 工程交付基线 b525185。当前设计治理基线6a5c01e，分支codex/ui-design-governance；用户已审核方案并授权实际改稿，保留此前档案、引导、任务恢复与编辑保护。不得修改桌面原仓库、其他任务、真实用户数据。演练入口只能填写表单；生成和保存须用户分别主动操作，不伪造在线地点或模型输出。
- 用户已于2026-11-23采用第一轮方案A“清爽发现”：后续视觉沿用暖白底、橙红品牌、明亮摄影及当前导航体系；具体记录见 docs/design/round1/REVIEW.md。
- 保留 Vue 3 / FastAPI / SQLAlchemy / PostgreSQL / Redis / MinIO 架构。SQLite 仅为明确标示的本地单机验证配置，不替代生产数据库。
- 小曦使用显式状态机、白名单工具、独立约束验证和持久化调用事件。未知信息必须保持未知，不得将本地样例、模型文本或测试替身标记为在线事实。
- 密钥仅来自环境或本地忽略文件，不提交密钥及立项书中的个人资料。默认外部服务关闭；开启付费模型调用必须由使用者明确配置并在界面授权。
- 正式行程／故事写入需服务端确认，绑定用户、内容摘要、有效期，具备幂等及并发保护。私人记忆读取和对外传输分别授权。禁止实现自主购买、公开发布或自动删除。
- 认证必须约束原有 username 参数，禁止仅靠客户端传入用户名授权。单机访问令牌模式须如实说明不等于多租户生产账号体系。
- Codex 完成的工作只记为 Codex；CodeArts 证据目录只能由实际使用 CodeArts 的开发者填充。
- 变更必须有针对性的真实测试。pytest 测试中的 Provider 替身必须命名清楚，并与在线集成结果分开。
- 协作边界：后端工作流负责人仅编辑新的 agent 模块、agent migration 和对应测试；基础安全负责人编辑 auth、config、database、main、原有 routers、CI 与启动脚本；主负责人编辑 web、总体文档及交付验证。交叉变更需先沟通。

## 前端设计约束

- 按用户任务组织页面：首屏有标题和主要行动，装饰英文／模块流水号／重复宣传不进入正式界面。保留日期、来源、未知、权限和错误事实。
- 语义令牌统一位于web/src/styles/design-tokens.css，共享按钮与状态见UiButton／UiStatus和ui.css。布局文件按职责命名，避免新增按轮次叠加的覆盖。
- 正文／字段16px，辅助14px，标签至少12px；按钮区分主、次、低优先级和危险操作；可见名称与键盘焦点不可丢失。
- 视觉变更在桌面和手机实页截图检查。布局、字段、触控与实色背景取样由design-governance.spec.ts验证；200%为文字放大，不能声称已完成全部WCAG认证。
- 改前／改后图及功能流程写入docs/design/governance，保留历史轮次证据。当前服务只读截取，功能测试使用verify_e2e.py的独立库。

## 验证命令

在 api：`python -m pytest -q`、`python -m ruff check app tests`、`python -m alembic upgrade head`。
在 web：`npm ci`、`npm run test`、`npm run build`、`npm audit --omit=dev`。
当前前端真实浏览器验收：在根目录执行 `api/.venv/Scripts/python.exe scripts/verify_e2e.py`；新建隔离测试库，报告位于 docs/design/governance，不向个人档案写入测试夹具。
启动／端到端与数据库迁移验证命令在 RUNBOOK.md 随实现更新。所有命令结果记录于 PROGRESS.md 与 docs/delivery/TEST_REPORT.md。
