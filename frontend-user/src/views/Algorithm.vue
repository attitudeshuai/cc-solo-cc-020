<template>
  <div class="algo-page">
    <!-- 我的兴趣画像 -->
    <div class="section-title"><span class="icon">📊</span><span>我的兴趣画像</span></div>
    <a-row :gutter="16" class="profile-section">
      <a-col :xs="24" :md="8">
        <div class="stat-card">
          <div class="stat-grid">
            <div class="stat-item"><div class="stat-value">{{ profile.stats?.total_actions || 0 }}</div><div class="stat-label">总互动</div></div>
            <div class="stat-item"><div class="stat-value">{{ profile.stats?.likes || 0 }}</div><div class="stat-label">点赞</div></div>
            <div class="stat-item"><div class="stat-value">{{ profile.stats?.ratings || 0 }}</div><div class="stat-label">评分</div></div>
            <div class="stat-item"><div class="stat-value">{{ profile.stats?.avg_rating || '-' }}</div><div class="stat-label">平均分</div></div>
          </div>
        </div>
      </a-col>
      <a-col :xs="24" :sm="12" :md="8">
        <div class="algo-card radar-card">
          <h3>📰 新闻兴趣分布</h3>
          <div class="chart-container" ref="newsChartRef"></div>
          <div class="no-data" v-if="!profile.news_radar?.labels?.length">暂无数据，多浏览新闻吧~</div>
        </div>
      </a-col>
      <a-col :xs="24" :sm="12" :md="8">
        <div class="algo-card radar-card">
          <h3>🎵 音乐兴趣分布</h3>
          <div class="chart-container" ref="musicChartRef"></div>
          <div class="no-data" v-if="!profile.music_radar?.labels?.length">暂无数据，多听听音乐吧~</div>
        </div>
      </a-col>
    </a-row>

    <!-- 算法原理 -->
    <div class="section-title" style="margin-top: 20px"><span class="icon">🧠</span><span>协同过滤算法原理</span></div>
    <a-spin :spinning="!algo">
      <template v-if="algo">
        <div class="algo-card intro-card">
          <div class="card-header"><h2>{{ algo.name }}</h2><div class="algo-badge">User-Based CF</div></div>
          <p class="principle">{{ algo.principle }}</p>
        </div>
        <div class="algo-card">
          <h3>📋 算法执行步骤</h3>
          <div class="steps-timeline">
            <div class="step-item" v-for="(step, i) in algo.steps" :key="i">
              <div class="step-marker"><div class="step-num">{{ i + 1 }}</div><div class="step-line" v-if="i < algo.steps.length - 1"></div></div>
              <div class="step-content"><div class="step-text">{{ step.replace(/^\d+\.\s*/, '') }}</div></div>
            </div>
          </div>
        </div>
        <div class="algo-card">
          <h3>📐 核心数学公式</h3>
          <div class="formula-grid">
            <div class="formula-box"><div class="formula-title">预测评分公式</div><div class="formula">{{ algo.formula }}</div><p class="formula-desc">{{ algo.formula_desc }}</p></div>
            <div class="formula-box"><div class="formula-title">余弦相似度</div><div class="formula">{{ algo.similarity_formula }}</div><p class="formula-desc">衡量两个用户评分向量在方向上的相似程度，值域 [-1, 1]</p></div>
          </div>
        </div>
        <a-row :gutter="16">
          <a-col :xs="24" :md="12"><div class="algo-card"><h3>✅ 算法优势</h3><div class="tag-list"><span class="tag-item pro" v-for="p in algo.pros" :key="p">{{ p }}</span></div></div></a-col>
          <a-col :xs="24" :md="12"><div class="algo-card"><h3>⚠️ 局限性</h3><div class="tag-list"><span class="tag-item con" v-for="c in algo.cons" :key="c">{{ c }}</span></div></div></a-col>
        </a-row>
      </template>
    </a-spin>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getAlgorithmInfo, getMyProfile } from '../api'

