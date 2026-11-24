const TOKEN_KEY = 'voyaura.access-token'
const USER_KEY = 'voyaura.owner'

export function getAccessToken(): string {
  return sessionStorage.getItem(TOKEN_KEY) ?? ''
}

export function setAccessToken(token: string): void {
  if (token.trim()) sessionStorage.setItem(TOKEN_KEY, token.trim())
  else sessionStorage.removeItem(TOKEN_KEY)
}

export function getOwnerUsername(): string {
  return sessionStorage.getItem(USER_KEY) ?? 'AuroraRovella'
}

export function setOwnerUsername(username: string): void {
  sessionStorage.setItem(USER_KEY, username)
}

export function clearSession(): void {
  sessionStorage.removeItem(TOKEN_KEY)
  sessionStorage.removeItem(USER_KEY)
}
