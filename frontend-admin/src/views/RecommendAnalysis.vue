<template>
  <div>
    <a-row :gutter="16">
      <a-col :span="12">
        <div class="chart-container">
          <div class="card-title">推荐算法分布</div>
          <v-chart :option="algoPieOption" autoresize style="height: 280px" />
        </div>
      </a-col>
      <a-col :span="12">
        <div class="chart-container">
          <div class="card-title">推荐评分分布</div>
          <v-chart :option="scoreBarOption" autoresize style="height: 280px" />
        </div>
      </a-col>
    </a-row>
    <a-row :gutter="16">
      <a-col :span="12">
        <div class="chart-container">
          <div class="card-title">每日推荐量趋势</div>
          <v-chart :option="dailyLineOption" autoresize style="height: 280px" />
        </div>
      </a-col>
      <a-col :span="12">
        <div class="chart-container">
          <div class="card-title">用户相似度热力图</div>
          <div class="search-bar" style="margin-bottom: 8px">
            <a-radio-group v-model:value="simType" size="small" @change="fetchSimilarity">
              <a-radio-button value="news">新闻</a-radio-button>
              <a-radio-button value="music">音乐</a-radio-button>
            </a-radio-group>
          </div>
          <v-chart :option="heatmapOption" autoresize style="height: 240px" />
        </div>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { PieChart, BarChart, LineChart, HeatmapChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent, VisualMapComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { getRecommendationAnalysis, getSimilarityMatrix } from '../api'

use([PieChart, BarChart, LineChart, HeatmapChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, VisualMapComponent, CanvasRenderer])

const recData = ref({})
const simData = ref({ user_ids: [], matrix: [] })
const simType = ref('news')

const algoPieOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { bottom: 0 },
  series: [{ type: 'pie', radius: ['40%', '70%'], data: (recData.value.algorithm_distribution || []).map(d => ({ name: d.algorithm, value: d.count })) }]
}))

const scoreBarOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: (recData.value.score_distribution || []).map(d => d.range) },
  yAxis: { type: 'value' },
  series: [{ type: 'bar', data: (recData.value.score_distribution || []).map(d => d.count), itemStyle: { color: '#722ed1', borderRadius: [4, 4, 0, 0] } }]
}))

const dailyLineOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: (recData.value.daily_recommendations || []).map(d => d.date) },
  yAxis: { type: 'value' },
  series: [{ type: 'line', data: (recData.value.daily_recommendations || []).map(d => d.count), smooth: true, areaStyle: { opacity: 0.15 }, itemStyle: { color: '#eb2f96' } }]
}))

const heatmapOption = computed(() => {
  const ids = simData.value.user_ids || []
  const matrix = simData.value.matrix || []
  const heatData = []
  for (let i = 0; i < matrix.length; i++) {
    for (let j = 0; j < (matrix[i] || []).length; j++) {
      heatData.push([j, i, parseFloat((matrix[i][j] || 0).toFixed(2))])
    }
  }
  return {
    tooltip: { formatter: p => `用户${ids[p.value[1]]} ↔ 用户${ids[p.value[0]]}: ${p.value[2]}` },
    xAxis: { type: 'category', data: ids.map(id => `U${id}`), splitArea: { show: true } },
    yAxis: { type: 'category', data: ids.map(id => `U${id}`), splitArea: { show: true } },
    visualMap: { min: 0, max: 1, calculable: true, orient: 'horizontal', left: 'center', bottom: 0, inRange: { color: ['#f0f2f5', '#1890ff'] } },
    series: [{ type: 'heatmap', data: heatData, emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' } } }]
  }
})

async function fetchSimilarity() {
  const res = await getSimilarityMatrix({ item_type: simType.value })
  if (res.code === 200) simData.value = res.data
}

onMounted(async () => {
  const [recRes] = await Promise.all([getRecommendationAnalysis(), fetchSimilarity()])
  if (recRes.code === 200) recData.value = recRes.data
})
</script>
