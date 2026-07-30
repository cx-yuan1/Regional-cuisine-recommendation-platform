import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { userApi } from '@/api/user'
import type { User, UserProfile, LoginForm, RegisterForm } from '@/types'
import { ElMessage } from 'element-plus'

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref<User | null>(null)
  const userProfile = ref<UserProfile | null>(null)
  const isLoggedIn = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isMerchant = computed(() => user.value?.role === 'merchant')
  /** 商家入驻已通过审核（可访问商家首页、店铺信息等） */
  const isMerchantApproved = computed(() => user.value?.merchant_status === 'approved')

  // 登录
  const login = async (loginForm: LoginForm) => {
    try {
      const response = await userApi.login(loginForm)
      // 后端返回的数据格式是 { code: 200, data: user, message: '登录成功' }
      // API拦截器已经处理了，这里直接使用 response.data
      user.value = response.data
      console.log('登录成功，用户数据:', user.value) // 调试日志
      ElMessage.success('登录成功')
      return response.data
    } catch (error) {
      console.error('登录失败:', error)
      throw error
    }
  }

  // 注册
  const register = async (registerForm: RegisterForm) => {
    try {
      const response = await userApi.register(registerForm)
      // 注册成功但不设置用户状态，需要用户手动登录
      return response.data
    } catch (error) {
      throw error
    }
  }

  // 退出登录
  const logout = async () => {
    try {
      await userApi.logout()
      user.value = null
      userProfile.value = null
      ElMessage.success('退出登录成功')
    } catch (error) {
      // 即使接口失败也清除本地状态
      user.value = null
      userProfile.value = null
    }
  }

  // 获取用户信息
  const getUserInfo = async () => {
    try {
      const response = await userApi.getUserInfo()
      user.value = response.data
      return response.data
    } catch (error) {
      // 如果获取用户信息失败，可能是未登录
      user.value = null
      throw error
    }
  }

  // 刷新用户信息（别名方法）
  const fetchUserInfo = async () => {
    return await getUserInfo()
  }

  // 获取用户详细资料
  const getUserProfile = async () => {
    try {
      const response = await userApi.getUserProfile()
      userProfile.value = response.data
      return response.data
    } catch (error) {
      throw error
    }
  }

  // 更新用户信息
  const updateUser = async (data: Partial<User>) => {
    try {
      const response = await userApi.updateUser(data)
      user.value = response.data
      ElMessage.success('更新成功')
      return response.data
    } catch (error) {
      throw error
    }
  }

  // 上传头像
  const uploadAvatar = async (file: File) => {
    try {
      const response = await userApi.uploadAvatar(file)
      if (user.value) {
        user.value.avatar = response.data.avatar
      }
      ElMessage.success('头像上传成功')
      return response.data
    } catch (error) {
      throw error
    }
  }

  // 初始化用户状态（应用启动时调用）
  const initUser = async () => {
    try {
      await getUserInfo()
    } catch (error) {
      // 静默处理，用户未登录
      console.log('用户未登录')
    }
  }

  // 获取登录后的重定向路径
  // redirectParam: 登录前尝试访问的页面路径（来自路由守卫）
  const getRedirectPath = (redirectParam?: string) => {
    if (!user.value) {
      return '/'
    }
    
    // 管理员：始终跳转到管理后台
    if (user.value.role === 'admin') {
      return '/admin/dashboard'
    }
    // 商家：入驻通过则跳转商家首页，否则跳转入驻申请
    if (user.value.role === 'merchant') {
      return user.value.merchant_status === 'approved' ? '/merchant/dashboard' : '/merchant/apply'
    }
    
    // 普通用户：有重定向参数且为前台页面则跳转回原页面，否则跳转到前台首页
    if (redirectParam && !redirectParam.startsWith('/admin') && !redirectParam.startsWith('/merchant')) {
      return redirectParam
    }
    return '/'
  }

  return {
    // 状态
    user,
    userProfile,
    isLoggedIn,
    isAdmin,
    isMerchant,
    isMerchantApproved,
    
    // 方法
    login,
    register,
    logout,
    getUserInfo,
    fetchUserInfo,
    getUserProfile,
    updateUser,
    uploadAvatar,
    initUser,
    getRedirectPath
  }
})