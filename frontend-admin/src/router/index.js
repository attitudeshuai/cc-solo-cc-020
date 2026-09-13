import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
      { path: 'users', name: 'Users', component: () => import('../views/Users.vue') },
      { path: 'news', name: 'News', component: () => import('../views/NewsManage.vue') },
      { path: 'music', name: 'Music', component: () => import('../views/MusicManage.vue') },
      { path: 'behavior', name: 'Behavior', component: () => import('../views/BehaviorAnalysis.vue') },
      { path: 'recommendation', name: 'Recommendation', component: () => import('../views/RecommendAnalysis.vue') },
      { path: 'algorithm', name: 'Algorithm', component: () => import('../views/AlgorithmView.vue') },
      { path: 'collect', name: 'Collect', component: () => import('../views/DataCollect.vue') },
      { path: 'logs', name: 'Logs', component: () => import('../views/Logs.vue') },
    ]
  }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('admin_token')
  if (to.path !== '/login' && !token) next('/login')
  else next()
})

export default router
