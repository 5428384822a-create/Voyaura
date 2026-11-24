import type { AppErrorInfo } from '../types'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8001/api/v1'

interface ApiErrorEnvelope {
  error?: {
    code?: string
    message?: string
    details?: Record<string, unknown>
    retryable?: boolean
    request_id?: string
  }
}

export class ApiClientError extends Error implements AppErrorInfo {
  code: string
  details: Record<string, unknown>
  retryable: boolean
  requestId?: string

  constructor(info: AppErrorInfo) {
    super(info.message)
    this.name = 'ApiClientError'
    this.code = info.code
    this.details = info.details
    this.retryable = info.retryable
    this.requestId = info.requestId
  }
}

export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${apiBaseUrl}${path}`, {
      ...init,
      headers: { 'Content-Type': 'application/json', ...init?.headers },
    })
  } catch {
    throw new ApiClientError({
      code: 'API_NETWORK_ERROR',
      message: '无法连接 Voyaura 服务。',
      details: { api_base_url: apiBaseUrl },
      retryable: true,
    })
  }

  if (!response.ok) {
    const payload = (await response.json().catch(() => ({}))) as ApiErrorEnvelope
    throw new ApiClientError({
      code: payload.error?.code ?? `HTTP_${response.status}`,
      message: payload.error?.message ?? '服务返回了无法识别的错误。',
      details: payload.error?.details ?? {},
      retryable: payload.error?.retryable ?? response.status >= 500,
      requestId: payload.error?.request_id ?? response.headers.get('X-Request-ID') ?? undefined,
    })
  }
  return response.json() as Promise<T>
}
