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
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Domains</h1>
          <p className="mt-2 text-sm text-gray-600">Manage domain mappings</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
        >
          <Plus className="h-5 w-5 mr-2" />
          Add Domain
        </button>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {domains?.map((domain) => (
            <li key={domain.id}>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Globe className="h-8 w-8 text-gray-400" />
                    <div className="ml-4">
                      <div className="text-sm font-medium text-gray-900">{domain.domain}</div>
                      <div className="mt-2 flex items-center text-sm text-gray-500">
                        <span className="capitalize">{domain.domain_type}</span>
                        {domain.ssl_enabled && (
                          <>
                            <span className="mx-2">•</span>
                            <span className="text-green-600">SSL Enabled</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        domain.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
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
        {domains?.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No domains found. Add a domain to get started.</p>
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
    mutationFn: (data: any) => api.post('/domains/', data),
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
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Add Domain</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Domain</label>
            <input
              type="text"
              required
              placeholder="example.com"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              value={formData.domain}
              onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
            />
          </div>
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
            <label className="block text-sm font-medium text-gray-700">Domain Type</label>
            <select
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              value={formData.domain_type}
              onChange={(e) => setFormData({ ...formData, domain_type: e.target.value })}
            >
              <option value="primary">Primary</option>
              <option value="alias">Alias</option>
              <option value="subdomain">Subdomain</option>
            </select>
          </div>
          <div className="flex items-center">
            <input
              type="checkbox"
              checked={formData.ssl_enabled}
              onChange={(e) => setFormData({ ...formData, ssl_enabled: e.target.checked })}
              className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
            <label className="ml-2 block text-sm text-gray-900">Enable SSL</label>
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
              {createMutation.isPending ? 'Adding...' : 'Add'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
