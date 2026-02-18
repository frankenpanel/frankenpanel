import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../services/api'
import { ArrowLeft, Play, Square } from 'lucide-react'

interface Site {
  id: number
  name: string
  slug: string
  site_type: string
  status: string
  php_version: string
  path: string
  worker_port: number
  created_at: string
}

export default function SiteDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data: site, isLoading } = useQuery<Site>({
    queryKey: ['site', id],
    queryFn: async () => {
      const response = await api.get(`/sites/${id}`)
      return response.data
    },
  })

  const startMutation = useMutation({
    mutationFn: () => api.post(`/sites/${id}/start`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['site', id] })
    },
  })

  const stopMutation = useMutation({
    mutationFn: () => api.post(`/sites/${id}/stop`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['site', id] })
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  if (!site) {
    return <div>Site not found</div>
  }

  return (
    <div>
      <button
        onClick={() => navigate('/sites')}
        className="mb-4 text-sm text-gray-600 hover:text-gray-900 flex items-center"
      >
        <ArrowLeft className="h-4 w-4 mr-1" />
        Back to Sites
      </button>

      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{site.name}</h1>
          <p className="mt-2 text-sm text-gray-600">Site details and configuration</p>
        </div>
        <div className="flex space-x-2">
          {site.status === 'active' ? (
            <button
              onClick={() => stopMutation.mutate()}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700"
            >
              <Square className="h-5 w-5 mr-2" />
              Stop
            </button>
          ) : (
            <button
              onClick={() => startMutation.mutate()}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
            >
              <Play className="h-5 w-5 mr-2" />
              Start
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Site Information</h3>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">Name</dt>
              <dd className="mt-1 text-sm text-gray-900">{site.name}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Slug</dt>
              <dd className="mt-1 text-sm text-gray-900">{site.slug}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Type</dt>
              <dd className="mt-1 text-sm text-gray-900">{site.site_type}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Status</dt>
              <dd className="mt-1">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  site.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                }`}>
                  {site.status}
                </span>
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">PHP Version</dt>
              <dd className="mt-1 text-sm text-gray-900">{site.php_version}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Worker Port</dt>
              <dd className="mt-1 text-sm text-gray-900">{site.worker_port}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Path</dt>
              <dd className="mt-1 text-sm text-gray-900 font-mono">{site.path}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Created</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {new Date(site.created_at).toLocaleString()}
              </dd>
            </div>
          </dl>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <a
              href={`/domains?site_id=${site.id}`}
              className="block text-sm text-indigo-600 hover:text-indigo-800"
            >
              → Manage domains
            </a>
            <a
              href={`/databases?site_id=${site.id}`}
              className="block text-sm text-indigo-600 hover:text-indigo-800"
            >
              → View databases
            </a>
            <a
              href={`/backups?site_id=${site.id}`}
              className="block text-sm text-indigo-600 hover:text-indigo-800"
            >
              → Create backup
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
