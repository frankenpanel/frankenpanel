import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import api from '../services/api'
import { Plus, Trash2, Globe } from 'lucide-react'
import { useState } from 'react'

interface Domain {
  id: number
  domain: string
  domain_type: string
  site_id: number
  ssl_enabled: boolean
  is_active: boolean
  created_at: string
}

export default function Domains() {
  const [searchParams] = useSearchParams()
  const siteId = searchParams.get('site_id')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const queryClient = useQueryClient()

  const { data: domains, isLoading } = useQuery<Domain[]>({
    queryKey: ['domains', siteId],
    queryFn: async () => {
      const params = siteId ? { site_id: siteId } : {}
      const response = await api.get('/domains/', { params })
      return response.data
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/domains/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['domains'] })
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
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Domains</h1>
          <p className="mt-1 text-sm text-gray-500">Manage domain mappings</p>
        </div>
        <button onClick={() => setShowCreateModal(true)} className="btn-primary">
          <Plus className="mr-2 h-5 w-5" />
          Add domain
        </button>
      </div>

      <div className="card-stripe overflow-hidden">
        <ul className="divide-y divide-stripe-border">
          {domains?.map((domain) => (
            <li key={domain.id}>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-stripe-primary/10">
                      <Globe className="h-5 w-5 text-stripe-primary" />
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-900">{domain.domain}</div>
                      <div className="mt-1 flex items-center gap-2 text-sm text-gray-500">
                        <span className="capitalize">{domain.domain_type}</span>
                        {domain.ssl_enabled && (
                          <>
                            <span>·</span>
                            <span className="text-emerald-600">SSL enabled</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span
                      className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${
                        domain.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-gray-100 text-gray-600'
                      }`}
                    >
                      {domain.is_active ? 'Active' : 'Inactive'}
                    </span>
                    <button
                      onClick={() => {
                        if (confirm('Are you sure you want to delete this domain?')) {
                          deleteMutation.mutate(domain.id)
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
        {domains?.length === 0 && (
          <div className="py-12 text-center">
            <p className="text-sm text-gray-500">No domains found. Add a domain to get started.</p>
          </div>
        )}
      </div>

      {showCreateModal && (
        <CreateDomainModal
          siteId={siteId ? parseInt(siteId) : undefined}
          onClose={() => setShowCreateModal(false)}
        />
      )}
    </div>
  )
}

function CreateDomainModal({
  siteId,
  onClose,
}: {
  siteId?: number
  onClose: () => void
}) {
  const [formData, setFormData] = useState({
    domain: '',
    site_id: siteId || '',
    domain_type: 'primary',
    ssl_enabled: true,
  })
  const queryClient = useQueryClient()

  const createMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => api.post('/domains/', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['domains'] })
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
        <h3 className="text-lg font-semibold text-gray-900">Add domain</h3>
        <form onSubmit={handleSubmit} className="mt-5 space-y-4">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-700">Domain</label>
            <input
              type="text"
              required
              placeholder="example.com"
              className="input-stripe"
              value={formData.domain}
              onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
            />
          </div>
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
            <label className="mb-1.5 block text-sm font-medium text-gray-700">Domain type</label>
            <select
              className="input-stripe"
              value={formData.domain_type}
              onChange={(e) => setFormData({ ...formData, domain_type: e.target.value })}
            >
              <option value="primary">Primary</option>
              <option value="alias">Alias</option>
              <option value="subdomain">Subdomain</option>
            </select>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={formData.ssl_enabled}
              onChange={(e) => setFormData({ ...formData, ssl_enabled: e.target.checked })}
              className="h-4 w-4 rounded border-stripe-border text-stripe-primary focus:ring-stripe-primary"
            />
            <label className="text-sm text-gray-700">Enable SSL</label>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" disabled={createMutation.isPending} className="btn-primary">
              {createMutation.isPending ? 'Adding…' : 'Add'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
