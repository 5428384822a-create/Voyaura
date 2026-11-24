import { afterEach, describe, expect, it, vi } from 'vitest'
import { request, uploadMediaFile } from './client'
import { clearSession, getAccessToken, setAccessToken } from './session'
import type { MediaUploadIntent } from '../types'

afterEach(() => {
  clearSession()
  vi.unstubAllGlobals()
})
describe('本页访问凭证边界', () => {
  it('API带Bearer且URL不包含令牌', async () => {
    vi.stubGlobal('localStorage', { setItem: vi.fn() })
    setAccessToken('explicit-test-token-only')
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ status: 'ok' }) })
    vi.stubGlobal('fetch', fetchMock)
    await request('/auth/me')
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/auth/me',
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: 'Bearer explicit-test-token-only' }),
      }),
    )
    expect(localStorage.setItem).not.toHaveBeenCalled()
    clearSession()
    expect(getAccessToken()).toBe('')
  })
  it('签名对象存储上传不携带API访问令牌', async () => {
    setAccessToken('explicit-test-token-only')
    const headers: Record<string, string> = {}
    class TestXHR {
      upload = {}
      status = 200
      onload?: () => void
      open() {}
      setRequestHeader(k: string, v: string) {
        headers[k] = v
      }
      send() {
        queueMicrotask(() => this.onload?.())
      }
    }
    vi.stubGlobal('XMLHttpRequest', TestXHR)
    const intent = {
      status: 'created',
      asset_id: 'test-asset',
      upload_url: 'http://storage.test/object',
      method: 'PUT',
      required_headers: { 'Content-Type': 'image/jpeg' },
      expires_at: '2099-01-01',
    } as MediaUploadIntent
    await uploadMediaFile(intent, new File(['test'], 'test.jpg', { type: 'image/jpeg' }))
    expect(headers.Authorization).toBeUndefined()
  })
})
