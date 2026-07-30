<template>
  <div class="announcement-list-page">
    <Header />
    
    <div class="page-container">
      <!-- 筛选区域 -->
      <div class="filter-section">
        <div class="filter-container">
          <!-- 搜索框 -->
          <div class="search-section">
            <el-input
              v-model="searchForm.keyword"
              placeholder="搜索公告..."
              class="search-input"
              size="large"
              @keyup.enter="handleSearch"
            >
              <template #append>
                <el-button @click="handleSearch">
                  <el-icon><Search /></el-icon>
                </el-button>
              </template>
            </el-input>
          </div>
          
          <!-- 类型筛选 -->
          <div class="filter-options">
            <div class="filter-item">
              <label>类型：</label>
              <el-select 
                v-model="searchForm.type" 
                placeholder="全部类型"
                size="large"
                clearable
                @change="handleSearch"
              >
                <el-option
                  v-for="type in announcementTypes"
                  :key="type.value"
                  :label="type.label"
                  :value="type.value"
                />
              </el-select>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 公告列表 -->
      <div class="announcement-list-section">
        <div class="list-header">
          <h2>公告列表</h2>
          <span class="total-count">共 {{ pagination.total }} 条公告</span>
        </div>
        
        <div v-loading="loading" class="announcement-list">
          <div 
            v-for="announcement in announcements" 
            :key="announcement.id"
            class="announcement-item"
            @click="goToDetail(announcement.id)"
          >
            <div class="announcement-body">
              <div class="announcement-image" v-if="announcement.image">
                <img 
                  :src="getAnnouncementImage(announcement.image)" 
                  :alt="announcement.title"
                  @error="handleImageError"
                />
              </div>
              <div class="announcement-info">
                <div class="announcement-header">
                  <div class="announcement-type">
                    <el-tag 
                      :type="getTypeTagType(announcement.type)"
                      size="small"
                    >
                      {{ getTypeLabel(announcement.type) }}
                    </el-tag>
                  </div>
                  <div class="announcement-date">
                    {{ formatDate(announcement.created_at) }}
                  </div>
                </div>
                
                <h3 class="announcement-title">{{ announcement.title }}</h3>
                
                <div class="announcement-content">
                  {{ getContentPreview(announcement.content) }}
                </div>
                
                <div class="announcement-footer">
              <div class="announcement-stats">
                <span class="view-count">
                  <el-icon><View /></el-icon>
                  {{ announcement.view_count || 0 }}
                </span>
              </div>
              <div class="announcement-priority" v-if="announcement.priority > 3">
                <el-tag type="warning" size="small">重要</el-tag>
              </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 空状态 -->
        <el-empty 
          v-if="!loading && announcements.length === 0"
          description="暂无公告"
        />
        
        <!-- 分页 -->
        <div class="pagination-wrapper" v-if="pagination.total > 0">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.per_page"
            :page-sizes="[10, 20, 30, 50]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </div>
    
    <Footer />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, View } from '@element-plus/icons-vue'
import { announcementApi } from '@/api/announcement'
import type { Announcement } from '@/types'

// 组件导入
import Header from '@/components/common/Header.vue'
import Footer from '@/components/common/Footer.vue'

const router = useRouter()

// 响应式数据
const announcements = ref<Announcement[]>([])
const announcementTypes = ref<Array<{ value: string; label: string }>>([])
const loading = ref(false)

// 搜索表单
const searchForm = reactive({
  keyword: '',
  type: ''
})

// 分页数据
const pagination = reactive({
  page: 1,
  per_page: 10,
  total: 0
})