const algo = ref(null)
const profile = ref({ stats: {}, news_radar: {}, music_radar: {} })
const newsChartRef = ref(null)
const musicChartRef = ref(null)
let newsChart = null, musicChart = null

function renderRadar(el, data, color) {
  if (!el || !data?.labels?.length) return null
  const chart = echarts.init(el)
  chart.setOption({
    radar: {
      indicator: data.labels.map(name => ({ name, max: 100 })),
      radius: '65%',
      axisName: { color: '#666', fontSize: 12 },
      splitArea: { areaStyle: { color: ['rgba(24,144,255,0.02)', 'rgba(24,144,255,0.05)'] } }
    },
    series: [{
      type: 'radar',
      data: [{ value: data.values, name: '兴趣值', areaStyle: { color: `rgba(${color},0.3)` }, lineStyle: { color: `rgb(${color})` }, itemStyle: { color: `rgb(${color})` } }]
    }]
  })
  return chart
}

onMounted(async () => {
  const [algoRes, profileRes] = await Promise.all([getAlgorithmInfo(), getMyProfile()])
  if (algoRes.code === 200) algo.value = algoRes.data
  if (profileRes.code === 200) profile.value = profileRes.data
  
  await nextTick()
  newsChart = renderRadar(newsChartRef.value, profile.value.news_radar, '24,144,255')
  musicChart = renderRadar(musicChartRef.value, profile.value.music_radar, '114,78,162')
})
</script>

<style lang="scss" scoped>
$primary: #1890ff; $success: #52c41a; $warning: #faad14; $text: #333; $text-muted: #666;

