<template>
  <div class="home">
    <!-- 顶部导航 -->
    <Header />
    
    <!-- 公告滚动区域 -->
    <AnnouncementBanner />
    
    <!-- 轮播图区域 -->
    <BannerCarousel />
    
    <!-- 美食分类导航 -->
    <CategoryNav />
    
    <!-- 美食推荐区域 -->
    <div class="food-sections">
      <!-- 热门推荐 -->
      <FoodSection 
        title="热门推荐" 
        :foods="hotFoods" 
        :loading="hotLoading"
        @more="goToFoodList({ sort: 'view_count' })"
      />
      
      <!-- 最新美食 -->
      <FoodSection 
        title="最新美食" 
        :foods="latestFoods" 
        :loading="latestLoading"
        @more="goToFoodList({ sort: 'created_at' })"
      />
      
      <!-- 高分推荐 -->
      <FoodSection 
        title="高分推荐" 
        :foods="recommendedFoods" 
        :loading="recommendedLoading"
        @more="goToFoodList({ sort: 'rating' })"
      />
      
      <!-- 个性化推荐（登录用户） -->
      <FoodSection 
        v-if="userStore.isLoggedIn"
        title="为你推荐" 
        :foods="personalFoods" 
        :loading="personalLoading"
        @more="goToFoodList()"
      />
    </div>
    
    <!-- 底部 -->
    <Footer />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { foodApi } from '@/api/food'
import { recommendApi } from '@/api/recommend'
import type { Food, FoodQuery } from '@/types'

// 组件导入
import Header from '@/components/common/Header.vue'
import Footer from '@/components/common/Footer.vue'
import AnnouncementBanner from '@/components/common/AnnouncementBanner.vue'
import BannerCarousel from '@/components/common/BannerCarousel.vue'
import CategoryNav from '@/components/common/CategoryNav.vue'
import FoodSection from '@/components/food/FoodSection.vue'

const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const hotFoods = ref<Food[]>([])
const latestFoods = ref<Food[]>([])
const recommendedFoods = ref<Food[]>([])
const personalFoods = ref<Food[]>([])

const hotLoading = ref(false)
const latestLoading = ref(false)
const recommendedLoading = ref(false)
const personalLoading = ref(false)

// 获取热门美食
const getHotFoods = async () => {
  hotLoading.value = true
  try {
    const response = await foodApi.getHotFoods(8)
    hotFoods.value = response.data
  } catch (error) {
    console.error('获取热门美食失败:', error)
  } finally {
    hotLoading.value = false
  }
}

// 获取最新美食
const getLatestFoods = async () => {
  latestLoading.value = true
  try {
    const response = await foodApi.getLatestFoods(8)
    latestFoods.value = response.data
  } catch (error) {
    console.error('获取最新美食失败:', error)
  } finally {
    latestLoading.value = false
  }
}

// 获取推荐美食
const getRecommendedFoods = async () => {
  recommendedLoading.value = true
  try {
    const response = await foodApi.getRecommendedFoods(8)
    recommendedFoods.value = response.data
  } catch (error) {
    console.error('获取推荐美食失败:', error)
  } finally {
    recommendedLoading.value = false
  }
}

// 获取个性化推荐
const getPersonalFoods = async () => {
  if (!userStore.isLoggedIn) return
  
  personalLoading.value = true
  try {
    const response = await recommendApi.getPersonalRecommend(8)
    personalFoods.value = response.data
  } catch (error) {
    console.error('获取个性化推荐失败:', error)
    // 如果个性化推荐失败，使用热门推荐作为备选
    try {
      const fallbackResponse = await foodApi.getHotFoods(8)
      personalFoods.value = fallbackResponse.data
    } catch (fallbackError) {
      console.error('获取备选推荐失败:', fallbackError)
    }
  } finally {
    personalLoading.value = false
  }
}

// 跳转到美食列表页
const goToFoodList = (query: FoodQuery = {}) => {
  router.push({
    path: '/foods',
    query: query
  })
}

// 页面初始化
onMounted(async () => {
  // 并行获取所有数据
  await Promise.all([
    getHotFoods(),
    getLatestFoods(),
    getRecommendedFoods(),
    getPersonalFoods()
  ])
})
</script>

<style scoped lang="scss">
.home {
  min-height: 100vh;
  background: #f8f9fa;
}

.food-sections {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px 40px;
}

// 响应式设计
@media (max-width: 768px) {
  .food-sections {
    padding: 0 16px 32px;
  }
}
</style>