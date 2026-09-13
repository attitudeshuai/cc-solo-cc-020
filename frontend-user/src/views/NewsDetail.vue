<template>
  <div>
    <a-button type="link" @click="$router.back()" style="padding: 0; margin-bottom: 16px">← 返回列表</a-button>
    <a-spin :spinning="loading">
      <div class="detail-page" v-if="news">
        <div class="detail-title">{{ news.title }}</div>
        <div class="detail-meta">
          <a-tag color="blue">{{ news.category }}</a-tag>
          <span>来源: {{ news.source }}</span>
          <span>浏览: {{ news.view_count }}</span>
          <span>{{ news.published_at }}</span>
        </div>
        <div class="detail-content">{{ news.content }}</div>
        <div style="margin-top: 24px; display: flex; gap: 12px; align-items: center">
          <a-button :type="liked ? 'primary' : 'default'" @click="handleLike">
            {{ liked ? '❤️ 已喜欢' : '🤍 喜欢' }}
          </a-button>
          <span style="margin-left: 12px; color: #666">评分:</span>
          <a-rate v-model:value="rating" @change="handleRate" allow-half />
        </div>
      </div>
    </a-spin>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import { getNewsDetail, recordBehavior, deleteBehavior, getUserBehaviors } from '../api'

const route = useRoute()
const news = ref(null)
const loading = ref(false)
const rating = ref(0)
const liked = ref(false)

async function loadBehaviors() {
  try {
    const res = await getUserBehaviors({ item_type: 'news' })
    if (res.code === 200) {
      const newsId = Number(route.params.id)
      const key = `news_${newsId}`
      liked.value = !!res.data.likes?.[key]
      rating.value = res.data.ratings?.[key] || 0
    }
  } catch (e) { console.error('加载行为数据失败', e) }
}

onMounted(async () => {
  loading.value = true
  try {
    await loadBehaviors()
    const res = await getNewsDetail(route.params.id)
    if (res.code === 200) news.value = res.data
  } finally { loading.value = false }
})

async function handleLike() {
  if (liked.value) {
    liked.value = false
    await deleteBehavior({ item_type: 'news', item_id: Number(route.params.id), action_type: 'like' })
    message.info('已取消喜欢')
  } else {
    liked.value = true
    await recordBehavior({ item_type: 'news', item_id: Number(route.params.id), action_type: 'like' })
    message.success('已喜欢')
  }
}

async function handleRate(val) {
  await recordBehavior({ item_type: 'news', item_id: Number(route.params.id), action_type: 'rate', rating: val })
  message.success(`评分: ${val}`)
}
</script>
