<template>
  <div class="food-section">
    <div class="section-header">
      <h3 class="section-title">{{ title }}</h3>
      <el-button 
        type="primary" 
        link 
        @click="$emit('more')"
        class="more-btn"
      >
        查看更多 <el-icon><ArrowRight /></el-icon>
      </el-button>
    </div>
    
    <div class="food-grid" v-loading="loading">
      <router-link
        v-for="food in foods"
        :key="food.id"
        :to="`/foods/${food.id}`"
        class="food-card-link"
      >
        <FoodCard :food="food" />
      </router-link>
    </div>
    
    <div v-if="!loading && foods.length === 0" class="empty-state">
      <el-empty description="暂无美食数据" />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Food } from '@/types'
import FoodCard from './FoodCard.vue'

interface Props {
  title: string
  foods: Food[]
  loading?: boolean
}

defineProps<Props>()
defineEmits<{
  more: []
}>()
</script>

<style lang="scss" scoped>
.food-section {
  margin-bottom: 50px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 25px;
}

.section-title {
  font-size: 24px;
  color: var(--text-primary);
  font-weight: 600;
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    bottom: -5px;
    left: 0;
    width: 40px;
    height: 3px;
    background: var(--primary-color);
    border-radius: 2px;
  }
}

.more-btn {
  font-size: 14px;
  
  .el-icon {
    margin-left: 4px;
    transition: transform 0.3s;
  }
  
  &:hover .el-icon {
    transform: translateX(2px);
  }
}

.food-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  min-height: 200px;
}

.food-card-link {
  display: block;
  text-decoration: none;
  color: inherit;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .section-title {
    font-size: 20px;
  }
  
  .food-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 15px;
  }
}

@media (max-width: 480px) {
  .food-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
}
</style>