import { useQuery } from '@tanstack/react-query'
import api from '../services/api'
import { Globe, Database, Link as LinkIcon, HardDrive, TrendingUp, Activity } from 'lucide-react'

interface Stats {
  sites: number
  databases: number
  domains: number
  backups: number
}

export default function Dashboard() {
  const { data: stats, isLoading } = useQuery<Stats>({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const [sitesRes, databasesRes, domainsRes, backupsRes] = await Promise.all([
        api.get('/sites/'),
        api.get('/databases/'),
        api.get('/domains/'),
        api.get('/backups/'),
      ])
      return {
        sites: sitesRes.data.length,
        databases: databasesRes.data.length,
        domains: domainsRes.data.length,
        backups: backupsRes.data.length,
      }
    },
  })

  const statCards = [
    {
      name: 'Total Sites',
      value: stats?.sites || 0,
      icon: Globe,
      color: 'bg-blue-500',
    },
    {
      name: 'Databases',
      value: stats?.databases || 0,
      icon: Database,
      color: 'bg-green-500',
    },
    {
      name: 'Domains',
      value: stats?.domains || 0,
      icon: LinkIcon,
      color: 'bg-purple-500',
    },
    {
      name: 'Backups',
      value: stats?.backups || 0,
      icon: HardDrive,
      color: 'bg-orange-500',
    },
  ]

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-sm text-gray-600">Overview of your FrankenPanel instance</p>
      </div>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((card) => (
          <div
            key={card.name}
            className="bg-white overflow-hidden shadow rounded-lg"
          >
            <div className="p-5">
              <div className="flex items-center">
                <div className={`${card.color} rounded-md p-3`}>
                  <card.icon className="h-6 w-6 text-white" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      {card.name}
                    </dt>
                    <dd className="text-lg font-semibold text-gray-900">
                      {card.value}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8 grid grid-cols-1 gap-5 lg:grid-cols-2">
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <a
              href="/sites"
              className="block text-sm text-indigo-600 hover:text-indigo-800"
            >
              → Create a new site
            </a>
            <a
              href="/backups"
              className="block text-sm text-indigo-600 hover:text-indigo-800"
            >
              → Create a backup
            </a>
            <a
              href="/domains"
              className="block text-sm text-indigo-600 hover:text-indigo-800"
            >
              → Add a domain
            </a>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">System Status</h3>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Backend API</span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                <Activity className="h-3 w-3 mr-1" />
                Online
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Database</span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                <Activity className="h-3 w-3 mr-1" />
                Connected
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
