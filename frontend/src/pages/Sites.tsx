import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import api from '../services/api'
import { Plus, Play, Square, Trash2, Edit } from 'lucide-react'
import { useState } from 'react'

interface Site {
  id: number
  name: string
  slug: string
  site_type: string
  status: string
  php_version: string
  created_at: string
}

export default function Sites() {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const queryClient = useQueryClient()

  const { data: sites, isLoading } = useQuery<Site[]>({
    queryKey: ['sites'],
    queryFn: async () => {
      const response = await api.get('/sites/')
      return response.data
    },
  })

  const startMutation = useMutation({
    mutationFn: (id: number) => api.post(`/sites/${id}/start`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sites'] })
    },
  })

  const stopMutation = useMutation({
    mutationFn: (id: number) => api.post(`/sites/${id}/stop`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sites'] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/sites/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sites'] })
    },
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'inactive':
        return 'bg-gray-100 text-gray-800'
      case 'suspended':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-yellow-100 text-yellow-800'
    }
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
          <h1 className="text-3xl font-bold text-gray-900">Sites</h1>
          <p className="mt-2 text-sm text-gray-600">Manage your PHP sites</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
        >
          <Plus className="h-5 w-5 mr-2" />
          Create Site
        </button>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {sites?.map((site) => (
            <li key={site.id}>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
                        <span className="text-indigo-600 font-medium">
                          {site.name.charAt(0).toUpperCase()}
                        </span>
                      </div>
                    </div>
                    <div className="ml-4">
                      <div className="flex items-center">
                        <Link
                          to={`/sites/${site.id}`}
                          className="text-sm font-medium text-indigo-600 hover:text-indigo-900"
                        >
                          {site.name}
                        </Link>
                        <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                          {site.site_type}
                        </span>
                      </div>
                      <div className="mt-2 flex items-center text-sm text-gray-500">
                        <span>PHP {site.php_version}</span>
                        <span className="mx-2">•</span>
                        <span>{new Date(site.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                        site.status
                      )}`}
                    >
                      {site.status}
                    </span>
                    {site.status === 'active' ? (
                      <button
                        onClick={() => stopMutation.mutate(site.id)}
                        className="text-gray-400 hover:text-gray-600"
                        title="Stop"
                      >
                        <Square className="h-5 w-5" />
                      </button>
                    ) : (
                      <button
                        onClick={() => startMutation.mutate(site.id)}
                        className="text-gray-400 hover:text-gray-600"
                        title="Start"
                      >
                        <Play className="h-5 w-5" />
                      </button>
                    )}
                    <Link
                      to={`/sites/${site.id}`}
                      className="text-gray-400 hover:text-gray-600"
                      title="Edit"
                    >
                      <Edit className="h-5 w-5" />
                    </Link>
                    <button
                      onClick={() => {
                        if (confirm('Are you sure you want to delete this site?')) {
                          deleteMutation.mutate(site.id)
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
        {sites?.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No sites yet. Create your first site to get started.</p>
          </div>
        )}
      </div>

      {showCreateModal && (
        <CreateSiteModal onClose={() => setShowCreateModal(false)} />
      )}
    </div>
  )
}

function CreateSiteModal({ onClose }: { onClose: () => void }) {
  const [formData, setFormData] = useState({
    name: '',
    site_type: 'wordpress',
    domain: '',
    php_version: '8.2',
    create_database: true,
  })
  const queryClient = useQueryClient()

  const createMutation = useMutation({
    mutationFn: (data: any) => api.post('/sites/', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sites'] })
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
        <h3 className="text-lg font-bold text-gray-900 mb-4">Create New Site</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Site Name</label>
            <input
              type="text"
              required
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Site Type</label>
            <select
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              value={formData.site_type}
              onChange={(e) => setFormData({ ...formData, site_type: e.target.value })}
            >
              <option value="wordpress">WordPress</option>
              <option value="joomla">Joomla</option>
              <option value="custom_php">Custom PHP</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Domain</label>
            <input
              type="text"
              required
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              value={formData.domain}
              onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">PHP Version</label>
            <select
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              value={formData.php_version}
              onChange={(e) => setFormData({ ...formData, php_version: e.target.value })}
            >
              <option value="8.2">8.2</option>
              <option value="8.1">8.1</option>
              <option value="8.0">8.0</option>
            </select>
          </div>
          <div className="flex items-center">
            <input
              type="checkbox"
              checked={formData.create_database}
              onChange={(e) => setFormData({ ...formData, create_database: e.target.checked })}
              className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
            <label className="ml-2 block text-sm text-gray-900">Create database automatically</label>
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
