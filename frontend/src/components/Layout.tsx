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
  X
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

  const isActive = (path: string) => location.pathname === path || location.pathname.startsWith(path + '/')

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar */}
      <div className={`fixed inset-0 z-40 lg:hidden ${sidebarOpen ? '' : 'hidden'}`}>
        <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setSidebarOpen(false)}></div>
        <div className="fixed inset-y-0 left-0 w-64 bg-white shadow-lg">
          <SidebarContent navigation={navigation} isActive={isActive} onClose={() => setSidebarOpen(false)} />
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-grow bg-white border-r border-gray-200">
          <SidebarContent navigation={navigation} isActive={isActive} />
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64 flex flex-col flex-1">
        {/* Top bar */}
        <div className="sticky top-0 z-10 flex-shrink-0 flex h-16 bg-white shadow">
          <button
            type="button"
            className="px-4 border-r border-gray-200 text-gray-500 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500 lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-6 w-6" />
          </button>
          <div className="flex-1 flex justify-between px-4">
            <div className="flex-1 flex">
              <h1 className="text-2xl font-semibold text-gray-900 self-center">FrankenPanel</h1>
            </div>
            <div className="ml-4 flex items-center md:ml-6">
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-700">{user?.username}</span>
                <button
                  onClick={logout}
                  className="p-2 text-gray-400 hover:text-gray-500"
                  title="Logout"
                >
                  <LogOut className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="flex-1">
          <div className="py-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
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
  onClose 
}: { 
  navigation: Array<{ name: string; href: string; icon: any }>
  isActive: (path: string) => boolean
  onClose?: () => void
}) {
  const { user } = useAuth()

  return (
    <div className="flex flex-col flex-grow pt-5 pb-4 overflow-y-auto">
      <div className="flex items-center flex-shrink-0 px-4">
        <h2 className="text-xl font-bold text-gray-900">FrankenPanel</h2>
        {onClose && (
          <button
            onClick={onClose}
            className="ml-auto p-2 text-gray-400 hover:text-gray-500"
          >
            <X className="h-6 w-6" />
          </button>
        )}
      </div>
      <nav className="mt-5 flex-1 px-2 space-y-1">
        {navigation.map((item) => {
          // Hide audit logs for non-superusers
          if (item.href === '/audit' && !user?.is_superuser) {
            return null
          }
          
          return (
            <Link
              key={item.name}
              to={item.href}
              onClick={onClose}
              className={`${
                isActive(item.href)
                  ? 'bg-indigo-50 text-indigo-600'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              } group flex items-center px-2 py-2 text-sm font-medium rounded-md`}
            >
              <item.icon
                className={`${
                  isActive(item.href) ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-500'
                } mr-3 flex-shrink-0 h-6 w-6`}
              />
              {item.name}
            </Link>
          )
        })}
      </nav>
    </div>
  )
}
