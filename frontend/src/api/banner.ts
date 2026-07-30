import { api } from './request'
import type { Banner } from '@/types'

// 轮播图API
export const bannerApi = {
  // 获取启用的轮播图列表
  getBanners() {
    return api.get<Banner[]>('/banners')
  },

  // 获取轮播图详情
  getBannerDetail(id: number) {
    return api.get<Banner>(`/banners/${id}`)
  }
}