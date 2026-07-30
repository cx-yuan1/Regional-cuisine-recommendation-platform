<template>
  <div class="food-card" @click="$emit('click')">
    <div class="card-image">
      <img 
        :src="getFoodImage(food.image)" 
        :alt="food.name"
        @error="handleImageError"
      />
      <div class="image-overlay">
        <div class="rating" v-if="food.rating > 0">
          <el-icon><Star /></el-icon>
          <span>{{ food.rating.toFixed(1) }}</span>
        </div>
      </div>
    </div>
    
    <div class="card-content">
      <h4 class="food-name">{{ food.name }}</h4>
      <p class="food-region">{{ food.region }}</p>
      <p class="food-category" v-if="food.category_name">{{ food.category_name }}</p>
      
      <div class="food-tags" v-if="food.taste_tags && food.taste_tags.length > 0">
        <el-tag 
          v-for="tag in food.taste_tags.slice(0, 3)" 
          :key="tag" 
          size="small"
          type="info"
        >
          {{ tag }}
        </el-tag>
      </div>
      
      <div class="card-footer">
        <div class="stats">
          <span class="view-count">
            <el-icon><View /></el-icon>
            {{ formatNumber(food.view_count) }}
          </span>
          <span class="price-range" v-if="food.price_range">{{ food.price_range }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Food } from '@/types'

interface Props {
  food: Food
}

defineProps<Props>()
defineEmits<{
  click: []
}>()

const getFoodImage = (imagePath?: string) => {
  if (!imagePath) {
    return '/placeholder-food.jpg' // 默认占位图
  }
  if (imagePath.startsWith('http')) {
    return imagePath
  }
  return `http://localhost:5000${imagePath}`
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = '/placeholder-food.jpg' // 加载失败时显示占位图
}

const formatNumber = (num: number) => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + 'w'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num.toString()
}
</script>

<style lang="scss" scoped>
.food-card {
  background: var(--card-bg);
  border-radius: var(--border-radius-base);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: var(--box-shadow-base);
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: var(--box-shadow-light);
  }
}

.card-image {
  position: relative;
  height: 200px;
  overflow: hidden;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
  }
  
  &:hover img {
    transform: scale(1.05);
  }
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.3));
  display: flex;
  align-items: flex-end;
  padding: 15px;
}

.rating {
  background: rgba(0, 0, 0, 0.7);
  color: #ffd700;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 2px;
  
  .el-icon {
    font-size: 12px;
  }
}

.card-content {
  padding: 16px;
}

.food-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.food-region {
  font-size: 14px;
  color: var(--primary-color);
  margin-bottom: 4px;
  font-weight: 500;
}

.food-category {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.food-tags {
  margin-bottom: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  
  .el-tag {
    font-size: 11px;
  }
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stats {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: var(--text-secondary);
}

.view-count {
  display: flex;
  align-items: center;
  gap: 2px;
  
  .el-icon {
    font-size: 12px;
  }
}

.price-range {
  color: var(--primary-color);
  font-weight: 500;
}

@media (max-width: 480px) {
  .card-image {
    height: 160px;
  }
  
  .card-content {
    padding: 12px;
  }
  
  .food-name {
    font-size: 15px;
  }
}
</style>