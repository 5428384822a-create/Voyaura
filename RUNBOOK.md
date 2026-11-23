# Voyaura 运行、部署与复现手册

## 已实际验证的环境

Windows；Python3.12.10；Node25.8.1/npm11.11.0；Chrome桌面1440×1000和移动390×844；SQLite。Node25对部分开发依赖有engine警告，团队复现与CI推荐Node24 LTS。本机无Docker。不要复制桌面.env或真实数据库到验收目录。

## 无Docker本地启动

在仓库根目录执行（路径有空格时使用引号）：

```powershell
uv venv api/.venv --python 3.12
uv pip install --python api/.venv/Scripts/python.exe --default-index https://pypi.org/simple --require-hashes -r api/requirements-dev.lock
npm --prefix web ci
api/.venv/Scripts/python.exe scripts/local_setup.py
```

已有venv无需重复创建。本任务实际使用Workbench自带Python3.12.10建venv；普通开发者可使用自己安装的Python3.12。若镜像返回403，使用上面的官方PyPI参数，不修改全局镜像配置。

首次初始化生成 `.local/api.env`、随机32字节访问令牌、空SQLite数据库，再逐项运行0001—0014真实Alembic迁移与幂等seed。seed仅用户和城市字典，无旅行经历；重复运行不替换已有profile或令牌。文件均被Git忽略。

开两个终端：

```powershell
api/.venv/Scripts/python.exe scripts/local_serve.py api
```

```powershell
api/.venv/Scripts/python.exe scripts/local_serve.py web
```

访问 `http://127.0.0.1:5188`，默认进入无需令牌的发现首页。点击“我的”或规划、私人地图、旅行记忆等入口时再连接；在本机查看 `.local/access-token.txt`，把令牌填入连接窗口；不要贴到Issue、报告或聊天记录。API为 `http://127.0.0.1:8018`，`/health`为存活检查（不是所有依赖就绪检查），`/docs`提供契约。服务只监听127.0.0.1。停止时在各自终端Ctrl+C，不结束其他任务进程。

自定义初始端口：`scripts/local_setup.py --api-port 8019 --web-port 5189`；已有profile继续使用原端口，需人工检查后修改，不自动覆盖。Web使用同源 `/api/v1`，启动脚本设置代理目标，无需把API token写入Vite环境。

## 验收命令

```powershell
# 从api目录执行
.venv/Scripts/python.exe -m pytest -q --junitxml=../docs/delivery/final-api.xml
.venv/Scripts/python.exe -m ruff check app tests
# 从web目录执行
npm run test
npm run build
npm audit --omit=dev
```

从仓库根目录执行真实浏览器验收：

```powershell
api/.venv/Scripts/python.exe scripts/verify_e2e.py
```

此运行器建立新的 `.local/e2e-随机编号/test.db` 和随机令牌，真实迁移、启动两个独立localhost子进程，执行桌面和手机10项Playwright测试，最后只停止自己创建的进程。**不读改个人profile数据库**。测试资料明确标为验收夹具，非真实旅行；不调用云API；不保存包含Authorization的网络trace。测试DB和服务日志留在忽略目录；当前前端改稿的JUnit与流程截图在docs/design/round2，第一轮材料保留于docs/design/round1，旧Agent交付证据仍在docs/delivery。

本机已安装Chrome，可直接运行。没有Chrome时，在web运行 `npx playwright install chromium`，再设置 `$env:VOYAURA_E2E_CHANNEL='chromium'` 后执行运行器。Linux可用 `npx playwright install --with-deps chromium`。直接 `npm run test:e2e` 会连接指定的现有本地profile并写测试夹具，团队应优先使用隔离运行器。

## 可选服务及生产配置

