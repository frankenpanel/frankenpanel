import { useQuery } from '@tanstack/react-query'
import api from '../services/api'
import { Users as UsersIcon, Shield } from 'lucide-react'

interface User {
  id: number
  username: string
  email: string
  full_name: string | null
  is_active: boolean
  is_superuser: boolean
  created_at: string
}

export default function Users() {
  const { data: users, isLoading } = useQuery<User[]>({
    queryKey: ['users'],
    queryFn: async () => {
      const response = await api.get('/users/')
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
        <h1 className="text-2xl font-semibold text-gray-900">Users</h1>
        <p className="mt-1 text-sm text-gray-500">Manage user accounts and permissions</p>
      </div>

      <div className="card-stripe overflow-hidden">
        <ul className="divide-y divide-stripe-border">
          {users?.map((user) => (
            <li key={user.id}>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-stripe-primary/10">
                      <UsersIcon className="h-5 w-5 text-stripe-primary" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-gray-900">{user.username}</span>
                        {user.is_superuser && (
                          <Shield className="h-4 w-4 text-amber-500" title="Superuser" />
                        )}
                      </div>
                      <div className="mt-1 flex items-center gap-2 text-sm text-gray-500">
                        <span>{user.email}</span>
                        {user.full_name && (
                          <>
                            <span>·</span>
                            <span>{user.full_name}</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  <span
                    className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ${
                      user.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>
            </li>
          ))}
        </ul>
        {users?.length === 0 && (
          <div className="py-12 text-center">
            <p className="text-sm text-gray-500">No users found.</p>
          </div>
        )}
      </div>
    </div>
  )
}
