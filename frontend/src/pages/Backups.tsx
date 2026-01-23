import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import api from '../services/api'
import { HardDrive, Plus, Download, Trash2, RotateCcw } from 'lucide-react'
import { useState } from 'react'

interface Backup {
  id: number
  site_id: number
  backup_type: string
  status: string
  file_path: string
  file_size: number
  encrypted: boolean
  created_at: string
  completed_at: string | null
}

export default function Backups() {
  const [searchParams] = useSearchParams()
  const siteId = searchParams.get('site_id')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const queryClient = useQueryClient()

  const { data: backups, isLoading } = useQuery<Backup[]>({
    queryKey: ['backups', siteId],
    queryFn: async () => {
      const params = siteId ? { site_id: siteId } : {}
      const response = await api.get('/backups/', { params })
      return response.data
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/backups/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['backups'] })
    },
  })

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Backups</h1>
          <p className="mt-2 text-sm text-gray-600">Manage site and database backups</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
        >
          <Plus className="h-5 w-5 mr-2" />
          Create Backup
        </button>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {backups?.map((backup) => (
            <li key={backup.id}>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <HardDrive className="h-8 w-8 text-gray-400" />
                    <div className="ml-4">
                      <div className="text-sm font-medium text-gray-900">
                        Backup #{backup.id} - {backup.backup_type}
                      </div>
                      <div className="mt-2 flex items-center text-sm text-gray-500">
                        <span>{formatFileSize(backup.file_size || 0)}</span>
                        {backup.encrypted && (
                          <>
                            <span className="mx-2">•</span>
                            <span>Encrypted</span>
                          </>
                        )}
                        <span className="mx-2">•</span>
                        <span>{new Date(backup.created_at).toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        backup.status === 'completed'
                          ? 'bg-green-100 text-green-800'
                          : backup.status === 'failed'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}
                    >
                      {backup.status}
                    </span>
                    {backup.status === 'completed' && (
                      <button
                        className="text-indigo-400 hover:text-indigo-600"
                        title="Restore"
                      >
                        <RotateCcw className="h-5 w-5" />
                      </button>
                    )}
                    <button
                      onClick={() => {
                        if (confirm('Are you sure you want to delete this backup?')) {
                          deleteMutation.mutate(backup.id)
                        }
                      }}
                      className="text-red-400 hover:text-red-600"
                      title="Delete"
                    >
                      <Trash2 className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ul>
        {backups?.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No backups found. Create a backup to get started.</p>
          </div>
        )}
      </div>

      {showCreateModal && (
        <CreateBackupModal
          siteId={siteId ? parseInt(siteId) : undefined}
          onClose={() => setShowCreateModal(false)}
        />
      )}
    </div>
  )
}

function CreateBackupModal({
  siteId,
  onClose,
}: {
  siteId?: number
  onClose: () => void
}) {
  const [formData, setFormData] = useState({
    site_id: siteId || '',
    backup_type: 'full',
    description: '',
  })
  const queryClient = useQueryClient()

  const createMutation = useMutation({
    mutationFn: (data: any) => api.post('/backups/', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['backups'] })
      onClose()
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate(formData)
  }

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Create Backup</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          {!siteId && (
            <div>
              <label className="block text-sm font-medium text-gray-700">Site ID</label>
              <input
                type="number"
                required
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                value={formData.site_id}
                onChange={(e) => setFormData({ ...formData, site_id: parseInt(e.target.value) })}
              />
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-gray-700">Backup Type</label>
            <select
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              value={formData.backup_type}
              onChange={(e) => setFormData({ ...formData, backup_type: e.target.value })}
            >
              <option value="full">Full (Site + Database)</option>
              <option value="site_only">Site Only</option>
              <option value="database_only">Database Only</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Description</label>
            <textarea
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              rows={3}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />
          </div>
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
            >
              {createMutation.isPending ? 'Creating...' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
