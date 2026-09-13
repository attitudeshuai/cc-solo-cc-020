<template>
  <div class="table-card">
    <div class="search-bar">
      <a-input v-model:value="keyword" placeholder="搜索新闻标题" style="width: 200px" allowClear @pressEnter="fetchData" />
      <a-select v-model:value="category" placeholder="分类筛选" style="width: 120px" allowClear @change="fetchData">
        <a-select-option v-for="c in categories" :key="c" :value="c">{{ c }}</a-select-option>
      </a-select>
      <a-button type="primary" @click="openCreate">新增新闻</a-button>
    </div>
    <a-table :dataSource="list" :columns="columns" :loading="loading" :pagination="pagination"
             @change="handleTableChange" rowKey="id" size="middle">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'category'">
          <a-tag color="blue">{{ record.category }}</a-tag>
        </template>
        <template v-if="column.key === 'action'">
          <a-space>
            <a-button size="small" @click="openEdit(record)">编辑</a-button>
            <a-popconfirm title="确认删除？" @confirm="handleDelete(record.id)">
              <a-button size="small" danger>删除</a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>

    <a-modal v-model:open="modalVisible" :title="isEdit ? '编辑新闻' : '新增新闻'" @ok="handleSubmit" :confirmLoading="submitLoading" width="640px">
      <a-form layout="vertical">
        <a-form-item label="标题"><a-input v-model:value="form.title" /></a-form-item>
        <a-form-item label="分类">
          <a-select v-model:value="form.category">
            <a-select-option v-for="c in categories" :key="c" :value="c">{{ c }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="来源"><a-input v-model:value="form.source" /></a-form-item>
        <a-form-item label="内容"><a-textarea v-model:value="form.content" :rows="4" /></a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { getNewsList, createNews, updateNews, deleteNews } from '../api'

const categories = ['科技', '财经', '体育', '娱乐', '教育', '健康']
const list = ref([])
const loading = ref(false)
const keyword = ref('')
const category = ref(undefined)
const pagination = reactive({ current: 1, pageSize: 10, total: 0 })

const columns = [
  { title: 'ID', dataIndex: 'id', width: 60 },
  { title: '标题', dataIndex: 'title', ellipsis: true },
  { title: '分类', key: 'category', width: 80 },
  { title: '来源', dataIndex: 'source', width: 120 },
  { title: '浏览量', dataIndex: 'view_count', width: 80 },
  { title: '发布时间', dataIndex: 'published_at', width: 170 },
  { title: '操作', key: 'action', width: 160 }
]

const modalVisible = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const form = reactive({ id: 0, title: '', content: '', category: '科技', source: '' })

async function fetchData() {
  loading.value = true
  try {
    const res = await getNewsList({ page: pagination.current, per_page: pagination.pageSize, keyword: keyword.value, category: category.value || '' })
    if (res.code === 200) { list.value = res.data.list; pagination.total = res.data.total }
  } finally { loading.value = false }
}

function handleTableChange(pag) { pagination.current = pag.current; fetchData() }

function openCreate() {
  isEdit.value = false
  Object.assign(form, { id: 0, title: '', content: '', category: '科技', source: '' })
  modalVisible.value = true
}

function openEdit(record) {
  isEdit.value = true
  Object.assign(form, record)
  modalVisible.value = true
}

async function handleSubmit() {
  if (!form.title || !form.content) { message.warning('请填写标题和内容'); return }
  submitLoading.value = true
  try {
    const res = isEdit.value ? await updateNews(form.id, form) : await createNews(form)
    if (res.code === 200) { message.success(isEdit.value ? '更新成功' : '创建成功'); modalVisible.value = false; fetchData() }
  } finally { submitLoading.value = false }
}

async function handleDelete(id) {
  const res = await deleteNews(id)
  if (res.code === 200) { message.success('删除成功'); fetchData() }
}

onMounted(fetchData)
</script>
