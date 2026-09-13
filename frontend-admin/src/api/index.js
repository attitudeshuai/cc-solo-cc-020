import axios from 'axios'
import { message } from 'ant-design-vue'
import router from '../router'

const api = axios.create({ baseURL: '/api', timeout: 15000 })

api.interceptors.request.use(config => {
  const token = localStorage.getItem('admin_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  res => res.data,
  err => {
    const msg = err.response?.data?.msg || '请求失败'
    if (err.response?.status === 401) {
      localStorage.removeItem('admin_token')
      router.push('/login')
    }
    message.error(msg)
    return Promise.reject(err)
  }
)

// Auth
export const login = data => api.post('/auth/login', data)
export const getProfile = () => api.get('/auth/profile')

// Admin - Users
export const getUsers = params => api.get('/admin/users', { params })
export const updateUser = (id, data) => api.put(`/admin/users/${id}`, data)
export const deleteUser = id => api.delete(`/admin/users/${id}`)

// Admin - News
export const getNewsList = params => api.get('/news', { params })
export const createNews = data => api.post('/admin/news', data)
export const updateNews = (id, data) => api.put(`/admin/news/${id}`, data)
export const deleteNews = id => api.delete(`/admin/news/${id}`)

// Admin - Music
export const getMusicList = params => api.get('/music', { params })
export const createMusic = data => api.post('/admin/music', data)
export const updateMusic = (id, data) => api.put(`/admin/music/${id}`, data)
export const deleteMusic = id => api.delete(`/admin/music/${id}`)

// Analytics
export const getOverview = () => api.get('/admin/analytics/overview')
export const getBehaviorAnalysis = params => api.get('/admin/analytics/behavior', { params })
export const getRecommendationAnalysis = () => api.get('/admin/analytics/recommendation')
export const getSimilarityMatrix = params => api.get('/admin/analytics/similarity', { params })
export const getAlgorithmInfo = () => api.get('/admin/analytics/algorithm')

// Logs
export const getLogs = params => api.get('/admin/logs', { params })

// Data Collection (采集操作耗时较长，设置3分钟超时)
export const triggerCollection = () => api.post('/admin/collect', {}, { timeout: 180000 })
export const getCollectionStatus = () => api.get('/admin/collect/status')

export default api
