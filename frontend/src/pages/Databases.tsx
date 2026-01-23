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
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Databases</h1>
        <p className="mt-2 text-sm text-gray-600">Manage MySQL/MariaDB databases</p>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {databases?.map((db) => (
            <li key={db.id}>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <DatabaseIcon className="h-8 w-8 text-gray-400" />
                    <div className="ml-4">
                      <div className="text-sm font-medium text-gray-900">{db.name}</div>
                      <div className="mt-2 flex items-center text-sm text-gray-500">
                        <span>{db.username}@{db.host}:{db.port}</span>
                        <span className="mx-2">•</span>
                        <span className="capitalize">{db.db_type}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ul>
        {databases?.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No databases found.</p>
          </div>
        )}
      </div>
    </div>
  )
}
