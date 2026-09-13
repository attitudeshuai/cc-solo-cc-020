<template>
  <div>
    <div class="search-bar">
      <a-radio-group v-model:value="itemType" button-style="solid" @change="fetchData">
        <a-radio-button value="news">新闻</a-radio-button>
        <a-radio-button value="music">音乐</a-radio-button>
      </a-radio-group>
    </div>
    <a-row :gutter="16">
      <a-col :span="12">
        <div class="chart-container">
          <div class="card-title">行为类型分布</div>
          <v-chart :option="actionPieOption" autoresize style="height: 280px" />
        </div>
      </a-col>
      <a-col :span="12">
        <div class="chart-container">
          <div class="card-title">评分分布</div>
          <v-chart :option="ratingBarOption" autoresize style="height: 280px" />
        </div>
      </a-col>
    </a-row>
    <a-row :gutter="16">
      <a-col :span="12">
        <div class="chart-container">
          <div class="card-title">每日行为趋势</div>
          <v-chart :option="trendLineOption" autoresize style="height: 280px" />
        </div>
      </a-col>
      <a-col :span="12">
        <div class="chart-container">
          <div class="card-title">分类热度</div>
          <v-chart :option="categoryBarOption" autoresize style="height: 280px" />
        </div>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { PieChart, BarChart, LineChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { getBehaviorAnalysis } from '../api'

use([PieChart, BarChart, LineChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, CanvasRenderer])

const itemType = ref('news')
const data = ref({})

const actionPieOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { bottom: 0 },
  color: ['#1890ff', '#52c41a', '#faad14', '#ff4d4f'],
  series: [{ type: 'pie', radius: ['40%', '70%'], data: (data.value.action_distribution || []).map(d => ({ name: d.type, value: d.count })) }]
}))

const ratingBarOption = computed(() => {
  const dist = data.value.rating_distribution || {}
  return {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: Object.keys(dist) },
    yAxis: { type: 'value' },
    series: [{ type: 'bar', data: Object.values(dist), itemStyle: { color: '#52c41a', borderRadius: [4, 4, 0, 0] } }]
  }
})

const trendLineOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: (data.value.daily_trend || []).map(d => d.date) },
  yAxis: { type: 'value' },
  series: [{ type: 'line', data: (data.value.daily_trend || []).map(d => d.count), smooth: true, areaStyle: { opacity: 0.15 }, itemStyle: { color: '#1890ff' } }]
}))

const categoryBarOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: (data.value.category_heat || []).map(d => d.category), axisLabel: { rotate: 30 } },
  yAxis: { type: 'value' },
  series: [{ type: 'bar', data: (data.value.category_heat || []).map(d => d.count), itemStyle: { color: '#faad14', borderRadius: [4, 4, 0, 0] } }]
}))

async function fetchData() {
  const res = await getBehaviorAnalysis({ item_type: itemType.value })
  if (res.code === 200) data.value = res.data
}

onMounted(fetchData)
</script>
