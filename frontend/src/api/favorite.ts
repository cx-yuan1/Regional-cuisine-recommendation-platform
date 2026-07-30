import { api } from './request'
import type { Favorite, PaginationResponse } from '@/types'

// 收藏API
export const favoriteApi = {
  // 收藏美食
  addFavorite(foodId: number) {
    return api.post<Favorite>('/favorites', { food_id: foodId })
  },

  // 取消收藏（通过收藏ID）
  deleteFavorite(id: number) {
    return api.delete(`/favorites/${id}`)
  },

  // 取消收藏（通过美食ID）
  deleteFavoriteByFood(foodId: number) {
    return api.delete(`/favorites/food/${foodId}`)
  },

  // 获取我的收藏
  getMyFavorites(params: { page?: number; per_page?: number } = {}) {
    return api.get<PaginationResponse<Favorite>>('/favorites/my', params)
  },

  // 检查是否已收藏
  checkFavorite(foodId: number) {
    return api.get<{ is_favorited: boolean; favorite_id?: number }>(`/favorites/check/${foodId}`)
  }
}