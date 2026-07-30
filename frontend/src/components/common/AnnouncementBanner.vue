<template>
  <div class="announcement-banner" v-if="announcements.length > 0">
    <div class="announcement-container">
      <div class="announcement-icon">
        <el-icon><Bell /></el-icon>
      </div>
      <div class="announcement-content">
        <el-carousel 
          :interval="4000" 
          direction="vertical" 
          height="40px"
          :arrow="'never'"
          :indicator-position="'none'"
        >
          <el-carousel-item v-for="announcement in announcements" :key="announcement.id">
            <div 
              class="announcement-item"
              @click="goToAnnouncementDetail(announcement.id)"
            >
              <span class="announcement-type">【{{ getTypeLabel(announcement.type) }}】</span>
              <span class="announcement-title">{{ announcement.title }}</span>
            </div>
          </el-carousel-item>
        </el-carousel>
      </div>
      <div class="announcement-more">
        <el-button 
          type="text" 
          size="small"
          @click="goToAnnouncementList"
        >
          更多
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Bell } from '@element-plus/icons-vue'
import { announcementApi } from '@/api/announcement'
import type { Announcement } from '@/types'

const router = useRouter()

// 响应式数据
const announcements = ref<Announcement[]>([])
const loading = ref(false)

// 获取最新公告
const getLatestAnnouncements = async () => {
  try {
    loading.value = true
    const response = await announcementApi.getLatestAnnouncements(5)
    announcements.value = response.data
  } catch (error) {
    console.error('获取最新公告失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取公告类型标签
const getTypeLabel = (type: string) => {
  const typeMap: Record<string, string> = {
    notice: '通知',
    event: '活动',
    system: '系统'
  }
  return typeMap[type] || '通知'
}

// 跳转到公告详情
const goToAnnouncementDetail = (id: number) => {
  router.push(`/announcements/${id}`)
}

// 跳转到公告列表
const goToAnnouncementList = () => {
  router.push('/announcements')
}

// 页面初始化
onMounted(() => {
  getLatestAnnouncements()
})
</script>

<style scoped lang="scss">
.announcement-banner {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border: 1px solid #dee2e6;
  border-radius: 8px;
  margin-bottom: 24px;
  overflow: hidden;
}

.announcement-container {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  gap: 16px;
}

.announcement-icon {
  color: #a8d8ea;
  font-size: 18px;
  flex-shrink: 0;
}

.announcement-content {
  flex: 1;
  overflow: hidden;
}

.announcement-item {
  display: flex;
  align-items: center;
  height: 40px;
  cursor: pointer;
  transition: color 0.3s ease;
  
  &:hover {
    color: #a8d8ea;
  }
}

.announcement-type {
  color: #6c757d;
  font-size: 12px;
  margin-right: 8px;
  flex-shrink: 0;
}

.announcement-title {
  font-size: 14px;
  color: #495057;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 40px;
}

.announcement-more {
  flex-shrink: 0;
}

// Element Plus 按钮样式覆盖
:deep(.el-button--text) {
  color: #a8d8ea;
  
  &:hover {
    color: #7fb3d3;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .announcement-container {
    padding: 10px 16px;
    gap: 12px;
  }
  
  .announcement-type {
    display: none;
  }
  
  .announcement-title {
    font-size: 13px;
  }
}
</style>