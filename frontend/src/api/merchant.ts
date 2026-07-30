import { api } from './request'
import type { Merchant, Food, Comment, PaginationResponse } from '@/types'

// 商家端API
export const merchantApi = {
  // 入驻申请
  apply(data: {
    name: string
    description?: string
    address?: string
    contact_phone?: string
    logo?: string
  }) {
    return api.post<Merchant>('/merchant/apply', data)
  },

  // 获取入驻申请状态
  getApplyStatus() {
    return api.get<{ has_applied: boolean; merchant: Merchant | null; status?: string }>('/merchant/apply/status')
  },

  // 获取我的店铺信息
  getMyStore() {
    return api.get<Merchant>('/merchant/me')
  },

  // 更新店铺信息
  updateStore(data: Partial<Merchant>) {
    return api.put<Merchant>('/merchant/me', data)
  },

  // 获取我的美食列表
  getMyFoods(params?: { page?: number; per_page?: number; keyword?: string; category_id?: number; region?: string }) {
    return api.get<PaginationResponse<Food>>('/merchant/foods', params)
  },

  // 发布美食
  createFood(data: Partial<Food>) {
    return api.post<Food>('/merchant/foods', data)
  },

  // 更新美食
  updateFood(foodId: number, data: Partial<Food>) {
    return api.put<Food>(`/merchant/foods/${foodId}`, data)
  },

  // 删除美食
  deleteFood(foodId: number) {
    return api.delete(`/merchant/foods/${foodId}`)
  },

  // 获取我的评论列表
  getMyComments(params?: { page?: number; per_page?: number }) {
    return api.get<PaginationResponse<Comment>>('/merchant/comments', params)
  },

  // 回复评论
  replyComment(commentId: number, content: string) {
    return api.post<Comment>(`/merchant/comments/${commentId}/reply`, { content })
  },

  // 获取商家统计数据
  getStatistics(params?: { days?: number }) {
    return api.get<{
      overview: {
        food_count: number
        comment_count: number
        favorite_count: number
        unreplied_count: number
        total_view_count: number
      }
      comment_trend: Array<{ date: string; count: number }>
      by_category: Array<{ name: string; count: number }>
      rating_distribution: Array<{ rating: number; count: number }>
      top_foods_by_view: Array<{ name: string; view_count: number }>
    }>('/merchant/statistics', params)
  }
}