1. 高德Web服务：服务端环境 `VOYAURA_AMAP_WEB_KEY` 与可选数字签名私钥；JS底图另需 `web/.env.local` 的Key与security code。只有用户在任务中允许外部服务才查询；无配置显示缺信息／示意图。10007是真实签名错误，不以假响应绕过。
2. 可选模型：`VOYAURA_AGENT_LLM_ENABLED=true`、`VOYAURA_AGENT_LLM_API_KEY`、`VOYAURA_AGENT_LLM_MODEL=deepseek-chat`，需界面额外同意可能收费的模型调用。适配器只提关键词，不做照片理解；本轮未在线验证。
3. 完整媒体栈：保留 `infra/compose.yml` 的PostgreSQL、Redis、MinIO及worker脚本，先阅读原docx/02、07、09说明。执行 `docker compose --env-file .env -f infra/compose.yml up -d` 后，在API工作目录配置自己的数据库/令牌/对象存储/扫描器，再运行Alembic、seed、Uvicorn与媒体worker。本轮未在本机实跑该组合。
4. API从当前工作目录的.env读取；生产在api/.env或进程环境配置，仓库根.env供Compose使用。不要误以为根.env自动成为API配置。
5. 生产构建的前端使用 `/api/v1`，由同源反向代理将该前缀转发到Uvicorn，其他路径提供web/dist与SPA回退。TLS、秘密管理、备份、角色/会话、限流、worker可靠交付、病毒扫描均须在上线前另行验收；本次没有公开部署。

升级已有数据库前做离线备份并在副本演练。迁移测试已保留0002历史文字、媒体、visit到0014，但不代替真实生产数据库备份或PostgreSQL验收。`.github/workflows/ci.yml` 已配置API/Web/浏览器/Postgres迁移作业，尚未在远程运行。

## 第一轮前端预览与路由

用户已于2026-11-23选择 A“清爽发现”，当前产品入口为 `http://127.0.0.1:5188/`，开发服务与生产构建默认均为 A。为复核原始设计对照，开发环境仍保留 `?style=immersive` 的 B 预览参数，两版共用真实交互和照片。离线截图对比与选择记录可打开 `docs/design/round1/index.html`。

客户端路径为 `/`（发现）、`/plan`（计划）、`/journey/map`（旅程地图）、`/journey/stories`（旅行记忆）、`/studio`（创作）。当前“我的”打开真实本机档案连接窗口，不代表已经实现账户中心。服务须将非文件、非API的路径回退到 `index.html`，例如Nginx `location / { try_files $uri $uri/ /index.html; }`；API代理另行匹配。Vite开发和预览服务支持该回退，其他托管环境尚未部署验收。

发现页旅行想法通过浏览器 history state 带入计划并支持当前历史项刷新，不写入URL；它是临时表单意图，不是已保存行程，清除浏览器历史或另开标签页不保证保留。私人档案保存仍须原有服务端确认。

## 数据与恢复

原城市记忆和新Agent档案位于不同表；保存计划不点亮城市。未确认故事来源变化会撤回，已确认快照独立保留。令牌清除只清浏览器副本；撤销本机访问需服务端更换令牌并重启。新任务中断后租约到期标失败，不自动重新收费；通过最近任务查看，必要时主动新建。

本任务早期浏览器验收曾在任务创建的 `.local/voyaura.db` 写入明确样例；完整保留为测试证据，没有接触桌面个人数据。交付时默认profile已切换到新建 `.local/clean-start.db`，用户没有虚构足迹。后续使用隔离E2E运行器。媒体完整功能需要真实存储、扫描与worker，不能只凭UI判定可用。


## 第二轮规划工作台

当前产品入口 `/plan` 沿用第一轮A视觉。输入按三组展开，生成后以每日安排为默认；地点地图和执行记录是真实视图，可用方向键、Home、End切换。个人档案连接与明确保存确认不变。历史任务恢复后，编辑条件会带入该任务的原始输入，外部工具须重新授权。

设计与真实截图：`docs/design/round2/index.html`（在本机浏览器中双击打开）、`overview.png`与`REVIEW.md`。截图审阅无需令牌；真实私人流程继续使用本机连接。

只读输入截图：启动API和Web后在web执行 `node scripts/capture-plan-input.mjs`。脚本仅在本地填写表单并读取已有服务信息，不向个人档案写入任务；四尺寸检查发现横向溢出、图片失败、pageerror或任何API写请求时退出失败。结果页等截图由隔离E2E生成，勿使用个人profile作为回归夹具库。
