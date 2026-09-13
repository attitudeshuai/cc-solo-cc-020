<template>
  <div>
    <a-row :gutter="16" style="margin-bottom: 16px">
      <a-col :span="6" v-for="item in stats" :key="item.label">
        <div class="stat-card">
          <div class="stat-value">{{ item.value }}</div>
          <div class="stat-label">{{ item.label }}</div>
        </div>
      </a-col>
    </a-row>
    <a-row :gutter="16">
      <a-col :span="12">
        <div class="chart-container">
          <div class="card-title">行为类型分布 (新闻)</div>
          <v-chart :option="actionChartOption" autoresize style="height: 280px" />
        </div>
      </a-col>
      <a-col :span="12">
        <div class="chart-container">
          <div class="card-title">分类热度</div>
          <v-chart :option="categoryChartOption" autoresize style="height: 280px" />
        </div>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { PieChart, BarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { getOverview, getBehaviorAnalysis } from '../api'

use([PieChart, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, CanvasRenderer])

const overview = ref({})
const behaviorData = ref({})

const stats = computed(() => [
  { label: '用户总数', value: overview.value.user_count || 0 },
  { label: '新闻总数', value: overview.value.news_count || 0 },
  { label: '音乐总数', value: overview.value.music_count || 0 },
  { label: '行为记录', value: overview.value.behavior_count || 0 }
])

const actionChartOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { bottom: 0 },
  series: [{
    type: 'pie', radius: ['40%', '70%'],
    data: (behaviorData.value.action_distribution || []).map(d => ({ name: d.type, value: d.count })),
    emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.5)' } }
  }]
}))

const categoryChartOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: (behaviorData.value.category_heat || []).map(d => d.category) },
  yAxis: { type: 'value' },
  series: [{
    type: 'bar', data: (behaviorData.value.category_heat || []).map(d => d.count),
    itemStyle: { color: '#1890ff', borderRadius: [4, 4, 0, 0] }
  }]
}))

onMounted(async () => {
  const [ovRes, bhRes] = await Promise.all([getOverview(), getBehaviorAnalysis({ item_type: 'news' })])
  if (ovRes.code === 200) overview.value = ovRes.data
  if (bhRes.code === 200) behaviorData.value = bhRes.data
})
</script>
