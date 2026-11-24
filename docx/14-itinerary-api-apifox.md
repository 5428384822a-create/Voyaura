# 正式行程 API 与 Apifox 验收

## 导入方式

API 启动后，在 Apifox 中导入 OpenAPI 地址：

```text
http://127.0.0.1:8001/openapi.json
```

行程接口位于 `itineraries` 分组。开发环境的 API 根地址为：

```text
http://127.0.0.1:8001/api/v1
```

## 1. 创建行程草稿

```http
POST /api/v1/trips
Content-Type: application/json
```

示例请求：

```json
{
  "username": "AuroraRovella",
  "client_request_id": "11111111-1111-4111-8111-111111111114",
  "title": "杭州三日摄影行程",
  "origin_city_name": "广州市",
  "origin_city_adcode": "440100",
  "destination_city_name": "杭州市",
  "destination_city_adcode": "330100",
  "start_date": "2026-12-01",
  "day_count": 3,
  "timezone": "Asia/Shanghai",
  "party_type": "solo",
  "pace": "relaxed",
  "interests": ["摄影", "历史"],
  "transport_modes": ["transit", "walking"],
  "dietary_constraints": [],
  "total_budget_yuan": "3000.00",
  "daily_start_time": "09:00:00",
  "daily_end_time": "21:00:00",
  "requirements_snapshot": {
    "source": "xiaoxi-planning-preview"
  }
}
```

成功返回 `201`。首次创建的 `status` 为 `created`；相同
`client_request_id` 和相同内容再次提交返回 `existing`，不会产生重复记录。同一请求编号
提交不同内容返回 `409 / TRIP_IDEMPOTENCY_CONFLICT`。

创建三日行程时会同时创建三条空的 `trip_days`。当前不会自动写入景点、餐厅或路线，避免
把尚未经过高德核验的模型候选保存成事实。

## 2. 查询行程列表

```http
GET /api/v1/trips?username=AuroraRovella&status=draft&limit=20&offset=0
```

`status` 可省略，可选值为：`draft`、`confirmed`、`planning`、`ready`、`archived`。

## 3. 查询行程详情

```http
GET /api/v1/trips/{trip_id}?username=AuroraRovella
```

详情返回 `days`、每日 `stops`、`transfer_legs` 以及整趟行程的 `evidence`。第一阶段创建后
`stops` 和 `evidence` 为空；下一阶段由高德候选池确认流程写入。

## 常见错误

| HTTP | 错误码 | 含义 |
| --- | --- | --- |
| `404` | `USER_NOT_FOUND` | 用户名不存在 |
| `404` | `TRIP_NOT_FOUND` | 行程不存在或不属于当前用户 |
| `409` | `TRIP_IDEMPOTENCY_CONFLICT` | 同一请求编号对应不同内容 |
| `422` | FastAPI 校验错误 | adcode、日期、天数或每日时间窗不合法 |

每个业务错误都保留统一错误结构和 `X-Request-ID`，可以在 Apifox 响应头与响应体中一起记录。

## Navicat 核验

```sql
SELECT id, title, status, destination_city_name, day_count,
       start_date, end_date, total_budget_yuan, created_at
FROM trips
ORDER BY created_at DESC;

SELECT t.title, d.day_number, d.travel_date, d.status,
       COUNT(s.id) AS stop_count
FROM trips AS t
JOIN trip_days AS d ON d.trip_id = t.id
LEFT JOIN itinerary_stops AS s ON s.trip_day_id = d.id
GROUP BY t.id, t.title, d.id, d.day_number, d.travel_date, d.status
ORDER BY t.created_at DESC, d.day_number;
```

Navicat 只用于查看和辅助调试。新增、修改和删除行程应通过 API，避免绕过幂等、来源证据
和后续状态机约束。
