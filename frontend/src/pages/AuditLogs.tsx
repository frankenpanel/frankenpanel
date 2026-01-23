import { useQuery } from '@tanstack/react-query'
import api from '../services/api'
import { FileText } from 'lucide-react'

interface AuditLog {
  id: number
  username: string | null
  action: string
  resource_type: string | null
  resource_id: number | null
  ip_address: string | null
  success: boolean
  created_at: string
}

export default function AuditLogs() {
  const { data: logs, isLoading } = useQuery<AuditLog[]>({
    queryKey: ['audit-logs'],
    queryFn: async () => {
      const response = await api.get('/audit/')
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
        <h1 className="text-3xl font-bold text-gray-900">Audit Logs</h1>
        <p className="mt-2 text-sm text-gray-600">System activity and security logs</p>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {logs?.map((log) => (
            <li key={log.id}>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <FileText className="h-6 w-6 text-gray-400" />
                    <div className="ml-4">
                      <div className="text-sm font-medium text-gray-900">
                        {log.action.toUpperCase()} {log.resource_type || ''}
                        {log.resource_id && ` #${log.resource_id}`}
                      </div>
                      <div className="mt-2 flex items-center text-sm text-gray-500">
                        <span>{log.username || 'System'}</span>
                        {log.ip_address && (
                          <>
                            <span className="mx-2">•</span>
                            <span>{log.ip_address}</span>
                          </>
                        )}
                        <span className="mx-2">•</span>
                        <span>{new Date(log.created_at).toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        log.success
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {log.success ? 'Success' : 'Failed'}
                    </span>
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ul>
        {logs?.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No audit logs found.</p>
          </div>
        )}
      </div>
    </div>
  )
}
