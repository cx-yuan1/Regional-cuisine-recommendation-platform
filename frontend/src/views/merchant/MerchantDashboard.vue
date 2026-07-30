<template>
  <div class="merchant-dashboard">
    <h2>商家首页</h2>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stats-card">
        <div class="card-icon food-icon">
          <el-icon><Food /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-title">美食数量</div>
          <div class="card-value">{{ stats.food_count }}</div>
        </div>
      </div>
      <div class="stats-card">
        <div class="card-icon comment-icon">
          <el-icon><ChatDotRound /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-title">评论总数</div>
          <div class="card-value">{{ stats.comment_count }}</div>
        </div>
      </div>
      <div class="stats-card">
        <div class="card-icon favorite-icon">
          <el-icon><Star /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-title">收藏总数</div>
          <div class="card-value">{{ stats.favorite_count }}</div>
        </div>
      </div>
      <div class="stats-card">
        <div class="card-icon view-icon">
          <el-icon><View /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-title">总浏览量</div>
          <div class="card-value">{{ stats.total_view_count }}</div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-container">
      <!-- 评论趋势（折线图） -->
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">评论趋势</h3>
          <el-radio-group v-model="trendDays" size="small" @change="loadData">
            <el-radio-button label="7">近7天</el-radio-button>
            <el-radio-button label="14">近14天</el-radio-button>
            <el-radio-button label="30">近30天</el-radio-button>
          </el-radio-group>
        </div>
        <div class="chart-content">
          <div ref="trendChartRef" class="chart"></div>
        </div>
      </div>

      <!-- 美食分类分布（饼图） -->
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">美食分类分布</h3>
        </div>
        <div class="chart-content">
          <div v-if="categoryData.length > 0" ref="categoryChartRef" class="chart"></div>
          <el-empty v-else description="暂无美食数据" />
        </div>
      </div>

      <!-- 评分分布（柱状图） -->
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">评分分布</h3>
        </div>
        <div class="chart-content">
          <div ref="ratingChartRef" class="chart"></div>
        </div>
      </div>

      <!-- 美食浏览量 TOP10（柱状图） -->
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">美食浏览量 TOP10</h3>
          <el-button type="primary" link @click="$router.push('/merchant/foods')">发布美食</el-button>
        </div>
        <div class="chart-content">
          <div v-if="topFoods.length > 0" ref="viewChartRef" class="chart"></div>
          <el-empty v-else description="暂无美食数据" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { Food, ChatDotRound, Star, View } from '@element-plus/icons-vue'
import { merchantApi } from '@/api/merchant'

const trendDays = ref('7')
const trendChartRef = ref<HTMLElement>()
const categoryChartRef = ref<HTMLElement>()
const ratingChartRef = ref<HTMLElement>()
const viewChartRef = ref<HTMLElement>()

const stats = reactive({
  food_count: 0,
  comment_count: 0,
  favorite_count: 0,
  unreplied_count: 0,
  total_view_count: 0
})

const commentTrend = ref<Array<{ date: string; count: number }>>([])
const categoryData = ref<Array<{ name: string; count: number }>>([])
const ratingDist = ref<Array<{ rating: number; count: number }>>([])
const topFoods = ref<Array<{ name: string; view_count: number }>>([])

let trendChart: echarts.ECharts | null = null
let categoryChart: echarts.ECharts | null = null
let ratingChart: echarts.ECharts | null = null
let viewChart: echarts.ECharts | null = null

const loadData = async () => {
  try {
    const res = await merchantApi.getStatistics({ days: parseInt(trendDays.value) })
    const data = res.data
    if (!data) return

    Object.assign(stats, data.overview || {})
    commentTrend.value = data.comment_trend || []
    categoryData.value = data.by_category || []
    ratingDist.value = data.rating_distribution || []
    topFoods.value = data.top_foods_by_view || []

    await nextTick()
    initTrendChart()
    initCategoryChart()
    initRatingChart()
    initViewChart()
  } catch (e) {
    console.error(e)
  }
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  trendChart = echarts.init(trendChartRef.value)
  const labels = commentTrend.value.map((t) => t.date.slice(5))
  const values = commentTrend.value.map((t) => t.count)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: labels },
    yAxis: { type: 'value' },
    series: [{
      name: '评论数',
      type: 'line',
      smooth: true,
      areaStyle: { opacity: 0.3 },
      data: values
    }]
  })
}

const initCategoryChart = () => {
  if (!categoryChartRef.value) return
  categoryChart = echarts.init(categoryChartRef.value)
  const colors = ['#67c23a', '#409eff', '#e6a23c', '#f56c6c', '#909399', '#a8d8ea']
  const data = categoryData.value.map((c, i) => ({
    value: c.count,
    name: c.name,
    itemStyle: { color: colors[i % colors.length] }
  }))
  categoryChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{ type: 'pie', radius: '60%', data }]
  })
}

const initRatingChart = () => {
  if (!ratingChartRef.value) return
  ratingChart = echarts.init(ratingChartRef.value)
  const labels = ratingDist.value.map((r) => `${r.rating}星`)
  const values = ratingDist.value.map((r) => r.count)
  ratingChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: labels },
    yAxis: { type: 'value' },
    series: [{
      name: '评论数',
      type: 'bar',
      itemStyle: { color: '#67c23a' },
      data: values
    }]
  })
}

const initViewChart = () => {
  if (!viewChartRef.value) return
  viewChart = echarts.init(viewChartRef.value)
  const labels = topFoods.value.map((f) => f.name.length > 8 ? f.name.slice(0, 8) + '...' : f.name)
  const values = topFoods.value.map((f) => f.view_count)
  viewChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: labels, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value' },
    series: [{
      name: '浏览量',
      type: 'bar',
      itemStyle: { color: '#409eff' },
      data: values
    }]
  })
}

watch(trendDays, () => {
  loadData()
})

onMounted(loadData)
</script>

<style scoped lang="scss">
.merchant-dashboard {
  h2 { margin: 0 0 24px 0; font-size: 20px; color: #303133; }
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stats-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 16px;
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
  &.food-icon { background: #67c23a; }
  &.comment-icon { background: #409eff; }
  &.favorite-icon { background: #e6a23c; }
  &.view-icon { background: #909399; }
}

.card-content {
  flex: 1;
  .card-title { font-size: 14px; color: #909399; margin-bottom: 4px; }
  .card-value { font-size: 22px; font-weight: 600; color: #303133; }
}

.charts-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  .chart-title { margin: 0; font-size: 16px; color: #303133; }
}

.chart-content {
  position: relative;
  .chart { width: 100%; height: 280px; }
}

@media (max-width: 1200px) {
  .stats-cards { grid-template-columns: repeat(2, 1fr); }
  .charts-container { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .stats-cards { grid-template-columns: 1fr; }
}
</style>
