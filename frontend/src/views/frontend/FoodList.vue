<template>
  <div class="food-list-page">
    <Header />
    
    <div class="page-container">
      <!-- 筛选区域 -->
      <div class="filter-section">
        <div class="filter-container">
          <!-- 搜索框 -->
          <div class="search-section">
            <el-input
              v-model="searchForm.keyword"
              placeholder="搜索美食..."
              class="search-input"
              @keyup.enter="handleSearch"
            >
              <template #append>
                <el-button @click="handleSearch">
                  <el-icon><Search /></el-icon>
                </el-button>
              </template>
            </el-input>
          </div>
          
          <!-- 筛选条件 -->
          <div class="filter-options">
            <div class="filter-item">
              <label>分类：</label>
              <el-select 
                v-model="searchForm.category_id" 
                placeholder="全部分类"
                clearable
                @change="handleSearch"
              >
                <el-option
                  v-for="category in categories"
                  :key="category.id"
                  :label="category.name"
                  :value="category.id"
                />
              </el-select>
            </div>
            
            <div class="filter-item">
              <label>地域：</label>
              <el-select 
                v-model="searchForm.region" 
                placeholder="全部地域"
                clearable
                @change="handleSearch"
              >
                <el-option
                  v-for="region in regions"
                  :key="region"
                  :label="region"
                  :value="region"
                />
              </el-select>
            </div>
            
            <div class="filter-item">
              <label>排序：</label>
              <el-select 
                v-model="sortOption" 
                @change="handleSortChange"
              >
                <el-option label="综合排序" value="rating-desc" />
                <el-option label="最新发布" value="created_at-desc" />
                <el-option label="浏览最多" value="view_count-desc" />
                <el-option label="评分最高" value="rating-desc" />
              </el-select>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 美食列表 -->
      <div class="food-list-section">
        <div class="list-header">
          <h2>美食列表</h2>
          <span class="total-count">共 {{ pagination.total }} 个美食</span>
        </div>
        
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
          description="暂无美食数据"
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
import { Search } from '@element-plus/icons-vue'
import { foodApi } from '@/api/food'
import { foodCategoryApi } from '@/api/foodCategory'
import type { Food, FoodCategory, FoodQuery } from '@/types'

// 组件导入
import Header from '@/components/common/Header.vue'
import Footer from '@/components/common/Footer.vue'
import FoodCard from '@/components/food/FoodCard.vue'

const route = useRoute()
const router = useRouter()

// 响应式数据
const foods = ref<Food[]>([])
const categories = ref<FoodCategory[]>([])
const regions = ref<string[]>([])
const loading = ref(false)

// 搜索表单
const searchForm = reactive({
  keyword: '',
  category_id: null as number | null,
  region: ''
})

// 排序选项
const sortOption = ref('rating-desc')

// 分页数据
const pagination = reactive({
  page: 1,
  per_page: 12,
  total: 0
})

// 获取美食列表
const getFoodList = async () => {
  try {
    loading.value = true
    
    // 构建查询参数
    const params: FoodQuery = {
      page: pagination.page,
      per_page: pagination.per_page
    }
    
    // 添加搜索条件
    if (searchForm.keyword) params.keyword = searchForm.keyword
    if (searchForm.category_id) params.category_id = searchForm.category_id
    if (searchForm.region) params.region = searchForm.region
    
    // 添加排序条件
    const [sort, order] = sortOption.value.split('-')
    params.sort = sort
    params.order = order
    
    const response = await foodApi.getFoodList(params)
    foods.value = response.data.items
    pagination.total = response.data.total
  } catch (error) {
    console.error('获取美食列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取分类列表
const getCategories = async () => {
  try {
    const response = await foodCategoryApi.getActiveCategories()
    categories.value = response.data
  } catch (error) {
    console.error('获取分类列表失败:', error)
  }
}

// 获取地域列表
const getRegions = async () => {
  try {
    const response = await foodApi.getRegions()
    regions.value = response.data
  } catch (error) {
    console.error('获取地域列表失败:', error)
  }
}

// 搜索处理
const handleSearch = () => {
  pagination.page = 1
  getFoodList()
  updateURL()
}

// 排序变化处理
const handleSortChange = () => {
  pagination.page = 1
  getFoodList()
  updateURL()
}

// 分页大小变化
const handleSizeChange = (size: number) => {
  pagination.per_page = size
  pagination.page = 1
  getFoodList()
  updateURL()
}

// 当前页变化
const handleCurrentChange = (page: number) => {
  pagination.page = page
  getFoodList()
  updateURL()
}

// 跳转到美食详情
const goToDetail = (id: number) => {
  router.push(`/foods/${id}`)
}

// 更新URL参数
const updateURL = () => {
  const query: any = {}
  
  if (searchForm.keyword) query.keyword = searchForm.keyword
  if (searchForm.category_id) query.category_id = searchForm.category_id
  if (searchForm.region) query.region = searchForm.region
  if (sortOption.value !== 'rating-desc') query.sort = sortOption.value
  if (pagination.page > 1) query.page = pagination.page
  if (pagination.per_page !== 12) query.per_page = pagination.per_page
  
  router.replace({ query })
}

// 从URL初始化搜索条件
const initFromURL = () => {
  const query = route.query
  
  if (query.keyword) searchForm.keyword = query.keyword as string
  if (query.category_id) searchForm.category_id = Number(query.category_id)
  if (query.region) searchForm.region = query.region as string
  if (query.sort) sortOption.value = query.sort as string
  if (query.page) pagination.page = Number(query.page)
  if (query.per_page) pagination.per_page = Number(query.per_page)
}

// 监听路由变化
watch(() => route.query, () => {
  initFromURL()
  getFoodList()
}, { deep: true })

// 页面初始化
onMounted(async () => {
  initFromURL()
  await Promise.all([
    getCategories(),
    getRegions(),
    getFoodList()
  ])
})
</script>

<style scoped lang="scss">
.food-list-page {
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
  max-width: 400px;
}

.filter-options {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: center;
  align-items: center;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
  
  label {
    font-size: 14px;
    color: #606266;
    white-space: nowrap;
  }
}

// 美食列表区域
.food-list-section {
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
:deep(.el-select) {
  min-width: 120px;
}

:deep(.el-pagination) {
  .el-pager li.is-active {
    background: #a8d8ea;
    border-color: #a8d8ea;
  }
  
  .el-pagination__jump {
    .el-input__inner:focus {
      border-color: #a8d8ea;
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .page-container {
    padding: 16px;
  }
  
  .filter-section,
  .food-list-section {
    padding: 20px;
  }
  
  .filter-options {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-item {
    justify-content: space-between;
  }
  
  .food-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 16px;
  }
  
  .list-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>