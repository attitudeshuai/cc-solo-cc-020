import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as loginApi, getProfile } from '../api'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('admin_token') || '')

  async function login(form) {
    const res = await loginApi(form)
    if (res.code === 200) {
      token.value = res.data.token
      user.value = res.data.user
      localStorage.setItem('admin_token', res.data.token)
    }
    return res
  }

  async function fetchProfile() {
    const res = await getProfile()
    if (res.code === 200) user.value = res.data
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('admin_token')
  }

  return { user, token, login, fetchProfile, logout }
})
