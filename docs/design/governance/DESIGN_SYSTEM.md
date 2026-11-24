# Voyaura 设计系统

实施路径：web/src/styles/design-tokens.css、ui.css，布局为product-shell.css、journey.css与工作台的scoped agent-workspace.css。main.ts统一引入，删除按轮次命名的旧样式入口；旧变量别名映射到同一套语义令牌。

## 文字、间距与表面

| 用途 | 令牌 | 默认值 |
| --- | --- | --- |
| 首页主视觉 | font-display | 桌面56px／窄屏36px |
| 页面标题 | font-title | 桌面30px／窄屏28px |
| 分区／卡片标题 | font-section／font-card | 22px／18px |
| 正文／字段 | font-body | 16px |
| 辅助／标签 | font-secondary／font-label | 14px／12px |
| 正文／标题行高 | line-body／line-heading | 1.75／1.35 |
| 间距 | space-1…8 | 4、8、12、16、24、32、48、64px |
| 控件／容器／摄影圆角 | radius-control／surface／photo | 6／10／16px |

字号使用rem，跟随根文字放大。品牌标志独立使用font-brand，避免文字放大时导航被标志挤出。按钮允许换行；必要的移动导航始终保留。容器以留白、底色与分隔线组织，浮层才使用shadow-float；输入边界使用border-control，选中使用action。

## 颜色与状态

| 用途 | 实际颜色 |
| --- | --- |
| 画布／内容表面／分组底色 | #faf9f6／#fffefb／#f2f0e8 |
| 标题／正文／辅助 | #23352b／#39483f／#606b61 |
| 品牌视觉／操作／悬停 | #e76840／#b94a2d／#a53c24 |
| 成功／警告／危险 | #2f6b49／#8a5b12／#b4232f |
| 输入边界／普通分隔／焦点 | #7d897f／#e6e3da／#a54023 |

UiStatus同时提供文字、图标和颜色；状态不能只靠颜色区分。行程阶段、日期、编号、错误原因、未核实事项与来源继续来自实际业务状态。摄影图中文字经人工查看，实色背景的对比取样见design-checks JSON。

## 操作层级

- Primary：当前主要任务，如生成草案、选择照片、核对后保存；使用实色action。
- Secondary：补地点、调整条件、添加照片；使用输入级边界。
- Tertiary：刷新、编辑、详情；保留文字及44px触控高度。
- Destructive：删除预览内确认；使用独立danger色及文字，保留原服务端确认。
- UiButton默认原生type=button，提交使用type=submit；支持外部form关联、原生必填校验、disabled、loading与aria-busy。loading期间禁止重复点击，名称仍保留。
- 焦点使用3px轮廓；常用HTML按钮、输入及详情展开区域至少44px。坐标图中空间标记另有可阅读的地点列表，时间线小圆点透明命中区域为44px。
- 城市档案“更多”仅展开菜单，点击删除才请求预览；添加照片与编辑始终可见。档案标签页支持方向键、Home、End及单一Tab焦点。
- 原有弹窗焦点约束、编辑离开保护和二阶段保存继续有效。

## 维护规则

在原规则中整改，避免持续叠加同名覆盖或全局!important。移除被同作用域后续规则替代的声明与删除节点样式时，保留其他选择器和条件规则的原有层叠顺序。共同字体、按钮、状态集中维护；页面局部CSS负责布局。API、授权及保存状态机不属于视觉改稿范围。
