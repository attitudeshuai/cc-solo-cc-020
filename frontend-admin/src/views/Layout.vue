<template>
  <a-layout style="min-height: 100vh">
    <a-layout-sider v-model:collapsed="collapsed" collapsible theme="dark" :width="220">
      <div class="logo">{{ collapsed ? 'CI' : '内容推荐' }}</div>
      <a-menu theme="dark" mode="inline" :selectedKeys="[currentRoute]">
        <a-menu-item key="dashboard" @click="$router.push('/dashboard')">
          <DashboardOutlined /><span>数据概览</span>
        </a-menu-item>
        <a-menu-item key="users" @click="$router.push('/users')">
          <UserOutlined /><span>用户管理</span>
        </a-menu-item>
        <a-menu-item key="news" @click="$router.push('/news')">
          <ReadOutlined /><span>新闻管理</span>
        </a-menu-item>
        <a-menu-item key="music" @click="$router.push('/music')">
          <CustomerServiceOutlined /><span>音乐管理</span>
        </a-menu-item>
        <a-sub-menu key="analytics">
          <template #title><BarChartOutlined /><span>数据分析</span></template>
          <a-menu-item key="behavior" @click="$router.push('/behavior')">行为分析</a-menu-item>
          <a-menu-item key="recommendation" @click="$router.push('/recommendation')">推荐分析</a-menu-item>
          <a-menu-item key="algorithm" @click="$router.push('/algorithm')">算法原理</a-menu-item>
        </a-sub-menu>
        <a-menu-item key="logs" @click="$router.push('/logs')">
          <FileTextOutlined /><span>操作日志</span>
        </a-menu-item>
        <a-menu-item key="collect" @click="$router.push('/collect')">
          <CloudDownloadOutlined /><span>数据采集</span>
        </a-menu-item>
      </a-menu>
    </a-layout-sider>
    <a-layout>
      <a-layout-header class="header-bar">
        <span class="header-title">{{ pageTitle }}</span>
        <div class="header-right">
          <span class="header-user">{{ userStore.user?.nickname || '管理员' }}</span>
          <a-button type="link" danger @click="handleLogout">退出</a-button>
        </div>
      </a-layout-header>
      <a-layout-content class="page-container">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import {
  DashboardOutlined, UserOutlined, ReadOutlined,
  CustomerServiceOutlined, BarChartOutlined, FileTextOutlined,
  CloudDownloadOutlined
} from '@ant-design/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const collapsed = ref(false)

const currentRoute = computed(() => route.name?.toLowerCase() || 'dashboard')

const titleMap = {
  dashboard: '数据概览', users: '用户管理', news: '新闻管理',
  music: '音乐管理', behavior: '行为分析', recommendation: '推荐分析',
  algorithm: '算法原理', logs: '操作日志', collect: '数据采集'
}
const pageTitle = computed(() => titleMap[currentRoute.value] || '内容推荐')

onMounted(() => { userStore.fetchProfile().catch(() => {}) })

function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>

<style lang="scss" scoped>
.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 2px;
}
.header-bar {
  background: #fff;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}
.header-title { font-size: 16px; font-weight: 600; }
.header-right { display: flex; align-items: center; gap: 12px; }
.header-user { color: #666; font-size: 14px; }
</style>
