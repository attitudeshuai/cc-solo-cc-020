<template>
  <div class="music-page">
    <div class="section-title"><span class="icon">🎵</span>音乐库</div>
    
    <!-- 搜索栏 -->
    <div class="search-bar">
      <a-input v-model:value="keyword" placeholder="搜索歌曲、歌手..." 
               style="width: 240px" allowClear @pressEnter="handleSearch">
        <template #prefix><span>🔍</span></template>
      </a-input>
      <a-select v-model:value="genre" placeholder="全部风格" style="width: 140px" 
                allowClear @change="handleSearch">
        <a-select-option v-for="g in genres" :key="g.value" :value="g.value">
          {{ g.label }}
        </a-select-option>
      </a-select>
      <a-button type="primary" @click="handleSearch">搜索</a-button>
    </div>
    
    <!-- 音乐列表 -->
    <a-spin :spinning="loading">
      <div class="music-list">
        <div v-for="item in list" :key="item.id" class="music-card">
          <div class="music-cover">♪</div>
          <div class="music-info">
            <div class="music-title">{{ item.title }}</div>
            <div class="music-artist">{{ item.artist }} {{ item.album ? '· ' + item.album : '' }}</div>
            <div class="music-meta">
              <a-tag color="green">{{ item.genre }}</a-tag>
              <span class="duration">{{ formatDuration(item.duration) }}</span>
              <span class="play-count">▶ {{ item.play_count }}</span>
            </div>
          </div>
          <div class="music-actions" @click.stop>
            <div class="like-btn" :class="{ liked: likedSet.has(item.id) }" @click="handleLike(item)">
              <HeartFilled v-if="likedSet.has(item.id)" /><HeartOutlined v-else />
            </div>
            <a-rate v-model:value="item._rating" :count="5" allow-half 
                    style="font-size: 14px" @change="val => handleRate(item, val)" />
          </div>
        </div>
      </div>
      
      <div class="empty-state" v-if="!loading && list.length === 0">
        <div class="empty-icon">🎧</div>
        <div class="empty-text">暂无音乐数据</div>
      </div>
    </a-spin>
    
    <!-- 分页 -->
    <div class="pagination-wrapper" v-if="total > 0">
      <a-pagination v-model:current="page" :total="total" :pageSize="10" 
                    @change="fetchData" show-quick-jumper />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { HeartOutlined, HeartFilled } from '@ant-design/icons-vue'
import { getMusicList, recordBehavior, deleteBehavior, getUserBehaviors } from '../api'

const genres = [
  { value: 'pop', label: '🎤 流行' },
  { value: 'rock', label: '🎸 摇滚' },
  { value: 'jazz', label: '🎷 爵士' },
  { value: 'classical', label: '🎻 古典' },
  { value: 'electronic', label: '🎹 电子' },
  { value: 'hiphop', label: '🎧 嘻哈' }
]

const list = ref([])
const loading = ref(false)
const keyword = ref('')
const genre = ref(undefined)
const page = ref(1)
const total = ref(0)
const likedSet = ref(new Set())
const ratingsMap = ref({})

function formatDuration(s) {
  if (!s) return '0:00'
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`
}

async function loadBehaviors() {
  try {
    const res = await getUserBehaviors({ item_type: 'music' })
    if (res.code === 200) {
      const likes = res.data.likes || {}
      const ratings = res.data.ratings || {}
      likedSet.value.clear()
      Object.keys(likes).forEach(key => {
        if (key.startsWith('music_')) likedSet.value.add(parseInt(key.split('_')[1]))
      })
      ratingsMap.value = {}
      Object.keys(ratings).forEach(key => {
        if (key.startsWith('music_')) ratingsMap.value[parseInt(key.split('_')[1])] = ratings[key]
      })
    }
  } catch (e) { console.error('加载行为数据失败', e) }
}

async function fetchData() {
  loading.value = true
  try {
    const res = await getMusicList({ 
      page: page.value, 
      per_page: 10, 
      keyword: keyword.value, 
      genre: genre.value || '' 
    })
    if (res.code === 200) {
      list.value = res.data.list.map(item => ({ 
        ...item, 
        _rating: ratingsMap.value[item.id] || 0 
      }))
      total.value = res.data.total
    }
  } finally { 
    loading.value = false 
  }
}

function handleSearch() {
  page.value = 1
  fetchData()
}

async function handleLike(item) {
  if (likedSet.value.has(item.id)) {
    likedSet.value.delete(item.id)
    await deleteBehavior({ item_type: 'music', item_id: item.id, action_type: 'like' })
    message.info('已取消喜欢')
  } else {
    likedSet.value.add(item.id)
    await recordBehavior({ item_type: 'music', item_id: item.id, action_type: 'like' })
    message.success('已添加到喜欢')
  }
}

async function handleRate(item, val) {
  ratingsMap.value[item.id] = val
  await recordBehavior({ item_type: 'music', item_id: item.id, action_type: 'rate', rating: val })
  message.success(`评分成功: ${val} 星`)
}

onMounted(async () => {
  await loadBehaviors()
  await fetchData()
})
</script>

<style lang="scss" scoped>
$primary: #1890ff; $text: #333; $text-muted: #666;

.music-page {
  .music-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  
  .music-card {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 16px 20px;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    transition: all 0.25s;
    border: 1px solid transparent;
    
    &:hover {
      box-shadow: 0 6px 20px rgba(0,0,0,0.12);
      border-color: $primary;
    }
    
    .music-cover {
      width: 56px;
      height: 56px;
      border-radius: 12px;
      background: linear-gradient(135deg, #667eea, #764ba2);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      color: #fff;
      font-size: 22px;
    }
    
    .music-info {
      flex: 1;
      min-width: 0;
      
      .music-title {
        font-size: 16px;
        font-weight: 600;
        color: $text;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      
      .music-artist {
        font-size: 13px;
        color: $text-muted;
        margin-top: 4px;
      }
      
      .music-meta {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 8px;
        font-size: 12px;
        color: #999;
      }
    }
    
    .music-actions {
      display: flex;
      align-items: center;
      gap: 16px;
      flex-shrink: 0;
      
      .like-btn {
        width: 42px; height: 42px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
        font-size: 20px; cursor: pointer; transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1); flex-shrink: 0;
        color: #d1d5db; background: linear-gradient(145deg, #f8f9fa, #e9ecef); 
        border: none; box-shadow: 2px 2px 6px rgba(0,0,0,0.08), -2px -2px 6px rgba(255,255,255,0.9);
        &:hover { color: #ff4d6d; transform: scale(1.08); box-shadow: 3px 3px 8px rgba(0,0,0,0.1), -2px -2px 6px rgba(255,255,255,0.9); }
        &:active { transform: scale(0.95); }
        &.liked { 
          color: #fff; background: linear-gradient(135deg, #ff6b81, #ff4757); 
          box-shadow: 0 4px 15px rgba(255,75,87,0.45), inset 0 1px 0 rgba(255,255,255,0.2);
          animation: heartBeat 0.4s ease;
          &:hover { box-shadow: 0 6px 20px rgba(255,75,87,0.5); transform: scale(1.1); }
        }
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
  
  .empty-state {
    text-align: center;
    padding: 60px 20px;
    
    .empty-icon { font-size: 48px; margin-bottom: 16px; }
    .empty-text { color: $text-muted; font-size: 15px; }
  }
  
  .pagination-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 32px;
    padding-top: 24px;
    border-top: 1px solid rgba(0, 0, 0, 0.06);
  }
}
</style>