import request from './request'

// 管理后台API接口

/**
 * 获取统计概览数据
 */
export const getStatisticsOverview = () => {
  return request.get('/admin/statistics/overview')
}

/**
 * 获取用户统计数据
 * @param days 统计天数
 */
export const getUserStatistics = (days: number = 7) => {
  return request.get('/admin/statistics/users', {
    params: { days }
  })
}

/**
 * 获取美食统计数据
 */
export const getFoodStatistics = () => {
  return request.get('/admin/statistics/foods')
}

/**
 * 获取用户列表
 */
export const getUsers = (params?: {
  keyword?: string
  role?: string
  page?: number
  per_page?: number
}) => {
  return request.get('/admin/users', { params })
}

/**
 * 更新用户信息
 */
export const updateUser = (userId: number, data: any) => {
  return request.put(`/admin/users/${userId}`, data)
}

/**
 * 删除用户
 */
export const deleteUser = (userId: number) => {
  return request.delete(`/admin/users/${userId}`)
}

/**
 * 获取管理后台美食列表
 */
export const getAdminFoods = (params?: {
  keyword?: string
  category_id?: number
  region?: string
  page?: number
  per_page?: number
}) => {
  return request.get('/admin/foods', { params })
}
/**
 * 创建美食
 */
export const createFood = (data: any) => {
  return request.post('/admin/foods', data)
}

/**
 * 更新美食
 */
export const updateFood = (foodId: number, data: any) => {
  return request.put(`/admin/foods/${foodId}`, data)
}

/**
 * 删除美食
 */
export const deleteFood = (foodId: number) => {
  return request.delete(`/admin/foods/${foodId}`)
}

/**
 * 获取管理后台评论列表
 */
export const getAdminComments = (params?: {
  keyword?: string
  food_id?: number
  user_id?: number
  page?: number
  per_page?: number
}) => {
  return request.get('/admin/comments', { params })
}

/**
 * 删除评论
 */
export const deleteComment = (commentId: number) => {
  return request.delete(`/admin/comments/${commentId}`)
}

/**
 * 获取管理后台轮播图列表
 */
export const getAdminBanners = () => {
  return request.get('/admin/banners')
}

/**
 * 创建轮播图
 */
export const createBanner = (data: any) => {
  return request.post('/admin/banners', data)
}

/**
 * 更新轮播图
 */
export const updateBanner = (bannerId: number, data: any) => {
  return request.put(`/admin/banners/${bannerId}`, data)
}

/**
 * 删除轮播图
 */
export const deleteBanner = (bannerId: number) => {
  return request.delete(`/admin/banners/${bannerId}`)
}

/**
 * 获取管理后台分类列表
 */
export const getAdminCategories = () => {
  return request.get('/admin/food-categories')
}

/**
 * 创建分类
 */
export const createCategory = (data: any) => {
  return request.post('/admin/food-categories', data)
}

/**
 * 更新分类
 */
export const updateCategory = (categoryId: number, data: any) => {
  return request.put(`/admin/food-categories/${categoryId}`, data)
}

/**
 * 删除分类
 */
export const deleteCategory = (categoryId: number) => {
  return request.delete(`/admin/food-categories/${categoryId}`)
}

/**
 * 获取管理后台公告列表
 */
export const getAdminAnnouncements = (params?: {
  keyword?: string
  type?: string
  status?: number
  page?: number
  per_page?: number
}) => {
  return request.get('/admin/announcements', { params })
}

/**
 * 创建公告
 */
export const createAnnouncement = (data: any) => {
  return request.post('/admin/announcements', data)
}

/**
 * 更新公告
 */
export const updateAnnouncement = (announcementId: number, data: any) => {
  return request.put(`/admin/announcements/${announcementId}`, data)
}

/**
 * 删除公告
 */
export const deleteAnnouncement = (announcementId: number) => {
  return request.delete(`/admin/announcements/${announcementId}`)
}

/**
 * 获取商家入驻申请列表
 */
export const getMerchantApplications = (params?: {
  status?: string
  page?: number
  per_page?: number
}) => {
  return request.get('/admin/merchants', { params })
}

/**
 * 通过商家入驻申请
 */
export const approveMerchant = (merchantId: number) => {
  return request.put(`/admin/merchants/${merchantId}/approve`)
}

/**
 * 拒绝商家入驻申请
 */
export const rejectMerchant = (merchantId: number, rejectReason?: string) => {
  return request.put(`/admin/merchants/${merchantId}/reject`, { reject_reason: rejectReason })
}