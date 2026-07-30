import { api } from './request'
import type { User, UserProfile, LoginForm, RegisterForm } from '@/types'

// 用户认证API
export const userApi = {
  // 用户注册
  register(data: RegisterForm) {
    return api.post<User>('/user/register', data)
  },

  // 用户登录
  login(data: LoginForm) {
    return api.post<User>('/user/login', data)
  },

  // 退出登录
  logout() {
    return api.post('/user/logout')
  },

  // 获取用户信息
  getUserInfo() {
    return api.get<User>('/user/info')
  },

  // 获取用户详细资料
  getUserProfile() {
    return api.get<UserProfile>('/user/profile')
  },

  // 更新用户信息
  updateUser(data: Partial<User>) {
    return api.put<User>('/user/update', data)
  },

  // 更新用户资料
  updateProfile(data: Partial<User>) {
    return api.put<User>('/user/profile', data)
  },

  // 上传头像
  uploadAvatar(file: File) {
    const formData = new FormData()
    formData.append('avatar', file)
    return api.upload('/user/update', formData)
  }
}