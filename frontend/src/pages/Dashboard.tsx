import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import api from '../services/api'
import { Globe, Database, Link as LinkIcon, HardDrive, Activity, ArrowRight } from 'lucide-react'

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
    { name: 'Sites', value: stats?.sites ?? 0, icon: Globe, href: '/sites' },
    { name: 'Databases', value: stats?.databases ?? 0, icon: Database, href: '/databases' },
    { name: 'Domains', value: stats?.domains ?? 0, icon: LinkIcon, href: '/domains' },
    { name: 'Backups', value: stats?.backups ?? 0, icon: HardDrive, href: '/backups' },
  ]

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-2 border-stripe-border border-t-stripe-primary" />
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">Overview of your FrankenPanel instance</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((card) => (
          <Link
            key={card.name}
            to={card.href}
            className="card-stripe p-5 transition hover:shadow-stripe-lg"
          >
            <div className="flex items-center gap-4">
              <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-stripe-primary/10">
                <card.icon className="h-5 w-5 text-stripe-primary" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-gray-500">{card.name}</p>
                <p className="text-xl font-semibold text-gray-900">{card.value}</p>
              </div>
            </div>
          </Link>
        ))}
      </div>

      <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="card-stripe p-6">
          <h3 className="text-base font-semibold text-gray-900">Quick actions</h3>
          <ul className="mt-4 space-y-2">
            <li>
              <Link
                to="/sites"
                className="flex items-center justify-between text-sm text-stripe-primary hover:underline"
              >
                Create a new site
                <ArrowRight className="h-4 w-4" />
              </Link>
            </li>
            <li>
              <Link
                to="/backups"
                className="flex items-center justify-between text-sm text-stripe-primary hover:underline"
              >
                Create a backup
                <ArrowRight className="h-4 w-4" />
              </Link>
            </li>
            <li>
              <Link
                to="/domains"
                className="flex items-center justify-between text-sm text-stripe-primary hover:underline"
              >
                Add a domain
                <ArrowRight className="h-4 w-4" />
              </Link>
            </li>
          </ul>
        </div>
        <div className="card-stripe p-6">
          <h3 className="text-base font-semibold text-gray-900">System status</h3>
          <ul className="mt-4 space-y-3">
            <li className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Backend API</span>
              <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700">
                <Activity className="h-3.5 w-3.5" />
                Online
              </span>
            </li>
            <li className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Database</span>
              <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700">
                <Activity className="h-3.5 w-3.5" />
                Connected
              </span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}
