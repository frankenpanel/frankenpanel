import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

let onUnauthorized: (() => void) | null = null

export function setOnUnauthorized(callback: () => void) {
  onUnauthorized = callback
}

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor: 401 → clear token and SPA redirect (no full page reload)
// Skip redirect for /auth/login so the login page can show "Incorrect username or password"
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const isLoginRequest = error.config?.url?.includes('/auth/login')
      localStorage.removeItem('access_token')
      if (!isLoginRequest && onUnauthorized) {
        onUnauthorized()
      }
    }
    return Promise.reject(error)
  }
)

export default api
