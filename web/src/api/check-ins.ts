import type {
  CheckInConfirmResult,
  CheckInCoordinates,
  CheckInPreview,
  ManualCityCheckIn,
} from '../types'
import { request } from './http'

export function previewCheckIn(payload: CheckInCoordinates): Promise<CheckInPreview> {
  return request('/check-ins/preview', { method: 'POST', body: JSON.stringify(payload) })
}

export function confirmCheckIn(payload: CheckInCoordinates): Promise<CheckInConfirmResult> {
  return request('/check-ins/confirm', { method: 'POST', body: JSON.stringify(payload) })
}

export function previewManualCheckIn(payload: ManualCityCheckIn): Promise<CheckInPreview> {
  return request('/check-ins/manual-preview', { method: 'POST', body: JSON.stringify(payload) })
}

export function confirmManualCheckIn(payload: ManualCityCheckIn): Promise<CheckInConfirmResult> {
  return request('/check-ins/manual-confirm', { method: 'POST', body: JSON.stringify(payload) })
}
