# 前端 API 分层

前端 API 按业务域放在 `web/src/api/`。这是一层请求服务路由，不是页面导航路由，因此不需要额外引入 Vue Router。

## 公共入口

- `http.ts`：读取 `VITE_API_BASE_URL`，发送请求，并统一转换网络错误、后端错误码和 `X-Request-ID`。
- `index.ts`：页面和组件使用的统一导出入口。
- `client.ts`：旧代码兼容入口；新代码不再向这个文件追加业务函数。

## 业务模块

| 前端模块 | 职责 | 主要后端路径 |
| --- | --- | --- |
| `map.ts` | 地图总览 | `/map/*` |
| `check-ins.ts` | 定位预览与城市点亮 | `/check-ins/*` |
| `memories.ts` | 城市记忆增删改查 | `/cities/{adcode}/memories/*` |
| `media.ts` | 照片、Vlog 上传与处理任务 | `/cities/{adcode}/*/media/*` |
| `images.ts` | 图片风格目录与生成任务 | `/image-styles`、`/image-jobs/*` |
| `poi.ts` | 高德 POI 搜索与详情 | `/tools/poi/*` |
| `routes.ts` | 市内路线与交通能力 | `/tools/routes/*` |
| `trips.ts` | 正式行程创建、列表与详情 | `/trips/*` |
| `xiaoxi.ts` | 小曦结构化规划 | `/xiaoxi/planning/*` |

## 新增接口规则

1. 页面和组件默认从 `src/api/index.ts` 导入，不直接拼接 API 根地址。
2. 新接口放入对应业务模块；只有出现新的独立业务域时才新增文件。
3. 所有 JSON 请求继续复用 `http.ts` 的 `request`，不要在页面中重复实现错误解析。
4. MinIO 文件直传仍放在 `media.ts`，因为它需要 `XMLHttpRequest` 的字节进度与取消能力。
5. `VITE_API_BASE_URL` 只放在环境文件中；高德和 DeepSeek 的服务端凭证不得写入业务模块。
