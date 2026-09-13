<template>
  <div class="login-page">
    <!-- 动态背景 -->
    <div class="bg-layer">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
      <div class="floating-shapes">
        <span v-for="i in 12" :key="i" class="shape" :style="{ '--delay': i * 0.5 + 's', '--x': Math.random() * 100 + '%', '--size': 10 + Math.random() * 20 + 'px' }"></span>
      </div>
    </div>
    
    <div class="login-container">
      <div class="visual-header">
        <h1 class="app-title">内容推荐与兴趣分析</h1>
        <p class="app-desc">按你的阅读与收听记录，挑出更合口味的内容</p>
      </div>

      <div class="glass-card">
        <a-tabs v-model:activeKey="tab" centered class="custom-tabs">
          <a-tab-pane key="login" tab="登录">
            <a-form :model="loginForm" @finish="handleLogin" layout="vertical" class="auth-form">
              <a-form-item name="username" :rules="[{ required: true, message: '请输入用户名' }]">
                <a-input v-model:value="loginForm.username" size="large" placeholder="用户名">
                  <template #prefix><UserOutlined style="color: #999" /></template>
                </a-input>
              </a-form-item>
              <a-form-item name="password" :rules="[{ required: true, message: '请输入密码' }]">
                <a-input-password v-model:value="loginForm.password" size="large" placeholder="密码">
                  <template #prefix><LockOutlined style="color: #999" /></template>
                </a-input-password>
              </a-form-item>
              <a-button type="primary" html-type="submit" size="large" block :loading="loading" class="submit-btn">登 录</a-button>
            </a-form>
          </a-tab-pane>
          <a-tab-pane key="register" tab="注册">
            <a-form :model="regForm" @finish="handleRegister" layout="vertical" class="auth-form">
              <a-form-item name="username" :rules="[{ required: true, message: '请输入用户名' }]">
                <a-input v-model:value="regForm.username" size="large" placeholder="用户名">
                  <template #prefix><UserOutlined style="color: #999" /></template>
                </a-input>
              </a-form-item>
              <a-form-item name="nickname">
                <a-input v-model:value="regForm.nickname" size="large" placeholder="昵称（选填）">
                  <template #prefix><SmileOutlined style="color: #999" /></template>
                </a-input>
              </a-form-item>
              <a-form-item name="password" :rules="[{ required: true, message: '请输入密码' }]">
                <a-input-password v-model:value="regForm.password" size="large" placeholder="密码">
                  <template #prefix><LockOutlined style="color: #999" /></template>
                </a-input-password>
              </a-form-item>
              <a-button type="primary" html-type="submit" size="large" block :loading="loading" class="submit-btn">注 册</a-button>
            </a-form>
          </a-tab-pane>
        </a-tabs>
      </div>
      <div class="footer-badge"><span>Collaborative Filtering · Machine Learning</span></div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { UserOutlined, LockOutlined, SmileOutlined } from '@ant-design/icons-vue'
import { useUserStore } from '../stores/user'

const router = useRouter(), userStore = useUserStore(), loading = ref(false), tab = ref('login')
const loginForm = reactive({ username: '', password: '' })
const regForm = reactive({ username: '', nickname: '', password: '' })

async function handleLogin() {
  loading.value = true
  try { const res = await userStore.login(loginForm); if (res.code === 200) { message.success('登录成功'); router.push('/home') } }
  finally { loading.value = false }
}
async function handleRegister() {
  loading.value = true
  try { const res = await userStore.doRegister(regForm); if (res.code === 200) { message.success('注册成功，请登录'); tab.value = 'login' } }
  finally { loading.value = false }
}
</script>

<style lang="scss" scoped>
$primary: #1890ff;
$accent: #722ed1;

.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  padding: 24px;
  position: relative;
  overflow: hidden;
}

// 动态背景层
.bg-layer {
  position: absolute;
  inset: 0;
  overflow: hidden;
  z-index: 0;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.6;
  animation: float-orb 20s ease-in-out infinite;
}

.orb-1 {
  width: 500px; height: 500px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  top: -150px; left: -100px;
  animation-delay: 0s;
}

.orb-2 {
  width: 400px; height: 400px;
  background: linear-gradient(135deg, #f093fb, #f5576c);
  bottom: -100px; right: -100px;
  animation-delay: -7s;
}

.orb-3 {
  width: 300px; height: 300px;
  background: linear-gradient(135deg, #4facfe, #00f2fe);
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: -14s;
}

@keyframes float-orb {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(30px, -30px) scale(1.05); }
  50% { transform: translate(-20px, 20px) scale(0.95); }
  75% { transform: translate(20px, 30px) scale(1.02); }
}

.floating-shapes {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.shape {
  position: absolute;
  width: var(--size, 12px);
  height: var(--size, 12px);
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  left: var(--x, 50%);
  bottom: -20px;
  animation: rise 15s ease-in-out infinite;
  animation-delay: var(--delay, 0s);
}

@keyframes rise {
  0% { transform: translateY(0) rotate(0deg); opacity: 0; }
  10% { opacity: 0.6; }
  90% { opacity: 0.6; }
  100% { transform: translateY(-100vh) rotate(720deg); opacity: 0; }
}

.login-container {
  display: flex; flex-direction: column; align-items: center;
  width: 400px; max-width: 100%;
  position: relative;
  z-index: 1;
}

.visual-header { text-align: center; margin-bottom: 28px; }

.app-title { font-size: 28px; font-weight: 700; color: #fff; margin: 0 0 8px; letter-spacing: 3px; text-shadow: 0 2px 20px rgba(0,0,0,0.2); }
.app-desc { font-size: 13px; color: rgba(255,255,255,0.9); margin: 0; text-shadow: 0 1px 10px rgba(0,0,0,0.1); }

.glass-card {
  width: 100%;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 32px 28px 24px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(255,255,255,0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.custom-tabs {
  :deep(.ant-tabs-nav::before) { border-bottom-color: #e8e8e8; }
  :deep(.ant-tabs-tab) { color: #999; font-size: 15px; }
  :deep(.ant-tabs-tab-active .ant-tabs-tab-btn) { color: #667eea; }
  :deep(.ant-tabs-ink-bar) { background: linear-gradient(90deg, #667eea, #764ba2); }
}

.auth-form {
  :deep(.ant-form-item) { margin-bottom: 18px; }
  :deep(.ant-input-affix-wrapper) {
    background: #f8f9fc;
    border: 1px solid #e8e8e8;
    border-radius: 12px; padding: 10px 14px;
    transition: all 0.3s;
    &:hover, &:focus-within { 
      border-color: #667eea; 
      box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
      background: #fff;
    }
  }
  :deep(.ant-input) { background: transparent; color: #333; font-size: 14px; &::placeholder { color: #bbb; } }
  :deep(.ant-input-password-icon) { color: #999; }
}

.submit-btn {
  height: 48px; border-radius: 12px; font-size: 15px; font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%) !important;
  background-size: 200% 200% !important;
  border: none !important; letter-spacing: 4px;
  box-shadow: 0 6px 20px rgba(118, 75, 162, 0.4);
  margin-top: 8px; transition: all 0.4s;
  animation: gradient-shift 5s ease infinite;
  &:hover { 
    transform: translateY(-2px); 
    box-shadow: 0 10px 30px rgba(118, 75, 162, 0.5);
  }
}

@keyframes gradient-shift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.footer-badge { margin-top: 28px; text-align: center;
  span { font-size: 11px; color: rgba(255,255,255,0.7); letter-spacing: 1px; font-family: 'Courier New', monospace; text-shadow: 0 1px 5px rgba(0,0,0,0.1); }
}
</style>
