<template>
  <div class="home-page">
    <div class="section">
      <div class="section-title"><span class="icon">📰</span><span>为你推荐的新闻</span></div>
      <a-spin :spinning="newsLoading">
        <a-row :gutter="[16, 16]">
          <a-col :xs="24" :sm="12" :lg="8" v-for="item in newsList" :key="item.id">
            <div class="news-card" @click="$router.push(`/news/${item.id}`)">
              <div class="rec-badge" v-if="item.rec_reason"><span>{{ item.rec_reason }}</span><span class="score">{{ (item.rec_score * 100).toFixed(0) }}%</span></div>
              <div class="card-title">{{ item.title }}</div>
              <div class="card-desc">{{ item.content }}</div>
              <div class="card-footer"><a-tag color="blue">{{ item.category }}</a-tag><span>{{ item.source }}</span><span>👁 {{ item.view_count }}</span></div>
            </div>
          </a-col>
        </a-row>
        <div class="empty-state" v-if="!newsLoading && newsList.length === 0"><div class="empty-icon">📭</div><div>暂无推荐</div></div>
      </a-spin>
    </div>
    <div class="section">
      <div class="section-title"><span class="icon">🎵</span><span>为你推荐的音乐</span></div>
      <a-spin :spinning="musicLoading">
        <a-row :gutter="[16, 16]">
          <a-col :xs="24" :sm="12" v-for="item in musicList" :key="item.id">
            <div class="music-card">
              <div class="music-cover">♪</div>
              <div class="music-info">
                <div class="music-title">{{ item.title }}</div>
                <div class="music-artist">{{ item.artist }}</div>
                <div class="music-meta"><a-tag color="green" size="small">{{ item.genre }}</a-tag><span v-if="item.rec_reason" class="rec-text">{{ item.rec_reason }}</span></div>
              </div>
              <div class="like-btn" :class="{ liked: likedMusic.has(item.id) }" @click="handleLike(item)">
                <HeartFilled v-if="likedMusic.has(item.id)" /><HeartOutlined v-else />
              </div>
            </div>
          </a-col>
        </a-row>
        <div class="empty-state" v-if="!musicLoading && musicList.length === 0"><div class="empty-icon">🎧</div><div>暂无推荐</div></div>
      </a-spin>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { HeartOutlined, HeartFilled } from '@ant-design/icons-vue'
import { getNewsRecommend, getMusicRecommend, recordBehavior, deleteBehavior, getUserBehaviors } from '../api'

const newsList = ref([]), musicList = ref([]), newsLoading = ref(false), musicLoading = ref(false), likedMusic = ref(new Set())

async function fetchData() {
  newsLoading.value = musicLoading.value = true
  try {
    const [newsRes, musicRes, behaviorRes] = await Promise.all([
      getNewsRecommend({ top_n: 6 }), getMusicRecommend({ top_n: 6 }), getUserBehaviors()
    ])
    if (newsRes.code === 200) newsList.value = newsRes.data
    if (musicRes.code === 200) musicList.value = musicRes.data
    if (behaviorRes.code === 200) {
      const likes = behaviorRes.data.likes || {}
      Object.keys(likes).forEach(key => {
        if (key.startsWith('music_')) likedMusic.value.add(parseInt(key.split('_')[1]))
      })
    }
  } finally { newsLoading.value = musicLoading.value = false }
}

async function handleLike(item) {
  if (likedMusic.value.has(item.id)) { 
    likedMusic.value.delete(item.id)
    await deleteBehavior({ item_type: 'music', item_id: item.id, action_type: 'like' })
    message.info('已取消喜欢') 
  }
  else { 
    likedMusic.value.add(item.id)
    await recordBehavior({ item_type: 'music', item_id: item.id, action_type: 'like' })
    message.success('已添加到喜欢') 
  }
}

onMounted(fetchData)
</script>

<style lang="scss" scoped>
$primary: #1890ff; $accent: #ff6b6b; $text: #333; $text-muted: #666; $like-color: #ff4d6d;
.section { margin-bottom: 40px; }
.section-title { font-size: 20px; font-weight: 600; margin-bottom: 20px; display: flex; align-items: center; gap: 12px; color: $text;
  .icon { width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, $primary, #40a9ff); display: flex; align-items: center; justify-content: center; font-size: 16px; }
}
.news-card { height: 100%; display: flex; flex-direction: column; background: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); cursor: pointer; transition: all 0.25s; border: 1px solid transparent;
  &:hover { box-shadow: 0 6px 20px rgba(0,0,0,0.12); transform: translateY(-2px); border-color: $primary; }
  .card-title { font-size: 16px; font-weight: 600; color: $text; margin-bottom: 8px; line-height: 1.4; }
  .card-desc { flex: 1; font-size: 13px; color: $text-muted; line-height: 1.6; margin-bottom: 12px; }
  .card-footer { display: flex; align-items: center; gap: 12px; font-size: 12px; color: #999; }
}
.rec-badge { display: inline-flex; align-items: center; gap: 8px; background: linear-gradient(135deg, $accent, #ee5a24); color: #fff; font-size: 12px; padding: 4px 12px; border-radius: 20px; margin-bottom: 12px;
  .score { background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 10px; font-weight: 600; }
}
.music-card { display: flex; align-items: center; gap: 16px; background: #fff; border-radius: 12px; padding: 16px 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); transition: all 0.25s; border: 1px solid transparent;
  &:hover { box-shadow: 0 6px 20px rgba(0,0,0,0.12); border-color: $primary; }
  .music-cover { width: 56px; height: 56px; border-radius: 12px; background: linear-gradient(135deg, #667eea, #764ba2); display: flex; align-items: center; justify-content: center; color: #fff; font-size: 22px; flex-shrink: 0; }
  .music-info { flex: 1; min-width: 0;
    .music-title { font-size: 15px; font-weight: 600; color: $text; }
    .music-artist { font-size: 13px; color: $text-muted; margin-top: 2px; }
    .music-meta { margin-top: 6px; display: flex; align-items: center; gap: 8px; .rec-text { font-size: 11px; color: $accent; } }
  }
  .like-btn {
    width: 42px; height: 42px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-size: 20px; cursor: pointer; transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1); flex-shrink: 0;
    color: #d1d5db; background: linear-gradient(145deg, #f8f9fa, #e9ecef); 
    border: none; box-shadow: 2px 2px 6px rgba(0,0,0,0.08), -2px -2px 6px rgba(255,255,255,0.9);
    &:hover { color: $like-color; transform: scale(1.08); box-shadow: 3px 3px 8px rgba(0,0,0,0.1), -2px -2px 6px rgba(255,255,255,0.9); }
    &:active { transform: scale(0.95); }
    &.liked { 
      color: #fff; background: linear-gradient(135deg, #ff6b81, #ff4757); 
      box-shadow: 0 4px 15px rgba(255,75,87,0.45), inset 0 1px 0 rgba(255,255,255,0.2);
      animation: heartBeat 0.4s ease;
      &:hover { box-shadow: 0 6px 20px rgba(255,75,87,0.5); transform: scale(1.1); }
    }
  }
}
@keyframes heartBeat {
  0% { transform: scale(1); }
  25% { transform: scale(1.25); }
  50% { transform: scale(1); }
  75% { transform: scale(1.15); }
  100% { transform: scale(1); }
}
.empty-state { text-align: center; padding: 48px 20px; color: #999; .empty-icon { font-size: 48px; margin-bottom: 12px; } }
</style>
