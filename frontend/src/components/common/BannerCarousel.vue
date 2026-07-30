<template>
  <div class="banner-carousel" v-if="banners.length > 0">
    <el-carousel 
      :interval="5000" 
      :arrow="banners.length > 1 ? 'hover' : 'never'"
      :indicator-position="banners.length > 1 ? 'outside' : 'none'"
      height="400px"
    >
      <el-carousel-item v-for="banner in banners" :key="banner.id">
        <div 
          class="banner-item" 
          :style="{ backgroundImage: `url(${getBannerImage(banner.image)})` }"
          @click="handleBannerClick(banner)"
        >
          <div class="banner-overlay">
            <div class="banner-content">
              <h2 class="banner-title">{{ banner.title }}</h2>
            </div>
          </div>
        </div>
      </el-carousel-item>
    </el-carousel>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { bannerApi } from '@/api/banner'
import type { Banner } from '@/types'
import { ElMessage } from 'element-plus'

const router = useRouter()

// 响应式数据
const banners = ref<Banner[]>([])
const loading = ref(false)

// 获取轮播图列表
const getBanners = async () => {
  try {
    loading.value = true
    const response = await bannerApi.getBanners()
    banners.value = response.data
  } catch (error) {
    console.error('获取轮播图失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取轮播图图片URL
const getBannerImage = (imagePath: string) => {
  if (!imagePath) return '/placeholder-banner.jpg'
  if (imagePath.startsWith('http')) return imagePath
  return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}${imagePath}`
}

// 处理轮播图点击
const handleBannerClick = (banner: Banner) => {
  if (banner.link_url) {
    if (banner.link_url.startsWith('http')) {
      // 外部链接
      window.open(banner.link_url, '_blank')
    } else {
      // 内部路由
      router.push(banner.link_url)
    }
  }
}

// 页面初始化
onMounted(() => {
  getBanners()
})
</script>

<style scoped lang="scss">
.banner-carousel {
  margin-bottom: 32px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.banner-item {
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  position: relative;
  cursor: pointer;
  transition: transform 0.3s ease;
  
  &:hover {
    transform: scale(1.02);
  }
}

.banner-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0.1) 0%,
    rgba(0, 0, 0, 0.3) 50%,
    rgba(0, 0, 0, 0.6) 100%
  );
  display: flex;
  align-items: flex-end;
  padding: 40px;
}

.banner-content {
  color: white;
  text-align: left;
}

.banner-title {
  font-size: 32px;
  font-weight: 600;
  margin: 0;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
  line-height: 1.2;
}

// Element Plus 轮播图样式覆盖
:deep(.el-carousel__indicator) {
  .el-carousel__button {
    background: rgba(255, 255, 255, 0.5);
    
    &.is-active {
      background: #a8d8ea;
    }
  }
}

:deep(.el-carousel__arrow) {
  background: rgba(168, 216, 234, 0.8);
  color: white;
  
  &:hover {
    background: rgba(168, 216, 234, 1);
  }
}

// 响应式设计
@media (max-width: 768px) {
  .banner-carousel {
    margin-bottom: 24px;
  }
  
  .banner-overlay {
    padding: 24px;
  }
  
  .banner-title {
    font-size: 24px;
  }
}
</style>