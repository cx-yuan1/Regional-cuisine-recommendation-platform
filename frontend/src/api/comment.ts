import { api } from './request'
import type { Comment, CommentForm, CommentQuery, PaginationResponse } from '@/types'

// 评论相关API
export const commentApi = {
  // 获取美食评论列表
  getFoodComments(foodId: number, params: CommentQuery = {}) {
    return api.get<PaginationResponse<Comment>>(`/comments/food/${foodId}`, params)
  },

  // 添加评论
  addComment(data: CommentForm) {
    return api.post<Comment>('/comments', data)
  },

  // 删除评论
  deleteComment(id: number) {
    return api.delete(`/comments/${id}`)
  },

  // 获取用户评论列表
  getUserComments(params: CommentQuery = {}) {
    return api.get<PaginationResponse<Comment>>('/comments/my', params)
  }
}