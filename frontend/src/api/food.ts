import { api } from './request'
import type { Food, FoodQuery, PaginationResponse } from '@/types'

// 美食API
export const foodApi = {
  // 获取美食列表
  getFoodList(params: FoodQuery = {}) {
    return api.get<PaginationResponse<Food>>('/foods', params)
  },

  // 获取美食详情
  getFoodDetail(foodId: number) {
    return api.get<Food>(`/foods/${foodId}`)
  },

  // 获取热门美食
  getHotFoods(limit: number = 10) {
    return api.get<Food[]>('/foods/hot', { limit })
  },

  // 获取最新美食
  getLatestFoods(limit: number = 10) {
    return api.get<Food[]>('/foods/latest', { limit })
  },

  // 获取推荐美食
  getRecommendedFoods(limit: number = 10, min_rating: number = 4.0) {
    return api.get<Food[]>('/foods/recommended', { limit, min_rating })
  },

  // 获取地域列表
  getRegions() {
    return api.get<string[]>('/foods/regions')
  }
}