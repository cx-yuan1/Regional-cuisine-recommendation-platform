import { api } from './request'
import type { Food } from '@/types'

// 推荐相关API
export const recommendApi = {
  // 获取个性化推荐（需登录）
  getPersonalRecommend(limit = 12) {
    return api.get<Food[]>('/recommend/personal', { limit })
  },

  // 获取热门推荐
  getHotRecommend(limit = 12, categoryId?: number, region?: string) {
    return api.get<Food[]>('/recommend/hot', { limit, category_id: categoryId, region })
  },

  // 获取相似美食推荐
  getSimilarFoods(foodId: number, limit = 4) {
    return api.get<Food[]>(`/recommend/similar/${foodId}`, { limit })
  },

  // 获取新品推荐
  getNewRecommend(limit = 12) {
    return api.get<Food[]>('/recommend/new', { limit })
  },

  // 获取趋势推荐
  getTrendingRecommend(limit = 12, days = 7) {
    return api.get<Food[]>('/recommend/trending', { limit, days })
  },

  // 按分类推荐
  getCategoryRecommend(categoryId: number, limit = 12) {
    return api.get<Food[]>(`/recommend/by-category/${categoryId}`, { limit })
  },

  // 按地域推荐
  getRegionRecommend(region: string, limit = 12) {
    return api.get<Food[]>('/recommend/by-region', { region, limit })
  }
}