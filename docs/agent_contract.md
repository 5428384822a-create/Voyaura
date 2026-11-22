# 小曦工作流 API 契约

所有接口前缀 `/api/v1/agent`，要求 `Authorization: Bearer <本机访问令牌>`。服务端 actor 决定归属，body 不接收 username。默认没有外部调用及私人记忆读取授权。

## 创建任务 POST /runs

必填：`client_request_id` UUID（同参数重试幂等），`goal` 2-1500字，`start_date` YYYY-MM-DD。

```json
{
  "client_request_id": "请使用 crypto.randomUUID()",
  "kind": "plan",
  "goal": "两天慢慢逛博物馆和公园，下午早点休息",
  "city_adcode": "440100",
  "city_name": "广州市",
  "start_date": "2026-12-01",
  "days": 2,
  "daily_start": "09:00",
  "daily_end": "18:00",
  "budget_yuan": null,
  "transport": "transit",
  "pace": "relaxed",
  "interests": ["博物馆", "公园"],
  "must_visit": [],
  "candidates": [],
  "allow_external": false,
  "allow_model": false,
  "allow_memory_access": false,
  "memory_ids": []
}
```

`days` 1-4；生产演示以2-4日为主。interests/must_visit各最多3个，每个80字。candidates最多12个，用户显式提供的事实：`{name, longitude, latitude, address?:'', stay_minutes?:60, opening_start?:null, opening_end?:null, cost_yuan?:null, must_visit?:false}`；坐标为GCJ-02，经度73-136，纬度3-54。开放窗口须同时填HH:MM，不支持跨夜。

`allow_external=true` 仅授权高德POI和路线查询，可能消耗服务额度；没有Key时记录配置缺失，不用替身返回。`allow_model=true` 还需allow_external且服务端显式启用/配置可选DeepSeek；不向模型发送私人记忆。默认执行可解释的有限规则提取，标记 `intent_source=local_rules`。

故事：`kind="story"`, `allow_memory_access=true`；按照city_adcode与start_date起days天读取当前actor已有CityMemory（memory_ids非空时进一步筛选）。不外传私人数据，故事模式拒绝allow_external/allow_model。没有记忆则needs_input，不造体验。仅已ready/clean照片计数，不读取图片字节、不声称视觉识别。日期/文字/数量来自数据库，之后可以编辑草稿。

## RunOut（创建、GET /runs/{id}、PATCH /runs/{id}/draft、POST /runs/{id}/confirm统一）

```typescript
interface AgentRun {
  id: string; kind: 'plan'|'story';
  status: 'running'|'needs_input'|'awaiting_confirmation'|'confirmed'|'failed';
  revision: number; title: string;
  request: Record<string, unknown>;
  result: {
    intent_source: 'local_rules'|'deepseek';
    verification_status: 'validated'|'conditional'|'conflict'|'information_missing';
    summary: string;
    warnings: string[]; unknowns: string[];
    candidates?: Candidate[];
    days?: DayPlan[];
    constraints?: Record<string, unknown>;
    validation?: {checks: Array<{code:string,status:string,message:string}>; known_cost_yuan:number; unknown_cost_count:number};
    source_memories?: Array<{id:string,title:string,body:string,date:string,city:string,photo_count:number,vlog_count:number}>;
    story_body?: string;
  };
  events: Array<{sequence:number,at:string,stage:string,tool:string,status:string,message:string,attempt:number,duration_ms?:number,details?:Record<string,unknown>}>;
  created_at:string; updated_at:string; saved_artifact_id:string|null;
}
interface Candidate {
  id:string;name:string;longitude:number;latitude:number;address:string;
  source:'amap'|'user_provided';verification:'verified'|'user_provided';
  source_url:string|null;queried_at:string;stay_minutes:number;
  opening_start:string|null;opening_end:string|null;cost_yuan:number|null;
  must_visit:boolean;
}
interface DayPlan {
  day:number;date:string;start:string;end:string;
  stops:Array<{candidate_id:string,name:string,longitude:number,latitude:number,arrival:string,departure:string,stay_minutes:number,timing_basis:'provider'|'planning_buffer',source:string}>;
  legs:Array<{from_id:string,to_id:string,duration_minutes:number|null,distance_meters:number|null,source:'amap'|'unknown',queried_at:string|null}>;
  total_minutes:number;
}
```

GET `/runs` 返回 `{items: AgentRun[]}`，最多最近20条，可刷新恢复。

## 编辑 PATCH /runs/{id}/draft

Body `{expected_revision:number, title?:string, story_body?:string, excluded_candidate_ids?:string[], daily_end?:'HH:MM'}`。前两项编辑故事，排除候选／每日结束时间可使计划基于原证据重新规划并重新验证，不重查外部服务。所有编辑会递增revision并作废旧确认。未确认任务可编辑；confirmed不可编辑。若rev冲突返回409。

## 确认预览 POST /runs/{id}/confirmation

Body `{expected_revision:number}`，响应 `{confirmation_token,content_digest,expires_at,revision,summary,requires_unverified_acknowledgement:boolean}`。有效期10分钟，绑定用户／任务／revision／完整内容。

## 保存 POST /runs/{id}/confirm

Body `{expected_revision,confirmation_token,content_digest,acknowledge_unverified:boolean}`。条件草案必须acknowledge_unverified=true；conflict/information_missing不可保存。成功返回RunOut，status=confirmed，saved_artifact_id非空。重复提交同token返回同artifact，无重复写入。草案确认只存私有计划／故事，不创建城市到访、不公开发布、不购买。

## 能力 GET /capabilities

返回 `{amap_configured:boolean, model_configured:boolean, intent_default:'local_rules', privacy_notice:string, limits:{days:4,candidates:12,search_topics:3,attempts:2}, tools:string[]}`，仅表示配置状态，不代表在线服务已经通过验收。
