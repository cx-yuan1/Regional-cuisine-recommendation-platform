// API响应类型
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

// 分页数据类型
export interface PaginationData {
  page: number
  per_page: number
  total: number
  pages: number
}

// 分页响应类型
export interface PaginationResponse<T = any> {
  items: T[]
  pagination: {
    total: number
    page: number
    per_page: number
    pages: number
  }
}

// 用户类型
export interface User {
  id: number
  username: string
  email?: string
  avatar?: string
  role: 'user' | 'admin' | 'merchant'
  /** 入驻申请状态：null 未申请，pending 审核中，approved 已通过，rejected 已拒绝 */
  merchant_status?: 'pending' | 'approved' | 'rejected' | null
  created_at: string
  updated_at: string
}

// 用户统计信息
export interface UserProfile extends User {
  statistics: {
    comment_count: number
    favorite_count: number
  }
}

// 美食分类类型
export interface FoodCategory {
  id: number
  name: string
  description?: string
  icon?: string
  sort_order: number
  status: number
  food_count: number
  created_at: string
  updated_at: string
}

// 美食类型
export interface Food {
  id: number
  name: string
  region: string
  category_id?: number
  category_name?: string
  merchant_id?: number
  merchant_name?: string
  description?: string
  image?: string
  price_range?: string
  taste_tags: string[]
  rating: number
  view_count: number
  created_at: string
  updated_at: string
  comment_count?: number
  favorite_count?: number
}
// 评论类型
export interface Comment {
  id: number
  user_id: number
  food_id: number
  content: string
  rating: number
  created_at: string
  user?: {
    id: number
    username: string
    avatar?: string
  }
  food?: {
    id: number
    name: string
    image?: string
  }
  reply_content?: string
  reply_at?: string
  replied_by?: number
}

// 商家类型
export interface Merchant {
  id: number
  user_id: number
  name: string
  description?: string
  logo?: string
  address?: string
  contact_phone?: string
  status: 'pending' | 'approved' | 'rejected'
  reject_reason?: string
  created_at: string
  updated_at: string
  user?: {
    id: number
    username: string
    email?: string
  }
}

// 收藏类型
export interface Favorite {
  id: number
  user_id: number
  food_id: number
  created_at: string
  food?: Food
}

// 轮播图类型
export interface Banner {
  id: number
  title: string
  image: string
  link_url?: string
  sort_order: number
  status: number
  created_at: string
}

// 公告类型
export interface Announcement {
  id: number
  title: string
  content: string
  type: 'notice' | 'event' | 'system'
  priority: number
  image?: string
  status: number
  start_time?: string
  end_time?: string
  view_count: number
  created_by: number
  created_at: string
  updated_at: string
}

// 公告类型选项
export interface AnnouncementType {
  value: string
  label: string
}

// 统计数据类型
export interface StatisticsOverview {
  user_count: number
  food_count: number
  comment_count: number
  favorite_count: number
  category_count: number
  today_user_count: number
}

// 美食统计类型
export interface FoodStatistics {
  by_category: Array<{ name: string; count: number }>
  by_region: Array<{ name: string; count: number }>
}

// 用户增长统计类型
export interface UserGrowthData {
  date: string
  count: number
}

// 表单类型
export interface LoginForm {
  username: string
  password: string
}

export interface RegisterForm {
  username: string
  password: string
  email?: string
  register_type?: 'user' | 'merchant'
  shop_name?: string
  shop_description?: string
  contact_phone?: string
  address?: string
}

export interface CommentForm {
  food_id: number
  content: string
  rating: number
}

// 查询参数类型
export interface FoodQuery {
  page?: number
  per_page?: number
  region?: string
  category_id?: number
  keyword?: string
  sort?: 'rating' | 'view_count' | 'created_at'
  order?: 'asc' | 'desc'
}

export interface CommentQuery {
  page?: number
  per_page?: number
  sort?: 'created_at' | 'rating'
  order?: 'asc' | 'desc'
}

export interface AnnouncementQuery {
  page?: number
  per_page?: number
  type?: string
  keyword?: string
}