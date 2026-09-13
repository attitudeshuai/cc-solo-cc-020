<template>
  <div>
    <a-card title="采集源配置" :bordered="false" style="margin-bottom: 16px">
      <a-table :dataSource="status.rss_sources || []" :columns="sourceColumns" rowKey="name" :pagination="false" size="small">
        <template #bodyCell="{ column, record }">
          <a-tag v-if="column.key === 'category'" color="blue">{{ record.category }}</a-tag>
        </template>
      </a-table>
      <div style="margin-top: 12px; color: #999; font-size: 13px">
        自动采集间隔：{{ status.collect_interval_hours || '-' }} 小时
      </div>
    </a-card>

    <a-card title="数据统计" :bordered="false" style="margin-bottom: 16px">
      <a-row :gutter="24">
        <a-col :span="12">
          <a-statistic title="新闻总数" :value="status.news_count || 0" style="text-align:center">
            <template #prefix><ReadOutlined /></template>
          </a-statistic>
        </a-col>
        <a-col :span="12">
          <a-statistic title="音乐总数" :value="status.music_count || 0" style="text-align:center">
            <template #prefix><CustomerServiceOutlined /></template>
          </a-statistic>
        </a-col>
      </a-row>
    </a-card>

    <a-card title="手动采集" :bordered="false">
      <p style="color: #666; margin-bottom: 16px">点击下方按钮立即触发一次数据采集（从 RSS 源抓取新闻、从 MusicBrainz 获取音乐）</p>
      <a-button type="primary" :loading="collecting" @click="handleCollect">
        <template #icon><CloudDownloadOutlined /></template>
        立即采集
      </a-button>
      <div v-if="result" style="margin-top: 16px">
        <a-alert type="success" showIcon>
          <template #message>
            采集完成 — 新闻新增 {{ result.news?.collected || 0 }} 条，音乐新增 {{ result.music?.collected || 0 }} 条
          </template>
          <template #description>{{ result.timestamp }}</template>
        </a-alert>
      </div>
    </a-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { ReadOutlined, CustomerServiceOutlined, CloudDownloadOutlined } from '@ant-design/icons-vue'
import { triggerCollection, getCollectionStatus } from '../api'

const status = ref({})
const collecting = ref(false)
const result = ref(null)

const sourceColumns = [
  { title: '名称', dataIndex: 'name', key: 'name' },
  { title: '分类', dataIndex: 'category', key: 'category' },
]

async function loadStatus() {
  try {
    const res = await getCollectionStatus()
    status.value = res.data || {}
  } catch { /* ignore */ }
}

async function handleCollect() {
  collecting.value = true
  result.value = null
  try {
    const res = await triggerCollection()
    result.value = res.data
    message.success('数据采集完成')
    loadStatus()
  } catch {
    message.error('采集失败，请稍后重试')
  } finally {
    collecting.value = false
  }
}

onMounted(loadStatus)
</script>
