import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, useNavigate, Link } from 'react-router-dom'
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
      <div className="flex h-64 items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-2 border-stripe-border border-t-stripe-primary" />
      </div>
    )
  }

  if (!site) {
    return (
      <div className="card-stripe p-6 text-center">
        <p className="text-gray-600">Site not found.</p>
        <button onClick={() => navigate('/sites')} className="btn-secondary mt-4">
          Back to sites
        </button>
      </div>
    )
  }

  return (
    <div>
      <button
        onClick={() => navigate('/sites')}
        className="mb-4 flex items-center text-sm text-gray-500 hover:text-gray-900"
      >
        <ArrowLeft className="mr-1 h-4 w-4" />
        Back to sites
      </button>

      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">{site.name}</h1>
          <p className="mt-1 text-sm text-gray-500">Site details and configuration</p>
        </div>
        <div className="flex gap-2">
          {site.status === 'active' ? (
            <button
              onClick={() => stopMutation.mutate()}
              className="btn-secondary border-red-200 text-red-700 hover:bg-red-50"
            >
              <Square className="mr-2 h-5 w-5" />
              Stop
            </button>
          ) : (
            <button
              onClick={() => startMutation.mutate()}
              className="btn-primary !bg-emerald-600 hover:!bg-emerald-700"
            >
              <Play className="mr-2 h-5 w-5" />
              Start
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="card-stripe p-6">
          <h3 className="text-base font-semibold text-gray-900">Site information</h3>
          <dl className="mt-4 space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">Name</dt>
              <dd className="mt-0.5 text-sm text-gray-900">{site.name}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Slug</dt>
              <dd className="mt-0.5 text-sm text-gray-900">{site.slug}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Type</dt>
              <dd className="mt-0.5 text-sm text-gray-900">{site.site_type}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Status</dt>
              <dd className="mt-0.5">
                <span
                  className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${
                    site.status === 'active' ? 'bg-emerald-50 text-emerald-700' : 'bg-gray-100 text-gray-700'
                  }`}
                >
                  {site.status}
                </span>
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">PHP version</dt>
              <dd className="mt-0.5 text-sm text-gray-900">{site.php_version}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Worker port</dt>
              <dd className="mt-0.5 text-sm text-gray-900">{site.worker_port}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Path</dt>
              <dd className="mt-0.5 font-mono text-sm text-gray-900">{site.path}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Created</dt>
              <dd className="mt-0.5 text-sm text-gray-900">
                {new Date(site.created_at).toLocaleString()}
              </dd>
            </div>
          </dl>
        </div>

        <div className="card-stripe p-6">
          <h3 className="text-base font-semibold text-gray-900">Quick actions</h3>
          <ul className="mt-4 space-y-2">
            <li>
              <Link
                to={`/domains?site_id=${site.id}`}
                className="text-sm text-stripe-primary hover:underline"
              >
                Manage domains →
              </Link>
            </li>
            <li>
              <Link
                to={`/databases?site_id=${site.id}`}
                className="text-sm text-stripe-primary hover:underline"
              >
                View databases →
              </Link>
            </li>
            <li>
              <Link
                to={`/backups?site_id=${site.id}`}
                className="text-sm text-stripe-primary hover:underline"
              >
                Create backup →
              </Link>
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}
