<template>
  <div v-if="algo">
    <div class="algo-section">
      <h3>{{ algo.name }}</h3>
      <p>{{ algo.principle }}</p>
    </div>

    <div class="algo-section">
      <h3>算法步骤</h3>
      <ul class="step-list">
        <li v-for="(step, i) in algo.steps" :key="i">{{ step }}</li>
      </ul>
    </div>

    <div class="algo-section">
      <h3>核心公式</h3>
      <div class="formula">{{ algo.formula }}</div>
      <p>{{ algo.formula_desc }}</p>
      <div class="formula">{{ algo.similarity_formula }}</div>
      <p>余弦相似度公式：计算两个用户评分向量的夹角余弦值</p>
    </div>

    <a-row :gutter="16">
      <a-col :span="12">
        <div class="algo-section">
          <h3>优势</h3>
          <div class="tag-group">
            <a-tag color="green" v-for="p in algo.pros" :key="p">{{ p }}</a-tag>
          </div>
        </div>
      </a-col>
      <a-col :span="12">
        <div class="algo-section">
          <h3>局限性</h3>
          <div class="tag-group">
            <a-tag color="orange" v-for="c in algo.cons" :key="c">{{ c }}</a-tag>
          </div>
        </div>
      </a-col>
    </a-row>

    <div class="algo-section">
      <h3>用户-物品评分矩阵示意</h3>
      <p>协同过滤的核心数据结构。行代表用户，列代表物品，值为用户对物品的评分（0表示未评分）。</p>
      <a-table :dataSource="matrixDemo" :columns="matrixColumns" :pagination="false" size="small" bordered style="margin-top: 12px" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAlgorithmInfo } from '../api'

const algo = ref(null)

const matrixColumns = [
  { title: '', dataIndex: 'user', width: 80 },
  { title: '物品A', dataIndex: 'a', align: 'center' },
  { title: '物品B', dataIndex: 'b', align: 'center' },
  { title: '物品C', dataIndex: 'c', align: 'center' },
  { title: '物品D', dataIndex: 'd', align: 'center' },
  { title: '物品E', dataIndex: 'e', align: 'center' }
]

const matrixDemo = [
  { key: 1, user: '用户1', a: 5, b: 3, c: 0, d: 1, e: 4 },
  { key: 2, user: '用户2', a: 4, b: 0, c: 4, d: 2, e: 0 },
  { key: 3, user: '用户3', a: 0, b: 2, c: 5, d: 0, e: 3 },
  { key: 4, user: '用户4', a: 3, b: 4, c: 0, d: 5, e: 2 }
]

onMounted(async () => {
  const res = await getAlgorithmInfo()
  if (res.code === 200) algo.value = res.data
})
</script>
