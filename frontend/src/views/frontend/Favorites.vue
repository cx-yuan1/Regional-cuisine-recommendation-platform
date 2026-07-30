<template>
  <div class="favorites-page">
    <Header />
    
    <div class="page-container">
      <div class="page-header">
        <h2>我的收藏</h2>
        <p class="subtitle">共收藏了 {{ pagination.total }} 个美食</p>
      </div>
      
      <div v-loading="loading" class="favorites-content">
        <div v-if="favorites.length > 0" class="food-grid">
          <FoodCard
            v-for="favorite in favorites"
            :key="favorite.id"
            :food="favorite.food"
            @click="goToDetail(favorite.food.id)"
          />
        </div>
        
        <el-empty 
          v-else-if="!loading"
          description="还没有收藏任何美食"
        >
          <el-button type="primary" @click="goToFoodList">
            去发现美食
          </el-button>
        </el-empty>
        
        <!-- 分页 -->
        <div class="pagination-wrapper" v-if="pagination.total > 0">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.per_page"
            :total="pagination.total"
            :page-sizes="[12, 24, 36]"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </div>
    </div>
    
    <Footer />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { favoriteApi } from '@/api/favorite'
import type { Favorite, PaginationData } from '@/types'

// 组件导入
import Header from '@/components/common/Header.vue'
import Footer from '@/components/common/Footer.vue'
import FoodCard from '@/components/food/FoodCard.vue'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const favorites = ref<Favorite[]>([])

const pagination = ref<PaginationData>({
  page: 1,
  per_page: 12,
  total: 0,
  pages: 0
})

// 获取收藏列表
const getFavorites = async () => {
  loading.value = true
  try {
    const response = await favoriteApi.getMyFavorites({
      page: pagination.value.page,
      per_page: pagination.value.per_page
    })
    favorites.value = response.data.items
    pagination.value = response.data.pagination
  } catch (error) {
    console.error('获取收藏列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 处理分页变化
const handlePageChange = (page: number) => {
  pagination.value.page = page
  getFavorites()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 处理每页数量变化
const handleSizeChange = (size: number) => {
  pagination.value.per_page = size
  pagination.value.page = 1
  getFavorites()
}

// 跳转到详情页
const goToDetail = (id: number) => {
  router.push({ name: 'FoodDetail', params: { id } })
}

// 跳转到美食列表
const goToFoodList = () => {
  router.push({ name: 'FoodList' })
}

onMounted(() => {
  getFavorites()
})
</script>

<style lang="scss" scoped>
.favorites-page {
  min-height: 100vh;
  background: var(--bg-color);
}

.page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
  
  h2 {
    color: var(--text-primary);
    font-size: 28px;
    margin-bottom: 10px;
  }
  
  .subtitle {
    color: var(--text-secondary);
    font-size: 16px;
    margin: 0;
  }
}

.food-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

@media (max-width: 768px) {
  .food-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 15px;
  }
}

@media (max-width: 480px) {
  .food-grid {
    grid-template-columns: 1fr;
  }
}
</style>