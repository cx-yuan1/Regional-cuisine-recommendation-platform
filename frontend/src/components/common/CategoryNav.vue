<template>
  <div class="category-nav" v-if="categories.length > 0">
    <div class="category-container">
      <h3 class="category-title">美食分类</h3>
      <div class="category-grid">
        <div 
          v-for="category in displayCategories" 
          :key="category.id"
          class="category-item"
          @click="goToCategoryFoods(category.id)"
        >
          <div class="category-icon">
            <img 
              v-if="category.icon" 
              :src="getCategoryIcon(category.icon)" 
              :alt="category.name"
              class="icon-image"
            />
            <el-icon v-else class="default-icon"><Food /></el-icon>
          </div>
          <div class="category-name">{{ category.name }}</div>
          <div class="category-desc" v-if="category.description">
            {{ category.description }}
          </div>
        </div>
        
        <!-- 更多分类按钮 -->
        <div 
          v-if="categories.length > maxDisplay"
          class="category-item more-item"
          @click="showAllCategories = !showAllCategories"
        >
          <div class="category-icon">
            <el-icon class="more-icon">
              <MoreFilled v-if="!showAllCategories" />
              <Fold v-else />
            </el-icon>
          </div>
          <div class="category-name">
            {{ showAllCategories ? '收起' : '更多' }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Food, MoreFilled, Fold } from '@element-plus/icons-vue'
import { foodCategoryApi } from '@/api/foodCategory'
import type { FoodCategory } from '@/types'

const router = useRouter()

// 响应式数据
const categories = ref<FoodCategory[]>([])
const loading = ref(false)
const showAllCategories = ref(false)
const maxDisplay = 8 // 默认显示的分类数量

// 计算显示的分类
const displayCategories = computed(() => {
  if (showAllCategories.value || categories.value.length <= maxDisplay) {
    return categories.value
  }
  return categories.value.slice(0, maxDisplay)
})

// 获取分类列表
const getCategories = async () => {
  try {
    loading.value = true
    const response = await foodCategoryApi.getActiveCategories()
    categories.value = response.data
  } catch (error) {
    console.error('获取分类列表失败:', error)
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

// 跳转到分类美食页面
const goToCategoryFoods = (categoryId: number) => {
  router.push(`/category/${categoryId}`)
}

// 页面初始化
onMounted(() => {
  getCategories()
})
</script>

<style scoped lang="scss">
.category-nav {
  margin-bottom: 32px;
}

.category-container {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.category-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 20px 0;
  text-align: center;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 20px;
  justify-items: center;
}

.category-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  border-radius: 12px;
  background: #f8f9fa;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 100px;
  text-align: center;
  
  &:hover {
    background: #e9ecef;
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  }
  
  &.more-item {
    background: linear-gradient(135deg, #a8d8ea 0%, #7fb3d3 100%);
    color: white;
    
    &:hover {
      background: linear-gradient(135deg, #7fb3d3 0%, #6ba3c7 100%);
    }
  }
}

.category-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
  border-radius: 50%;
  background: rgba(168, 216, 234, 0.1);
}

.icon-image {
  width: 32px;
  height: 32px;
  object-fit: cover;
  border-radius: 50%;
}

.default-icon {
  font-size: 24px;
  color: #a8d8ea;
}

.more-icon {
  font-size: 24px;
  color: white;
}

.category-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
  
  .more-item & {
    color: white;
  }
}

.category-desc {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
  text-align: center;
}

// 响应式设计
@media (max-width: 768px) {
  .category-container {
    padding: 20px;
  }
  
  .category-grid {
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 16px;
  }
  
  .category-item {
    padding: 12px;
    min-width: 80px;
  }
  
  .category-icon {
    width: 40px;
    height: 40px;
  }
  
  .icon-image {
    width: 28px;
    height: 28px;
  }
  
  .default-icon,
  .more-icon {
    font-size: 20px;
  }
  
  .category-name {
    font-size: 13px;
  }
  
  .category-desc {
    font-size: 11px;
  }
}
</style>