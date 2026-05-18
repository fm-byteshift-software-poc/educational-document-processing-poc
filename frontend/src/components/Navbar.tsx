import { useNavigate } from 'react-router'
import { useAuth } from '@/hooks/useAuth'

export default function Navbar() {
  const { tenantId, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <div className="navbar bg-base-100 shadow-sm">
      <div className="flex-1">
        <span className="text-xl font-bold">Educational Document Processing PoC</span>
      </div>
      <div className="flex-none gap-4">
        <span className="text-sm opacity-70">Tenant: {tenantId?.slice(0, 8)}...</span>
        <button onClick={handleLogout} className="btn btn-ghost btn-sm">Logout</button>
      </div>
    </div>
  )
}