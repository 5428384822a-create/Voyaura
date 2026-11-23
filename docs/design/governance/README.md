# 本轮改稿体验入口

真实产品：<http://127.0.0.1:5188/>；本机API为8018。私人页面需要在当前浏览器标签页连接本机访问令牌，本材料不包含令牌。

在浏览器打开同目录index.html，查看7个页面的桌面／手机前后对照。按钮只切换截图；“打开真实…”进入可操作产品。私人身份和记录文字已遮盖；流程截图来自隔离测试库，测试输入明确标注。旧轮次证据保留。

## 建议体验顺序

1. 发现：浏览摄影、筛选灵感，输入旅行想法。目的地不明时先选城，再带入计划。
2. 计划：首屏输入想法，往下选城市、日期与偏好。无在线地点服务时，基本安排后可补自己的地点，或点“填入离线演练条件”；填表不创建任务。
3. 主动“开始演练”后查看真实本地结果：宽屏时间线与地图同屏，手机切换视图。点编号联动日期与地点，再查看执行记录。
4. 修改／核对后，主动预览保存摘要，勾选确认后才保存。保存计划不等于到访记录。
5. “我的”恢复最近任务，读取原版本；不自动重新生成或保存。指南和服务状态按需展开。
6. 旅程按城市查看记忆。新建私人抵达、文字或照片时自行选择并核对；系统不会为了展示自动添加。
7. 档案“添加照片”“编辑”直接可见；“更多 → 删除记忆”打开预览，核对对象与后果后才确认，也可取消保留。
8. 创作页从自己的记忆选照片。未连接服务时如实提示，参考摄影不代表个人作品或生成结果。

## 复现验证

在仓库根目录：

~~~powershell
api/.venv/Scripts/python.exe scripts/verify_e2e.py
~~~

运行器新建.local/e2e-随机值/test.db，执行迁移、API与Chrome交互，仅写独立数据库。可追加Playwright文件／过滤选项，如design-governance.spec.ts --project=desktop。报告与截图默认写本目录，复跑会更新本轮证据。

在web：

~~~powershell
npm ci
npm run test -- --reporter=default --reporter=junit --outputFile.junit=../docs/design/governance/web-tests.xml
npm run build
~~~

首屏与附加屏宽图在before／after；结果、授权和确认图在各流程子目录；字体、触控与对比取样在design-checks。200%指根文字16→32px的放大检查。没有进行真实手机硬件、读屏软件和全部WCAG条目认证。在线地图／模型／影像及完整媒体服务仍需真实环境联调。


只读重拍当前页面：先启动项目，再在web执行node scripts/capture-design-pages.mjs。默认从本机忽略文件.local/access-token.txt内部读取令牌；也可配置VOYAURA_DESIGN_TOKEN、VOYAURA_DESIGN_TOKEN_FILE和VOYAURA_DESIGN_WEB_URL。脚本限定localhost服务，主动拦截API写请求，遮盖私人身份与任务文字，只更新本轮after截图和布局检查，不覆盖before。令牌不会输出到控制台或报告。