.section-title { font-size: 20px; font-weight: 600; margin-bottom: 20px; display: flex; align-items: center; gap: 12px; color: $text;
  .icon { width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, $primary, #40a9ff); display: flex; align-items: center; justify-content: center; font-size: 16px; }
}

.profile-section { margin-bottom: 24px; }

.stat-card {
  background: linear-gradient(135deg, $primary, #40a9ff); border-radius: 12px; padding: 24px; height: 100%; min-height: 200px;
  display: flex; align-items: center;
  .stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; width: 100%; }
  .stat-item { text-align: center; }
  .stat-value { font-size: 28px; font-weight: 700; color: #fff; }
  .stat-label { font-size: 13px; color: rgba(255,255,255,0.85); margin-top: 4px; }
}

.algo-card { background: #fff; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); padding: 20px; margin-bottom: 16px;
  h3 { font-size: 15px; font-weight: 600; color: $text; margin-bottom: 12px; }
}

.radar-card { height: 100%; min-height: 200px; display: flex; flex-direction: column;
  .chart-container { flex: 1; min-height: 160px; }
  .no-data { flex: 1; display: flex; align-items: center; justify-content: center; color: #999; font-size: 13px; }
}

.intro-card {
  .card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; flex-wrap: wrap; gap: 12px;
    h2 { font-size: 20px; font-weight: 700; color: $primary; margin: 0; }
    .algo-badge { background: linear-gradient(135deg, $primary, #40a9ff); color: #fff; padding: 5px 14px; border-radius: 20px; font-size: 12px; }
  }
  .principle { font-size: 14px; line-height: 1.8; color: $text-muted; margin: 0; }
}

.steps-timeline { display: flex; flex-direction: column; }
.step-item { display: flex; gap: 14px; }
.step-marker { display: flex; flex-direction: column; align-items: center;
  .step-num { width: 26px; height: 26px; border-radius: 50%; background: linear-gradient(135deg, $primary, #40a9ff); color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 12px; }
  .step-line { width: 2px; flex: 1; background: linear-gradient(to bottom, $primary, transparent); min-height: 16px; }
}
.step-content { flex: 1; padding-bottom: 12px; }
.step-text { font-size: 13px; color: $text-muted; line-height: 26px; }

.formula-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; }
.formula-box { background: rgba($primary, 0.05); border-left: 3px solid $primary; border-radius: 0 8px 8px 0; padding: 14px;
  .formula-title { font-size: 12px; font-weight: 600; color: $primary; margin-bottom: 8px; }
  .formula { font-family: 'Fira Code', monospace; font-size: 13px; font-weight: 600; color: $text; margin-bottom: 8px; word-break: break-all; }
  .formula-desc { font-size: 11px; color: $text-muted; margin: 0; line-height: 1.5; }
}

.tag-list { display: flex; flex-wrap: wrap; gap: 8px; }
.tag-item { padding: 5px 12px; border-radius: 16px; font-size: 12px;
  &.pro { background: rgba($success, 0.1); color: $success; }
  &.con { background: rgba($warning, 0.1); color: #d48806; }
}
</style>

<style lang="scss" scoped>
$primary: #1890ff; $purple: #722ed1; $success: #52c41a; $warning: #faad14; $text: #333; $text-muted: #666;

.section-title { font-size: 20px; font-weight: 600; margin-bottom: 24px; display: flex; align-items: center; gap: 12px; color: $text;
  .icon { width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, $primary, #40a9ff); display: flex; align-items: center; justify-content: center; font-size: 16px; }
}

.algo-card { background: #fff; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); padding: 24px; margin-bottom: 20px;
  h3 { font-size: 16px; font-weight: 600; color: $text; margin-bottom: 16px; }
}

.chart-card {
  .chart-container { height: 220px; }
  .top-interest { text-align: center; font-size: 13px; color: $text-muted; margin-top: 8px;
    .highlight { color: $primary; font-weight: 600; }
  }
}

.stats-summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px;
  .stat-item { background: #fff; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    .stat-value { font-size: 28px; font-weight: 700; color: $primary; }
    .stat-label { font-size: 13px; color: $text-muted; margin-top: 4px; }
  }
}

.empty-stats { text-align: center; padding: 48px; background: #fff; border-radius: 12px; color: $text-muted; margin-bottom: 20px;
  .empty-icon { font-size: 48px; margin-bottom: 12px; }
}

.intro-card {
  .card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; flex-wrap: wrap; gap: 12px;
    h2 { font-size: 22px; font-weight: 700; color: $primary; margin: 0; }
    .algo-badge { background: linear-gradient(135deg, $primary, #40a9ff); color: #fff; padding: 6px 16px; border-radius: 20px; font-size: 13px; }
  }
  .principle { font-size: 14px; line-height: 1.8; color: $text-muted; margin: 0; }
}

.steps-timeline { display: flex; flex-direction: column; }
.step-item { display: flex; gap: 16px; }
.step-marker { display: flex; flex-direction: column; align-items: center;
  .step-num { width: 28px; height: 28px; border-radius: 50%; background: linear-gradient(135deg, $primary, #40a9ff); color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13px; }
  .step-line { width: 2px; flex: 1; background: linear-gradient(to bottom, $primary, transparent); min-height: 20px; }
}
.step-content { flex: 1; padding-bottom: 16px; }
.step-text { font-size: 14px; color: $text-muted; line-height: 28px; }

.formula-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }
.formula-box { background: rgba($primary, 0.05); border-left: 4px solid $primary; border-radius: 0 10px 10px 0; padding: 16px;
  .formula-title { font-size: 13px; font-weight: 600; color: $primary; margin-bottom: 10px; }
  .formula { font-family: 'Fira Code', monospace; font-size: 14px; font-weight: 600; color: $text; margin-bottom: 10px; word-break: break-all; }
  .formula-desc { font-size: 12px; color: $text-muted; margin: 0; line-height: 1.6; }
}

.tag-list { display: flex; flex-wrap: wrap; gap: 10px; }
.tag-item { padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 500;
  &.pro { background: rgba($success, 0.1); color: $success; border: 1px solid rgba($success, 0.2); }
  &.con { background: rgba($warning, 0.1); color: #d48806; border: 1px solid rgba($warning, 0.2); }
}

@media (max-width: 768px) {
  .stats-summary { grid-template-columns: repeat(2, 1fr); }
}
</style>
