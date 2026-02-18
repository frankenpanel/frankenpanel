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
        return 'bg-emerald-50 text-emerald-700'
      case 'inactive':
        return 'bg-gray-100 text-gray-700'
      case 'suspended':
        return 'bg-red-50 text-red-700'
      default:
        return 'bg-amber-50 text-amber-700'
    }
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
          <h1 className="text-2xl font-semibold text-gray-900">Sites</h1>
          <p className="mt-1 text-sm text-gray-500">Manage your PHP sites</p>
        </div>
        <button onClick={() => setShowCreateModal(true)} className="btn-primary">
          <Plus className="h-5 w-5 mr-2" />
          Create site
        </button>
      </div>

      <div className="card-stripe overflow-hidden">
        <ul className="divide-y divide-stripe-border">
          {sites?.map((site) => (
            <li key={site.id}>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-stripe-primary/10">
                      <span className="text-sm font-semibold text-stripe-primary">
                        {site.name.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <Link
                          to={`/sites/${site.id}`}
                          className="text-sm font-medium text-gray-900 hover:text-stripe-primary"
                        >
                          {site.name}
                        </Link>
                        <span className="rounded-md bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600">
                          {site.site_type}
                        </span>
                      </div>
                      <div className="mt-1 flex items-center gap-2 text-sm text-gray-500">
                        <span>PHP {site.php_version}</span>
                        <span>·</span>
                        <span>{new Date(site.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span
                      className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ${getStatusColor(
                        site.status
                      )}`}
                    >
                      {site.status}
                    </span>
                    {site.status === 'active' ? (
                      <button
                        onClick={() => stopMutation.mutate(site.id)}
                        className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 hover:text-gray-700"
                        title="Stop"
                      >
                        <Square className="h-5 w-5" />
                      </button>
                    ) : (
                      <button
                        onClick={() => startMutation.mutate(site.id)}
                        className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 hover:text-gray-700"
                        title="Start"
                      >
                        <Play className="h-5 w-5" />
                      </button>
                    )}
                    <Link
                      to={`/sites/${site.id}`}
                      className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 hover:text-gray-700"
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
        {sites?.length === 0 && (
          <div className="py-12 text-center">
            <p className="text-sm text-gray-500">No sites yet. Create your first site to get started.</p>
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
    site_type: 'custom_php' as 'wordpress' | 'custom_php' | 'joomla',
    domain: '',
    php_version: '8.2',
    create_database: true,
    wp_site_title: '',
    wp_admin_user: '',
    wp_admin_password: '',
    wp_admin_email: '',
  })
  const queryClient = useQueryClient()
  const isWordPress = formData.site_type === 'wordpress'

  const createMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => api.post('/sites/', { site_data: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sites'] })
      onClose()
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const payload: Record<string, unknown> = {
      name: formData.name,
      site_type: formData.site_type,
      domain: formData.domain,
      php_version: formData.php_version,
      create_database: isWordPress ? true : formData.create_database,
    }
    if (isWordPress) {
      payload.wp_site_title = formData.wp_site_title
      payload.wp_admin_user = formData.wp_admin_user
      payload.wp_admin_password = formData.wp_admin_password
      payload.wp_admin_email = formData.wp_admin_email
    }
    createMutation.mutate(payload)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/40 p-4 pt-20">
      <div className="card-stripe w-full max-w-md p-6 shadow-stripe-lg">
        <h3 className="text-lg font-semibold text-gray-900">Create new site</h3>
        <p className="mt-1 text-sm text-gray-500">
          {isWordPress ? 'WordPress will be installed and set live on the domain.' : 'Create site with name, domain, and PHP version.'}
        </p>
        <form onSubmit={handleSubmit} className="mt-5 space-y-4">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-700">Site name</label>
            <input
              type="text"
              required
              className="input-stripe"
              placeholder="e.g. my-site"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-700">Domain</label>
            <input
              type="text"
              required
              className="input-stripe"
              placeholder="example.com"
              value={formData.domain}
              onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
            />
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-700">Site type</label>
            <select
              className="input-stripe"
              value={formData.site_type}
              onChange={(e) => setFormData({ ...formData, site_type: e.target.value as 'wordpress' | 'custom_php' | 'joomla' })}
            >
              <option value="custom_php">Custom PHP</option>
              <option value="wordpress">WordPress</option>
              <option value="joomla">Joomla</option>
            </select>
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-700">PHP version</label>
            <select
              className="input-stripe"
              value={formData.php_version}
              onChange={(e) => setFormData({ ...formData, php_version: e.target.value })}
            >
              <option value="8.2">8.2</option>
              <option value="8.1">8.1</option>
              <option value="8.0">8.0</option>
            </select>
          </div>

          {!isWordPress && (
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={formData.create_database}
                onChange={(e) => setFormData({ ...formData, create_database: e.target.checked })}
                className="h-4 w-4 rounded border-stripe-border text-stripe-primary focus:ring-stripe-primary"
              />
              <label className="text-sm text-gray-700">Create database automatically</label>
            </div>
          )}

          {isWordPress && (
            <>
              <div className="border-t border-stripe-border pt-4 mt-2">
                <p className="text-sm font-medium text-gray-900 mb-3">WordPress setup (auto-install)</p>
                <p className="text-xs text-gray-500 mb-3">Database and admin user will be created. Site will be started on the domain.</p>
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-gray-700">Site title</label>
                <input
                  type="text"
                  required={isWordPress}
                  className="input-stripe"
                  placeholder="My WordPress Site"
                  value={formData.wp_site_title}
                  onChange={(e) => setFormData({ ...formData, wp_site_title: e.target.value })}
                />
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-gray-700">Admin username</label>
                <input
                  type="text"
                  required={isWordPress}
                  className="input-stripe"
                  placeholder="admin"
                  value={formData.wp_admin_user}
                  onChange={(e) => setFormData({ ...formData, wp_admin_user: e.target.value })}
                />
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-gray-700">Admin password</label>
                <input
                  type="password"
                  required={isWordPress}
                  className="input-stripe"
                  placeholder="••••••••"
                  value={formData.wp_admin_password}
                  onChange={(e) => setFormData({ ...formData, wp_admin_password: e.target.value })}
                />
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-gray-700">Admin email</label>
                <input
                  type="email"
                  required={isWordPress}
                  className="input-stripe"
                  placeholder="admin@example.com"
                  value={formData.wp_admin_email}
                  onChange={(e) => setFormData({ ...formData, wp_admin_email: e.target.value })}
                />
              </div>
            </>
          )}

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
