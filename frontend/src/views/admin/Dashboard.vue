<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stats-card">
        <div class="card-icon user-icon">
          <el-icon><User /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-title">用户总数</div>
          <div class="card-value">{{ stats.userCount }}</div>
          <div class="card-trend">
            <span class="trend-text">今日新增: {{ stats.todayUsers }}</span>
          </div>
        </div>
      </div>
      
      <div class="stats-card">
        <div class="card-icon food-icon">
          <el-icon><Food /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-title">美食总数</div>
          <div class="card-value">{{ stats.foodCount }}</div>
          <div class="card-trend">
            <span class="trend-text">本月新增: {{ stats.monthlyFoods }}</span>
          </div>
        </div>
      </div>
      
      <div class="stats-card">
        <div class="card-icon comment-icon">
          <el-icon><ChatDotRound /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-title">评论总数</div>
          <div class="card-value">{{ stats.commentCount }}</div>
          <div class="card-trend">
            <span class="trend-text">今日新增: {{ stats.todayComments }}</span>
          </div>
        </div>
      </div>
      
      <div class="stats-card">
        <div class="card-icon favorite-icon">
          <el-icon><Star /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-title">收藏总数</div>
          <div class="card-value">{{ stats.favoriteCount }}</div>
          <div class="card-trend">
            <span class="trend-text">今日新增: {{ stats.todayFavorites }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-container">
      <!-- 用户增长趋势 -->
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">用户增长趋势</h3>
          <div class="chart-actions">
            <el-radio-group v-model="userGrowthPeriod" size="small">
              <el-radio-button label="7">近7天</el-radio-button>
              <el-radio-button label="30">近30天</el-radio-button>
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
    </div>

    <!-- 最新数据 -->
    <div class="recent-data">
      <!-- 最新用户 -->
      <div class="data-card">
        <div class="data-header">
          <h3 class="data-title">最新用户</h3>
          <el-button type="text" @click="$router.push('/admin/users')">
            查看更多
          </el-button>
        </div>
        <div class="data-content">
          <div v-if="recentUsers.length === 0" class="empty-data">
            <el-empty description="暂无数据" />
          </div>
          <div v-else class="user-list">
            <div 
              v-for="user in recentUsers" 
              :key="user.id"
              class="user-item"
            >
              <img 
                :src="getUserAvatar(user.avatar)" 
                :alt="user.username"
                class="user-avatar"
              />
              <div class="user-info">
                <div class="user-name">{{ user.username }}</div>
                <div class="user-time">{{ formatTime(user.created_at) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 最新评论 -->
      <div class="data-card">
        <div class="data-header">
          <h3 class="data-title">最新评论</h3>
          <el-button type="text" @click="$router.push('/admin/comments')">
            查看更多
          </el-button>
        </div>
        <div class="data-content">
          <div v-if="recentComments.length === 0" class="empty-data">
            <el-empty description="暂无数据" />
          </div>
          <div v-else class="comment-list">
            <div 
              v-for="comment in recentComments" 
              :key="comment.id"
              class="comment-item"
            >
              <div class="comment-header">
                <span class="comment-user">{{ comment.user?.username }}</span>
                <el-rate 
                  v-model="comment.rating" 
                  disabled 
                  size="small"
                />
              </div>
              <div class="comment-content">{{ comment.content }}</div>
              <div class="comment-time">{{ formatTime(comment.created_at) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { User, Food, ChatDotRound, Star } from '@element-plus/icons-vue'
import { getStatisticsOverview, getUserStatistics, getFoodStatistics, getUsers, getAdminComments } from '@/api/admin'
import { ElMessage } from 'element-plus'
import type { User as UserType, Comment } from '@/types'

const router = useRouter()

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

const recentUsers = ref<UserType[]>([])
const recentComments = ref<Comment[]>([])
const userGrowthPeriod = ref('7')

// 图表引用
const userGrowthChart = ref<HTMLElement>()
const categoryChart = ref<HTMLElement>()

// 图表实例
let userGrowthChartInstance: echarts.ECharts | null = null
let categoryChartInstance: echarts.ECharts | null = null

// 获取统计数据
const getStatistics = async () => {
  try {
    const response = await getStatisticsOverview()
    if (response.code === 200 && response.data) {
      const data = response.data
      stats.value = {
        userCount: data.user_count || 0,
        foodCount: data.food_count || 0,
        commentCount: data.comment_count || 0,
        favoriteCount: data.favorite_count || 0,
        todayUsers: data.today_user_count || 0,
        monthlyFoods: data.monthly_food_count || 0,
        todayComments: data.today_comment_count || 0,
        todayFavorites: data.today_favorite_count || 0
      }
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
    // 使用默认数据，避免页面崩溃
    stats.value = {
      userCount: 0,
      foodCount: 0,
      commentCount: 0,
      favoriteCount: 0,
      todayUsers: 0,
      monthlyFoods: 0,
      todayComments: 0,
      todayFavorites: 0
    }
  }
}

// 获取最新用户
const getRecentUsers = async () => {
  try {
    const response = await getUsers({ page: 1, per_page: 5 })
    if (response.code === 200 && response.data) {
      recentUsers.value = response.data.items || []
    }
  } catch (error) {
    console.error('获取最新用户失败:', error)
    recentUsers.value = []
  }
}

// 获取最新评论
const getRecentComments = async () => {
  try {
    const response = await getAdminComments({ page: 1, per_page: 5 })
    if (response.code === 200 && response.data) {
      recentComments.value = response.data.items || []
    }
  } catch (error) {
    console.error('获取最新评论失败:', error)
    recentComments.value = []
  }
}

// 初始化用户增长图表
const initUserGrowthChart = async () => {
  if (!userGrowthChart.value) return
  
  try {
    const response = await getUserStatistics(parseInt(userGrowthPeriod.value))
    let chartData = []
    let dateLabels = []
    
    if (response.code === 200 && response.data) {
      const data = response.data || []
      chartData = data.map((item: any) => item.count)
      dateLabels = data.map((item: any) => {
        const date = new Date(item.date)
        return `${date.getMonth() + 1}-${date.getDate()}`
      })
    }
    
    // 如果没有数据，使用默认数据
    if (chartData.length === 0) {
      chartData = [0, 0, 0, 0, 0, 0, 0]
      dateLabels = ['03-06', '03-07', '03-08', '03-09', '03-10', '03-11', '03-12']
    }
    
    userGrowthChartInstance = echarts.init(userGrowthChart.value)
    
    const option = {
      title: {
        show: false
      },
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
        data: dateLabels
      },
      yAxis: {
        type: 'value'
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
    
    if (response.code === 200 && response.data) {
      const data = response.data.by_category || []
      const colors = ['#a8d8ea', '#aa96da', '#ffd93d', '#6bcf7f', '#ff9a9e', '#a8edea']
      
      categoryData = data.map((item: any, index: number) => ({
        value: item.count,
        name: item.name,
        itemStyle: { color: colors[index % colors.length] }
      }))
    }
    
    // 如果没有数据，使用默认数据
    if (categoryData.length === 0) {
      categoryData = [
        { value: 0, name: '暂无数据', itemStyle: { color: '#e4e7ed' } }
      ]
    }
    
    categoryChartInstance = echarts.init(categoryChart.value)
    
    const option = {
      title: {
        show: false
      },
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
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

// 工具函数
const getUserAvatar = (avatarPath?: string) => {
  if (!avatarPath) return '/default-avatar.png'
  if (avatarPath.startsWith('http')) return avatarPath
  return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}${avatarPath}`
}

const formatTime = (timeStr: string) => {
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (minutes < 60) {
    return `${minutes}分钟前`
  } else if (hours < 24) {
    return `${hours}小时前`
  } else if (days < 30) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString()
  }
}

// 监听时间周期变化
watch(userGrowthPeriod, async () => {
  // 重新获取数据并更新图表
  if (userGrowthChartInstance) {
    await initUserGrowthChart()
  }
})

// 页面初始化
onMounted(async () => {
  await Promise.all([
    getStatistics(),
    getRecentUsers(),
    getRecentComments()
  ])
  
  // 等待DOM更新后初始化图表
  await nextTick()
  initUserGrowthChart()
  initCategoryChart()
  
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    userGrowthChartInstance?.resize()
    categoryChartInstance?.resize()
  })
})
</script>

<style scoped lang="scss">
.dashboard {
  padding: 0;
}

// 统计卡片区域
.stats-cards {
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

.trend-text {
  font-size: 12px;
  color: #67c23a;
}

// 图表区域
.charts-container {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  margin-bottom: 32px;
}

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
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

// 最新数据区域
.recent-data {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.data-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.data-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f2f5;
}

.data-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0;
  text-align: center;
}

.data-content {
  text-align: center;
}

.empty-data {
  padding: 40px 0;
  text-align: center;
}

// 用户列表
.user-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  background: #f8f9fa;
  transition: background-color 0.3s ease;
  
  &:hover {
    background: #e9ecef;
  }
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #e4e7ed;
}

.user-info {
  flex: 1;
  text-align: left;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.user-time {
  font-size: 12px;
  color: #909399;
}

// 评论列表
.comment-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comment-item {
  padding: 16px;
  border-radius: 8px;
  background: #f8f9fa;
  transition: background-color 0.3s ease;
  
  &:hover {
    background: #e9ecef;
  }
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.comment-user {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.comment-content {
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
  margin-bottom: 8px;
  text-align: left;
}

.comment-time {
  font-size: 12px;
  color: #909399;
  text-align: right;
}

// 响应式设计
@media (max-width: 1200px) {
  .charts-container {
    grid-template-columns: 1fr;
  }
  
  .recent-data {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-cards {
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
  
  .data-card {
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
    background: #409eff;
    border-color: #409eff;
    color: white;
  }
}

:deep(.el-rate) {
  .el-rate__icon {
    font-size: 14px;
  }
}

:deep(.el-empty) {
  .el-empty__description {
    color: #909399;
    font-size: 14px;
  }
}
</style>