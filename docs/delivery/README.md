# Voyaura 开发交付索引

本次交付位于独立Git分支 `codex/xiaoxi-evidence-agent`，原始基线 `cbdab47`；远程main已只读核对同为该提交。桌面原仓库、原始立项书与其他任务保持原处。没有推送或合并远程。

## 从这里开始

1. [运行与部署手册](../../RUNBOOK.md)：无Docker启动、凭证位置、隔离E2E与云服务配置。
2. [工程评估](../../ARCHITECTURE_REVIEW.md)：已验证事实／推断／待确认、立项书对照和优先级。
3. [软件架构](ARCHITECTURE.md) 与 [接口契约](../agent_contract.md)：实际实现、状态和确认、来源与隐私边界。
4. [功能与测试报告](TEST_REPORT.md)：最终结果、原始JUnit、浏览器、依赖审计和未验收项。
5. [独立基线审查](BASELINE_CODE_AUDIT.md)、[最终独立审查](FINAL_INDEPENDENT_REVIEW.md)。
6. [创新分析](INNOVATION.md)、[参赛技术报告初稿](TECHNICAL_REPORT_DRAFT.md)、[PPT内容大纲](PPT_OUTLINE.md)、[Demo流程与解说词](DEMO_SCRIPT.md)。
7. [CodeArts实质任务及真实证据方案](CODEARTS_EVIDENCE_PLAN.md)：本次Codex工作不能替代码道证明。

当前能验收的是本地受控工作流，不能宣称完整一年研究目标、在线云Provider或多用户生产系统全部完成。正式参赛包需真实码道工作、合法Provider和最终通知核验，不自动上传。

## 原始证据

- `competition_rules_snapshot.json`：北京时间2026-11-22官方赛事公开数据快照。
- `baseline-api.xml` / `baseline-web.xml`：原代码API37/Web33基线。
- `final-api.xml` / `final-web.xml` / `e2e.xml`：最终实跑结果，具体数量见TEST_REPORT。
- `python-dependency-audit.before.json` / `python-dependency-audit.json`：安全修复前后扫描；npm结果见对应审计文件。
- `screenshots/journey-desktop.png`、`journey-mobile.png`、`story-desktop.png`、`story-mobile.png`：真实Chrome本地运行，内容明确为测试输入。

源码审查与Git差异均可在本地检查。`.local`、密钥、数据库、venv和node_modules不进入Git或参赛源代码包。

## 可直接使用的文档

- [技术报告Word](Voyaura_技术报告初稿.docx) / [PDF](Voyaura_技术报告初稿.pdf)
- [10页答辩PPT初稿](Voyaura_答辩演示初稿.pptx)

Word已实际渲染为PDF并核对3个关键文本；PPT已重新打开检查10页与画布边界，截图来自真实浏览器。正式答辩前需填充真实CodeArts实质开发成果与证据。
