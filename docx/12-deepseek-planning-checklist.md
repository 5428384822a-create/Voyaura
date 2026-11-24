# DeepSeek + LangChain 旅行规划接入清单

## 1. 当前算法边界

第一版采用以下分层流程：

```text
用户与小曦对话
  -> DeepSeek 提取结构化需求并提出候选假设
  -> 高德核验 POI、坐标和基础属性
  -> 根据旅行天数进行约束感知区域分组
  -> 每日内部路线优化和时间传播
  -> 跨日 relocate/swap 修复
  -> 最终真实路线边复核
```

DeepSeek 不负责提供坐标、开放时间、票价、真实交通时间或判断最终方案可行。模型输出的景点名称
统一标记为 `待高德核验假设`，不能直接写入已确认行程。

## 2. 已完成

- [x] 在 API 中固定 `langchain-core` 和 `langchain-deepseek` 依赖范围。
- [x] 使用 LangChain `ChatDeepSeek` 和 `deepseek-chat`；未使用不支持结构化输出的 `deepseek-reasoner`。
- [x] 增加 DeepSeek Key、模型、Base URL、温度、超时和重试环境配置。
- [x] 建立结构化 `PlanningIntent`：城市、天数、同行身份、节奏、兴趣、必去、排除、饮食、交通、时间和预算。
- [x] 建立 `AttractionHypothesis` 和 `PoiSearchTheme`，区分模型候选假设与高德检索任务。
- [x] 建立 `GET /api/v1/xiaoxi/planning/capability` 模型能力接口。
- [x] 建立 `POST /api/v1/xiaoxi/planning/preview` 结构化规划预览接口。
- [x] 已确认上下文优先于模型猜测；城市或天数缺失时生成追问并清空候选。
- [x] 未配置 Key、鉴权失败、限流、超时、结构化输出失败和 Provider 异常均返回稳定错误码。
- [x] 小曦网页/手机共用面板已接入真实 API，包含加载、错误、候选、搜索主题和未核验警告。
- [x] 后端 42 项测试、Ruff、前端 34 项测试和生产构建通过。

## 3. 环境配置

只在 `api/.env` 配置服务端凭证，不要把 DeepSeek Key 放进 `web/.env.local`、Git 或聊天记录：

```dotenv
VOYAURA_DEEPSEEK_API_KEY=你的服务端Key
VOYAURA_DEEPSEEK_MODEL=deepseek-chat
VOYAURA_DEEPSEEK_BASE_URL=https://api.deepseek.com
VOYAURA_DEEPSEEK_TEMPERATURE=0.1
VOYAURA_DEEPSEEK_TIMEOUT_SECONDS=30
VOYAURA_DEEPSEEK_MAX_RETRIES=2
```

修改后必须重启 FastAPI。能力检查：

```powershell
Invoke-RestMethod http://127.0.0.1:8001/api/v1/xiaoxi/planning/capability
```

## 4. 下一阶段：模型候选到高德候选池

- [ ] **P01 解析并确认城市**：将城市名解析为高德城市 `adcode`；存在同名城市时要求用户确认。
- [ ] **P02 执行搜索主题**：按 `PoiSearchTheme` 调用高德文本检索，不让模型生成高德 typecode。
- [ ] **P03 核验具名假设**：逐项搜索 `AttractionHypothesis.name`，记录匹配、歧义、未找到和 Provider 错误。
- [ ] **P04 实体去重**：优先使用高德 POI ID，再使用规范化名称、100 米坐标和地址辅助去重。
- [ ] **P05 类别配额**：按兴趣主题和地理覆盖保留候选，避免热门景点占满 `天数 x 10` 的候选池。
- [ ] **P06 数据门禁**：坐标、城市范围、来源和查询时间必须完整；未知开放时间保持 `null`。
- [ ] **P07 预览确认**：向用户展示哪些模型建议已找到、未找到或存在歧义，确认后再进入算法。
- [ ] **P08 固定快照**：把本次候选池保存为不可变实验输入，模型和高德查询不在求解循环中重复执行。

## 5. 下一阶段：按天区域划分

- [ ] **C01 建立交通时间距离**：优先使用高德有向交通时间，缺边只能使用显式标记的估算下界。
- [ ] **C02 初始区域分组**：实现带容量约束的 k-medoids，`k = 旅行天数`，不直接用普通经纬度 k-means。
- [ ] **C03 每日容量约束**：使用景点停留时间、交通时间和每日可用分钟数限制每组负载。
- [ ] **C04 锚点处理**：已购票、必去点和唯一开放日期先分配，普通候选围绕锚点聚类。
- [ ] **C05 每日路线求解**：每个区域先用现有 greedy insertion + 2-opt 构造可行路线。
- [ ] **C06 跨日修复**：使用 relocate/swap 处理闭馆、超载和区域边界附近的景点。
- [ ] **C07 独立验证**：最终路线必须通过开放时间、餐食、预算、返程和真实边验证。
- [ ] **C08 对照实验**：比较普通 k-means、约束 k-medoids、无聚类直接求解三种方法的质量和耗时。

## 6. 真实 DeepSeek 验收用例

输入：

```text
帮我规划杭州三天的独自摄影旅行，节奏轻松，公共交通为主。
```

验收：

- 城市为杭州、天数为 3、身份为独自、节奏为轻松；
- 摄影进入兴趣标签，公交地铁进入交通方式；
- 候选池目标为 30，但模型只提出少量优先核验假设；
- 不出现模型编造的坐标、开放时间、门票或交通耗时；
- 每条候选都能追溯到随后执行的高德匹配结果；
- 相同输入重复运行时允许措辞变化，但结构字段和硬需求应稳定。

当前机器已经配置 `VOYAURA_DEEPSEEK_API_KEY`，能力接口返回 `available=true`。自动测试仍使用
可替换的结构化假模型保证稳定性；上面的真实输入用例需要单独执行并记录 Provider 返回，不能把
自动测试结果冒充真实 DeepSeek 结果。
