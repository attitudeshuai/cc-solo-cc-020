<template>
  <div class="table-card">
    <div class="search-bar">
      <a-button type="primary" @click="fetchData">刷新</a-button>
    </div>
    <a-table :dataSource="list" :columns="columns" :loading="loading" :pagination="pagination"
             @change="handleTableChange" rowKey="id" size="middle">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'role'">
          <a-tag :color="record.role === 'admin' ? 'red' : 'blue'">{{ record.role === 'admin' ? '管理员' : '用户' }}</a-tag>
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

    <a-modal v-model:open="editVisible" title="编辑用户" @ok="handleEdit" :confirmLoading="editLoading">
      <a-form layout="vertical">
        <a-form-item label="昵称">
          <a-input v-model:value="editForm.nickname" />
        </a-form-item>
        <a-form-item label="角色">
          <a-select v-model:value="editForm.role">
            <a-select-option value="user">用户</a-select-option>
            <a-select-option value="admin">管理员</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { getUsers, updateUser, deleteUser } from '../api'

const list = ref([])
const loading = ref(false)
const pagination = reactive({ current: 1, pageSize: 10, total: 0 })

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: '用户名', dataIndex: 'username', key: 'username' },
  { title: '昵称', dataIndex: 'nickname', key: 'nickname' },
  { title: '角色', key: 'role' },
  { title: '注册时间', dataIndex: 'created_at', key: 'created_at' },
  { title: '操作', key: 'action', width: 160 }
]

const editVisible = ref(false)
const editLoading = ref(false)
const editForm = reactive({ id: 0, nickname: '', role: 'user' })

async function fetchData() {
  loading.value = true
  try {
    const res = await getUsers({ page: pagination.current, per_page: pagination.pageSize })
    if (res.code === 200) {
      list.value = res.data.list
      pagination.total = res.data.total
    }
  } finally { loading.value = false }
}

function handleTableChange(pag) {
  pagination.current = pag.current
  fetchData()
}

function openEdit(record) {
  Object.assign(editForm, { id: record.id, nickname: record.nickname, role: record.role })
  editVisible.value = true
}

async function handleEdit() {
  editLoading.value = true
  try {
    const res = await updateUser(editForm.id, { nickname: editForm.nickname, role: editForm.role })
    if (res.code === 200) { message.success('更新成功'); editVisible.value = false; fetchData() }
  } finally { editLoading.value = false }
}

async function handleDelete(id) {
  const res = await deleteUser(id)
  if (res.code === 200) { message.success('删除成功'); fetchData() }
}

onMounted(fetchData)
</script>
