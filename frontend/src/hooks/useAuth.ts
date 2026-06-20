import { useEffect, useState } from 'react'
import { getToken, loginWithCognito, parseTokensFromHash, removeToken, storeToken } from '../lib/cognito'

const AUTH_DISABLED = import.meta.env.VITE_AUTH_DISABLED === 'true'

interface AuthState {
  isAuthenticated: boolean
  isLoading: boolean
  login: () => void
  logout: () => void
  token: string | null
}

export function useAuth(): AuthState {
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (AUTH_DISABLED) {
      setToken('dev-token')
      setIsLoading(false)
      return
    }

    const hashTokens = parseTokensFromHash()
    if (hashTokens) {
      storeToken(hashTokens.accessToken)
      setToken(hashTokens.accessToken)
    } else {
      const stored = getToken()
      setToken(stored)
    }
    setIsLoading(false)
  }, [])

  const login = () => {
    if (AUTH_DISABLED) return
    loginWithCognito()
  }

  const logout = () => {
    if (AUTH_DISABLED) return
    removeToken()
    setToken(null)
  }

  return {
    isAuthenticated: !!token,
    isLoading,
    login,
    logout,
    token,
  }
}
