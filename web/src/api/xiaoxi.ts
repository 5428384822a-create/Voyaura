import type {
  XiaoxiPlanningCapability,
  XiaoxiPlanningPreview,
  XiaoxiPlanningPreviewDraft,
} from '../types'
import { request } from './http'

export function previewXiaoxiPlanning(
  payload: XiaoxiPlanningPreviewDraft,
): Promise<XiaoxiPlanningPreview> {
  return request('/xiaoxi/planning/preview', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function getXiaoxiPlanningCapability(): Promise<XiaoxiPlanningCapability> {
  return request('/xiaoxi/planning/capability')
}
