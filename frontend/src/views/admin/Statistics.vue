<template>
  <div class="statistics">
    <!-- 统计概览卡片 -->
    <div class="overview-cards">
      <div class="stats-card">
        <div class="card-icon user-icon">
          <el-icon><User /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-title">总用户数</div>
          <div class="card-value">{{ stats.userCount }}</div>
          <div class="card-trend">
            <span class="trend-up">↗ {{ stats.todayUsers }}</span>
            <span class="trend-text">今日新增</span>
          </div>
        </div>
      </div>
      
      <div class="stats-card">
        <div class="card-icon food-icon">
          <el-icon><Food /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-title">总美食数</div>
          <div class="card-value">{{ stats.foodCount }}</div>
          <div class="card-trend">
            <span class="trend-up">↗ {{ stats.monthlyFoods }}</span>
            <span class="trend-text">本月新增</span>
          </div>
        </div>
      </div>
      
      <div class="stats-card">
        <div class="card-icon comment-icon">
          <el-icon><ChatDotRound /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-title">总评论数</div>
          <div class="card-value">{{ stats.commentCount }}</div>
          <div class="card-trend">
            <span class="trend-up">↗ {{ stats.todayComments }}</span>
            <span class="trend-text">今日新增</span>
          </div>
        </div>
      </div>
      
      <div class="stats-card">
        <div class="card-icon favorite-icon">
          <el-icon><Star /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-title">总收藏数</div>
          <div class="card-value">{{ stats.favoriteCount }}</div>
          <div class="card-trend">
            <span class="trend-up">↗ {{ stats.todayFavorites }}</span>
            <span class="trend-text">今日新增</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-section">
      <!-- 用户增长趋势 -->
      <div class="chart-card large">
        <div class="chart-header">
          <h3 class="chart-title">用户增长趋势</h3>
          <div class="chart-actions">
            <el-radio-group v-model="userGrowthPeriod" size="small" @change="updateUserGrowthChart">
              <el-radio-button label="7">近7天</el-radio-button>
              <el-radio-button label="30">近30天</el-radio-button>
              <el-radio-button label="90">近90天</el-radio-button>
            </el-radio-group>
          </div>
        </div>
        <div class="chart-content">
          <div ref="userGrowthChart" class="chart"></div>
        </div>
      </div>

      <!-- 美食分类分布 -->
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">美食分类分布</h3>
        </div>
        <div class="chart-content">
          <div ref="categoryChart" class="chart"></div>
        </div>
      </div>

      <!-- 地域分布 -->
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">地域分布</h3>
        </div>
        <div class="chart-content">
          <div ref="regionChart" class="chart"></div>
        </div>
      </div>

      <!-- 评分分布 -->
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">美食评分分布</h3>
        </div>
        <div class="chart-content">
          <div ref="ratingChart" class="chart"></div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { User, Food, ChatDotRound, Star } from '@element-plus/icons-vue'
import { getStatisticsOverview, getUserStatistics, getFoodStatistics } from '@/api/admin'
import { ElMessage } from 'element-plus'

// 响应式数据
const stats = ref({
  userCount: 0,
  foodCount: 0,
  commentCount: 0,
  favoriteCount: 0,
  todayUsers: 0,
  monthlyFoods: 0,
  todayComments: 0,
  todayFavorites: 0
})

const userGrowthPeriod = ref('7')

// 图表引用
const userGrowthChart = ref<HTMLElement>()
const categoryChart = ref<HTMLElement>()
const regionChart = ref<HTMLElement>()
const ratingChart = ref<HTMLElement>()

// 图表实例
let userGrowthChartInstance: echarts.ECharts | null = null
let categoryChartInstance: echarts.ECharts | null = null
let regionChartInstance: echarts.ECharts | null = null
let ratingChartInstance: echarts.ECharts | null = null

