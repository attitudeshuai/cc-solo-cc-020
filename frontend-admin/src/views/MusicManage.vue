<template>
  <div class="table-card">
    <div class="search-bar">
      <a-input v-model:value="keyword" placeholder="搜索音乐" style="width: 200px" allowClear @pressEnter="fetchData" />
      <a-select v-model:value="genre" placeholder="风格筛选" style="width: 120px" allowClear @change="fetchData">
        <a-select-option v-for="g in genres" :key="g" :value="g">{{ g }}</a-select-option>
      </a-select>
      <a-button type="primary" @click="openCreate">新增音乐</a-button>
    </div>
    <a-table :dataSource="list" :columns="columns" :loading="loading" :pagination="pagination"
             @change="handleTableChange" rowKey="id" size="middle">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'genre'">
          <a-tag color="green">{{ record.genre }}</a-tag>
        </template>
        <template v-if="column.key === 'duration'">{{ formatDuration(record.duration) }}</template>
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

    <a-modal v-model:open="modalVisible" :title="isEdit ? '编辑音乐' : '新增音乐'" @ok="handleSubmit" :confirmLoading="submitLoading" width="560px">
      <a-form layout="vertical">
        <a-form-item label="歌曲名"><a-input v-model:value="form.title" /></a-form-item>
        <a-form-item label="艺术家"><a-input v-model:value="form.artist" /></a-form-item>
        <a-form-item label="专辑"><a-input v-model:value="form.album" /></a-form-item>
        <a-form-item label="风格">
          <a-select v-model:value="form.genre">
            <a-select-option v-for="g in genres" :key="g" :value="g">{{ g }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="时长(秒)"><a-input-number v-model:value="form.duration" :min="0" style="width: 100%" /></a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { getMusicList, createMusic, updateMusic, deleteMusic } from '../api'

const genres = ['pop', 'rock', 'jazz', 'classical', 'electronic', 'hiphop']
const list = ref([])
const loading = ref(false)
const keyword = ref('')
const genre = ref(undefined)
const pagination = reactive({ current: 1, pageSize: 10, total: 0 })

const columns = [
  { title: 'ID', dataIndex: 'id', width: 60 },
  { title: '歌曲名', dataIndex: 'title', ellipsis: true },
  { title: '艺术家', dataIndex: 'artist', width: 120 },
  { title: '专辑', dataIndex: 'album', ellipsis: true, width: 150 },
  { title: '风格', key: 'genre', width: 100 },
  { title: '时长', key: 'duration', width: 80 },
  { title: '播放量', dataIndex: 'play_count', width: 80 },
  { title: '操作', key: 'action', width: 160 }
]

const modalVisible = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const form = reactive({ id: 0, title: '', artist: '', album: '', genre: 'pop', duration: 0 })

function formatDuration(s) { return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}` }

async function fetchData() {
  loading.value = true
  try {
    const res = await getMusicList({ page: pagination.current, per_page: pagination.pageSize, keyword: keyword.value, genre: genre.value || '' })
    if (res.code === 200) { list.value = res.data.list; pagination.total = res.data.total }
  } finally { loading.value = false }
}

function handleTableChange(pag) { pagination.current = pag.current; fetchData() }
function openCreate() { isEdit.value = false; Object.assign(form, { id: 0, title: '', artist: '', album: '', genre: 'pop', duration: 0 }); modalVisible.value = true }
function openEdit(record) { isEdit.value = true; Object.assign(form, record); modalVisible.value = true }

async function handleSubmit() {
  if (!form.title || !form.artist) { message.warning('请填写歌曲名和艺术家'); return }
  submitLoading.value = true
  try {
    const res = isEdit.value ? await updateMusic(form.id, form) : await createMusic(form)
    if (res.code === 200) { message.success(isEdit.value ? '更新成功' : '创建成功'); modalVisible.value = false; fetchData() }
  } finally { submitLoading.value = false }
}

async function handleDelete(id) {
  const res = await deleteMusic(id)
  if (res.code === 200) { message.success('删除成功'); fetchData() }
}

onMounted(fetchData)
</script>
