<template>
  <div class="login-page">
    <div class="bg-nodes">
      <span v-for="i in 20" :key="i" class="node" :style="nodeStyle(i)" />
    </div>

    <div class="login-wrapper">
      <div class="brand-panel">
        <div class="brand-inner">
          <div class="brand-icon">
            <svg viewBox="0 0 80 80" width="56" height="56" fill="none">
              <circle cx="40" cy="40" r="36" stroke="rgba(255,255,255,0.3)" stroke-width="2"/>
              <circle cx="24" cy="28" r="5" fill="#fff" opacity="0.9"/>
              <circle cx="56" cy="28" r="5" fill="#fff" opacity="0.9"/>
              <circle cx="40" cy="52" r="5" fill="#fff" opacity="0.9"/>
              <circle cx="20" cy="50" r="4" fill="#fff" opacity="0.6"/>
              <circle cx="60" cy="50" r="4" fill="#fff" opacity="0.6"/>
              <line x1="24" y1="28" x2="56" y2="28" stroke="rgba(255,255,255,0.4)" stroke-width="1.5"/>
              <line x1="24" y1="28" x2="40" y2="52" stroke="rgba(255,255,255,0.4)" stroke-width="1.5"/>
              <line x1="56" y1="28" x2="40" y2="52" stroke="rgba(255,255,255,0.4)" stroke-width="1.5"/>
              <line x1="20" y1="50" x2="40" y2="52" stroke="rgba(255,255,255,0.25)" stroke-width="1"/>
              <line x1="60" y1="50" x2="40" y2="52" stroke="rgba(255,255,255,0.25)" stroke-width="1"/>
            </svg>
          </div>
          <h1 class="brand-title">内容推荐与兴趣分析</h1>
          <p class="brand-desc">Collaborative Filtering Engine</p>
          <div class="brand-divider" />
          <div class="brand-features">
            <div class="feature-item" v-for="f in ['协同过滤算法','用户行为分析','可视化数据洞察']" :key="f">
              <span class="feature-dot" /><span>{{ f }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="login-card">
        <div class="card-header">
          <div class="avatar-ring">
            <UserOutlined style="font-size: 24px; color: #667eea" />
          </div>
          <h2 class="card-title">管理后台</h2>
          <p class="card-subtitle">请使用管理员账号登录</p>
        </div>

        <a-form :model="form" @finish="handleLogin" layout="vertical" class="login-form">
          <a-form-item name="username" :rules="[{ required: true, message: '请输入用户名' }]">
            <a-input v-model:value="form.username" size="large" placeholder="用户名">
              <template #prefix><UserOutlined style="color: #bfbfbf" /></template>
            </a-input>
          </a-form-item>
          <a-form-item name="password" :rules="[{ required: true, message: '请输入密码' }]">
            <a-input-password v-model:value="form.password" size="large" placeholder="密码">
              <template #prefix><LockOutlined style="color: #bfbfbf" /></template>
            </a-input-password>
          </a-form-item>
          <a-button type="primary" html-type="submit" size="large" block :loading="loading" class="login-btn">
            登 录
          </a-button>
        </a-form>

        <div class="card-footer">
          <span class="footer-text">Powered by Collaborative Filtering · ML</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const form = reactive({ username: '', password: '' })

function nodeStyle(i) {
  const size = 4 + Math.random() * 6
  return {
    width: `${size}px`, height: `${size}px`,
    left: `${Math.random() * 100}%`, top: `${Math.random() * 100}%`,
    animationDelay: `${Math.random() * 6}s`,
    animationDuration: `${6 + Math.random() * 8}s`
  }
}

async function handleLogin() {
  loading.value = true
  try {
    const res = await userStore.login(form)
    if (res.code === 200) { message.success('登录成功'); router.push('/dashboard') }
  } finally { loading.value = false }
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
  position: relative;
  overflow: hidden;
  padding: 24px;
}

.bg-nodes {
  position: absolute; inset: 0; pointer-events: none;
  .node {
    position: absolute; border-radius: 50%;
    background: rgba(255, 255, 255, 0.15);
    animation: float-node linear infinite;
  }
}
@keyframes float-node {
  0%, 100% { transform: translateY(0) scale(1); opacity: 0.2; }
  50% { transform: translateY(-30px) scale(1.3); opacity: 0.6; }
}

.login-wrapper {
  display: flex;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.45);
  position: relative;
  z-index: 1;
  width: 780px;
  max-width: 100%;
  min-height: 480px;
}

.brand-panel {
  flex: 0 0 50%;
  width: 50%;
  background: linear-gradient(160deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  position: relative;
  overflow: hidden;
  &::before {
    content: ''; position: absolute; width: 220px; height: 220px;
    border-radius: 50%; background: rgba(255,255,255,0.06);
    top: -70px; right: -70px;
  }
  &::after {
    content: ''; position: absolute; width: 160px; height: 160px;
    border-radius: 50%; background: rgba(255,255,255,0.04);
    bottom: -50px; left: -50px;
  }
}
.brand-inner { position: relative; z-index: 1; padding: 48px 36px; }
.brand-icon { margin-bottom: 24px; }
.brand-title {
  font-size: 28px; font-weight: 800; color: #fff;
  margin: 0 0 8px; letter-spacing: 2px;
}
.brand-desc {
  font-size: 13px; color: rgba(255,255,255,0.6);
  margin: 0 0 36px; font-family: 'Courier New', monospace;
}
.brand-divider {
  width: 36px; height: 3px; border-radius: 2px;
  background: rgba(255,255,255,0.35); margin: 0 0 20px;
}
.brand-features { display: flex; flex-direction: column; gap: 14px; }
.feature-item {
  display: flex; align-items: center; gap: 10px;
  color: rgba(255,255,255,0.85); font-size: 14px;
}
.feature-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: rgba(255,255,255,0.7); flex-shrink: 0;
  box-shadow: 0 0 8px rgba(255,255,255,0.4);
}

.login-card {
  flex: 0 0 50%;
  width: 50%;
  background: #fff;
  padding: 44px 40px 32px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.card-header { text-align: center; margin-bottom: 28px; }
.avatar-ring {
  width: 60px; height: 60px; border-radius: 50%;
  background: linear-gradient(135deg, #f0f0ff, #e8e6ff);
  display: inline-flex; align-items: center; justify-content: center;
  margin-bottom: 14px;
  box-shadow: 0 4px 16px rgba(102,126,234,0.15);
}
.card-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin: 0 0 4px; }
.card-subtitle { font-size: 13px; color: #999; margin: 0; }

.login-form {
  :deep(.ant-input-affix-wrapper) {
    border-radius: 10px; border-color: #e8e8ef;
    padding: 8px 14px; transition: all 0.3s;
    &:hover, &:focus-within {
      border-color: #667eea;
      box-shadow: 0 0 0 3px rgba(102,126,234,0.08);
    }
  }
  :deep(.ant-input) { font-size: 15px; }
}

.login-btn {
  height: 48px; border-radius: 10px; font-size: 16px; font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  border: none !important; letter-spacing: 4px;
  box-shadow: 0 4px 16px rgba(102,126,234,0.35);
  transition: all 0.3s;
  &:hover { transform: translateY(-1px); box-shadow: 0 6px 24px rgba(102,126,234,0.45); opacity: 0.95; }
  &:active { transform: translateY(0); }
}

.card-footer {
  text-align: center; margin-top: 20px; padding-top: 14px;
  border-top: 1px solid #f0f0f0;
}
.footer-text { font-size: 11px; color: #ccc; letter-spacing: 0.5px; }
</style>
