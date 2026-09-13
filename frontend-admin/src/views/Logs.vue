<template>
  <div class="table-card">
    <a-table :dataSource="list" :columns="columns" :loading="loading" :pagination="pagination"
             @change="handleTableChange" rowKey="id" size="middle">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'action'">
          <a-tag :color="actionColor(record.action)">{{ record.action }}</a-tag>
        </template>
      </template>
    </a-table>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getLogs } from '../api'

const list = ref([])
const loading = ref(false)
const pagination = reactive({ current: 1, pageSize: 20, total: 0 })

const columns = [
  { title: 'ID', dataIndex: 'id', width: 60 },
  { title: '用户ID', dataIndex: 'user_id', width: 80 },
  { title: '模块', dataIndex: 'module', width: 80 },
  { title: '操作', key: 'action', width: 80 },
  { title: '详情', dataIndex: 'detail', ellipsis: true },
  { title: 'IP', dataIndex: 'ip', width: 120 },
  { title: '时间', dataIndex: 'created_at', width: 170 }
]

function actionColor(action) {
  const map = { login: 'blue', create: 'green', update: 'orange', delete: 'red' }
  return map[action] || 'default'
}

async function fetchData() {
  loading.value = true
  try {
    const res = await getLogs({ page: pagination.current, per_page: pagination.pageSize })
    if (res.code === 200) { list.value = res.data.list; pagination.total = res.data.total }
  } finally { loading.value = false }
}

function handleTableChange(pag) { pagination.current = pag.current; fetchData() }

onMounted(fetchData)
</script>
