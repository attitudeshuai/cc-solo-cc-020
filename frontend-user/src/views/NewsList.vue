<template>
  <div class="news-page">
    <div class="section-title">
      <span class="icon">📰</span>
      <span>新闻资讯</span>
    </div>
    
    <div class="search-bar">
      <a-input v-model:value="keyword" placeholder="搜索新闻..." style="width: 240px" allowClear @pressEnter="handleSearch">
        <template #prefix><SearchOutlined style="color: #999" /></template>
      </a-input>
      <a-select v-model:value="category" placeholder="全部分类" style="width: 140px" allowClear @change="handleSearch">
        <a-select-option v-for="c in categories" :key="c" :value="c">{{ c }}</a-select-option>
      </a-select>
      <a-button type="primary" @click="handleSearch">搜索</a-button>
    </div>
    
    <a-spin :spinning="loading">
      <div class="news-list">
        <div v-for="item in list" :key="item.id" class="news-card" @click="$router.push(`/news/${item.id}`)">
          <div class="news-content">
            <div class="card-title">{{ item.title }}</div>
            <div class="card-desc">{{ item.content }}</div>
            <div class="card-footer">
              <a-tag color="blue">{{ item.category }}</a-tag>
              <span class="meta-item">{{ item.source }}</span>
              <span class="meta-item">👁 {{ item.view_count }}</span>
              <span class="meta-item">{{ formatDate(item.published_at) }}</span>
            </div>
          </div>
          <div class="news-arrow">→</div>
        </div>
      </div>
      <div class="empty-state" v-if="!loading && list.length === 0">
        <div class="empty-icon">📭</div>
        <div class="empty-text">暂无新闻数据</div>
      </div>
    </a-spin>
    
    <div class="pagination-wrapper" v-if="total > 0">
      <a-pagination v-model:current="page" :total="total" :pageSize="10" @change="fetchData" show-quick-jumper size="small" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { SearchOutlined } from '@ant-design/icons-vue'
import { getNewsList } from '../api'

const categories = ['科技', '财经', '体育', '娱乐', '教育', '健康']
const list = ref([]), loading = ref(false), keyword = ref(''), category = ref(undefined), page = ref(1), total = ref(0)

function formatDate(d) { return d ? d.split(' ')[0] : '' }

async function fetchData() {
  loading.value = true
  try {
    const res = await getNewsList({ page: page.value, per_page: 10, keyword: keyword.value, category: category.value || '' })
    if (res.code === 200) { list.value = res.data.list; total.value = res.data.total }
  } finally { loading.value = false }
}

function handleSearch() { page.value = 1; fetchData() }
onMounted(fetchData)
</script>

<style lang="scss" scoped>
$primary: #1890ff; $text: #333; $text-muted: #666; $border: #e8e8e8;

.section-title { font-size: 20px; font-weight: 600; margin-bottom: 20px; display: flex; align-items: center; gap: 12px; color: $text;
  .icon { width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, $primary, #40a9ff); display: flex; align-items: center; justify-content: center; font-size: 16px; }
}

.search-bar { background: #fff; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); padding: 16px 20px; margin-bottom: 20px; display: flex; gap: 12px; flex-wrap: wrap; }

.news-list { display: flex; flex-direction: column; gap: 12px; }

.news-card { display: flex; align-items: center; gap: 16px; padding: 20px 24px; background: #fff; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); cursor: pointer; transition: all 0.25s; border: 1px solid transparent;
  &:hover { box-shadow: 0 6px 20px rgba(0,0,0,0.12); border-color: $primary; }
  
  .news-content { flex: 1; min-width: 0;
    .card-title { font-size: 17px; font-weight: 600; color: $text; margin-bottom: 8px; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
    .card-desc { font-size: 14px; color: $text-muted; line-height: 1.6; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 12px; }
    .card-footer { display: flex; align-items: center; gap: 16px; font-size: 13px; color: #999; flex-wrap: wrap; }
  }
  
  .news-arrow { font-size: 20px; color: #ccc; opacity: 0; transition: all 0.3s; }
  &:hover .news-arrow { opacity: 1; transform: translateX(4px); color: $primary; }
}

.empty-state { text-align: center; padding: 60px 20px; color: #999; .empty-icon { font-size: 48px; margin-bottom: 12px; opacity: 0.6; } }
.pagination-wrapper { display: flex; justify-content: center; margin-top: 32px; padding-top: 24px; border-top: 1px solid $border; }
</style>
