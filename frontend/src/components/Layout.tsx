import { Outlet, Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import {
  LayoutDashboard,
  Globe,
  Database,
  Link as LinkIcon,
  HardDrive,
  Users,
  FileText,
  LogOut,
  Menu,
  X,
} from 'lucide-react'
import { useState } from 'react'

export default function Layout() {
  const { user, logout } = useAuth()
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Sites', href: '/sites', icon: Globe },
    { name: 'Databases', href: '/databases', icon: Database },
    { name: 'Domains', href: '/domains', icon: LinkIcon },
    { name: 'Backups', href: '/backups', icon: HardDrive },
    { name: 'Users', href: '/users', icon: Users },
    { name: 'Audit Logs', href: '/audit', icon: FileText },
  ]

  const isActive = (path: string) =>
    location.pathname === path || location.pathname.startsWith(path + '/')

  return (
    <div className="min-h-screen bg-stripe-bg">
      {/* Mobile sidebar overlay */}
      <div
        className={`fixed inset-0 z-40 lg:hidden ${sidebarOpen ? '' : 'hidden'}`}
        aria-hidden="true"
      >
        <div
          className="fixed inset-0 bg-stripe-navy/60"
          onClick={() => setSidebarOpen(false)}
        />
        <div className="fixed inset-y-0 left-0 w-72 max-w-[85vw] card-stripe border-0 shadow-stripe-lg">
          <SidebarContent
            navigation={navigation}
            isActive={isActive}
            onClose={() => setSidebarOpen(false)}
          />
        </div>
      </div>

      {/* Desktop sidebar - Stripe navy */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-1 flex-col bg-stripe-navy">
          <SidebarContent navigation={navigation} isActive={isActive} />
        </div>
      </div>

      <div className="lg:pl-64 flex flex-col min-h-screen">
        {/* Top bar - white, subtle border */}
        <header className="sticky top-0 z-30 flex h-14 flex-shrink-0 items-center border-b border-stripe-border bg-white px-4 sm:px-6">
          <button
            type="button"
            className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-stripe-primary/20 lg:hidden"
            onClick={() => setSidebarOpen(true)}
            aria-label="Open menu"
          >
            <Menu className="h-5 w-5" />
          </button>
          <div className="flex flex-1 items-center justify-between pl-2">
            <h1 className="text-lg font-semibold text-gray-900">FrankenPanel</h1>
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-600">{user?.username}</span>
              <button
                onClick={logout}
                className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 hover:text-gray-700"
                title="Log out"
              >
                <LogOut className="h-5 w-5" />
              </button>
            </div>
          </div>
        </header>

        <main className="flex-1">
          <div className="py-6">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
              <Outlet />
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

function SidebarContent({
  navigation,
  isActive,
  onClose,
}: {
  navigation: Array<{ name: string; href: string; icon: React.ComponentType<{ className?: string }> }>
  isActive: (path: string) => boolean
  onClose?: () => void
}) {
  const { user } = useAuth()

  return (
    <div className="flex flex-1 flex-col overflow-y-auto pt-5 pb-4">
      <div className="flex flex-shrink-0 items-center justify-between px-4">
        <span className="text-lg font-semibold text-white">FrankenPanel</span>
        {onClose && (
          <button
            onClick={onClose}
            className="rounded-lg p-2 text-slate-400 hover:bg-white/10 hover:text-white"
            aria-label="Close menu"
          >
            <X className="h-5 w-5" />
          </button>
        )}
      </div>
      <nav className="mt-6 flex-1 space-y-0.5 px-3">
        {navigation.map((item) => {
          if (item.href === '/audit' && !user?.is_superuser) return null
          const active = isActive(item.href)
          return (
            <Link
              key={item.name}
              to={item.href}
              onClick={onClose}
              className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition ${
                active
                  ? 'bg-white/15 text-white'
                  : 'text-slate-400 hover:bg-white/10 hover:text-white'
              }`}
            >
              <item.icon className="h-5 w-5 flex-shrink-0" />
              {item.name}
            </Link>
          )
        })}
      </nav>
    </div>
  )
}
