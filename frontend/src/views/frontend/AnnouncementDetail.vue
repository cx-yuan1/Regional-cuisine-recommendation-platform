<template>
  <div class="announcement-detail-page">
    <Header />
    
    <div class="page-container" v-if="announcement">
      <div class="announcement-detail">
        <!-- 返回按钮 -->
        <div class="back-section">
          <el-button @click="goBack" size="small">
            <el-icon><ArrowLeft /></el-icon>
            返回列表
          </el-button>
        </div>
        
        <!-- 公告头部 -->
        <div class="announcement-header">
          <div class="announcement-meta">
            <el-tag 
              :type="getTypeTagType(announcement.type)"
              size="small"
            >
              {{ getTypeLabel(announcement.type) }}
            </el-tag>
            <span class="announcement-date">
              {{ formatDate(announcement.created_at) }}
            </span>
            <span class="view-count">
              <el-icon><View /></el-icon>
              {{ announcement.view_count || 0 }} 次浏览
            </span>
          </div>
          
          <h1 class="announcement-title">{{ announcement.title }}</h1>
          
          <div class="announcement-priority" v-if="announcement.priority > 3">
            <el-tag type="warning">重要公告</el-tag>
          </div>
        </div>
        
        <!-- 公告图片 -->
        <div class="announcement-image" v-if="announcement.image">
          <img :src="getAnnouncementImage(announcement.image)" :alt="announcement.title" />
        </div>
        
        <!-- 公告内容 -->
        <div class="announcement-content">
          <div class="content-html" v-html="announcement.content"></div>
        </div>
        
        <!-- 公告时间范围 -->
        <div class="announcement-time-range" v-if="announcement.start_time || announcement.end_time">
          <div class="time-range-title">有效期：</div>
          <div class="time-range-content">
            <span v-if="announcement.start_time">
              {{ formatDateTime(announcement.start_time) }}
            </span>
            <span v-if="announcement.start_time && announcement.end_time"> 至 </span>
            <span v-if="announcement.end_time">
              {{ formatDateTime(announcement.end_time) }}
            </span>
            <span v-if="!announcement.start_time && !announcement.end_time">
              长期有效
            </span>
          </div>
        </div>
        
        <!-- 相关公告推荐 -->
        <div class="related-announcements" v-if="relatedAnnouncements.length > 0">
          <h3>相关公告</h3>
          <div class="related-list">
            <div 
              v-for="related in relatedAnnouncements" 
              :key="related.id"
              class="related-item"
              @click="goToAnnouncement(related.id)"
            >
              <div class="related-type">
                <el-tag 
                  :type="getTypeTagType(related.type)"
                  size="small"
                >
                  {{ getTypeLabel(related.type) }}
                </el-tag>
              </div>
              <div class="related-title">{{ related.title }}</div>
              <div class="related-date">{{ formatDate(related.created_at) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-else-if="loading" class="loading-container">
      <el-skeleton :rows="8" animated />
    </div>
    
    <!-- 错误状态 -->
    <div v-else class="error-container">
      <el-empty description="公告不存在或已被删除">
        <el-button type="primary" @click="goBack">返回列表</el-button>
      </el-empty>
    </div>
    
    <Footer />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, View } from '@element-plus/icons-vue'
import { announcementApi } from '@/api/announcement'
import type { Announcement } from '@/types'

// 组件导入
import Header from '@/components/common/Header.vue'
import Footer from '@/components/common/Footer.vue'

const route = useRoute()
const router = useRouter()

// 响应式数据
const announcement = ref<Announcement | null>(null)
const relatedAnnouncements = ref<Announcement[]>([])
const loading = ref(false)

// 获取公告详情
const getAnnouncementDetail = async () => {
  const announcementId = Number(route.params.id)
  if (!announcementId) return
  
  try {
    loading.value = true
    const response = await announcementApi.getAnnouncementDetail(announcementId)
    announcement.value = response.data
    
    // 获取相关公告（同类型的其他公告）
    await getRelatedAnnouncements(response.data.type, announcementId)
  } catch (error) {
    console.error('获取公告详情失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取相关公告
const getRelatedAnnouncements = async (type: string, excludeId: number) => {
  try {
    const response = await announcementApi.getAnnouncements({
      type,
      per_page: 5
    })
    
    // 排除当前公告
    relatedAnnouncements.value = response.data.items.filter(item => item.id !== excludeId)
  } catch (error) {
    console.error('获取相关公告失败:', error)
  }
}

// 返回列表
const goBack = () => {
  router.push('/announcements')
}

// 跳转到其他公告
const goToAnnouncement = (id: number) => {
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

// 格式化日期时间
const formatDateTime = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取公告图片URL
const getAnnouncementImage = (imagePath: string) => {
  if (!imagePath) return ''
  if (imagePath.startsWith('http')) return imagePath
  return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}${imagePath}`
}

// 页面初始化
onMounted(() => {
  getAnnouncementDetail()
})
</script>

<style scoped lang="scss">
.announcement-detail-page {
  min-height: 100vh;
  background: #f8f9fa;
}

.page-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.announcement-detail {
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.back-section {
  margin-bottom: 24px;
}

.announcement-header {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid #f0f2f5;
}

.announcement-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.announcement-date {
  font-size: 14px;
  color: #909399;
}

.view-count {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: #909399;
}

.announcement-title {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 16px 0;
  line-height: 1.4;
}

.announcement-image {
  margin-bottom: 32px;
  text-align: center;
  
  img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
}

.announcement-content {
  margin-bottom: 32px;
}

.content-html {
  font-size: 16px;
  line-height: 1.8;
  color: #303133;
  
  // 富文本内容样式
  :deep(p) {
    margin-bottom: 16px;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  :deep(h1, h2, h3, h4, h5, h6) {
    margin: 24px 0 16px 0;
    font-weight: 600;
    
    &:first-child {
      margin-top: 0;
    }
  }
  
  :deep(ul, ol) {
    margin-bottom: 16px;
    padding-left: 24px;
  }
  
  :deep(li) {
    margin-bottom: 8px;
  }
  
  :deep(blockquote) {
    border-left: 4px solid #a8d8ea;
    padding-left: 16px;
    margin: 16px 0;
    color: #606266;
    font-style: italic;
  }
  
  :deep(img) {
    max-width: 100%;
    height: auto;
    border-radius: 4px;
    margin: 16px 0;
  }
}

.announcement-time-range {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 32px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.time-range-title {
  font-weight: 600;
  color: #303133;
  flex-shrink: 0;
}

.time-range-content {
  color: #606266;
  font-size: 14px;
}

.related-announcements {
  border-top: 1px solid #f0f2f5;
  padding-top: 32px;
  
  h3 {
    font-size: 18px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 20px 0;
  }
}

.related-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.related-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid #f0f2f5;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #a8d8ea;
    background: rgba(168, 216, 234, 0.05);
  }
}

.related-title {
  flex: 1;
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.related-date {
  font-size: 12px;
  color: #909399;
  flex-shrink: 0;
}

.loading-container,
.error-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
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

// 响应式设计
@media (max-width: 768px) {
  .page-container {
    padding: 16px;
  }
  
  .announcement-detail {
    padding: 24px;
  }
  
  .announcement-title {
    font-size: 24px;
  }
  
  .announcement-meta {
    gap: 12px;
  }
  
  .content-html {
    font-size: 15px;
  }
  
  .related-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>