import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import api from '../services/api'
import { HardDrive, Plus, Trash2, RotateCcw } from 'lucide-react'
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
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
  }

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-2 border-stripe-border border-t-stripe-primary" />
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Backups</h1>
          <p className="mt-1 text-sm text-gray-500">Manage site and database backups</p>
        </div>
        <button onClick={() => setShowCreateModal(true)} className="btn-primary">
          <Plus className="mr-2 h-5 w-5" />
          Create backup
        </button>
      </div>

      <div className="card-stripe overflow-hidden">
        <ul className="divide-y divide-stripe-border">
          {backups?.map((backup) => (
            <li key={backup.id}>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-stripe-primary/10">
                      <HardDrive className="h-5 w-5 text-stripe-primary" />
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        Backup #{backup.id} · {backup.backup_type}
                      </div>
                      <div className="mt-1 flex items-center gap-2 text-sm text-gray-500">
                        <span>{formatFileSize(backup.file_size || 0)}</span>
                        {backup.encrypted && (
                          <>
                            <span>·</span>
                            <span>Encrypted</span>
                          </>
                        )}
                        <span>·</span>
                        <span>{new Date(backup.created_at).toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span
                      className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${
                        backup.status === 'completed'
                          ? 'bg-emerald-50 text-emerald-700'
                          : backup.status === 'failed'
                            ? 'bg-red-50 text-red-700'
                            : 'bg-amber-50 text-amber-700'
                      }`}
                    >
                      {backup.status}
                    </span>
                    {backup.status === 'completed' && (
                      <button
                        className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 hover:text-gray-700"
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
                      className="rounded-lg p-2 text-red-500 hover:bg-red-50 hover:text-red-700"
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
          <div className="py-12 text-center">
            <p className="text-sm text-gray-500">No backups found. Create a backup to get started.</p>
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
    mutationFn: (data: Record<string, unknown>) => api.post('/backups/', data),
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
    <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/40 p-4 pt-20">
      <div className="card-stripe w-full max-w-md p-6 shadow-stripe-lg">
        <h3 className="text-lg font-semibold text-gray-900">Create backup</h3>
        <form onSubmit={handleSubmit} className="mt-5 space-y-4">
          {!siteId && (
            <div>
              <label className="mb-1.5 block text-sm font-medium text-gray-700">Site ID</label>
              <input
                type="number"
                required
                className="input-stripe"
                value={formData.site_id}
                onChange={(e) => setFormData({ ...formData, site_id: parseInt(e.target.value) || '' })}
              />
            </div>
          )}
          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-700">Backup type</label>
            <select
              className="input-stripe"
              value={formData.backup_type}
              onChange={(e) => setFormData({ ...formData, backup_type: e.target.value })}
            >
              <option value="full">Full (Site + Database)</option>
              <option value="site_only">Site only</option>
              <option value="database_only">Database only</option>
            </select>
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-700">Description</label>
            <textarea
              className="input-stripe min-h-[80px] resize-y"
              rows={3}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" disabled={createMutation.isPending} className="btn-primary">
              {createMutation.isPending ? 'Creating…' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
