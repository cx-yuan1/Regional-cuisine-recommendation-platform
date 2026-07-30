import { api } from './request'
import type { FoodCategory, Food, PaginationResponse } from '@/types'

// 美食分类API
export const foodCategoryApi = {
  // 获取所有启用的分类
  getActiveCategories() {
    return api.get<FoodCategory[]>('/food-categories/active')
  },

  // 获取分类列表（分页）
  getCategoryList(params: { page?: number; per_page?: number; status?: number } = {}) {
    return api.get<PaginationResponse<FoodCategory>>('/food-categories', params)
  },

  // 获取分类详情
  getCategoryDetail(id: number) {
    return api.get<FoodCategory>(`/food-categories/${id}`)
  },

  // 获取分类下的美食
  getCategoryFoods(id: number, params: {
    page?: number
    per_page?: number
    sort?: 'rating' | 'view_count' | 'created_at'
    order?: 'asc' | 'desc'
  } = {}) {
    return api.get<{
      category: FoodCategory
      foods: PaginationResponse<Food>
    }>(`/food-categories/${id}/foods`, params)
  }
}