import type { LocalRouteDraft, LocalRouteResult, RouteCapabilities } from '../types'
import { request } from './http'

export function getRouteCapabilities(): Promise<RouteCapabilities> {
  return request('/tools/routes/capabilities')
}

export function planLocalRoute(payload: LocalRouteDraft): Promise<LocalRouteResult> {
  return request('/tools/routes/plan', { method: 'POST', body: JSON.stringify(payload) })
}
