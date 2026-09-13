import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    redirect: '/home',
    children: [
      { path: 'home', name: 'Home', component: () => import('../views/Home.vue') },
      { path: 'news', name: 'NewsList', component: () => import('../views/NewsList.vue') },
      { path: 'news/:id', name: 'NewsDetail', component: () => import('../views/NewsDetail.vue') },
      { path: 'music', name: 'MusicList', component: () => import('../views/MusicList.vue') },
      { path: 'algorithm', name: 'Algorithm', component: () => import('../views/Algorithm.vue') },
    ]
  }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('user_token')
  if (to.path !== '/login' && !token) next('/login')
  else next()
})

export default router