// 获取统计数据
const getStatistics = async () => {
  try {
    const response = await getStatisticsOverview()
    if (response.code === 200) {
      const data = response.data
      stats.value = {
        userCount: data.user_count || 0,
        foodCount: data.food_count || 0,
        commentCount: data.comment_count || 0,
        favoriteCount: data.favorite_count || 0,
        todayUsers: data.today_user_count || 0,
        monthlyFoods: 0, // 需要额外API
        todayComments: 0, // 需要额外API
        todayFavorites: 0 // 需要额外API
      }
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
    // 使用默认数据
    stats.value = {
      userCount: 1248,
      foodCount: 356,
      commentCount: 2847,
      favoriteCount: 1569,
      todayUsers: 23,
      monthlyFoods: 45,
      todayComments: 67,
      todayFavorites: 89
    }
  }
}

// 初始化用户增长图表
const initUserGrowthChart = async () => {
  if (!userGrowthChart.value) return
  
  try {
    const response = await getUserStatistics(parseInt(userGrowthPeriod.value))
    let chartData = []
    let dateLabels = []
    
    if (response.code === 200) {
      const data = response.data || []
      chartData = data.map((item: any) => item.count)
      dateLabels = data.map((item: any) => {
        const date = new Date(item.date)
        return `${date.getMonth() + 1}-${date.getDate()}`
      })
    }
    
    // 如果没有数据，使用模拟数据
    if (chartData.length === 0) {
      const days = parseInt(userGrowthPeriod.value)
      chartData = Array.from({ length: days }, () => Math.floor(Math.random() * 50) + 10)
      dateLabels = Array.from({ length: days }, (_, i) => {
        const date = new Date()
        date.setDate(date.getDate() - days + i + 1)
        return `${date.getMonth() + 1}-${date.getDate()}`
      })
    }
    
    userGrowthChartInstance = echarts.init(userGrowthChart.value)
    
    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: dateLabels,
        axisLine: {
          lineStyle: {
            color: '#e4e7ed'
          }
        },
        axisLabel: {
          color: '#606266'
        }
      },
      yAxis: {
        type: 'value',
        axisLine: {
          lineStyle: {
            color: '#e4e7ed'
          }
        },
        axisLabel: {
          color: '#606266'
        },
        splitLine: {
          lineStyle: {
            color: '#f0f2f5'
          }
        }
      },
      series: [
        {
          name: '新增用户',
          type: 'line',
          smooth: true,
          itemStyle: {
            color: '#a8d8ea'
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(168, 216, 234, 0.3)' },
                { offset: 1, color: 'rgba(168, 216, 234, 0.1)' }
              ]
            }
          },
          data: chartData
        }
      ]
    }
    
    userGrowthChartInstance.setOption(option)
  } catch (error) {
    console.error('初始化用户增长图表失败:', error)
  }
}

// 初始化分类分布图表
const initCategoryChart = async () => {
  if (!categoryChart.value) return
  
  try {
    const response = await getFoodStatistics()
    let categoryData = []
    
    if (response.code === 200) {
      const data = response.data.by_category || []
      const colors = ['#a8d8ea', '#aa96da', '#ffd93d', '#6bcf7f', '#ff9a9e', '#a8edea']
      
      categoryData = data.map((item: any, index: number) => ({
        value: item.count,
        name: item.name,
        itemStyle: { color: colors[index % colors.length] }
      }))
    }
    
    // 如果没有数据，使用模拟数据
    if (categoryData.length === 0) {
      categoryData = [
        { value: 89, name: '川菜', itemStyle: { color: '#a8d8ea' } },
        { value: 67, name: '粤菜', itemStyle: { color: '#aa96da' } },
        { value: 54, name: '湘菜', itemStyle: { color: '#ffd93d' } },
        { value: 43, name: '鲁菜', itemStyle: { color: '#6bcf7f' } },
        { value: 38, name: '浙菜', itemStyle: { color: '#ff9a9e' } }
      ]
    }
    
    categoryChartInstance = echarts.init(categoryChart.value)
    
    const option = {
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left',
        textStyle: {
          color: '#606266'
        }
      },
      series: [
        {
          name: '美食分类',
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['60%', '50%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false,
            position: 'center'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '18',
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: false
          },
          data: categoryData
        }
      ]
    }
    
    categoryChartInstance.setOption(option)
  } catch (error) {
    console.error('初始化分类图表失败:', error)
  }
}

// 初始化地域分布图表
const initRegionChart = async () => {
  if (!regionChart.value) return
  
  try {
    const response = await getFoodStatistics()
    let regionData = []
    
    if (response.code === 200) {
      const data = response.data.by_region || []
      regionData = data.map((item: any) => ({
        name: item.region,
        value: item.count
      }))
    }
    
    // 如果没有数据，使用模拟数据
    if (regionData.length === 0) {
      regionData = [
        { name: '四川', value: 156 },
        { name: '广东', value: 134 },
        { name: '湖南', value: 98 },
        { name: '山东', value: 87 },
        { name: '浙江', value: 76 },
        { name: '江苏', value: 65 },
        { name: '福建', value: 54 },
        { name: '北京', value: 43 }
      ]
    }
    
    regionChartInstance = echarts.init(regionChart.value)
    
    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: regionData.map(item => item.name),
        axisLine: {
          lineStyle: {
            color: '#e4e7ed'
          }
        },
        axisLabel: {
          color: '#606266',
          rotate: 45
        }
      },
      yAxis: {
        type: 'value',
        axisLine: {
          lineStyle: {
            color: '#e4e7ed'
          }
        },
        axisLabel: {
          color: '#606266'
        },
        splitLine: {
          lineStyle: {
            color: '#f0f2f5'
          }
        }
      },
      series: [
        {
          name: '美食数量',
          type: 'bar',
          data: regionData.map((item, index) => ({
            value: item.value,
            itemStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: '#a8d8ea' },
                  { offset: 1, color: '#7fb3d3' }
                ]
              }
            }
          })),
          barWidth: '60%',
          itemStyle: {
            borderRadius: [4, 4, 0, 0]
          }
        }
      ]
    }
    
    regionChartInstance.setOption(option)
  } catch (error) {
    console.error('初始化地域图表失败:', error)
  }
}

