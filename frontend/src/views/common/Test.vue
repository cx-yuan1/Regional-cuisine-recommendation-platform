<template>
  <div class="test-page">
    <div class="page-container">
      <h1>功能测试页面</h1>
      
      <!-- API测试区域 -->
      <div class="test-section">
        <h2>API接口测试</h2>
        <div class="test-buttons">
          <el-button @click="testFoodList">测试美食列表</el-button>
          <el-button @click="testCategories">测试分类列表</el-button>
          <el-button @click="testBanners">测试轮播图</el-button>
          <el-button @click="testAnnouncements">测试公告</el-button>
        </div>
        
        <div class="test-results" v-if="testResult">
          <h3>测试结果：</h3>
          <pre>{{ testResult }}</pre>
        </div>
      </div>
      
      <!-- 组件测试区域 -->
      <div class="test-section">
        <h2>组件测试</h2>
        
        <!-- 美食卡片测试 -->
        <div class="component-test">
          <h3>美食卡片组件</h3>
          <div class="food-cards">
            <FoodCard 
              v-for="food in sampleFoods" 
              :key="food.id" 
              :food="food"
              @click="handleFoodClick(food)"
            />
          </div>
        </div>
        
        <!-- 分类导航测试 -->
        <div class="component-test">
          <h3>分类导航组件</h3>
          <CategoryNav />
        </div>
      </div>
      
      <!-- 样式测试区域 -->
      <div class="test-section">
        <h2>样式测试</h2>
        <div class="style-test">
          <el-button>默认按钮</el-button>
          <el-button type="primary">主要按钮</el-button>
          <el-button type="success">成功按钮</el-button>
          <el-button type="warning">警告按钮</el-button>
          <el-button type="danger">危险按钮</el-button>
        </div>
        
        <div class="style-test">
          <el-input placeholder="请输入内容" style="width: 200px;" />
          <el-select placeholder="请选择" style="width: 200px; margin-left: 10px;">
            <el-option label="选项1" value="1" />
            <el-option label="选项2" value="2" />
          </el-select>
        </div>
        
        <div class="style-test">
          <el-tag>默认标签</el-tag>
          <el-tag type="success">成功标签</el-tag>
          <el-tag type="info">信息标签</el-tag>
          <el-tag type="warning">警告标签</el-tag>
          <el-tag type="danger">危险标签</el-tag>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { foodApi } from '@/api/food'
import { foodCategoryApi } from '@/api/foodCategory'
import { bannerApi } from '@/api/banner'
import { announcementApi } from '@/api/announcement'
import FoodCard from '@/components/food/FoodCard.vue'
import CategoryNav from '@/components/common/CategoryNav.vue'
import type { Food } from '@/types'

// 响应式数据
const testResult = ref('')

// 示例美食数据
const sampleFoods = ref<Food[]>([
  {
    id: 1,
    name: '北京烤鸭',
    region: '北京',
    category_id: 1,
    category_name: '特色菜',
    description: '北京最著名的特色美食',
    image: '/placeholder-food.jpg',
    price_range: '100-200元',
    taste_tags: ['香脆', '鲜美', '经典'],
    rating: 4.8,
    view_count: 1520,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z'
  },
  {
    id: 2,
    name: '四川火锅',
    region: '四川',
    category_id: 2,
    category_name: '火锅',
    description: '正宗四川麻辣火锅',
    image: '/placeholder-food.jpg',
    price_range: '80-150元',
    taste_tags: ['麻辣', '鲜香', '热辣'],
    rating: 4.6,
    view_count: 2340,
    created_at: '2024-01-02T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z'
  }
])

// API测试方法
const testFoodList = async () => {
  try {
    const response = await foodApi.getFoodList({ page: 1, per_page: 5 })
    testResult.value = JSON.stringify(response, null, 2)
    ElMessage.success('美食列表API测试成功')
  } catch (error) {
    testResult.value = `错误: ${error}`
    ElMessage.error('美食列表API测试失败')
  }
}

const testCategories = async () => {
  try {
    const response = await foodCategoryApi.getActiveCategories()
    testResult.value = JSON.stringify(response, null, 2)
    ElMessage.success('分类列表API测试成功')
  } catch (error) {
    testResult.value = `错误: ${error}`
    ElMessage.error('分类列表API测试失败')
  }
}

const testBanners = async () => {
  try {
    const response = await bannerApi.getBanners()
    testResult.value = JSON.stringify(response, null, 2)
    ElMessage.success('轮播图API测试成功')
  } catch (error) {
    testResult.value = `错误: ${error}`
    ElMessage.error('轮播图API测试失败')
  }
}

const testAnnouncements = async () => {
  try {
    const response = await announcementApi.getAnnouncements({ page: 1, per_page: 5 })
    testResult.value = JSON.stringify(response, null, 2)
    ElMessage.success('公告API测试成功')
  } catch (error) {
    testResult.value = `错误: ${error}`
    ElMessage.error('公告API测试失败')
  }
}

const handleFoodClick = (food: Food) => {
  ElMessage.info(`点击了美食: ${food.name}`)
}
</script>

<style lang="scss" scoped>
.test-page {
  min-height: 100vh;
  background: var(--bg-color);
  padding: 20px;
}

.page-container {
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  text-align: center;
  color: var(--text-primary);
  margin-bottom: 40px;
}

.test-section {
  background: var(--card-bg);
  border-radius: var(--border-radius-base);
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: var(--box-shadow-base);
  
  h2 {
    color: var(--text-primary);
    margin-bottom: 20px;
    border-bottom: 2px solid #a8d8ea;
    padding-bottom: 8px;
  }
  
  h3 {
    color: var(--text-regular);
    margin-bottom: 16px;
  }
}

.test-buttons {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.test-results {
  background: #f8f9fa;
  border-radius: var(--border-radius-base);
  padding: 16px;
  
  pre {
    max-height: 300px;
    overflow-y: auto;
    font-size: 12px;
    line-height: 1.4;
  }
}

.component-test {
  margin-bottom: 30px;
}

.food-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 16px;
}

.style-test {
  margin-bottom: 20px;
  
  .el-button + .el-button {
    margin-left: 10px;
  }
  
  .el-tag + .el-tag {
    margin-left: 10px;
  }
}

@media (max-width: 768px) {
  .test-buttons {
    flex-direction: column;
  }
  
  .food-cards {
    grid-template-columns: 1fr;
  }
  
  .style-test {
    .el-button,
    .el-input,
    .el-select {
      margin-bottom: 10px;
      margin-left: 0 !important;
    }
  }
}
</style>