import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import api from '../services/api'
import { Database as DatabaseIcon } from 'lucide-react'

interface Database {
  id: number
  name: string
  db_type: string
  site_id: number
  username: string
  host: string
  port: number
  created_at: string
}

export default function Databases() {
  const [searchParams] = useSearchParams()
  const siteId = searchParams.get('site_id')

  const { data: databases, isLoading } = useQuery<Database[]>({
    queryKey: ['databases', siteId],
    queryFn: async () => {
      const params = siteId ? { site_id: siteId } : {}
      const response = await api.get('/databases/', { params })
      return response.data
    },
  })

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
        <h1 className="text-2xl font-semibold text-gray-900">Databases</h1>
        <p className="mt-1 text-sm text-gray-500">Manage MySQL/MariaDB databases</p>
      </div>

      <div className="card-stripe overflow-hidden">
        <ul className="divide-y divide-stripe-border">
          {databases?.map((db) => (
            <li key={db.id}>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center gap-4">
                  <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-stripe-primary/10">
                    <DatabaseIcon className="h-5 w-5 text-stripe-primary" />
                  </div>
                  <div>
                    <div className="text-sm font-medium text-gray-900">{db.name}</div>
                    <div className="mt-1 flex items-center gap-2 text-sm text-gray-500">
                      <span>{db.username}@{db.host}:{db.port}</span>
                      <span>·</span>
                      <span className="capitalize">{db.db_type}</span>
                    </div>
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ul>
        {databases?.length === 0 && (
          <div className="py-12 text-center">
            <p className="text-sm text-gray-500">No databases found.</p>
          </div>
        )}
      </div>
    </div>
  )
}
