import { api } from './request'
import type { Announcement, PaginationResponse } from '@/types'

// 公告API
export const announcementApi = {
  // 获取公告列表
  getAnnouncements(params: {
    type?: string
    status?: number
    keyword?: string
    page?: number
    per_page?: number
  } = {}) {
    return api.get<PaginationResponse<Announcement>>('/announcements', params)
  },

  // 获取公告详情
  getAnnouncementDetail(id: number) {
    return api.get<Announcement>(`/announcements/${id}`)
  },

  // 获取最新公告（首页展示）
  getLatestAnnouncements(limit: number = 5) {
    return api.get<Announcement[]>('/announcements/latest', { limit })
  },

  // 获取公告类型列表
  getAnnouncementTypes() {
    return api.get<Array<{ value: string; label: string }>>('/announcements/types')
  }
}