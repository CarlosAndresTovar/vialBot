import type { ReactNode } from 'react'
import { useAuth } from '../hooks/useAuth'

const AUTH_DISABLED = import.meta.env.VITE_AUTH_DISABLED === 'true'

interface AuthGuardProps {
  children: ReactNode
}

export function AuthGuard({ children }: AuthGuardProps) {
  const { isAuthenticated, isLoading, login } = useAuth()

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-brand-600 border-t-transparent" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center px-4">
        <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-lg">
          <h1 className="mb-2 text-center text-2xl font-bold text-gray-900">vialBot</h1>
          <p className="mb-6 text-center text-gray-600">
            Tu asistente experto en el Código Nacional de Tránsito de Colombia.
          </p>
          {AUTH_DISABLED ? (
            <p className="text-center text-sm text-gray-500">
              Modo desarrollo activado. Recarga la página para continuar.
            </p>
          ) : (
            <button
              onClick={login}
              className="w-full rounded-lg bg-brand-600 px-4 py-3 font-medium text-white transition hover:bg-brand-700"
            >
              Iniciar sesión
            </button>
          )}
        </div>
      </div>
    )
  }

  return <>{children}</>
}