// 获取公告列表
const getAnnouncementList = async () => {
  try {
    loading.value = true
    
    const params = {
      page: pagination.page,
      per_page: pagination.per_page,
      keyword: searchForm.keyword || undefined,
      type: searchForm.type || undefined
    }
    
    const response = await announcementApi.getAnnouncements(params)
    announcements.value = response.data.items || []
    pagination.total = response.data.pagination?.total ?? 0
  } catch (error) {
    console.error('获取公告列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取公告类型列表
const getAnnouncementTypes = async () => {
  try {
    const response = await announcementApi.getAnnouncementTypes()
    announcementTypes.value = response.data
  } catch (error) {
    console.error('获取公告类型失败:', error)
  }
}

// 搜索处理
const handleSearch = () => {
  pagination.page = 1
  getAnnouncementList()
}

// 分页大小变化
const handleSizeChange = (size: number) => {
  pagination.per_page = size
  pagination.page = 1
  getAnnouncementList()
}

// 当前页变化
const handleCurrentChange = (page: number) => {
  pagination.page = page
  getAnnouncementList()
}

// 跳转到公告详情
const goToDetail = (id: number) => {
  router.push(`/announcements/${id}`)
}

// 获取类型标签类型
const getTypeTagType = (type: string) => {
  const typeMap: Record<string, string> = {
    notice: '',
    event: 'success',
    system: 'warning'
  }
  return typeMap[type] || ''
}

// 获取类型标签
const getTypeLabel = (type: string) => {
  const typeMap: Record<string, string> = {
    notice: '通知',
    event: '活动',
    system: '系统'
  }
  return typeMap[type] || '通知'
}

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// 获取内容预览
const getContentPreview = (content: string) => {
  // 移除HTML标签
  const textContent = content.replace(/<[^>]*>/g, '')
  return textContent.length > 100 ? textContent.substring(0, 100) + '...' : textContent
}

// 获取公告图片URL
const getAnnouncementImage = (imagePath: string) => {
  if (!imagePath) return ''
  if (imagePath.startsWith('http')) return imagePath
  return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}${imagePath}`
}

// 图片加载失败时使用占位图
const handleImageError = (e: Event) => {
  const target = e.target as HTMLImageElement
  target.src = '/placeholder-food.jpg'
  target.onerror = null
}

// 页面初始化
onMounted(async () => {
  await Promise.all([
    getAnnouncementTypes(),
    getAnnouncementList()
  ])
})
</script>

<style scoped lang="scss">
.announcement-list-page {
  min-height: 100vh;
  background: #f8f9fa;
}

.page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

// 筛选区域
.filter-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.filter-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.search-section {
  display: flex;
  justify-content: center;
}

.search-input {
  max-width: 500px;
  width: 100%;
}

.filter-options {
  display: flex;
  justify-content: center;
  align-items: center;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
  
  label {
    font-size: 15px;
    color: #606266;
    white-space: nowrap;
  }
  
  .el-select {
    min-width: 150px;
  }
}

// 公告列表区域
.announcement-list-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f2f5;
  
  h2 {
    font-size: 20px;
    font-weight: 600;
    color: #303133;
    margin: 0;
  }
}

.total-count {
  font-size: 14px;
  color: #909399;
}

.announcement-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 32px;
}

.announcement-item {
  border: 1px solid #f0f2f5;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #a8d8ea;
    box-shadow: 0 4px 12px rgba(168, 216, 234, 0.2);
    transform: translateY(-2px);
  }
}

.announcement-body {
  display: flex;
  gap: 20px;
  padding: 20px;
}

.announcement-image {
  flex-shrink: 0;
  width: 160px;
  height: 120px;
  border-radius: 8px;
  overflow: hidden;
  background: #f5f7fa;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.announcement-info {
  flex: 1;
  min-width: 0;
}

.announcement-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.announcement-date {
  font-size: 12px;
  color: #909399;
}

.announcement-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px 0;
  line-height: 1.4;
}

.announcement-content {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 16px;
}

.announcement-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.announcement-stats {
  display: flex;
  align-items: center;
  gap: 16px;
}

.view-count {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding-top: 24px;
  border-top: 1px solid #f0f2f5;
}

// Element Plus 组件样式覆盖
:deep(.el-tag) {
  &.el-tag--success {
    background: rgba(107, 207, 127, 0.2);
    border-color: #6bcf7f;
    color: #67c23a;
  }
  
  &.el-tag--warning {
    background: rgba(255, 211, 61, 0.2);
    border-color: #ffd93d;
    color: #e6a23c;
  }
}

:deep(.el-pagination) {
  .el-pager li.is-active {
    background: #a8d8ea;
    border-color: #a8d8ea;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .page-container {
    padding: 16px;
  }
  
  .filter-section,
  .announcement-list-section {
    padding: 20px;
  }
  
  .announcement-item {
    .announcement-body {
      flex-direction: column;
      padding: 16px;
    }
    
    .announcement-image {
      width: 100%;
      height: 160px;
    }
  }
  
  .announcement-title {
    font-size: 16px;
  }
  
  .announcement-content {
    font-size: 13px;
  }
  
  .list-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>