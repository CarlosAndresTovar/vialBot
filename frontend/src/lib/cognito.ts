const COGNITO_DOMAIN = import.meta.env.VITE_COGNITO_DOMAIN
const CLIENT_ID = import.meta.env.VITE_COGNITO_CLIENT_ID
const REDIRECT_URI = import.meta.env.VITE_COGNITO_REDIRECT_URI
const SCOPE = import.meta.env.VITE_COGNITO_SCOPE || 'openid email profile'

export function loginWithCognito(): void {
  const url = new URL(`${COGNITO_DOMAIN}/oauth2/authorize`)
  url.searchParams.set('client_id', CLIENT_ID)
  url.searchParams.set('response_type', 'token')
  url.searchParams.set('scope', SCOPE)
  url.searchParams.set('redirect_uri', REDIRECT_URI)
  window.location.href = url.toString()
}

export function parseTokensFromHash(): { accessToken: string; expiresIn: number } | null {
  const hash = window.location.hash.replace(/^#/, '')
  const params = new URLSearchParams(hash)
  const accessToken = params.get('access_token')
  const expiresIn = params.get('expires_in')

  if (!accessToken) return null

  window.history.replaceState({}, document.title, window.location.pathname)
  return {
    accessToken,
    expiresIn: expiresIn ? parseInt(expiresIn, 10) : 3600,
  }
}

export function storeToken(token: string): void {
  localStorage.setItem('vialbot_access_token', token)
}

export function getToken(): string | null {
  return localStorage.getItem('vialbot_access_token')
}

export function removeToken(): void {
  localStorage.removeItem('vialbot_access_token')
}
