<template>
  <a-layout class="app-layout">
    <a-layout-header class="user-header">
      <div class="header-inner">
        <div class="logo" @click="$router.push('/home')">
          <span class="logo-icon">🎯</span>
          <span class="logo-text">个性化推荐</span>
        </div>
        <div class="nav-menu">
          <div v-for="item in menuItems" :key="item.key"
               :class="['nav-item', { active: currentRoute === item.key }]"
               @click="$router.push(item.path)">
            <span class="nav-icon">{{ item.icon }}</span>
            <span>{{ item.label }}</span>
          </div>
        </div>
        <div class="header-right">
          <div class="user-avatar">{{ (userStore.user?.nickname || '用')[0] }}</div>
          <span class="user-name">{{ userStore.user?.nickname || '用户' }}</span>
          <a-button type="text" size="small" class="logout-btn" @click="handleLogout">退出</a-button>
        </div>
      </div>
    </a-layout-header>
    <a-layout-content>
      <div class="page-content">
        <router-view />
      </div>
    </a-layout-content>
  </a-layout>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const menuItems = [
  { key: 'home', path: '/home', label: '首页', icon: '🏠' },
  { key: 'newslist', path: '/news', label: '新闻', icon: '📰' },
  { key: 'musiclist', path: '/music', label: '音乐', icon: '🎵' },
  { key: 'algorithm', path: '/algorithm', label: '算法', icon: '🧠' }
]

const currentRoute = computed(() => route.name?.toLowerCase() || 'home')

onMounted(() => { userStore.fetchProfile().catch(() => {}) })

function handleLogout() { userStore.logout(); router.push('/login') }
</script>

<style lang="scss" scoped>
$primary: #1890ff;
$text: #333;
$text-muted: #666;
$border: #e8e8e8;
$bg: #f5f7fa;

.app-layout {
  min-height: 100vh;
  background: $bg;
}

.user-header {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  padding: 0;
  position: sticky;
  top: 0;
  z-index: 100;
  height: 60px;
  line-height: 60px;
}

.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  padding: 0 24px;
  height: 100%;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  margin-right: 40px;

  .logo-icon { font-size: 24px; }

  .logo-text {
    font-size: 18px;
    font-weight: 700;
    color: $primary;
  }
}

.nav-menu {
  flex: 1;
  display: flex;
  gap: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  border-radius: 18px;
  color: $text-muted;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 14px;
  line-height: 1.5;
  position: relative;
  overflow: hidden;

  .nav-icon {
    font-size: 16px;
    transition: transform 0.3s ease;
  }

  &:hover {
    background: rgba($primary, 0.08);
    color: $primary;

    .nav-icon {
      transform: scale(1.1);
    }
  }

  &.active {
    background: linear-gradient(135deg, $primary, #40a9ff);
    color: #fff;
    font-weight: 600;
    box-shadow: 0 2px 8px rgba($primary, 0.35);

    .nav-icon {
      transform: scale(1.05);
    }

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: -100%;
      width: 100%;
      height: 100%;
      background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.25), transparent);
      animation: shine 2.5s infinite;
    }
  }
}

@keyframes shine {
  0% { left: -100%; }
  50%, 100% { left: 100%; }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, $primary, #40a9ff);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
}

.user-name {
  color: $text;
  font-size: 14px;
}

.logout-btn {
  color: $text-muted !important;
  &:hover { color: #ff4d4f !important; }
}
</style>
