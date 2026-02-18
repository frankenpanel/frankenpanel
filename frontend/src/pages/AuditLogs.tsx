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
      <div className="flex h-64 items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-2 border-stripe-border border-t-stripe-primary" />
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-gray-900">Audit logs</h1>
        <p className="mt-1 text-sm text-gray-500">System activity and security logs</p>
      </div>

      <div className="card-stripe overflow-hidden">
        <ul className="divide-y divide-stripe-border">
          {logs?.map((log) => (
            <li key={log.id}>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-gray-100">
                      <FileText className="h-5 w-5 text-gray-500" />
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {log.action.toUpperCase()} {log.resource_type || ''}
                        {log.resource_id != null && ` #${log.resource_id}`}
                      </div>
                      <div className="mt-1 flex items-center gap-2 text-sm text-gray-500">
                        <span>{log.username || 'System'}</span>
                        {log.ip_address && (
                          <>
                            <span>·</span>
                            <span>{log.ip_address}</span>
                          </>
                        )}
                        <span>·</span>
                        <span>{new Date(log.created_at).toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                  <span
                    className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${
                      log.success ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'
                    }`}
                  >
                    {log.success ? 'Success' : 'Failed'}
                  </span>
                </div>
              </div>
            </li>
          ))}
        </ul>
        {logs?.length === 0 && (
          <div className="py-12 text-center">
            <p className="text-sm text-gray-500">No audit logs found.</p>
          </div>
        )}
      </div>
    </div>
  )
}
