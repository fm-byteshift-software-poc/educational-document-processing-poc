import { createContext, useContext, useState, ReactNode } from 'react'

interface AuthContextType {
  token: string | null
  tenantId: string | null
  login: (token: string, tenantId: string) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))
  const [tenantId, setTenantId] = useState<string | null>(localStorage.getItem('tenantId'))

  const login = (newToken: string, newTenantId: string) => {
    setToken(newToken)
    setTenantId(newTenantId)
    localStorage.setItem('token', newToken)
    localStorage.setItem('tenantId', newTenantId)
  }

  const logout = () => {
    setToken(null)
    setTenantId(null)
    localStorage.removeItem('token')
    localStorage.removeItem('tenantId')
  }

  return (
    <AuthContext.Provider value={{ token, tenantId, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}