import axios from 'axios'
import { message } from 'ant-design-vue'
import router from '../router'

const api = axios.create({ baseURL: '/api', timeout: 15000 })

api.interceptors.request.use(config => {
  const token = localStorage.getItem('user_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  res => res.data,
  err => {
    const msg = err.response?.data?.msg || '请求失败'
    if (err.response?.status === 401) {
      localStorage.removeItem('user_token')
      router.push('/login')
    }
    message.error(msg)
    return Promise.reject(err)
  }
)

export const login = data => api.post('/auth/login', data)
export const register = data => api.post('/auth/register', data)
export const getProfile = () => api.get('/auth/profile')

export const getNewsList = params => api.get('/news', { params })
export const getNewsDetail = id => api.get(`/news/${id}`)
export const getMusicList = params => api.get('/music', { params })
export const getMusicDetail = id => api.get(`/music/${id}`)

export const getNewsRecommend = params => api.get('/recommend/news', { params })
export const getMusicRecommend = params => api.get('/recommend/music', { params })
export const getAlgorithmInfo = () => api.get('/recommend/algorithm')
export const getMyStats = () => api.get('/recommend/my-stats')
export const getMyProfile = () => api.get('/recommend/my-profile')
export const recordBehavior = data => api.post('/recommend/behavior', data)
export const deleteBehavior = params => api.delete('/recommend/behavior', { params })
export const getUserBehaviors = params => api.get('/recommend/behavior', { params })

export default api
