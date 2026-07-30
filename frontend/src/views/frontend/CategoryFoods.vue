<template>
  <div class="category-foods-page">
    <Header />
    
    <div class="page-container">
      <!-- 分类信息 -->
      <div class="category-header" v-if="category">
        <div class="category-info">
          <div class="category-icon" v-if="category.icon">
            <img :src="getCategoryIcon(category.icon)" :alt="category.name" />
          </div>
          <div class="category-details">
            <h1 class="category-name">{{ category.name }}</h1>
            <p class="category-description" v-if="category.description">
              {{ category.description }}
            </p>
          </div>
        </div>
        
        <!-- 排序选项 -->
        <div class="sort-options">
          <el-select v-model="sortOption" @change="handleSortChange">
            <el-option label="综合排序" value="rating-desc" />
            <el-option label="最新发布" value="created_at-desc" />
            <el-option label="浏览最多" value="view_count-desc" />
            <el-option label="评分最高" value="rating-desc" />
          </el-select>
        </div>
      </div>
      
      <!-- 美食列表 -->
      <div class="foods-section">
        <div v-loading="loading" class="food-grid">
          <FoodCard
            v-for="food in foods"
            :key="food.id"
            :food="food"
            @click="goToDetail(food.id)"
          />
        </div>
        
        <!-- 空状态 -->
        <el-empty 
          v-if="!loading && foods.length === 0"
          description="该分类下暂无美食"
        />
        
        <!-- 分页 -->
        <div class="pagination-wrapper" v-if="pagination.total > 0">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.per_page"
            :page-sizes="[12, 24, 36, 48]"
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
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { foodCategoryApi } from '@/api/foodCategory'
import type { Food, FoodCategory } from '@/types'

// 组件导入
import Header from '@/components/common/Header.vue'
import Footer from '@/components/common/Footer.vue'
import FoodCard from '@/components/food/FoodCard.vue'

const route = useRoute()
const router = useRouter()

// 响应式数据
const category = ref<FoodCategory | null>(null)
const foods = ref<Food[]>([])
const loading = ref(false)

// 排序选项
const sortOption = ref('rating-desc')

// 分页数据
const pagination = reactive({
  page: 1,
  per_page: 12,
  total: 0
})

// 获取分类美食
const getCategoryFoods = async () => {
  const categoryId = Number(route.params.id)
  if (!categoryId) return
  
  try {
    loading.value = true
    
    // 构建查询参数
    const params = {
      page: pagination.page,
      per_page: pagination.per_page
    }
    
    // 添加排序条件
    const [sort, order] = sortOption.value.split('-')
    params.sort = sort
    params.order = order
    
    const response = await foodCategoryApi.getCategoryFoods(categoryId, params)
    category.value = response.data.category
    foods.value = response.data.foods.items
    pagination.total = response.data.foods.total
  } catch (error) {
    console.error('获取分类美食失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取分类图标URL
const getCategoryIcon = (iconPath: string) => {
  if (!iconPath) return ''
  if (iconPath.startsWith('http')) return iconPath
  return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}${iconPath}`
}

// 排序变化处理
const handleSortChange = () => {
  pagination.page = 1
  getCategoryFoods()
}

// 分页大小变化
const handleSizeChange = (size: number) => {
  pagination.per_page = size
  pagination.page = 1
  getCategoryFoods()
}

// 当前页变化
const handleCurrentChange = (page: number) => {
  pagination.page = page
  getCategoryFoods()
}

// 跳转到美食详情
const goToDetail = (id: number) => {
  router.push(`/foods/${id}`)
}

// 监听路由参数变化
watch(() => route.params.id, () => {
  pagination.page = 1
  getCategoryFoods()
})

// 页面初始化
onMounted(() => {
  getCategoryFoods()
})
</script>

<style scoped lang="scss">
.category-foods-page {
  min-height: 100vh;
  background: #f8f9fa;
}

.page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

// 分类头部
.category-header {
  background: white;
  border-radius: 12px;
  padding: 32px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.category-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.category-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.category-details {
  flex: 1;
}

.category-name {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.category-description {
  font-size: 16px;
  color: #606266;
  margin: 0;
  line-height: 1.5;
}

.sort-options {
  flex-shrink: 0;
}

// 美食列表区域
.foods-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.food-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding-top: 24px;
  border-top: 1px solid #f0f2f5;
}

// Element Plus 组件样式覆盖
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
  
  .category-header {
    padding: 24px;
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
  }
  
  .category-info {
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 16px;
  }
  
  .category-icon {
    width: 60px;
    height: 60px;
  }
  
  .category-name {
    font-size: 24px;
  }
  
  .category-description {
    font-size: 14px;
  }
  
  .foods-section {
    padding: 20px;
  }
  
  .food-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 16px;
  }
}
</style>