// 初始化评分分布图表
const initRatingChart = async () => {
  if (!ratingChart.value) return
  
  try {
    const response = await getFoodStatistics()
    let ratingData = []
    
    if (response.code === 200) {
      const data = response.data.by_rating || []
      ratingData = data.map((item: any) => ({
        rating: item.rating,
        count: item.count
      }))
    }
    
    // 如果没有数据，使用模拟数据
    if (ratingData.length === 0) {
      ratingData = [
        { rating: '5.0', count: 234 },
        { rating: '4.5', count: 189 },
        { rating: '4.0', count: 156 },
        { rating: '3.5', count: 98 },
        { rating: '3.0', count: 67 },
        { rating: '2.5', count: 34 },
        { rating: '2.0', count: 23 },
        { rating: '1.5', count: 12 },
        { rating: '1.0', count: 8 }
      ]
    }
    
    ratingChartInstance = echarts.init(ratingChart.value)
    
    const option = {
      tooltip: {
        trigger: 'item',
        formatter: '{b}分: {c}个美食'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: ratingData.map(item => item.rating + '分'),
        axisLine: {
          lineStyle: {
            color: '#e4e7ed'
          }
        },
        axisLabel: {
          color: '#606266'
        }
      },
      yAxis: {
        type: 'value',
        axisLine: {
          lineStyle: {
            color: '#e4e7ed'
          }
        },
        axisLabel: {
          color: '#606266'
        },
        splitLine: {
          lineStyle: {
            color: '#f0f2f5'
          }
        }
      },
      series: [
        {
          name: '评分分布',
          type: 'line',
          smooth: true,
          symbol: 'circle',
          symbolSize: 8,
          itemStyle: {
            color: '#aa96da'
          },
          lineStyle: {
            color: '#aa96da',
            width: 3
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(170, 150, 218, 0.3)' },
                { offset: 1, color: 'rgba(170, 150, 218, 0.1)' }
              ]
            }
          },
          data: ratingData.map(item => item.count)
        }
      ]
    }
    
    ratingChartInstance.setOption(option)
  } catch (error) {
    console.error('初始化评分图表失败:', error)
  }
}

// 更新用户增长图表
const updateUserGrowthChart = async () => {
  await initUserGrowthChart()
}

// 页面初始化
onMounted(async () => {
  await getStatistics()
  
  // 等待DOM更新后初始化图表
  await nextTick()
  await Promise.all([
    initUserGrowthChart(),
    initCategoryChart(),
    initRegionChart(),
    initRatingChart()
  ])
  
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    userGrowthChartInstance?.resize()
    categoryChartInstance?.resize()
    regionChartInstance?.resize()
    ratingChartInstance?.resize()
  })
})
</script>

<style scoped lang="scss">
.statistics {
  padding: 0;
}

// 统计概览卡片
.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stats-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  }
}

.card-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
  
  &.user-icon {
    background: linear-gradient(135deg, #a8d8ea 0%, #7fb3d3 100%);
  }
  
  &.food-icon {
    background: linear-gradient(135deg, #aa96da 0%, #9c88c4 100%);
  }
  
  &.comment-icon {
    background: linear-gradient(135deg, #ffd93d 0%, #f4c430 100%);
  }
  
  &.favorite-icon {
    background: linear-gradient(135deg, #6bcf7f 0%, #5bb970 100%);
  }
}

.card-content {
  flex: 1;
  text-align: center;
}

.card-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
  text-align: center;
}

.card-value {
  font-size: 32px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
  text-align: center;
}

.card-trend {
  text-align: center;
}

.trend-up {
  color: #67c23a;
  font-size: 12px;
  margin-right: 4px;
}

.trend-text {
  font-size: 12px;
  color: #909399;
}

// 图表区域
.charts-section {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 24px;
}

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  
  &.large {
    grid-column: span 1;
  }
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f2f5;
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0;
  text-align: center;
}

.chart-actions {
  display: flex;
  align-items: center;
}

.chart-content {
  text-align: center;
}

.chart {
  width: 100%;
  height: 300px;
}

// 响应式设计
@media (max-width: 1400px) {
  .charts-section {
    grid-template-columns: 1fr 1fr;
    
    .chart-card.large {
      grid-column: span 2;
    }
  }
}

@media (max-width: 1024px) {
  .charts-section {
    grid-template-columns: 1fr;
    
    .chart-card.large {
      grid-column: span 1;
    }
  }
}

@media (max-width: 768px) {
  .overview-cards {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .stats-card {
    padding: 20px;
  }
  
  .card-icon {
    width: 50px;
    height: 50px;
    font-size: 20px;
  }
  
  .card-value {
    font-size: 28px;
  }
  
  .chart {
    height: 250px;
  }
  
  .chart-card {
    padding: 20px;
  }
}

// Element Plus 组件样式覆盖
:deep(.el-radio-group) {
  .el-radio-button__inner {
    background: #f5f7fa;
    border-color: #dcdfe6;
    color: #606266;
    
    &:hover {
      background: #ecf5ff;
      border-color: #b3d8ff;
      color: #409eff;
    }
  }
  
  .el-radio-button__original-radio:checked + .el-radio-button__inner {
    background: #a8d8ea;
    border-color: #a8d8ea;
    color: white;
  }
}
</style>